# -*- coding: utf-8 -*-

def merge_topology_dicts(*args):

    res = {}

    for topology_dict in args:

        for k in topology_dict:

            if not k in res:
                res[k] = topology_dict[k]

            for sub_k in topology_dict[k]:
                res[k][sub_k] = res[k][sub_k] or topology_dict[k][sub_k]

    return res
