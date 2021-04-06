# -*- coding: utf-8 -*-

import re
import string
import pkg_resources
from pathlib import Path
import os
from src.helpers.Errors import *
from src.helpers.mergers_and_convertors import merge_topology_dicts
from src.helpers.entity_type_checker import is_mac, is_ip_address


static_folder = 'static'
constants_path = pkg_resources.resource_filename(__name__, static_folder)
p = Path(static_folder)

def normalize_mac_address(mac_address):
    res = ''
    for char in mac_address:
        if char in string.hexdigits:
            res += char.lower()
        if len(res) == 6:
            res += '.'

    if len(res) != 13:
        raise NotRightMacAddressLength

    return res


def normalize_interface_name(interface):

    row_interface_name = ''
    interface_name = ''
    interface_number = ''

    # for procurve numbering
    if interface.isdigit():

        interface_name = 'Fe'
        interface_number = interface

    else:

        interfaces_names_list = []
        with open(p.parent / static_folder / 'interfaces_names') as f:
            interfaces_names_list.extend(map(str.strip, f.readlines()))

        interfaces_names_list.sort(key=len, reverse=True)

        interfaces_dictionary = {
            'Po': ['Eth-Trunk', 'Eth-Trunk', 'Po', 'Bridge-Aggregation', 'Po'],
            '10Ge': ['Ten-GigabitEthernet', '10GE', '10Ge'],
            'Ge': ['Gi', 'GE', 'GigabitEthernet', 'sfp', 'Ge'],
            'Fe': ['Eth', 'Fast', 'Fa', 'FastEthernet', 'Ethernet', 'ether', 'Fe'],
            'local': ['CPU', 'Switch', 'Router', 'Self', 'local']
        }

        for name in interfaces_names_list:
            if name in interface:
                row_interface_name = name
                break

        for normalized_name, list_of_row_int_name in interfaces_dictionary.items():
            if [x for x in list_of_row_int_name if x == row_interface_name]:

                interface_name = normalized_name
                interface_number = interface.split(row_interface_name)[-1]
                break

        if not interface_name:
            raise NormalizeErrorNoInterfaceName(f'no interface_name: "{interface}"')
        if not interface_number and interface_name.lower() != 'local':
            raise NormalizeErrorNoInterfaceNumber('no interface_number')

    return interface_name + interface_number


