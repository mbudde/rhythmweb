## Rhythmweb - A web site for your Rhythmbox ##

Rhythmweb lets you control [Rhythmbox](http://www.gnome.org/projects/rhythmbox/)
remotely, from your web browser. It is not an Internet radio server - it does
not play music in your web browser, rather it lets you control Rhythmbox
on a machine other than the one it is running on.

Rhythmweb was inspired by Joe Shaw's Banshee Media Server, which /is/ a
Internet radio server.

This version is a fork of the original project created by Michael Gratton.
The original version is available from [his website](http://web.vee.net/projects/rhythmweb).

### Requirements ###

To use Rhythmweb, you must have the following installed:

 - Rhythmbox v0.11 (v0.10 might work)
 - Python 2.5.
 - python-gconf
 - python-gtk2
 - python-gobject

### Installation ###

To install Rhythmweb run the following command as root:
    make install
To install in the local plugin dir use:
    make install-user
This will install the plugin to `~/.local/share/rhythmbox/plugins' which
requires you use atleast Rhythmbox 0.12.0. Are you using an older version use:
    DESTDIR=~/.gnome2/rhythmbox/plugins make install

When the plugin has been enabled in Rhythmbox you can browse to the machine
running Rhythmbox (per default the server will listen to port 8000, but that can
be changed in the plugin preferences), eg: http://you-rb-host:8000/

### License ###

Copyright (C) 2007 Michael Gratton.  
Copyright (C) 2009 Michael Budde.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

