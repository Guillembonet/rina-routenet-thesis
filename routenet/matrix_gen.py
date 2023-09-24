import networkx as nx
import tensorflow as tf
import numpy as np

from utils import hypergraph_to_input_data, network_to_hypergraph
from objects import TimeDist, SizeDist
from typing import List

# all with traffic
def get_traffic_matrix(matrix: List[List[float]]):
    result_matrix = []
    for row in matrix:
        result_row = []
        for element in row:
            if element > 0:
                pkt_size = 200.
                total_pkts_gen = 1000
                result_row.append({'AggInfo': {'AvgBw': element, 'PktsGen': element/pkt_size, 'TotalPktsGen': total_pkts_gen},
                                   'Flows': [{'TimeDist': TimeDist(0),
                                              'TimeDistParams': {'EqLambda': element, 'AvgPktsLambda': element/pkt_size, 'ExpMaxFactor': 10.0},
                                              'SizeDist': SizeDist(2),
                                              'SizeDistParams': {'AvgPktSize': pkt_size, 'PktSize1': pkt_size, 'PktSize2': pkt_size},
                                              'AvgBw': element,
                                              'PktsGen': element/pkt_size,
                                              'TotalPktsGen': total_pkts_gen,
                                              'ToS': 0.0}]})
            else:
                result_row.append({'AggInfo': {'AvgBw': 0.0, 'PktsGen': 0.0, 'TotalPktsGen': 0.0},'Flows': []})
        result_matrix.append(result_row)
    return np.matrix(result_matrix)

# all direct connections
def get_routing_matrix(matrix: List[List[List[int]]]):
    result_matrix = []
    i = 0
    for row in matrix:
        j = 0
        result_row = []
        for route in row:
            result_row.append(route)
            j += 1
        result_matrix.append(result_row)
        i += 1
    return np.array(result_matrix, dtype=object)

# its not important
def get_performance_matrix(n: int):
    result_matrix = []
    for i in range(0, n):
        result_row = []
        for j in range(0, n):
            if i == j:
                result_row.append({'AggInfo': {'PktsDrop': 0.0, 'AvgDelay': 0.0, 'AvgLnDelay': 0.0, 'p10': 0.0, 'p20': 0.0, 'p50': 0.0, 'p80': 0.0, 'p90': 0.0, 'Jitter': 0.0},
                                   'Flows': [{'PktsDrop': 0.0, 'AvgDelay': 0.0, 'AvgLnDelay': 0.0, 'p10': 0.0, 'p20': 0.0, 'p50': 0.0, 'p80': 0.0, 'p90': 0.0, 'Jitter': 0.0}]})
            else:
                result_row.append({'AggInfo': {'PktsDrop': 0.0, 'AvgDelay': 0.0, 'AvgLnDelay': 0.0, 'p10': 0.0, 'p20': 0.0, 'p50': 0.0, 'p80': 0.0, 'p90': 0.0, 'Jitter': 0.0,
                                               'Losses': 0.115, 'Delay': 354},
                                    'Flows': [{'PktsDrop': 0.0, 'AvgDelay': 0.0, 'AvgLnDelay': 0.0, 'p10': 0.0, 'p20': 0.0, 'p50': 0.0, 'p80': 0.0, 'p90': 0.0, 'Jitter': 0.0}]})
        result_matrix.append(result_row)
    return np.matrix(result_matrix)

# all direct connections
def get_graph(matrix: List[List[float]]):
    g = nx.MultiDiGraph()
    for i in range(0, len(matrix)):
        g.add_node(i, queueSizes="32", schedulingPolicy="FIFO", levelsQoS=1)
    i = 0
    n = [0] * len(matrix)
    for row in matrix:
        j = 0
        for b in row:
            if b > 0:
                g.add_edge(i, j, weight=1, key=0, port=n[i], bandwidth=b)
                n[i] += 1
            j += 1
        i += 1
    return nx.DiGraph(g)

def generator(MG, MT, MR):
    G = get_graph(MG)
    T = get_traffic_matrix(MT)
    R = get_routing_matrix(MR)
    P = get_performance_matrix(len(MG))
    HG = network_to_hypergraph(G=G, R=R, T=T, P=P)
    ret = hypergraph_to_input_data(HG)
    yield ret

def input_fn(MG: List[List[float]], MT: List[List[float]], MR: List[List[List[int]]]):
    ds = tf.data.Dataset.from_generator(lambda: generator(MG, MT, MR),
        args=[],
        output_signature=(
            {"traffic": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "packets": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "length": tf.TensorSpec(shape=None, dtype=tf.int32),
                "model": tf.TensorSpec(shape=None, dtype=tf.int32),
                "eq_lambda": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "avg_pkts_lambda": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "exp_max_factor": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "pkts_lambda_on": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "avg_t_off": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "avg_t_on": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "ar_a": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "sigma": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "capacity": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "queue_size": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "policy": tf.TensorSpec(shape=None, dtype=tf.int32),
                "priority": tf.TensorSpec(shape=None, dtype=tf.int32),
                "weight": tf.TensorSpec(shape=(None, 1), dtype=tf.float32),
                "link_to_path": tf.RaggedTensorSpec(shape=(None, 1), dtype=tf.int32),
                "queue_to_path": tf.RaggedTensorSpec(shape=(None, 1), dtype=tf.int32),
                "queue_to_link": tf.RaggedTensorSpec(shape=(None, 1), dtype=tf.int32),
                "path_to_queue": tf.RaggedTensorSpec(shape=(None, None, 2), dtype=tf.int32,
                                                    ragged_rank=1),
                "path_to_link": tf.RaggedTensorSpec(shape=(None, None, 2), dtype=tf.int32,
                                                    ragged_rank=1)
            }
            , tf.TensorSpec(shape=None, dtype=tf.float32)
        ))

    ds = ds.prefetch(tf.data.experimental.AUTOTUNE)
    return ds
