docker run -it --rm --name routenet -v $(pwd):/home tensorflow/tensorflow:2.6.1 sh -c "pip install networkx; cd home; bash"

#docker run -d --name routenet -v $(pwd):/home tensorflow/tensorflow:2.6.1 sh -c "pip install networkx; sleep infinity"