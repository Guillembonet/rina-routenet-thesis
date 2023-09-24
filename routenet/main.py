import os
import re
import sys
import tensorflow as tf
import json
from matrix_gen import input_fn

from models.delay_model import RouteNet_Fermi as routenet_delay
from models.jitter_model import RouteNet_Fermi as routenet_jitter
from models.loss_model import RouteNet_Fermi as routenet_loss

if len(sys.argv) != 3:
    print("usage: main.py <type (delay, jitter or losses)> <traffic_matrix>")
    sys.exit()

model = routenet_delay()
cp_folder = f'./trained/ckpt_delay'
loss_object = tf.keras.losses.MeanAbsolutePercentageError()
if sys.argv[1] == "jitter":
    model = routenet_jitter()
    cp_folder = f'./models/ckpt_jitter'
    loss_object = tf.keras.losses.MeanSquaredError()
elif sys.argv[1] == "losses":
    model = routenet_loss()
    cp_folder = f'./trained/ckpt_losses'
    loss_object = tf.keras.losses.BinaryCrossentropy(from_logits=False)

#load model
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

model.compile(loss=loss_object,
              optimizer=optimizer,
              run_eagerly=False)
best = None
best_mre = float('inf')
for f in os.listdir(cp_folder):
    if os.path.isfile(os.path.join(cp_folder, f)):
        reg = re.findall("\d+\.\d+", f)
        if len(reg) > 0:
            mre = float(reg[0])
            if mre <= best_mre:
                best = f.replace('.index', '')
                best = best.replace('.data', '')
                best = best.replace('-00000-of-00001', '')
                best_mre = mre
model.load_weights(os.path.join(cp_folder, best))

# traffic_matrix = json.loads(sys.argv[2])
# #Make predictions
# ds_test = input_fn(
#     MG=[
#         [0,0,2000,0],
#         [0,0,2000,0],
#         [2000,2000,0,2000],
#         [0,0,2000,0]
#     ],
#     MT=traffic_matrix,
#     MR=[
#         [[0]    ,[0,2,1],[0,2],[0,2,3]],
#         [[1,2,0],[1]    ,[1,2],[1,2,3]],
#         [[2,0]  ,[2,1]  ,[2]  ,[2,3]  ],
#         [[3,2,0],[3,2,1],[3,2],[3]    ],
#     ]
# )
ds_test = input_fn(
    MG=[
        [0,0,2000,0],
        [0,0,2000,0],
        [2000,2000,0,2000],
        [0,0,2000,0]
    ],
    MT=[
        [0,0,1000,1000],
        [0,0,0,0],
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
ds_test = ds_test.prefetch(tf.data.experimental.AUTOTUNE)
predictions = model.predict(ds_test, verbose=1)
print(json.dumps(predictions.tolist()))
