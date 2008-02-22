#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free  Software Foundation; either version 2 of the License, or
# (at your option)  any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.

import os.path
import unittest
import virtinst.CapabilitiesParser as capabilities

class TestCapabilities(unittest.TestCase):

    def _compareGuest(self, (arch, os_type, hypervisor_type, features), guest):
        self.assertEqual(arch,            guest.arch)
        self.assertEqual(os_type,         guest.os_type)
        self.assertEqual(hypervisor_type, guest.hypervisor_type)
        for n in features:
            self.assertEqual(features[n],        guest.features[n])

    def _testCapabilities(self, path, (host_arch, host_features), guests):
        caps = capabilities.parse(file(os.path.join("tests", path)).read())

        self.assertEqual(host_arch,     caps.host.arch)
        for n in host_features:
            self.assertEqual(host_features[n], caps.host.features[n])

        map(self._compareGuest, guests, caps.guests)

    def testCapabilities1(self):
        host = ( 'x86_64', {'vmx': capabilities.FEATURE_ON} )

        guests = [
            ( 'x86_64', 'xen', 'xen', {} ),
            ( 'i686',   'xen', 'xen', { 'pae': capabilities.FEATURE_ON } ),
            ( 'i686',   'hvm', 'xen', { 'pae': capabilities.FEATURE_ON|capabilities.FEATURE_OFF } ),
            ( 'x86_64', 'hvm', 'xen', {} )
        ]

        self._testCapabilities("capabilities-xen.xml", host, guests)

    def testCapabilities2(self):
        host = ( 'x86_64', {} )

        guests = [
            ( 'x86_64', 'hvm', 'qemu', {} ),
            ( 'i686',   'hvm', 'qemu', {} ),
            ( 'mips',   'hvm', 'qemu', {} ),
            ( 'mipsel', 'hvm', 'qemu', {} ),
            ( 'sparc',  'hvm', 'qemu', {} ),
            ( 'ppc',    'hvm', 'qemu', {} ),
        ]

        self._testCapabilities("capabilities-qemu.xml", host, guests)

    def testCapabilities3(self):
        host = ( 'i686', { 'pae': capabilities.FEATURE_ON|capabilities.FEATURE_OFF } )

        guests = [
            ( 'i686', 'linux', 'test', { 'pae': capabilities.FEATURE_ON|capabilities.FEATURE_OFF } ),
        ]

        self._testCapabilities("capabilities-test.xml", host, guests)

if __name__ == "__main__":
    unittest.main()
