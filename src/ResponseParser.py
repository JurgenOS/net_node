# -*- coding: utf-8 -*-

import pkg_resources
from os import scandir
import re
from pathlib import Path

from src.helpers.ugly_charset import delete_line_breaker, replace_empty_line
from src.helpers.string_exclusions import vendor_exclusions
from src.VendorDependedCommands import VendorDependedCommands
from src.helpers.names_and_regex import corrupted_images_names, node_id_reg, max_vty_line_number_reg
from src.helpers.Errors import *

path = 'helpers/static/'
constants_path = pkg_resources.resource_filename(__name__, path)
p = Path(constants_path)


class ResponseParser(VendorDependedCommands):

    def __init__(self, ip, log_dir):

        super().__init__(ip, log_dir)

    @property
    def string_id_list(self):
        strings = []

        for file in scandir(p / 'string_ids'):
            with open(file) as f:
                strings.extend(map(str.strip, f.readlines()))

        strings.sort(key=len, reverse=True)

        return strings

    @property
    def image_version_list(self):

        versions = []
        for file in scandir(p / 'images_versions'):
            with open(file) as f:
                versions.extend(map(str.strip, f.readlines()))

        versions.sort(key=len, reverse=True)

        return versions

    @property
    def images_list(self):
        images = []

        for file in scandir(p / 'images_names_old'):
            with open(file) as f:
                images.extend(
                    map(
                        str.lower,
                        map(str.strip, f.readlines())
                    )
                )

        images += corrupted_images_names
        images.sort(key=len, reverse=True)

        return images

    @property
    def vendors_dict(self):
        result = {}
        for file in scandir(p / 'vendors'):
            with open(file) as f:
                result[file.name] = list(map(str.strip, f.readlines()))

        return result

    @property
    def vendors_tuple(self):

        result = []

        for file in scandir(p / 'vendors'):
            with open(file) as f:
                for string in list(map(str.strip, f.readlines())):
                    result.append((string, file.name))

        result.sort(key=lambda x: len(x[0]), reverse=True)

        return result

    @property
    def platforms_list(self):

        platforms = []
        for file in scandir(p / 'platforms'):
            with open(file) as f:
                platforms.extend(map(str.strip, f.readlines()))

        platforms.sort(key=len, reverse=True)
        return platforms

    @property
    def releases_list(self):

        releases = []
        for file in scandir(p / 'images_releases'):
            with open(file) as f:
                releases.extend(f.readlines())

        releases.sort(key=len, reverse=True)

        return releases

    @property
    def patches_list(self):

        patches = []
        for file in scandir(p / 'patches_names'):
            with open(file) as f:
                patches.extend(map(str.strip, f.readlines()))

        patches.sort(key=len, reverse=True)

        return patches

    @property
    def patches_versions_list(self):

        patches_versions = []
        for file in scandir(p / 'patches_versions'):
            with open(file) as f:
                patches_versions.extend(map(str.strip, f.readlines()))

        patches_versions.sort(key=len, reverse=True)
        return patches_versions

    @property
    def oss_list(self):

        oss = []
        for file in scandir(p / 'oss'):
            with open(file) as f:
                oss.extend(map(str.strip, f.readlines()))

        oss.sort(key=len, reverse=True)
        return oss

    @property
    def last_user_terminal_interface_number_strings_list(self):

        lines = []

        with open(p / 'last_user_terminal_interface_number') as f:
            lines.extend(map(str.strip, f.readlines()))

        lines.sort(key=len, reverse=True)

        return lines

    def find_id(self, input_string):

        res = ''
        for id_string in self.string_id_list:
            if id_string.lower() in input_string.lower():
                res = re.search(f'{id_string.lower()} {node_id_reg}', input_string.lower())
                break

        try:
            res = res[1]
        except Exception as e:
            # self.logger.critical(f'ERROR: no node id in {res} the error is "{e.__str__()}"')
            res = f'no_id. res: "{res}" ERROR: "{e.__str__()}"'

        return res

    def find_vendor(self, input_string):

        res = ''

        if [x for x in vendor_exclusions if x in input_string]:
            return res

        for string, vendor in self.vendors_tuple:
            if string in input_string:
                res = vendor
                break

        return res

    def find_image_file_name(self, input_string):
        res = ''

        for image in self.images_list:
            if image.lower() in input_string.lower():
                res = image
                break
        return res

    def find_image_version(self, input_string):

        res = ''

        for version in self.image_version_list:
            if version in input_string:
                res = version.strip()
                break

        return res

    def find_platform(self, input_string):

        res = ''

        for platform in self.platforms_list:
            if platform in input_string:
                res = platform
                break

        return res

    def find_os(self, input_string):

        res = ''

        for os in self.oss_list:
            if os in input_string:
                res = os
                break

        if res.lower() == 'ProCurve':
            res = 'HP ProVision'

        return res

    def find_release(self, input_string):

        res = ''
        for release in self.releases_list:
            if delete_line_breaker(release) in input_string:
                res = release.strip()
                break

        return res

    def find_info(self, input_string):

        vendor_tmp = self.find_vendor(input_string)
        release_tmp = self.find_release(input_string)

        self.vendor = self.vendor or vendor_tmp
        self.release = self.find_release(input_string).strip() or release_tmp

        if not self.image_name:
            self.image_name = self.find_image_file_name(input_string)

        if not self.image_version:
            self.image_version = self.find_image_version(input_string)

        # if not self.release:
        # self.release = self.find_release(input_string).strip()

        if not self.platform:
            self.platform = self.find_platform(input_string)

        if not self.id:
            self.id = self.find_id(input_string)

        if not self.os:

            #for cisco catos
            if self.vendor.lower() == 'cisco' and 'NmpSW:' in self.image_version and 'cat' in self.image_name:
                self.os = 'CatOS'
            else:
                self.os = self.find_os(input_string)

    def find_patch_file_name(self, input_string):
        for patch in self.patches_list:
            if patch in input_string:
                return patch

    def find_patch_version(self, input_string):
        for patch_version in self.patches_versions_list:
            if patch_version in input_string:
                return patch_version

    def find_vty_max_number(self, input_string):

        res = ''
        r = ''

        for line in self.last_user_terminal_interface_number_strings_list:

            for input_line in input_string.split('\n'):

                if line.strip() in input_line.strip():

                    r = re.search(max_vty_line_number_reg, input_line.strip())
        try:
            res = r[1]
        except:
            pass

        return res

    def find_vty_max_configured_number(self, input_string):

        max_vty = ''

        if not self.vendor:
            raise FailedGetVendor
        for line in input_string.split('\n'):
            if self.command_vty_config_mode in line:
                max_vty = line.strip().split(' ')[-1]

        return max_vty

    def find_acl_on_vty(self, input_string):

        acl = ''

        if not self.vendor:
            raise FailedGetVendor

        is_vty_start_line_found = False

        for line in input_string.split('\n'):

            if self.command_vty_config_mode in line:
                is_vty_start_line_found = True

            if not is_vty_start_line_found:
                continue

            if self.command_access_list_on_vty(acl).split(' ')[0] in line and \
                    self.command_access_list_on_vty(acl).split(' ')[-1] in line:
                acl = line.strip().split(' ')[1]

        return acl

    def find_acl_on_snmp(self, input_string, snmp_community):

        acl = ''
        acl_set: set = set()

        snmp_community_line_reg = re.compile(self.command_access_list_on_snmp('(.+?)', '(\S+)'))

        if not self.vendor:
            raise FailedGetVendor

        for line in input_string.split('\n'):

            res = snmp_community_line_reg.search(line)
            if res:
                acl_set.add(res.groups()[1])

        return acl_set
