# -*- coding: utf-8 -*-

vendor_exclusions = [
    'Cisco ISE'
]


def no_screen_length_disable(platform, vendor):

    res = False

    if 'Quidway S2008-EI'.lower() in platform.lower() or \
            'HP 7503'.lower() in platform.lower() or \
            'H3C S3100'.lower() in platform.lower() or \
            'H3C S3600-52P-SI' in platform.lower() or \
            'H3C S3600-52P-PWR-SI' in platform.lower() or \
            'H3C S3600-28TP-SI' in platform.lower() or \
            'H3C S5100-24P-EI' in platform.lower() or \
            'H3C S5600-26C'.lower() in platform.lower() or \
            ('S3600-28P-EI'.lower() in platform.lower() and 'H3C'.lower() in vendor.lower()) or \
            ('S3600-52P-EI'.lower() in platform.lower() and 'H3C'.lower() in vendor.lower()) or \
            ('S5600-50C'.lower() in platform.lower() and 'H3C'.lower() in vendor.lower()):

        res = True

    return res
