#
# Rhythmweb - a web site for your Rhythmbox.
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

import gtk
import gtk.glade
import gconf
import os

class Preference(object):
    def __init__(self, path, default):
        self.gconf = gconf.client_get_default()
        self.path = path
        self.default = default

    def get(self):
        try:
            return self.gconf.get_value(self.path)
        except ValueError:
            self.set(self.default)
            return self.default

    def set(self, val):
        self.gconf.set_value(self.path, val)

    def shutdown(self):
        del self.gconf


class PreferenceManager(object):

    def __init__(self, dir):
        self.prefs_dir = dir
        self.prefs = {}

    def shutdown(self):
        for key in self.prefs:
            self.prefs[key].shutdown()

    def __getitem__(self, key):
        return self.prefs[key]

    def add_pref(self, key, default):
        path = '%s/%s' % (self.prefs_dir, key)
        self.prefs[key] = Preference(path, default)


class RhythmwebPrefs(PreferenceManager):
    plugin_gconf_dir = '/apps/rhythmbox/plugins/rhythmweb'

    def __init__(self):
        super(RhythmwebPrefs, self).__init__(self.plugin_gconf_dir)

        self.add_pref('port', 8000)


class RhythmwebPrefsDialog(object):
    
    def __init__(self, plugin):
        self.plugin = plugin
        glade_file = plugin.find_file('rhythmweb-prefs.glade')
        gladexml = gtk.glade.XML(glade_file)

        self.dialog = gladexml.get_widget('dialog')
        self.port = gladexml.get_widget('port')
        self.port.set_value(self.plugin.prefs['port'].get())

        self.dialog.connect('response', self.dialog_response)

    def shutdown(self):
        del self.plugin

    def dialog_response(self, dialog, response):
        self.plugin.prefs['port'].set(int(self.port.get_value()))
        dialog.hide()
        
    def get_dialog(self):
        return self.dialog