def normalize_mac_address_table(input_string):
    """
    :param input_string: cli string has been get from network device by command like "show mac-address table"
    :return: {(mac_address', 'vlan'): 'l2_interface'}
    """

    res = {}

    same_local_mac_address_count: int = 0
    mac_address_number: int = 0

    # if where is no mac address number line
    mac_address_line_count: int = 0

    vlan_reg = re.compile(
        '\s([0-9]{1,4}?)\/?-?\s|' \
        '^([0-9]{1,4}?)\/?-?\s|' \
        'All'
                          )

    mac_reg = re.compile(
                            '(?:[0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5})|' \
                            '(?:[0-9a-fA-F]{4}(?:\.[0-9a-fA-F]{4}){2})|' \
                            '(?:[0-9a-fA-F]{4}(?:-[0-9a-fA-F]{4}){2})|' \
                            '(?:[0-9a-fA-F]{6}(?:-[0-9a-fA-F]{6}))'
                         )
    interface_reg = re.compile('Vlan\S+|' \
                    'Eth\S+|' \
                    'Fa\w+[0-9]{0,1}\/?[0-9]{0,2}\/?[0-9]{0,2}\/?[0-9]{0,2}|' \
                    '10GE\w+[0-9]{0,1}\/?[0-9]{1,2}\/?[0-9]{0,2}\/?[0-9]{0,2}|' \
                    'G\w+[0-9]{0,1}\/?[0-9]{1,2}\/?[0-9]{0,2}\/?[0-9]{0,2}|' \
                    'XGE\w+[0-9]{0,1}\/?[0-9]{1,2}\/?[0-9]{0,2}\/?[0-9]{0,2}|' \
                    'Ten-GigabitEthernet\w+[0-9]{0,1}\/?[0-9]{1,2}\/?[0-9]{0,2}\/?[0-9]{0,2}|' \
                    'Bridge-Aggregation[0-9]{0,1}\/?[0-9]{1,2}\/?[0-9]{0,2}\/?[0-9]{0,2}|' \
                    'BAGG[0-9]{0,1}\/?[0-9]{1,2}\/?[0-9]{0,2}\/?[0-9]{0,2}|' \
                    'Po\S+|'\
                    'CPU|'\
                    'Self|'\
                               'ether\d|'\
                               'sfp\d|'\
                               'bridge\d'

                               )

    procurve_mac_address_line_reg = re.compile('(?:[0-9a-fA-F]{6}(?:-[0-9a-fA-F]{6}))\s+?[0-9]{1,4} *([0-9]{1,4})?')
    mikrotik_mac_address_line_reg = re.compile('(?:[0-9A-F]{2}(?::[0-9A-F]{2}){5})')

    for line in re.split('\r\n|\n', input_string):
        # find line with total mac addresses number
        if 'Total Mac' in line or \
                'Total items: ' in line or \
                'mac address(es) found' in line or\
                'Total items displayed =' in line:

            mac_address_number_line = re.search(r'\d+', line)

            if mac_address_number_line:

                mac_address_number = int(mac_address_number_line.group())

        mac_address_line = mac_reg.search(line)

        if not mac_address_line:
            continue

        mac_address_line_count += 1

        l2_interface = ''
        vlan = ''  # default vlan

        procurve_mac_address_line = procurve_mac_address_line_reg.search(line)
        mikrotik_mac_address_line = mikrotik_mac_address_line_reg.search(line)

        l2_interface_line = interface_reg.search(line)
        vlan_line = vlan_reg.search(line)

        # for procurve mac address format
        if procurve_mac_address_line:
            procurve_line = procurve_mac_address_line.group()

            if len(procurve_line.split()) == 3:
                mac_address, l2_interface, vlan = procurve_line.split()
            else:
                mac_address, l2_interface = procurve_line.split()

            mac_address = normalize_mac_address(mac_address)

        # for mikrotik format
        if mikrotik_mac_address_line:

            mac_address_number, mac_address_type, mac_address, vlan, l2_interface = re.split('\s+', line.strip())[:5]
            mac_address_number = int(mac_address_number) + 1
            mac_address = normalize_mac_address(mac_address)

            if not vlan.isdigit():
                l2_interface = vlan
                vlan = ''

            if 'L' in mac_address_type:
                l2_interface = 'local'

        else:
            mac_address = normalize_mac_address(mac_address_line.group())

            if l2_interface_line:
                l2_interface = l2_interface_line.group()

            if vlan_line:
                vlan = vlan_line.group().split('/')[0]

        # to compare found mac address number with shown by cli
        if (mac_address, vlan) in res:

            if res[(mac_address, vlan)] == 'local':

                same_local_mac_address_count += 1

            else:
                raise L2LoopDetection(f'{normalize_interface_name(l2_interface)}, {vlan} : {mac_address} <--> '
                                      f'{res[(mac_address, vlan)]}, {vlan}: {mac_address}')

        res[(mac_address, vlan)] = normalize_interface_name(l2_interface)

    if not mac_address_number:
        mac_address_number = mac_address_line_count

    if not int(len(res)) == (mac_address_number - same_local_mac_address_count):
        raise NotFullMacAddressTableFound(f'normalized table {len(res)} != '
                                          f'{mac_address_number - same_local_mac_address_count} in cli table')

    return res


def normalize_neighbors_table(input_string):

    res = []
    temp_res = []

    for k, v in merge_topology_dicts(

                        normalize_cdp_table_cisco(input_string),
                        normalize_lldp_table_cisco(input_string),
                        normalize_cdp_table_huawei(input_string),
                        normalize_lldp_table_huawei(input_string),
                        normalize_cdp_table_hp(input_string),
                        normalize_lldp_table_hp(input_string),
                        normalize_cdp_table_hp_procurve(input_string),
                        normalize_lldp_table_hp_procurve(input_string),
                        normalize_cdp_table_h3c(input_string),
                        normalize_lldp_table_h3c(input_string),
                        normalize_cdp_table_mikrotik(input_string),
                        normalize_lldp_table_mikrotik(input_string)

                ).items():
        res.append({k: v})

    return res


