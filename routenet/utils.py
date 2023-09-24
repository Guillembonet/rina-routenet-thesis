import tensorflow as tf
import networkx as nx
import numpy as np

POLICIES = np.array(['WFQ', 'SP', 'DRR', 'FIFO'])

def hypergraph_to_input_data(HG):
    n_q = 0
    n_p = 0
    n_l = 0
    mapping = {}
    for entity in list(HG.nodes()):
        if entity.startswith('q'):
            mapping[entity] = ('q_{}'.format(n_q))
            n_q += 1
        elif entity.startswith('p'):
            mapping[entity] = ('p_{}'.format(n_p))
            n_p += 1
        elif entity.startswith('l'):
            mapping[entity] = ('l_{}'.format(n_l))
            n_l += 1

    HG = nx.relabel_nodes(HG, mapping)

    link_to_path = []
    queue_to_path = []
    path_to_queue = []
    queue_to_link = []
    path_to_link = []

    for node in HG.nodes:
        in_nodes = [s for s, d in HG.in_edges(node)]
        if node.startswith('q_'):
            path = []
            for n in in_nodes:
                if n.startswith('p_'):
                    path_pos = []
                    for _, d in HG.out_edges(n):
                        if d.startswith('q_'):
                            path_pos.append(d)
                    path.append([int(n.replace('p_', '')), path_pos.index(node)])
            if len(path) == 0:
                print(in_nodes)
            path_to_queue.append(path)
        elif node.startswith('p_'):
            links = []
            queues = []
            for n in in_nodes:
                if n.startswith('l_'):
                    links.append(int(n.replace('l_', '')))
                elif n.startswith('q_'):
                    queues.append(int(n.replace('q_', '')))
            link_to_path.append(links)
            queue_to_path.append(queues)
        elif node.startswith('l_'):
            queues = []
            paths = []
            for n in in_nodes:
                if n.startswith('q_'):
                    queues.append(int(n.replace('q_', '')))
                elif n.startswith('p_'):
                    path_pos = []
                    for _, d in HG.out_edges(n):
                        if d.startswith('l_'):
                            path_pos.append(d)
                    paths.append([int(n.replace('p_', '')), path_pos.index(node)])
            path_to_link.append(paths)
            queue_to_link.append(queues)

    return {"traffic": np.expand_dims(list(nx.get_node_attributes(HG, 'traffic').values()), axis=1),
            "packets": np.expand_dims(list(nx.get_node_attributes(HG, 'packets').values()), axis=1),
            "length": list(nx.get_node_attributes(HG, 'length').values()),
            "model": list(nx.get_node_attributes(HG, 'model').values()),
            "eq_lambda": np.expand_dims(list(nx.get_node_attributes(HG, 'eq_lambda').values()), axis=1),
            "avg_pkts_lambda": np.expand_dims(list(nx.get_node_attributes(HG, 'avg_pkts_lambda').values()), axis=1),
            "exp_max_factor": np.expand_dims(list(nx.get_node_attributes(HG, 'exp_max_factor').values()), axis=1),
            "pkts_lambda_on": np.expand_dims(list(nx.get_node_attributes(HG, 'pkts_lambda_on').values()), axis=1),
            "avg_t_off": np.expand_dims(list(nx.get_node_attributes(HG, 'avg_t_off').values()), axis=1),
            "avg_t_on": np.expand_dims(list(nx.get_node_attributes(HG, 'avg_t_on').values()), axis=1),
            "ar_a": np.expand_dims(list(nx.get_node_attributes(HG, 'ar_a').values()), axis=1),
            "sigma": np.expand_dims(list(nx.get_node_attributes(HG, 'sigma').values()), axis=1),
            "capacity": np.expand_dims(list(nx.get_node_attributes(HG, 'capacity').values()), axis=1),
            "queue_size": np.expand_dims(list(nx.get_node_attributes(HG, 'queue_size').values()), axis=1),
            "policy": list(nx.get_node_attributes(HG, 'policy').values()),
            "priority": list(nx.get_node_attributes(HG, 'priority').values()),
            "weight": np.expand_dims(list(nx.get_node_attributes(HG, 'weight').values()), axis=1),
            "link_to_path": tf.ragged.constant(link_to_path),
            "queue_to_path": tf.ragged.constant(queue_to_path),
            "queue_to_link": tf.ragged.constant(queue_to_link),
            "path_to_queue": tf.ragged.constant(path_to_queue, ragged_rank=1),
            "path_to_link": tf.ragged.constant(path_to_link, ragged_rank=1)
            }, list(nx.get_node_attributes(HG, 'delay').values())


