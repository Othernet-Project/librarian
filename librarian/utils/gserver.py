"""
gserver.py: Code to start and manage servers

Allows Librarian to communicate with ONDD.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

from gevent import pywsgi


class ServerManager(object):

    def __init__(self):
        self.servers = {}

    def start_server(self, label, conf, app):
        """ Start a new server for specified app

        :param label:   label assigned to the server
        :param conf:    configuration dictionary
        :param
        """
        host = conf['{}.bind'.format(label)]
        port = conf['{}.port'.format(label)]
        server = pywsgi.WSGIServer((host, port), app, log=None)
        server.start()  # non-blocking
        assert server.started, 'Expected server to be running'
        logging.debug("Started server %s on http://%s:%s/", label, host, port)
        self.servers[label] = {
            'server': server,
            'app': app,
            'host': host,
            'port': port,
        }

    def stop_all(self, timeout=5):
        """ Stops all running servers """
        servers = self.servers.keys()
        for server in servers:
            self.stop_server(server, timeout)

    def stop_server(self, label, timeout=5):
        """ Stops server identified by label

        :param label:       label of the server to stop
        :param timeout:     timeout (seconds) before server thread is killed
        :returns:           True if server is stopped, False otherwise
        """
        server_conf = self.servers.pop(label, None)
        if not server_conf:
            logging.error("Request to stop '%s': not running", label)
            return False
        server = server_conf['server']
        server.stop(timeout=timeout)
        assert not server.started, 'Expected server to be stopped'
        return True

    def get(self, label):
        server_conf = self.servers.get(label)
        if not server_conf:
            return None
        return server_conf['server']

    def status(self, label):
        server_conf = self.servers.get(label)
        if not server_conf:
            return ('not running', None, None)
        return ('running', server_conf['host'], server_conf['port'])

    @property
    def server_data(self):
        for label, conf in self.servers.items():
            yield (label, conf['host'], conf['port'])
