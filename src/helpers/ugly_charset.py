# -*- coding: utf-8 -*-

import re
import chardet


def replace_ansi_char(bin_string):
    """
    :param bin_string: bin
    :return: bin
    """

    if not bin_string:
        return bin_string

    ansi_line_break = b'\x1bE'
    ansi_emtpy_line = b'\\x1b\[\S+?;?\d{0,2}H'
    mikrotik_color = b'\x1b\[\d?\d?;?\d?m'
    is_ansi = re.search(b'(\x1b\[\d?\d?;?\d?m)|((\\x1b\S)?\\x1b\[\S+?;\d{0,2}H)', bin_string)

    if is_ansi:

        return re.sub(ansi_emtpy_line,
                      b'',
                      re.sub(
                          ansi_line_break,
                          b'\n',
                          re.sub(
                              mikrotik_color,
                              b'',
                              bin_string
                          )
                      )
                      )

    return bin_string


def delete_line_breaker(s):

    res = s.strip()
    if "'" in res:
        res = re.sub("'", "", res)

    return res


def convert_to_utf(bin_sting):

    try:

        return bin_sting.decode('utf-8')

    except UnicodeDecodeError:

        try:
            return bin_sting.decode(
                chardet.detect(bin_sting)['encoding']
            )

        except:

            return bin_sting.decode('utf-8', 'replace')


def replace_empty_line(input_str):
    res = []
    for line in input_str.split('\n'):
        if not line.strip():
            continue
        res.append(line)

    return res