def normalize_cdp_table_cisco(input_string):

    res = {}

    local_iinterface = ''
    fqdn_neighbor_hostname = ''
    neighbor_ip = ''
    neighbor_platform = ''
    neighbor_interface = ''
    neighbor_holdtime = ''

    for line in re.split('\r\n|\n\n|\n', input_string.strip()):
        line = line.strip()

        if 'Device ID: ' in line:
 
            fqdn_neighbor_hostname = line.split(' ')[-1].strip()

        if 'IP address: ' in line:

            neighbor_ip = line.split(' ')[-1].strip()

        if 'Platform: ' in line:

            neighbor_platform = ' '.join(line.split(' ')[1:3])[:-1]

        if 'Interface: ' in line and 'Port ID (outgoing port):' in line:

            local_iinterface = line.split(' ')[1].strip()[:-1]
            neighbor_interface = line.split(' ')[-1].strip()

            local_iinterface = normalize_interface_name(local_iinterface)
            neighbor_interface = normalize_interface_name(neighbor_interface)

        if 'Holdtime' in line:
            'Holdtime : 123 sec'
            'Holdtime: 142 sec'
            neighbor_holdtime = ' '.join(line.split(' ')[-2::])

        if local_iinterface:

            res.update({local_iinterface: { 'local_inteface_description': '',
                                            'fqdn_neighbor_hostname': fqdn_neighbor_hostname,
                                            'neighbor_ip': neighbor_ip,
                                            'neighbor_platform': neighbor_platform,
                                            'neighbor_interface': neighbor_interface,
                                            'neighbor_holdtime': neighbor_holdtime,
                                            'neighbor_interface_description': ''}})

    return res


def normalize_lldp_table_cisco(input_string):
    res = {}

    local_interface = ''

    fqdn_neighbor_hostname = ''
    neighbor_ip = ''
    neighbor_platform = ''
    neighbor_interface = ''
    neighbor_interface_description = ''
    neighbor_holdtime = ''

    # general fields
    local_intf = ''
    chassis_id = ''  # ip address
    port_id = ''     # mac address
    port_description = ''
    system_capabilities_supported = ''
    system_name = ''
    system_description = ''

    # phone fields
    manufacturer = ''
    model = ''

    # switch fields
    ip = ''
    expired_time = ''

    system_description_shutter = False

    for line in re.split('\r\n|\n\n|\n', input_string.strip()):
        line = line.strip()

        if 'Local Intf:' in line:
            local_intf = line.split(':')[-1].strip()
            continue

        if 'Chassis id:' in line:
            chassis_id = line.split(':')[-1].strip()
            continue

        if 'Port id:' in line:
            port_id = line.split(':')[-1].strip()
            continue

        if 'Port Description' in line:
            port_description = line.split(':')[-1].strip()
            continue

        if 'System Name:' in line:
            system_name = line.split(':')[-1].strip()
            continue

        if 'System Description:' in line:

            system_description_shutter = True
            continue

        if 'Time remaining:' in line:

            system_description_shutter = False

            expired_time = line.split(':')[-1].strip()
            continue

        if system_description_shutter:
            system_description += line + '\n'
            continue

        if 'System Capabilities:' in line:
            system_capabilities_supported = line.split(':')[-1].strip()

        # phone fields
        if 'Manufacturer:' in line:
            manufacturer = line.split(':')[-1].strip()

        if 'Model:' in line:
            model = line.split(':')[-1].strip()


        # switch fields
        if 'IP:' in line:
            ip = line.split(':')[-1].strip()

        if system_capabilities_supported and \
            chassis_id and \
            port_id:

                if not local_intf:
                    continue

                if manufacturer and \
                    model and \
                        't' in system_capabilities_supported.lower():

                        fqdn_neighbor_hostname = model
                        neighbor_ip = chassis_id
                        neighbor_platform = manufacturer
                        neighbor_interface = 'phone input'
                        neighbor_interface_description = 'lan interface'
                        neighbor_holdtime = ''

                elif port_description and \
                    system_name and \
                    system_description and \
                    ip and \
                    expired_time and \
                    'b' in system_capabilities_supported.lower():

                        fqdn_neighbor_hostname = system_name
                        neighbor_ip = ip
                        neighbor_platform = system_description
                        neighbor_interface = normalize_interface_name(port_id)
                        neighbor_interface_description = port_description
                        neighbor_holdtime = expired_time

                else:
                    continue

                # general fields
                chassis_type = ''
                port_id_type = ''
                system_capabilities_supported = ''
                chassis_id = ''  # ip address
                port_id = ''  # mac address

                # phone fields
                manufacturer_name = ''
                model_name = ''

                # switch fields
                port_description = ''
                system_name = ''
                system_description = ''
                management_address_value = ''
                expired_time = ''

                res.update({normalize_interface_name(local_intf):
                            { 'local_inteface_description': '',
                              'fqdn_neighbor_hostname': fqdn_neighbor_hostname,
                              'neighbor_ip': neighbor_ip,
                              'neighbor_platform': neighbor_platform,
                              'neighbor_interface': neighbor_interface,
                              'neighbor_interface_description': neighbor_interface_description,
                              'neighbor_holdtime': neighbor_holdtime}
                            }
                           )

    return res


