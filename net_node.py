# -*- coding: utf-8 -*-

from src.NodeSource import MainNode


class Node(MainNode):
    def __init__(self, ip, log_dir=''):

        super().__init__(ip, log_dir=log_dir)
