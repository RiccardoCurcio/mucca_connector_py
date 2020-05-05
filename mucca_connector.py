# Copyright 2018 Federica Cricchio
# fefender@gmail.com
#
# This file is part of mucca_connector_py.
#
# mucca_connector_py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mucca_connector_py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mucca_connector_py.  If not, see <http://www.gnu.org/licenses/>.
"""Mucca Connector."""
import socket
import sys
import os
import json
from vendor.mucca_logging_py.mucca_logging_py import logging
from vendor.mucca_connector_py.src.muccaChunckRecvfrom.muccaChunckRecvfrom import muccaChunckRecvfrom
from vendor.mucca_connector_py.src.muccaChunckSendTo.muccaChunckSendTo import muccaChunckSendTo


class mucca_connector:
    """Mucca_connector class."""

    def __init__(self):
        """Init."""
        pass

    def tcpServerHandler(self, ports, chunckSize, eventFlag, callback=None):
        """Tcp client."""
        # Create a TCP/IP socket
        for port in ports:
            newRef = os.fork()
            if newRef == 0:
                # children
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = ('localhost', port)
                try:
                    sock.bind(server_address)
                    sock.listen(1)
                    while True:
                        logging.log_info(
                            'Wait connection on {}:{}'.format(*server_address),
                            os.path.abspath(__file__),
                            sys._getframe().f_lineno
                        )
                        connection, client_address = sock.accept()
                        response = muccaChunckRecvfrom.run(
                            connection,
                            int(chunckSize),
                            logging
                        )
                        callResponse = callback(response)
                        callResponse = bytes(callResponse.encode())
                        if eventFlag is False:
                            muccaChunckSendTo.run(
                                connection,
                                int(chunckSize),
                                str(callResponse, "utf-8"),
                                logging
                            )
                except Exception as e:
                    logging.log_error(
                        'Not bind on {}:{}'.format(*server_address),
                        os.path.abspath(__file__),
                        sys._getframe().f_lineno
                    )
                    pass
                # ---- children
        for port in ports:
            os.waitpid(0, 0)
        pass

    def getServiceFromRegistry(self, serviceName, serviceVersion):
        """Get service from registry."""
        listOfPorts = (os.getenv("REG_PORT")).split(',')
        listOfPorts = list(map(int, listOfPorts))
        message = {
            "service": {
                "version": os.getenv("REG_VERSION"),
                "serviceName": os.getenv("REG_SERVICE_NAME"),
                "action": "read",
                "origin": os.getenv("SERVICE_NAME")
                },
            "query": {},
            "body": {
                "version": serviceVersion,
                "serviceName":  serviceName
                }
        }

        response = self.tcpClientCall(
            listOfPorts,
            os.getenv("REG_HOST"),
            json.dumps(message),
            False,
            int(os.getenv("BUFFERSIZE")),
            os.getenv("REG_SERVICE_NAME"),
            os.getenv("REG_VERSION")
            )
        response = json.loads(response)
        if response["service"]["status"] == "200":
            return response["body"]["host"], response["body"]["port"], response["body"]["eventFlag"]
        # return host, ports

    def tcpClient(self, serviceName, serviceVersion, message):
        """Tcp Client."""
        regResponse = self.getServiceFromRegistry(serviceName, serviceVersion)
        response = self.tcpClientCall(
            regResponse[1],
            regResponse[0],
            message,
            regResponse[2],
            int(os.getenv("BUFFERSIZE")),
            serviceName,
            serviceVersion
            )
        return response

    def tcpClientCall(self, ports, ip, message, eventFlag, chunckSize, serviceName, serviceVersion):
        """Tcp client call."""
        envName = ("{}_{}_INDEX".format(serviceName, serviceVersion)).upper()
        clientIndex = os.getenv(envName)
        numberOfPort = len(ports)

        if clientIndex is None:
            os.environ[envName] = "0"
            clientIndex = int(os.getenv(envName))
        else:
            clientIndex = int(os.getenv(envName))
            clientIndex = clientIndex + 1
            os.environ[envName] = str(clientIndex)
            if clientIndex >= numberOfPort:
                os.environ[envName] = "0"
                clientIndex = int(os.getenv(envName))
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = (ip, ports[clientIndex])
        logging.log_info(
            'Connection to {}:{}'.format(*server_address),
            os.path.abspath(__file__),
            sys._getframe().f_lineno
        )
        sock.connect(server_address)

        try:
            c_message = bytes(message.encode())
            try:
                muccaChunckSendTo.run(
                    sock,
                    int(chunckSize),
                    str(c_message, "utf-8"),
                    logging
                )
            except InterruptedError as emsg:
                logging.log_error(
                    'Interrupted signal error, sendto fail',
                    os.path.abspath(__file__),
                    sys._getframe().f_lineno
                )
            if eventFlag is False:
                response = muccaChunckRecvfrom.run(sock, int(chunckSize), logging)
            else:
                response = True

        finally:
            logging.log_info(
                'Socket close',
                os.path.abspath(__file__),
                sys._getframe().f_lineno
            )
            sock.close()
        return response