def normalize_lldp_table_huawei(input_string):

    res = {}

    local_interface = ''
    fake_description = ''

    fqdn_neighbor_hostname = ''
    neighbor_ip = ''
    neighbor_platform = ''
    neighbor_interface = ''
    neighbor_interface_description = ''
    neighbor_holdtime = ''

    # general fields
    chassis_type = ''
    port_id_type = ''
    system_capabilities_supported = ''
    chassis_id = ''  # ip address
    port_id = ''  # mac address

    # phone fields
    manufacturer_name = ''
    model_name = ''

    # switch fields
    port_description = ''
    system_name = ''
    system_description = ''
    management_address_value = ''
    expired_time = ''

    for line in re.split('\r\n|\n\n|\n', input_string.strip()):
        line = line.strip()

        if 'neighbor(s):' in line or 'neighbors:' in line:

            local_interface = line.split()[0].strip()
            continue

        if 'Chassis type' in line:
            chassis_type = line.split(':')[-1].strip()
            continue

        if 'Port ID type' in line:
            port_id_type = line.split(':')[-1].strip()
            continue

        if 'Port ID' in line:
            port_id = line.split(':')[-1]
            continue

        if 'System capabilities supported' in line:
            system_capabilities_supported = line.split(':')[-1]
            continue

        if 'Manufacturer name' in line:
            manufacturer_name = line.split(':')[-1]
            continue

        if 'Model name' in line:
            model_name = line.split(':')[-1]
            continue

        if 'Port description ' in line:
            port_description = line.split(':')[-1]
            continue

        if 'System name' in line:
            system_name = line.split(':')[-1]
            continue

        if 'System description' in line:
            system_description = line.split(':')[-1]
            continue

        if 'Chassis ID' in line:
            chassis_id = line.split(':')[-1]
            continue

        if 'Management address value' in line or 'Management address       :' in line:
            management_address_value = line.split(':')[-1]
            continue

        if 'Expired time' in line:
            expired_time = line.split(':')[-1]
            continue

        if  chassis_type and \
            port_id_type and \
            system_capabilities_supported and \
            chassis_id and \
            port_id:

                if not local_interface:
                    continue

                if manufacturer_name and \
                    model_name and \
                        'telephone' in system_capabilities_supported.lower():

                        if is_ip_address(chassis_id):
                            port_id = chassis_id

                        neighbor_ip = port_id
                        neighbor_platform = manufacturer_name + ' ' + model_name
                        neighbor_interface = 'phone input'
                        neighbor_interface_description = 'lan interface'
                        neighbor_holdtime = ''

                elif port_description and \
                    system_name and \
                    system_description and \
                    management_address_value and \
                    expired_time:

                    if 'phone' in system_capabilities_supported.lower():
                        neighbor_interface = 'phone input'

                    elif 'bridge' in system_capabilities_supported.lower():
                        neighbor_interface = normalize_interface_name(port_id)

                    fqdn_neighbor_hostname = system_name
                    neighbor_ip = management_address_value
                    neighbor_platform = system_description
                    neighbor_interface_description = port_description
                    neighbor_holdtime = expired_time

                else:
                    continue

                # general fields
                chassis_type = ''
                port_id_type = ''
                system_capabilities_supported = ''
                chassis_id = ''  # ip address for phone
                port_id = ''  # mac address for phone

                # phone fields
                manufacturer_name = ''
                model_name = ''

                # switch fields
                port_description = ''
                system_name = ''
                system_description = ''
                management_address_value = ''
                expired_time = ''

                res.update({normalize_interface_name(local_interface):
                            { 'local_inteface_description': '',
                              'fqdn_neighbor_hostname': fqdn_neighbor_hostname,
                              'neighbor_ip': neighbor_ip,
                              'neighbor_platform': neighbor_platform,
                              'neighbor_interface': neighbor_interface,
                              'neighbor_interface_description': neighbor_interface_description,
                              'neighbor_holdtime': neighbor_holdtime}
                            }
                           )


    return res


