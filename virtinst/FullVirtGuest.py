#!/usr/bin/python -tt
#
# Fullly virtualized guest support
#
# Copyright 2006  Red Hat, Inc.
# Jeremy Katz <katzj@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os,stat,time,sys
import string

import libvirt

import XenGuest
import util

if os.uname()[4] in ("x86_64"):
    qemu = "/usr/lib64/xen/bin/qemu-dm"
else:
    qemu = "/usr/lib/xen/bin/qemu-dm"

class FullVirtGuest(XenGuest.XenGuest):
    def __init__(self, hypervisorURI=None):
        XenGuest.XenGuest.__init__(self, hypervisorURI=hypervisorURI)
        self._cdrom = None
        self.disknode = "hd"
        self.features = { "acpi": True, "pae": util.is_pae_capable(), "apic": True }

    def get_cdrom(self):
        return self._cdrom
    def set_cdrom(self, val):
        val = os.path.abspath(val)
        if not os.path.exists(val):
            raise ValueError, "CD device must exist!"
        self._cdrom = val
    cdrom = property(get_cdrom, set_cdrom)

    def _get_disk_xml(self):
        # ugh, this is disgusting, but the HVM disk stuff isn't nice :/
        xml = XenGuest.XenGuest._get_disk_xml(self)
        if self.cdrom:
            disk = XenGuest.XenDisk(self.cdrom, readOnly = True, device=XenGuest.XenDisk.DEVICE_CDROM)
            # XXX no need to hardcode hdc in newer xen
            xml += disk.get_xml_config("hdc")
        return xml

    def _get_features_xml(self):
        ret = ""
        for (k, v) in self.features.items():
            if v:
                ret += "<%s/>" %(k,)
        return ret

    def _get_features_xen(self):
        ret = ""
        for (k, v) in self.features.items():
            if v:
                ret += "%s=1\n" %(k,)
        return ret

    def _get_network_xen(self):
        # Sick copying this from XenGuest.py, but ultimately all
        # XM config stuff will be moved to xend/libvirt and so this
        # will go away.
        """Get the network config in the xend python format"""
        if len(self.nics) == 0: return ""
        ret = "vif = [ "
        for n in self.nics:
            ret += "'type=ioemu, mac=%(mac)s, bridge=%(bridge)s', " % { "bridge": n.bridge, "mac": n.macaddr }
        ret += "]"
        return ret


    def _get_config_xml(self, install = True):
        # FIXME: hard-codes that we're booting from CD as hdd
        if install:
            action = "destroy"
            bootdev = "cdrom"
        else:
            action = "restart"
            bootdev = "hd"
            
        return """<domain type='xen'>
  <name>%(name)s</name>
  <os>
    <type>hvm</type>
    <loader>/usr/lib/xen/boot/hvmloader</loader>
    <boot dev='%(bootdev)s'/>
  </os>
  <features>
    %(features)s
  </features>
  <memory>%(ramkb)s</memory>
  <vcpu>%(vcpus)d</vcpu>
  <uuid>%(uuid)s</uuid>
  <on_reboot>%(action)s</on_reboot>
  <on_crash>%(action)s</on_crash>
  <on_poweroff>destroy</on_poweroff>
  <devices>
    <emulator>%(qemu)s</emulator>
%(disks)s
    %(networks)s
    %(graphics)s
  </devices>
</domain>
""" % { "qemu": qemu, "name": self.name, "vcpus": self.vcpus, "uuid": self.uuid, "ramkb": self.memory * 1024, "disks": self._get_disk_xml(), "networks": self._get_network_xml(), "graphics": self._get_graphics_xml(), "features": self._get_features_xml(), "action": action, "bootdev": bootdev }

    def _get_config_xen(self):
        return """# Automatically generated xen config file
name = "%(name)s"
builder = "hvm"
memory = "%(ram)s"
%(disks)s
%(networks)s
uuid = "%(uuid)s"
device_model = "%(qemu)s"
kernel = "/usr/lib/xen/boot/hvmloader"
%(graphics)s
%(features)s
vcpus=%(vcpus)s
serial = "pty" # enable serial console
on_reboot   = 'restart'
on_crash    = 'restart'
""" % { "name": self.name, "ram": self.memory, "disks": self._get_disk_xen(), "networks": self._get_network_xen(), "uuid": self.uuid, "qemu": qemu, "graphics": self._get_graphics_xen(), "vcpus": self.vcpus, "features": self._get_features_xen() }

    def validate_parms(self):
        if not self.cdrom:
            raise RuntimeError, "A CD must be specified to boot from"
        XenGuest.XenGuest.validate_parms(self)