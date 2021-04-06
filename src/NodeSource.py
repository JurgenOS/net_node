# -*- coding: utf-8 -*-

from time import sleep

from src.Connect import Connect
from src.helpers.Errors import *
from src.helpers.normalizers import normalize_mac_address_table


class MainNode(Connect):

    def __init__(self, ip, log_dir):

        super().__init__(ip, log_dir)

        self.enable: str = ''
        self.authentication_domain: str = ''
        self.user: str = ''
        self.password: str = ''

        self.snmp_community_list: list = []

        self.running_config: str = ''
        self.arp_table: str = ''
        self.mac_address_table: str = ''
        self.cdp_neighbors_table: str = ''
        self.route_table: str = ''
        self.bgp_neighbors_table: str = ''
        self.bgp_route_table: str = ''
        self.mng_protocol: str = ''
        self.neighbors_table: dict = {}

        self.date_of_last_login: str = ''
        self.date_of_last_config: str = ''

        self.logging_directory: str = ''

    def log_in(self):

        try:

            if not self.password:
                raise NotCredentials('no credentials')

            self._log_in()

        except NotCredentials as e:
            self.logger.critical(e.__str__())

        except NotMngProtocol as e:
            self.logger.critical(e.__str__())

        except NoConnection as e:
            self.logger.critical(e.__str__())

    def get_info_snmp(self):

        for snmp_community in self.snmp_community_list:

            try:
                response = self.scan_snmp_system_info(snmp_community)

                if not response:
                    continue
                else:

                    self.vendor = self.find_vendor(response)

                    break

            except FailedSnmpCommunity:
                continue

    def get_running_config(self):

        try:

            self.running_config = self.get_show_command_output(self.command_show_running_config)

        except Exception as e:

            self.logger.critical(e.__str__())

            raise NotRunningConfig

    def get_mac_address_table(self):

        row_mac_address_table = self.get_show_command_output(self.command_show_mac_address_table)
        self.mac_address_table = normalize_mac_address_table(row_mac_address_table)

    def bruteforce(self, password_dictionary_file):
        """

        :param password_dictionary_file: text file in format "login<space>password"
        if where is no login, it is replaced by space
        :return:
        """

        with open(password_dictionary_file) as f:
            login_password_list = f.readlines()

        for line in login_password_list:
            login, password = line.split()

            if not password:
                raise NoBruteforcePassword

            self.user = login.strip()
            self.password = password.strip()

            try:

                if not self.mng_protocol:
                    self.scan_mng_protocols()

                if self.mng_protocol.lower() == 'ssh':
                    self.connection = self.login_via_ssh()

                elif self.mng_protocol.lower() == 'telnet':
                    self.connection = self.login_via_telnet()

                sleep(2)

            except:
                print(f'"{login}" "{password}" FAILED')

            if self.connection:
                self.connection.close()
                return login, password
