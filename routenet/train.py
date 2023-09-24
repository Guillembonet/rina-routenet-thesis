import os
import re
import sys
import tensorflow as tf
from matrix_gen import input_fn

from models.delay_model import RouteNet_Fermi as routenet_delay
from models.jitter_model import RouteNet_Fermi as routenet_jitter
from models.loss_model import RouteNet_Fermi as routenet_loss

def denorm_MAPE(y_true, y_pred):
    denorm_y_true = tf.math.exp(y_true)
    denorm_y_pred = tf.math.exp(y_pred)
    mape = tf.abs((denorm_y_pred - denorm_y_true) / denorm_y_true) * 100
    return mape

def R_squared(y, y_pred):
    residual = tf.reduce_sum(tf.square(tf.subtract(y, y_pred)))
    total = tf.reduce_sum(tf.square(tf.subtract(y, tf.reduce_mean(y))))
    r2 = tf.subtract(1.0, tf.math.divide(residual, total))
    return r2

if len(sys.argv) != 2:
    print("provide one argument: delay, jitter or losses")
    sys.exit()

model = routenet_delay()
cp_folder = f'./trained/ckpt_delay'
loss_object = tf.keras.losses.MeanAbsolutePercentageError()
metrics = None
ckpt_dir = './trained/ckpt_delay'
if sys.argv[1] == "delay":
    print("training delay")
elif sys.argv[1] == "jitter":
    model = routenet_jitter()
    cp_folder = f'./models/ckpt_jitter'
    loss_object = tf.keras.losses.MeanSquaredError()
    metrics=[denorm_MAPE]
    ckpt_dir = './trained/ckpt_jitter'
    print("training jitter")
elif sys.argv[1] == "losses":
    model = routenet_loss()
    cp_folder = f'./trained/ckpt_losses'
    loss_object = tf.keras.losses.BinaryCrossentropy(from_logits=False)
    metrics = [R_squared, "MAE"]
    ckpt_dir = './trained/ckpt_losses'
    print("training losses")
else:
    print("unknown model, will default to delay")

#load model
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(loss=loss_object,
              optimizer=optimizer,
              run_eagerly=False,
              metrics=metrics)

latest = tf.train.latest_checkpoint(cp_folder)

if latest is None:
    print("no pretrained model")
    #sys.exit()
else:
    print("Found a pretrained model, restoring...")
    model.load_weights(latest)

filepath = os.path.join(ckpt_dir, "{epoch:02d}-0.2")

cp_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=filepath,
    verbose=1,
    mode="min",
    monitor='val_loss',
    save_best_only=False,
    save_weights_only=True,
    save_freq='epoch')

print("loaded checkpoint")

#Make predictions
print("training...")
ds_test = input_fn(
    MG=[
        [0,0,2000,0],
        [0,0,2000,0],
        [2000,2000,0,2000],
        [0,0,2000,0]
    ],
    MT=[
        [0,0,0,1000],
        [0,0,0,1000],
        [0,0,0,0],
        [0,0,0,0]
    ],
    MR=[
        [[0]    ,[0,2,1],[0,2],[0,2,3]],
        [[1,2,0],[1]    ,[1,2],[1,2,3]],
        [[2,0]  ,[2,1]  ,[2]  ,[2,3]  ],
        [[3,2,0],[3,2,1],[3,2],[3]    ],
    ]
)
# ds_test = input_fn(
#     MG=[
#         [0,500,0],
#         [500,0,500],
#         [0,500,0],
#     ],
#     MT=[
#         [0,1000,1000],
#         [0,0,0],
#         [0,0,0]
#     ],
#     MR=[
#         [[0]  ,[0,1],[0,1,2]],
#         [[1,0],[1],[1,2]],
#         [[2,1,0],[2,1],[2]]
#     ]
# )
if sys.argv[1] == "delay":
    model.fit(ds_test,
        epochs=1,
        steps_per_epoch=1,
        validation_steps=1,
        callbacks=[cp_callback],
        use_multiprocessing=True)
elif sys.argv[1] == "jitter":
    model.fit(ds_test,
        epochs=150,
        steps_per_epoch=2000,
        validation_steps=200,
        callbacks=[cp_callback],
        use_multiprocessing=True)
elif sys.argv[1] == "losses":
    model.fit(ds_test,
        epochs=1,
        steps_per_epoch=1,
        validation_steps=1,
        callbacks=[cp_callback],
        use_multiprocessing=True)