def normalize_cdp_table_huawei(input_string):
    res = {}

    return res


def normalize_cdp_table_hp(input_string):
    res = {}

    return res


def normalize_lldp_table_hp(input_string):
    res = {}

    return res


def normalize_cdp_table_hp_procurve(input_string):
    res = {}

    local_interface = ''

    fqdn_neighbor_hostname = ''
    neighbor_ip = ''
    neighbor_platform = ''
    neighbor_interface = ''
    neighbor_interface_description = ''
    neighbor_holdtime = ''

    neighbor_interface_description_temp = ''

    port = ''
    device_id = ''
    address_type = ''
    address = ''
    platform = ''
    capability = ''
    device_port = ''
    verison = ''

    for line in re.split('\r\n|\n\n|\n', input_string.strip()):
        line = line

        if '  Port :' in line:
            port = line.split(':')[-1].strip()
            continue

        if '  Device ID :' in line:
            device_id = line.split(':')[-1].strip()
            continue

        if '  Address Type :' in line:
            address_type = line.split(':')[-1].strip()
            continue

        if '  Address      :' in line:
            address = line.split(':')[-1].strip()
            continue

        if '  Platform     :' in line:
            platform = line.split(':')[-1].strip()
            continue

        if '  Capability   :' in line:
            capability = line.split(':')[-1].strip()
            continue

        if '  Device Port  :' in line:
            device_port = line.split(':')[-1].strip()
            continue

        if '  Version      :' in line:
            verison = line.split(':')[-1].strip()
            continue

        if  port and \
            device_id and \
            address_type and \
            address:

            local_interface = port

            # net device
            if platform and \
                capability and \
                device_port and \
                verison:

                if address_type == 'UNKNOWN' and 'E129' in platform:
                    platform = 'phone'
                    device_port = 'phone input'
                    neighbor_interface_description_temp = 'lan interface'

                if address == 'Unsupported format':
                    address = ''

                fqdn_neighbor_hostname = ''
                neighbor_ip = address
                neighbor_platform = platform
                neighbor_interface = device_port
                neighbor_interface_description = neighbor_interface_description_temp
                neighbor_holdtime = ''

            else:
                if is_mac(''.join(device_port.split())):
                    device_port = ''

                platform = 'phone'
                device_port = 'phone input'

                fqdn_neighbor_hostname = ''
                neighbor_ip = address
                neighbor_platform = platform
                neighbor_interface = device_port
                neighbor_interface_description = 'lan interface'
                neighbor_holdtime = ''

            port = ''
            device_id = ''
            address_type = ''
            address = ''
            platform = ''
            capability = ''
            device_port = ''
            verison = ''

            res.update({normalize_interface_name(local_interface):
                        { 'local_inteface_description': '',
                          'fqdn_neighbor_hostname': fqdn_neighbor_hostname,
                          'neighbor_ip': neighbor_ip,
                          'neighbor_platform': neighbor_platform,
                          'neighbor_interface': neighbor_interface,
                          'neighbor_interface_description': neighbor_interface_description,
                          'neighbor_holdtime': neighbor_holdtime}
                        }
                       )

    return res


def normalize_lldp_table_hp_procurve(input_string):
    res = {}

    return res


def normalize_cdp_table_h3c(input_string):
    res = {}

    return res


def normalize_lldp_table_h3c(input_string):
    res = {}

    return res


def normalize_cdp_table_mikrotik(input_string):
    res = {}

    return res


def normalize_lldp_table_mikrotik(input_string):
    res = {}

    return res
