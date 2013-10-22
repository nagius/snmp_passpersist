#!/usr/bin/python -u
# The -u parameter in the shebang line is critical

import snmp_passpersist
import settings
import syslog

POLLING_INTERVAL = 6
NET_SNMP_EXTEND_MIB = "1.3.6.1.4.1.8072.1.3.1"
BASE_OID = NET_SNMP_EXTEND_MIB + '.2'


class SipSettings(Settings):
    FNAME = '/etc/asterisk/sip.conf'


class SnmpExtBase(object):
    POLLING_INTERVAL = 60
    BASE_OID = None

    def __init__(self, base_oid=None):
        if base_oid:
            self.BASE_OID = base_oid
        self.snmp = snmp_passpersist.PassPersist(self.BASE_OID)
        self.update()

    def update(self):
        raise NotImplemented

    def start(self):
        self.snmp.start(self.update, self.POLLING_INTERVAL)


class SipSnmpExt(SnmpExtBase):
    NAME_SUFIX = '.1.0'
    VALUE_SUFIX = '.2.0'

    def __init__(self):
        self.settings = settings.Tmip()
        self.assign_oids()
        super(TmipSnmpExt, self).__init__()
        self.snmp.registerSetter(self.BASE_OID, self.setter)

    def assign_oids(self):
        self.oids = dict()
        for i, section in enumerate(sorted(self.settings.sections())):
            for j, attr in enumerate(sorted(self.settings.items(section))):
                attr_name, value = attr
                oid = '%i.%i' % (i + 1, j + 1)
                self.oids[oid] = (section, attr_name)

    def getNameOid(self, oid):
        return '%s%s' % (oid, self.NAME_SUFIX)

    def getValueOid(self, oid):
        return '%s%s' % (oid, self.VALUE_SUFIX)

    def update(self):
        if self.settings.updateFromFile():
            syslog.syslog(syslog.LOG_INFO, 'SipSnmp: reading settings')
            self.assign_oids()
        for oid, setting in self.oids.items():
            section, attr_name = setting
            attr_value = self.settings.get(section, attr_name)
            self.snmp.add_str(self.getNameOid(oid),  attr_name)
            self.snmp.add_str(self.getValueOid(oid), attr_value)

    def getSectionAttr(self, oid):
        key = oid.strip()
        if key.endswith(self.VALUE_SUFIX):
            key = key[:-len(self.VALUE_SUFIX)].rstrip('.')
        if key.startswith(self.BASE_OID):
            key = key[len(self.BASE_OID):].lstrip('.')
        if key in self.oids:
            return self.oids[key]

    def setter(self, oid, type_, value):
        try:
            section, attr_name = self.getSectionAttr(oid)
        except:
            syslog.syslog(syslog.LOG_ERR, 'SipSnmp: unknown OID: %s' % oid)
            return False
        try:
            self.settings.set(section, attr_name, str(value))
            self.settings.write()
            self.update()
            self.snmp.commit()
            return True
        except Exception as e:
            syslog.syslog(syslog.LOG_ERR,
                          'SipSnmp: error calling set(%s, %s, %s): %s' %
                          (section, attr_name, str(value), str(e)))
            return False


if __name__ == '__main__':
    sipext = SipSnmpExt()
    sipext.start()