def network_to_hypergraph(G, R, T, P):
    D_G = nx.DiGraph()
    for src in range(G.number_of_nodes()):
        for dst in range(G.number_of_nodes()):
            if src != dst:
                if G.has_edge(src, dst):
                    D_G.add_node('l_{}_{}'.format(src, dst),
                                 capacity=G.edges[src, dst]['bandwidth'],
                                 policy=np.where(G.nodes[src]['schedulingPolicy'] == POLICIES)[0][0])
                for f_id in range(len(T[src, dst]['Flows'])):
                    if T[src, dst]['Flows'][f_id]['AvgBw'] != 0 and T[src, dst]['Flows'][f_id]['PktsGen'] != 0:

                        time_dist_params = [0] * 8

                        flow = T[src, dst]['Flows'][f_id]
                        model = flow['TimeDist'].value
                        if model == 6 and flow['TimeDistParams']['Distribution'] == 'AR1-1':
                            model += 1
                        if 'EqLambda' in flow['TimeDistParams']:
                            time_dist_params[0] = flow['TimeDistParams']['EqLambda']
                        if 'AvgPktsLambda' in flow['TimeDistParams']:
                            time_dist_params[1] = flow['TimeDistParams']['AvgPktsLambda']
                        if 'ExpMaxFactor' in flow['TimeDistParams']:
                            time_dist_params[2] = flow['TimeDistParams']['ExpMaxFactor']
                        if 'PktsLambdaOn' in flow['TimeDistParams']:
                            time_dist_params[3] = flow['TimeDistParams']['PktsLambdaOn']
                        if 'AvgTOff' in flow['TimeDistParams']:
                            time_dist_params[4] = flow['TimeDistParams']['AvgTOff']
                        if 'AvgTOn' in flow['TimeDistParams']:
                            time_dist_params[5] = flow['TimeDistParams']['AvgTOn']
                        if 'AR-a' in flow['TimeDistParams']:
                            time_dist_params[6] = flow['TimeDistParams']['AR-a']
                        if 'sigma' in flow['TimeDistParams']:
                            time_dist_params[7] = flow['TimeDistParams']['sigma']
                        D_G.add_node('p_{}_{}_{}'.format(src, dst, f_id),
                                     source=src,
                                     destination=dst,
                                     tos=int(T[src, dst]['Flows'][0]['ToS']),
                                     traffic=T[src, dst]['Flows'][f_id]['AvgBw'],
                                     packets=T[src, dst]['Flows'][f_id]['PktsGen'],
                                     length=len(R[src, dst]) - 1,
                                     model=model,
                                     eq_lambda=time_dist_params[0],
                                     avg_pkts_lambda=time_dist_params[1],
                                     exp_max_factor=time_dist_params[2],
                                     pkts_lambda_on=time_dist_params[3],
                                     avg_t_off=time_dist_params[4],
                                     avg_t_on=time_dist_params[5],
                                     ar_a=time_dist_params[6],
                                     sigma=time_dist_params[7],
                                     losses=P[src, dst]['AggInfo']['Losses'],
                                     delay=P[src, dst]['AggInfo']['Delay'],
                                     )

                    for h_1, h_2 in [R[src, dst][i:i + 2] for i in range(0, len(R[src, dst]) - 1)]:
                        # D_G.add_edge('p_{}_{}'.format(src, dst), 'l_{}_{}'.format(h_1, h_2))
                        D_G.add_edge('l_{}_{}'.format(h_1, h_2), 'p_{}_{}_{}'.format(src, dst, f_id))
                        D_G.add_edge('p_{}_{}_{}'.format(src, dst, f_id), 'l_{}_{}'.format(h_1, h_2))
                        if 'bufferSizes' in G.nodes[h_1]:
                            q_s = str(G.nodes[h_1]['bufferSizes']).split(',')
                        elif 'queueSizes' in G.nodes[h_1]:
                            q_s = [int(q)*(T[src, dst]['Flows'][f_id]['AvgBw']/T[src, dst]['Flows'][f_id]['PktsGen']) for q in str(G.nodes[h_1]['queueSizes']).split(',')]
                        # policy = G.nodes[h_1]['schedulingPolicy']
                        if 'schedulingWeights' in G.nodes[h_1]:
                            if G.nodes[h_1]['schedulingWeights'] != '-':
                                q_w = [float(w) for w in str(G.nodes[h_1]['schedulingWeights']).split(',')]
                                w_sum = sum(q_w)
                                q_w = [w/w_sum for w in q_w]
                            else:
                                q_w = ['-']
                        else:
                            q_w = ['-']
                        if 'tosToQoSqueue' in G.nodes[h_1]:
                            q_map = [m.split(',') for m in str(G.nodes[h_1]['tosToQoSqueue']).split(';')]
                        else:
                            q_map = [['0'], ['1'], ['2']]
                        q_n = 0
                        for q in range(G.nodes[h_1]['levelsQoS']):
                            D_G.add_node('q_{}_{}_{}'.format(h_1, h_2, q),
                                         queue_size=int(q_s[q]),
                                         priority=q_n,
                                         weight=q_w[q] if q_w[0] != '-' else 0)

                            D_G.add_edge('q_{}_{}_{}'.format(h_1, h_2, q), 'l_{}_{}'.format(h_1, h_2))
                            if str(int(T[src, dst]['Flows'][0]['ToS'])) in q_map[q]:
                                D_G.add_edge('p_{}_{}_{}'.format(src, dst, f_id), 'q_{}_{}_{}'.format(h_1, h_2, q))
                                D_G.add_edge('q_{}_{}_{}'.format(h_1, h_2, q), 'p_{}_{}_{}'.format(src, dst, f_id))
                            q_n += 1

    #print([node for node, in_degree in D_G.out_degree() if in_degree == 0])
    D_G.remove_nodes_from([node for node, in_degree in D_G.in_degree() if in_degree == 0])

    return D_G