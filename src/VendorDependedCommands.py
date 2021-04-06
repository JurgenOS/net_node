# -*- coding: utf-8 -*-

import logging
import logging.config

from src.helpers.logger_builder import config
from src.helpers.string_exclusions import no_screen_length_disable


class VendorDependedCommands:

    def __init__(self, ip, log_dir):

        logging.config.dictConfig(
                                    config(log_dir, ip)
        )

        self.logger = logging.getLogger(ip)

        self.ip: str = ip
        self.id: str = ''
        self.vendor: str = ''
        self.os: str = ''
        self.image_name: str = ''
        self.image_directory: str = ''
        self.image_version: str = ''
        self.release: str = ''
        self.platform: str = ''

    @property
    def command_show_running_config(self):

        res = ''

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'procurve' or \
                self.vendor.lower() == 'attika':

            res = '\nshow running-config\n'

        if self.vendor.lower() == 'mikrotik':
            res = '\n/export verbose\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = '\nshow running-config\n'
            else:
                res = '\ndisplay current-configuration\n'

        return res

    @property
    def command_show_mac_address_table(self):

        res = ''

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            res = '\nshow mac address-table\n'

        if self.vendor.lower() == 'mikrotik':
            res = '\n/interface bridge host print\n'

        if self.vendor.lower() == 'd-link':
            res = '\nshow fdb\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = '\nshow mac-address\n'
            else:
                res = '\ndisplay mac-address\n'

        return res

    @property
    def command_logout(self):

        res = '\nqu '

        if 'IOS-XE'.lower() in self.os.lower():
            res = 'exit'

        if self.vendor.lower() == 'mikrotik':
            res = 'quit'

        if 'procurve' in self.platform.lower():
            res = '\nexit \nexit \ny'

        if no_screen_length_disable(
            self.platform, self.vendor
        ):

            res = 'return \n \n'
            res += 'system-view\n \n'
            res += 'user-interface vty 0 4\n \n'
            res += 'undo screen-length\n \n'
            res += 'return\n \n'
            res += '\nqu\n \n'

        return res

    @property
    def char_delete_mark(self):

        res = ''

        if self.vendor.lower() == 'cisco' or \
            self.vendor.lower() == 'attika' or \
                self.vendor.lower() == 'mikrotik':

            res = 'no'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = 'no'
            else:
                res = 'undo'

        return res

    @property
    def char_delimiter_mark(self):

        res = ''

        if self.vendor.lower() == 'cisco':
            res = '\n!\n'

        if self.vendor.lower() == 'attika':
            res = '\n$\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            res = '\n#\n'

        if self.vendor.lower() == 'mikrotik':
            res = '/'

        return res

    @property
    def command_level_back(self):

        res = ''

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            res = '\nexit\n'

        if self.vendor.lower() == 'mikrotik':
            res = '/'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = '\nexit\n '
            else:
                res = '\nquit\n'

        return res

    @property
    def command_config_mode(self):

        res = ''

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            res = '\nconfigure terminal\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = '\nconfigure terminal\n '
            else:
                res = '\nsystem-view\n'

        return res

    @property
    def command_to_root(self):
        res = ''

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            res = '\nend\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = '\nend\n '
            else:
                res = '\nreturn\n'

        if self.vendor.lower() == 'mikrotik':
            res = '\r\n//\r\n'

        return res

    @property
    def command_save(self):
        res = ''
        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            res = '\nwrite\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = '\n write memory \n '
            else:
                res = '\nsave\ny\n'

        return res

    @property
    def command_info(self):

        # if there is no vendor and platform
        res = '\ndisplay patch-information\n \ndisplay version\n \n dir\n' + '\nshow version\n \ndir\ndir\n'

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            res = '\nshow version\n \ndir\ndir\n'

        if self.vendor.lower() == 'mikrotik':
            res = '\n/system export\n'
            res += '\n/system routerboard print\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            if 'procurve' in self.platform.lower():
                res = '\n show version \n '
                res += '\n \n'
            else:
                res = '\ndisplay patch-information\n \ndisplay version\n \n dir\n'

        return res

    @property
    def command_vty_config_mode(self):

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':
            return 'line vty'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            return 'user-interface vty'

    @property
    def command_find_max_vty_number(self):

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            return 'line vty 0 ?'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':

            return 'user-interface vty 0 ?'

    @property
    def command_screen_length_disable(self):

        res = 'screen-length disable\n \n' \
                    'screen-length 0 temporary\n \n' \
                    'terminal length 0\n \n' \
                    'no page\n \n'

        if no_screen_length_disable(
            self.platform, self.vendor
        ):

            res = 'system-view\n \n'
            res += 'user-interface vty 0 4\n \n'
            res += 'screen-length 0\n \n'
            res += 'return'

        else:

            if self.vendor.lower() == 'cisco' or \
                    self.vendor.lower() == 'attika':

                if self.os.lower() == 'catos':
                    res = 'set length 0'
                else:
                    res = 'terminal length 0\n \n'

            if self.vendor.lower() == 'huawei':
                res = 'screen-length 0 temporary\n \n'

            if self.vendor.lower() == 'hp' or \
                    self.vendor.lower() == 'h3c':

                if 'procurve' in self.platform.lower():
                    res = 'no page\n \n'
                    res += 'terminal width 1920'
                else:
                    res = 'screen-length disable\n \n'

            if self.vendor.lower() == 'mikrotik':
                res = ''

        return res

    @property
    def command_line_break(self):

        res = '\n'

        if self.vendor.lower() == 'mikrotik':
            res = '\r\n'

        return res

    def command_access_list_on_vty(self, acl_on_vty):

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':
            return f'access-class {acl_on_vty} in'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':
            return f'acl {acl_on_vty} inbound'

    def command_access_list_on_snmp(self, community, acl_on_snmp):

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':
            return f'snmp-server community {community} RO {acl_on_snmp}'

        if self.vendor.lower() == 'h3c':

            return f'snmp-agent community read {community} acl {acl_on_snmp}'

        if self.vendor.lower() == 'hp':
            return f'snmp-agent community read {community} acl {acl_on_snmp}'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'quidway':

            return f'snmp-agent community read {community} acl {acl_on_snmp}'



    def command_implement_acl_on_interface_in(self, acl):

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':
            return f'ip access-group {acl} in'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':
            return f'traffic-filter inbound acl {acl}'

    def command_implement_acl_on_interface_out(self, acl):

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':
            return f'ip access-group {acl} out'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':
            return f'traffic-filter outbound acl {acl}'

    def command_implement_acl_on_vty(self, acl):

        if self.vendor.lower() == 'cisco' or \
                self.vendor.lower() == 'attika':

            return f'\nline vty 0 15\naccess-class {acl} in\n'

        if self.vendor.lower() == 'huawei' or \
                self.vendor.lower() == 'hp' or \
                self.vendor.lower() == 'h3c' or \
                self.vendor.lower() == 'quidway':
                return f'\nuser-interface vty 0 15\nacl {acl} inbound\n'
