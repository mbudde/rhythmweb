#
# Rhythmweb - a web site for your Rhythmbox.
# Copyright (C) 2007 Michael Gratton.
# Copyright (C) 2009 Michael Budde
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import socket

import rb
import rhythmdb

# try to load avahi, don't complain if it fails
try:
    import dbus
    import avahi
    use_mdns = True
except:
    use_mdns = False

from preferences import RhythmwebPrefs, RhythmwebPrefsDialog
from server.server import RhythmwebServer


class RhythmwebPlugin(rb.Plugin):

    def __init__(self):
        super(RhythmwebPlugin, self).__init__()

    def activate (self, shell):
        self.db = shell.props.db
        self.shell = shell
        self.player = shell.get_player()
        self.prefs = RhythmwebPrefs()
        self.prefs_dialog = RhythmwebPrefsDialog(self)
        self.server = RhythmwebServer('', self.prefs['port'].get(), self)
        self._mdns_publish()

    def deactivate(self, shell):
        self._mdns_withdraw()
        self.server.shutdown()
        self.prefs.shutdown()
        self.prefs_dialog.shutdown()
        del self.server
        del self.prefs
        del self.prefs_dialog
        del self.player
        del self.shell
        del self.db

    def create_configure_dialog(self, dialog=None):
        if not dialog:
            dialog = self.prefs_dialog.get_dialog()
        dialog.present()
        return dialog

    def _mdns_publish(self):
        if use_mdns:
            bus = dbus.SystemBus()
            avahi_bus = bus.get_object(avahi.DBUS_NAME,
                                       avahi.DBUS_PATH_SERVER)
            avahi_svr = dbus.Interface(avahi_bus,
                                       avahi.DBUS_INTERFACE_SERVER)

            servicetype = '_http._tcp'
            servicename = 'Rhythmweb on %s' % (socket.gethostname())

            eg_path = avahi_svr.EntryGroupNew()
            eg_obj = bus.get_object(avahi.DBUS_NAME, eg_path)
            self.entrygroup = dbus.Interface(
                    eg_obj,
                    avahi.DBUS_INTERFACE_ENTRY_GROUP
            )
            self.entrygroup.AddService(
                    avahi.IF_UNSPEC,
                    avahi.PROTO_UNSPEC,
                    0,
                    servicename,
                    servicetype,
                    "",
                    "",
                    dbus.UInt16(self.prefs['port'].get()),
                    ()
            )
            self.entrygroup.Commit()

    def _mdns_withdraw(self):
        if use_mdns and self.entrygroup != None:
            self.entrygroup.Reset()
            self.entrygroup.Free()
            self.entrygroup = None

