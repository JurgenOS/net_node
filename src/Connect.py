# -*- coding: utf-8 -*-

import time
import re
import os
import paramiko
import telnetlib
from subprocess import run, PIPE, DEVNULL
from socket import socket, AF_INET, SOCK_STREAM
from multiprocessing.pool import ThreadPool as Pool
from src.ResponseParser import ResponseParser
from src.helpers.names_and_regex import HOST_NAME_REG
from src.helpers.ugly_charset import replace_ansi_char, convert_to_utf
from src.helpers.Errors import *

from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, \
    UdpTransportTarget, ContextData, ObjectType, ObjectIdentity


class Connect(ResponseParser):

    def __init__(self, ip, log_dir):

        super().__init__(ip, log_dir)

        self.connection: object = None
        self.mng_protocol: str = ''
        self.ssh: str = ''
        self.telnet: str = ''
        self.http: str = ''
        self.https: str = ''
        self.answer_delay: int = 10
        self.connection_timeout: int = 70

        self.date_of_last_ping: str = ''
        self.is_available: str = ''

    def is_available_by_icmp(self):

        res = ''

        correct_answer = b"ttl="
        command = "ping -c 2 {}".format(self.ip)

        if 'win' in os.sys.platform.lower():
            command = "ping -n 2 {}".format(self.ip)

        response = run(command, shell=True,  stdout=PIPE, stderr=DEVNULL)

        if response.returncode == 0:

            if correct_answer in response.stdout.lower():

                self.logger.info(response.stdout.lower())
                res = ' '.join(time.asctime().split()[1:-1])
                self.is_available = res

            else:

                self.logger.info('not available')

        return res

    def scan_ports(self, *ports):

        output = b''
        result = []

        for port in ports:

            port = str(port)

            client_socket = socket(AF_INET, SOCK_STREAM)
            client_socket.settimeout(15)

            try:
                client_socket.connect((self.ip, port))
                output += client_socket.recv(4096)
                time.sleep(1)
                output += client_socket.recv(4096)

                if b'connection refused' in output or \
                        b'connection closed by remote host!' in output:
                    result.append('')
                    continue
            except:
                result.append('')
                continue

            client_socket.close()

            result.append(output)

        return result

    def scan_port(self, port):

        output = b''
        port = int(port)
        delay: int = 0

        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.settimeout(10)

        try:
            start_time = time.time()
            client_socket.connect((self.ip, port))
            time.sleep(3)
            output += client_socket.recv(4096)

            if b'connection refused' in output or \
                    b'connection closed by remote host!' in output:
                output = b''

            delay = round(
                time.time() - start_time
            )

        except:
            delay = 0
            output = b''

        client_socket.close()
        return port, output.decode('utf-8', 'ignore'), delay

    def scan_mng_ports(self):
        """
        return a list in format:['SSH'|'SSHv1','Telnet', 'Http, 'Https', 'Vendor','Nov 29 10:11:17']
        """
        result = []
        vendor = ''
        res = []
        delay_list = []
        list_of_ports = [22, 23, 80, 443]

        # ===== multithreading =====
        worker = self.scan_port
        pool = Pool(4)
        res.extend(pool.map(worker, list_of_ports))
        pool.close()
        pool.join()

        # ===== for debug =====
        # for port in list_of_ports:
        #     res.append(self.scan_port(port))

        for item in res:

            port, response, delay = item

            delay_list.append(delay)

            if not response:
                result.append('')
                continue

            if port == 22:
                if 'SSH-2.0' in response:
                    result.append('SSH')

                if 'SSH-1.99' in response:
                    result.append('SSH')

                if 'SSH-1.5' in response:
                    result.append('SSHv1')

            if port == 23:
                result.append('Telnet')
            if port == 80:
                result.append('Http')
            if port == 443:
                result.append('Https')

            if not vendor:
                vendor = self.find_vendor(response)

        self.answer_delay = max(delay_list)

        result.append(vendor)
        result.append(' '.join(time.asctime().split()[1:-1]))
        self.logger.info(result)

        return result

    def scan_mng_protocols(self):

        if not self.is_available_by_icmp():
            raise NotAvailable

        ssh, telnet, http, https, vendor, date = self.scan_mng_ports()

        self.date_of_last_ping = date
        self.telnet = telnet
        self.ssh = ssh
        self.http = http
        self.https = https

        if not self.vendor:
            self.vendor = vendor

        if telnet.lower() == 'telnet':
            self.mng_protocol = 'telnet'
        if ssh.lower() == 'ssh':
            self.mng_protocol = 'ssh'

    def scan_snmp_system_info(self, snmp_community):

        snmp_version = 0

        while True:

            if snmp_version == 3:
                break

            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(SnmpEngine(),
                       CommunityData(snmp_community, mpModel=snmp_version),
                       UdpTransportTarget(('{}'.format(self.ip), 161),
                                          timeout=2.0,
                                          retries=1),
                       ContextData(),
                       ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
            )

            if errorIndication.__str__() =='No SNMP response received before timeout':
                raise FailedSnmpCommunity(snmp_community)

            if errorIndication.__str__() == 'No SNMP response received before timeout':
                snmp_version += 1

            if errorIndication:
                snmp_version += 1

            elif errorStatus:
                snmp_version += 1

            else:
                return varBinds[0].prettyPrint()

    def send_short_commands(self, commands_str, log_out=False):

        self.logger.critical('START')

        list_of_commands = list(
            map(
                str.strip, commands_str.split('\n')
            )
        )

        if self.mng_protocol.lower() == 'telnet':

            res = self.send_command_via_telnet(list_of_commands, log_out=log_out)
        else:
            res = self.send_command_via_ssh(list_of_commands, log_out=log_out)

        for line in res.split('\n'):
            self.logger.critical(f'answers: {line.strip()}')

        self.logger.critical('END')

        return res

    def send_command_via_telnet(self, list_of_commands, log_out=False):

        res = ''
        output = ''
        answer = b''

        # to clear the output
        self.connection.write(b"\n")
        time.sleep(self.answer_delay)
        self.connection.read_very_eager()

        try:

            for line in list_of_commands:

                self.logger.critical(f'command: {line.strip()}')

                self.connection.write(line.encode('utf-8') + b'\n')

                time.sleep(int(self.answer_delay) * 2)

                answer = self.connection.read_very_eager()

                if not answer:
                    raise ConfigurationError(f'{line.strip()} has no answers')

                # replace ansi abra-cadabra like "\x1b[24;1H"
                answer = replace_ansi_char(answer)

                output += answer.decode('utf-8')

            # end execution in case of log out command

            if log_out:
                return ''

            self.connection.write(self.command_to_root.encode('utf-8'))  # ^Z == b"\x1A"
            time.sleep(self.answer_delay)
            self.connection.write('\n'.encode("utf-8"))

            # to get full command response
            start_time = time.time()


            while True:
                answer = b''

                self.connection.write('\n'.encode("utf-8"))
                if time.time() - start_time > 60:
                    raise ConfigurationError(f'to long output waiting.'
                                             f'Output: "{output}"')

                self.connection.write('\n'.encode("utf-8"))

                answer += self.connection.read_very_eager()

                if answer:

                    # replace abra-cadabra like "\x1b[24;1H"
                    answer = replace_ansi_char(answer)
                    output += convert_to_utf(answer)

                    if re.search(HOST_NAME_REG, answer.split(b'\n')[-1].strip()):
                        break

                time.sleep(self.answer_delay)


            for line in re.split('\r\n|\n', output):
                res += line + '\n'

            return res

        except Exception as e:
            self.logger.critical(e.__str__())
            self.logger.exception(e.__str__())

        if not self.connection:
            self._log_in()

        return ''

    def send_command_via_ssh(self, list_of_commands, log_out=False):

        res = ''
        output = ''

        # to clear the output
        self.connection.send(self.command_line_break.encode('utf-8'))

        time.sleep(self.answer_delay)
        if self.vendor.lower() == 'mikrotik':
            time.sleep(self.answer_delay)

        self.connection.recv(65000)

        try:

            # send command one by one
            for line in list_of_commands:

                self.logger.critical(f'command: {line.strip()}')

                self.connection.send(line.encode('utf-8') + self.command_line_break.encode('utf-8'))

                time.sleep(self.answer_delay)
                if self.vendor.lower() == 'mikrotik':
                    time.sleep(self.answer_delay)

                output_bin = self.connection.recv(65000)
                # replace ansi abra-cadabra like "\x1b[24;1H"
                output_bin = replace_ansi_char(output_bin)
                output += convert_to_utf(output_bin)

                if not output:
                    raise ConfigurationError(f'{line.strip()} has no answers')

            # end execution in case of log out command
            if 'closed' in self.connection.__str__() and log_out:
                return ''

            # return to root
            self.connection.send(self.command_to_root.encode('utf-8'))  # ^Z == b"\x1A"

            time.sleep(self.answer_delay)
            if self.vendor.lower() == 'mikrotik':
                time.sleep(self.answer_delay)

            self.connection.send(self.command_line_break.encode('utf-8'))

            # to get full command response
            start_time = time.time()

            while True:

                answer = b''
                out = b''

                if time.time() - start_time > 60:
                    raise ConfigurationError(f'to long output waiting.'
                                             f'Output: "{output}"')

                # send empty line
                self.connection.send(line.encode('utf-8') + self.command_line_break.encode('utf-8'))

                time.sleep(self.answer_delay)
                if self.vendor.lower() == 'mikrotik':
                    time.sleep(self.answer_delay)

                # get response
                answer += self.connection.recv(65000)

                if answer:
                    # replace ansi abra-cadabra like "\x1b[24;1H"
                    clear_answer = replace_ansi_char(answer)
                    output += clear_answer.decode('utf-8')

                    if re.search(
                            HOST_NAME_REG, re.split(b'\r|\n|\r\n|\n\r', clear_answer)[-1].strip()
                    ):
                        break

                time.sleep(self.answer_delay)
                continue

            for line in re.split('\r\n|\n', output):
                res += line + '\n'

            return res

        except Exception as e:
            self.logger.critical(e.__str__())
            self.logger.exception(e.__str__())

        if not self.connection:
            self._log_in()

        return ''

    def get_show_command_output(self, command):

        host_names_set: set = set()  # len of set should be equal to 1

        if not self.connection:
            self.logger.critical('no connection')
            return ''

        output = self.send_short_commands(command)
        clear_result = ''
        start = False

        for line in map(str.strip, output.split('\n')):
            if not line:
                continue

            if command.strip() in line:
                start = True
                continue

            if re.search(HOST_NAME_REG.decode('utf-8'), line):

                # sometimes name of version may there be in line line "[V200R005C20SPC200]",
                # net_node look at this like hostname.
                # To eliminate this
                if [x for x in self.releases_list if x.lower().strip() in line.lower().strip()]:
                    continue
                # if self.release.lower() in line.lower() and self.vendor.lower() == 'huawei':
                #
                #     continue
                host_names_set.add(line)
                start = False

            if start:
                clear_result += line + '\n'

        if len(host_names_set) != 1:
            raise NotSingleHostnameFound(f'ERROR: find more than 1 hostname_lines {host_names_set}')

        if output and not clear_result:
            raise NotClearOutput(f'ERROR: len of row output: {len(output)} and no clear_result')

        return clear_result

    def login_via_telnet(self):

        answer = b''

        try:

            tn = telnetlib.Telnet(self.ip, 23, self.answer_delay + 10)

            try:
                exp = tn.expect([b"Press any key to continue"], timeout=2)

                if exp[1]:
                    answer += exp[2]
                    tn.write(b'1\n')
                    time.sleep(self.answer_delay)

            except:
                pass

            try:
                exp = tn.expect(
                    [b"Username: ",
                     b"login: ",
                     b"login as: ",
                     b"Username:",
                     b"username:",
                     b"username: ",
                     b"login:",
                     b"UserName:",
                     b"Tacacs UserName:",
                     b"Radius UserName:"],
                     timeout=self.answer_delay)

                if exp[1]:
                    answer += exp[2]

                tn.write(self.user.encode("utf-8") + b"\n")
                time.sleep(self.answer_delay + 10)

            except:
                self.logger.critical('no "Username:" string')

            finally:
                tn.write(self.password.encode("utf-8") + b"\n")
                time.sleep(self.answer_delay)

                password_string = replace_ansi_char(tn.read_very_eager())
                answer += password_string
                find = False
                for line in password_string.split(b'\n'):
                    if re.search(HOST_NAME_REG, line.strip()): find = True

                if not find:
                    raise ConnectionRefusedError('HOST_NAME_REG was not find after credentials was sent')

            answer += tn.read_very_eager()
            self.find_info(replace_ansi_char(answer).decode('utf-8'))

            self.logger.critical('SUCCESS')

            return tn

        except Exception as e:

            self.logger.critical(e.__str__())
            self.logger.exception(e.__str__())
            return

    def login_via_ssh(self):
        try:

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(hostname=self.ip,
                           username=self.user,
                           password=self.password,
                           look_for_keys=False,
                           allow_agent=False,
                           timeout=self.connection_timeout,
                           banner_timeout=70)

            ssh = client.invoke_shell()
            ssh.timeout = self.connection_timeout
            time.sleep(self.answer_delay)

            self.logger.critical('SUCCESS')

            return ssh

        except paramiko.ssh_exception.SSHException as e:

            if 'Incompatible ssh server' in e.__str__() or \
                    'Negotiation failed.' in e.__str__() or \
                    'Bad authentication type' in e.__str__() and self.telnet:

                self.logger.critical('ssh corrupted version, manage protocol switch to telnet')
                self.mng_protocol = 'telnet'
                return self.login_via_telnet()
        except:
            self.logger.critical('error')
            self.logger.exception('error')

    def _log_in(self):

        """
        return connected_object
        """

        answer_string = b''

        if not self.mng_protocol:
            self.scan_mng_protocols()

        if not self.mng_protocol:
            raise NotMngProtocol('no ssh no telnet')

        if self.mng_protocol.lower() == 'ssh':
            self.connection = self.login_via_ssh()

        elif self.mng_protocol.lower() == 'telnet':
            self.connection = self.login_via_telnet()

        if self.connection:

            # for telnet get_info executed in "login_via_telnet" section
            if self.mng_protocol.lower() == 'ssh':

                while True:

                    if self.connection.recv_ready():
                        break

                    self.connection.send(self.command_line_break)

                    time.sleep(self.answer_delay)
                    if self.vendor.lower() == 'mikrotik':
                        time.sleep(self.answer_delay)

                answer_string = self.connection.recv(65000)

                answer_string = replace_ansi_char(answer_string).decode('utf-8')

                self.find_info(answer_string)

                if not (
                    self.vendor and
                    self.os and
                    self.image_name and
                    self.image_version and
                    self.release and
                    self.platform
                ):

                    self.find_info(
                        self.send_short_commands(
                            self.command_info
                        )
                    )

            self.send_short_commands(
                self.command_screen_length_disable
            )

            if not (
                    self.vendor and
                    self.os and
                    self.image_name and
                    self.image_version and
                    self.release and
                    self.platform
            ):

                self.find_info(
                    self.send_short_commands(
                        self.command_info
                    )
                )

            self.send_short_commands(
                self.command_screen_length_disable
            )

        else:
            raise NoConnection

    def log_out(self):

        if not self.connection:
            self.logger.critical('no connection')
            return False

        logout_command = self.command_logout
        if self.mng_protocol.lower() == 'telnet':
            logout_command = logout_command

        try:

            self.send_short_commands(logout_command, log_out=True)

            time.sleep(10)

            self.connection.close()
            self.connection = None

        except Exception as e:

            self.logger.exception(e.__str__())

        self.logger.critical('SUCCESS')
