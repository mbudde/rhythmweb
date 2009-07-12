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

import time
import cgi
import sys
import os
from wsgiref.simple_server import WSGIRequestHandler
from wsgiref.simple_server import make_server
import gtk
import gobject

from interface import RhythmwebInterface

class RhythmwebServer(object):

    def __init__(self, hostname, port, plugin):
        self.plugin = plugin
        self.running = True
        self._httpd = make_server(hostname, port, self._wsgi,
                                  handler_class=LoggingWSGIRequestHandler)
        self._watch_cb_id = gobject.io_add_watch(self._httpd.socket,
                                                 gobject.IO_IN,
                                                 self._idle_cb)
        self.interface = RhythmwebInterface(plugin)

    def shutdown(self):
        gobject.source_remove(self._watch_cb_id)
        self.interface.shutdown()
        self.running = False
        del self.interface
        del self.plugin

    def _idle_cb(self, source, cb_condition):
        if not self.running:
            return False
        self._httpd.handle_request()
        return True

    def _wsgi(self, environ, start_response):
        path = environ['PATH_INFO']
        if path in ('/', ''):
            return self._handle_interface(environ, start_response)
        elif path.startswith('/control'):
            return self._handle_control(environ, start_response)
        elif path.startswith('/stock/'):
            return self._handle_stock(environ, start_response)
        else:
            return self._handle_static(environ, start_response)

    def _handle_interface(self, environ, start_response):
        return self.interface.send(start_response)

    def _handle_control(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            params = parse_post(environ)
            if 'action' in params:
                action = params['action'][0]
                return self.interface.handle_action(action,
                                                    start_response)
        response_headers = [('Content-type', 'text/plain')]
        start_response('400 Bad Request', response_headers)
        return 'No action specified'

    def _handle_stock(self, environ, start_response):
        path = environ['PATH_INFO']
        stock_id = path[len('/stock/'):]

        icons = gtk.icon_theme_get_default()
        iconinfo = icons.lookup_icon(stock_id, 24, ())
        if not iconinfo:
            iconinfo = icons.lookup_icon(stock_id, 32, ())
        if not iconinfo:
            iconinfo = icons.lookup_icon(stock_id, 48, ())
        if not iconinfo:
            iconinfo = icons.lookup_icon(stock_id, 16, ())

        if iconinfo:
            filename = iconinfo.get_filename()
            icon = open(filename)
            lastmod = time.gmtime(os.path.getmtime(filename))
            lastmod = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                    lastmod)
            response_headers = [('Content-type','image/png'),
                                ('Last-Modified', lastmod)]
            start_response('200 OK', response_headers)
            return icon
        else:
            response_headers = [('Content-type','text/plain')]
            start_response('404 Not Found', response_headers)
            return 'Stock not found: %s' % stock_id

    def _handle_static(self, environ, start_response):
        rpath = environ['PATH_INFO']

        path = rpath.replace('/', os.sep)
        path = os.path.normpath(path)
        if path[0] == os.sep:
            path = path[1:]

        file_path = self.plugin.find_file(path)
        if file_path == None:
            file_path = self.plugin.find_file(os.path.join('client',
                                                           path))

        if os.path.isfile(file_path):
            lastmod = time.gmtime(os.path.getmtime(file_path))
            lastmod = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                    lastmod)
            response_headers = [('Content-type','text/css'),
                                ('Last-Modified', lastmod)]
            start_response('200 OK', response_headers)
            return open(file_path)
        else:
            response_headers = [('Content-type','text/plain')]
            start_response('404 Not Found', response_headers)
            return 'File not found: %s' % rpath


class LoggingWSGIRequestHandler(WSGIRequestHandler):

    def log_message(self, format, *args):
        # RB redirects stdout to its logging system, to these
        # request log messages, run RB with -D rhythmweb
        sys.stdout.write("%s -- %s\n" %
                         (self.address_string(),
                          format%args))


def parse_post(environ):
    if 'CONTENT_TYPE' in environ:
        length = -1
        if 'CONTENT_LENGTH' in environ:
            length = int(environ['CONTENT_LENGTH'])
        if environ['CONTENT_TYPE'].find('application/x-www-form-urlencoded') != -1:
            return cgi.parse_qs(environ['wsgi.input'].read(length))
        if environ['CONTENT_TYPE'].find('multipart/form-data') != -1:
            return cgi.parse_multipart(environ['wsgi.input'].read(length))
    return None

