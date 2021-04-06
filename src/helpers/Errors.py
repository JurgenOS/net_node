# -*- coding: utf-8 -*-

class ConfigurationError(Exception):

    def init(self):
        super().__init__(self)

class NoConnection(Exception):

    def init(self):
        super().__init__(self)

class InformationError(Exception):

    def init(self):
        super().__init__(self)


class FailedGetInfo(Exception):

    def init(self):
        super().__init__(self)


class FailedGetVendor(Exception):

    def init(self):
        super().__init__(self)


class FailedGetConnection(Exception):

    def init(self):
        super().__init__(self)


class FailedGetImage(Exception):

    def init(self):
        super().__init__(self)


class FailedAuthentication(Exception):

    def init(self):
        super().__init__(self)


class FailedSnmpCommunity(Exception):

    def init(self):
        super().__init__(self)


class NoAclOnVty(Exception):

    def init(self):
        super().__init__(self)


class VtyAclOnInterface(Exception):

    def init(self):
        super().__init__(self)


class NoAcl(Exception):

    def init(self):
        super().__init__(self)


class NoDetailAclStr(Exception):

    def init(self):
        super().__init__(self)


class DenyInLastLine(Exception):

    def init(self):
        super().__init__(self)


class NotAclLineNumber(Exception):

    def init(self):
        super().__init__(self)


class NoAclType(Exception):

    def init(self):
        super().__init__(self)


class NonexistentAcl(Exception):

    def init(self):
        super().__init__(self)


class AclIsMissed(Exception):

    def init(self):
        super().__init__(self)


class NoBruteforcePassword(Exception):

    def init(self):
        super().__init__(self)


class NotRightMacAddressLength(Exception):

    def init(self):
        super().__init__(self)


class NormalizeErrorNoInterfaceName(Exception):

    def init(self):
        super().__init__(self)


class NormalizeErrorNoInterfaceNumber(Exception):

    def init(self):
        super().__init__(self)


class L2LoopDetection(Exception):

    def init(self):
        super().__init__(self)


class NotFullMacAddressTableFound(Exception):

    def init(self):
        super().__init__(self)


class NotAvailable(Exception):

    def init(self):
        super().__init__(self)


class NotLogDir(Exception):

    def init(self):
        super().__init__(self)


class NotMngProtocol(Exception):

    def init(self):
        super().__init__(self)


class NotCredentials(Exception):

    def init(self):
        super().__init__(self)


class NotClearOutput(Exception):

    def init(self):
        super().__init__(self)


class NotNodeID(Exception):

    def init(self):
        super().__init__(self)


class NotAppliedCommands(Exception):

    def init(self):
        super().__init__(self)


class NotCheckConnection(Exception):

    def init(self):
        super().__init__(self)


class NotTheSameAclSnmp(Exception):

    def init(self):
        super().__init__(self)


class NoAclOnSnmp(Exception):

    def init(self):
        super().__init__(self)


class SnmpAclOnInterface(Exception):

    def init(self):
        super().__init__(self)


class NotSingleHostnameFound(Exception):

    def init(self):
        super().__init__(self)


class NotRunningConfig(Exception):

    def init(self):
        super().__init__(self)
