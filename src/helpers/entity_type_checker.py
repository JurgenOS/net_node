# -*- coding: utf-8 -*-

import ipaddress


def is_mac(input_str):

    try:
        int(input_str, 16)
    except:
        return False

    return True


def is_ip_address(input_str):

    try:

        ipaddress.ip_address(input_str.strip())

    except:
        return False

    return True


def is_string_int(string):
    try:
        int(string)
        return True
    except:
        return False
