#
# Copyright 2006-2009  Red Hat, Inc.
# Daniel P. Berrange <berrange@redhat.com>
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

import Installer

class PXEInstaller(Installer.Installer):

    # General Installer methods

    def prepare(self, guest, meter, distro = None):
        pass

    def get_install_xml(self, guest, isinstall):
        if isinstall:
            bootdev = "network"
        else:
            # TODO: This can be smarter, take into account different
            #       disk types, media availability, etc. Probably relevant
            #       for other installers as well.
            if len(guest.disks) == 0:
                bootdev = "network"
            else:
                bootdev = "hd"

        return self._get_osblob_helper(isinstall=isinstall, guest=guest,
                                       kernel=None, bootdev=bootdev)