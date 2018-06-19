# -*- coding: utf-8 -*-

from __future__ import absolute_import

import traceback
import binascii
import logging
import socket
import struct

logger = logging.getLogger('Doctopus.ak')

STX = 0x02
ETX = 0x03
BLANK = 0x20
K = ord('K')

AK_CONNECTED = 1
AK_DISCONNECTED = 0


class AKClient(object):
    """ AK Client """

    def __init__(self, conf):
        """ init """

        self.conf = conf

        self.host = conf["host"]
        self.port = conf["port"]
        self.timeout = conf["timeout"]
        self.allowed_cmds = set()

        for item in conf["allowed_cmds"]:
            self.allowed_cmds.add(item.upper())

        self.status = AK_DISCONNECTED
        self.error_msg = None

    def connect(self):
        """ connect """

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.settimeout(self.timeout)

        try:

            self.sock.connect((self.host, self.port))
            self.status = AK_CONNECTED
        except:
            self.status = AK_DISCONNECTED

    def __del__(self):
        """   """

        logger.debug("__del__")
        self.sock.close()

    def _send(self, buf):
        """ send """

        try:
            self.sock.sendall(buf)
        except Exception as ex:
            traceback.print_exc()
            # logger.debug(ex)
            # self.error_msg = ex.message
            raise (Exception(ex))

    def _recv(self):
        """ recv """

        try:
            data = self.sock.recv(1024)

        except Exception as ex:
            logger.debug(ex)
            # self.error_msg = ex.message
            raise (Exception(ex))
        return data

    def validate(self, cmd):
        """   """

        if cmd in self.allowed_cmds:
            return True
        else:
            return False

    def query(self, cmd):
        """ query """
        # channel number for build struct
        channel_number = 0
        # flag of if data is recv enough
        RECV_ENOUGH = 0
        out = b''
        data = {}

        cmd = cmd.upper()

        if True: 

            msg = self.pack(cmd, channel_number)
            # print "------ ak.py-msg--- %s" % (msg)
            self._send(msg)

            while not RECV_ENOUGH:
                data_recv = self._recv()
                
                RECV_ENOUGH = self.check_data_recv(data_recv)
                # accumulate recv data if not enough
                out = out + data_recv

            out = self.unpack(out)
                # print(len(out))


            if len(out) > 6:
                data[cmd] = out[6]
            else:
                data[cmd] = cmd

            return data

        else:
            logger.warning("not allowed:[%s]" % cmd)
            return {}
    
    @staticmethod
    def check_data_recv(data):
        """
        check recv data if enough by the last byte
        """
        end = bytes([ETX])
        if data.endswith(end):
            return True
        else:
            return False
        
    def query_all(self, cmds):
        """ query """

        # channel number for build struct
        channel_number = 0

        data = {}

        cmds_set = set()

        for cmd in cmds:

            cmd = cmd.upper()

            if self.validate(cmd):
                cmds_set.add(cmd)
            else:
                logger.warning("not allowed:[%s]" % cmd)
                continue

        logger.debug(cmds_set)

        for cmd in cmds_set:

            msg = self.pack(cmd, channel_number)

            self._send(msg)

            data_recv = self._recv()
            # print(data_recv)
            out = self.unpack(data_recv)
            # print(len(out))

            if len(out) > 6:
                data[cmd] = out[6]
            else:
                data[cmd] = cmd

        return data

    def pack(self, cmd, channel_number, code=None):
        """ AK command pack """

        # cmd = "AVFI"
        # print(channel_number, cmd, code)
        # cmd = cmd.upper()

        if cmd.count('AFLT') == 1:
            """ The dyno will return the fault text within double quotes (102 characters max data.)
                If the fault number is not found, just the two double quotes will be returned.
            """
            code = cmd.split(" ")[1]
            if code is None:
                raise (Exception("The fault number must be specified with the AFLT request."))

            else:

                clen = len(cmd)

                # AK Command telegram
                fmt = "!2b%ds5b" % clen
                # print fmt
                # channel_number = 0

                buf = struct.pack(fmt, STX, BLANK, cmd, BLANK, K, channel_number, BLANK, ETX)
                # logger.debug(buf)

                return buf

        else:

            clen = len(cmd)

            # AK Command telegram
            fmt = "!2b%ds5b" % clen
            # print fmt
            # channel_number = 0


            # for python2
            # buf = struct.pack(fmt, STX, BLANK, cmd.encode('utf-8'), BLANK, K, channel_number, BLANK, ETX) 
            # for python3
            buf = struct.pack(fmt, STX, BLANK, cmd.encode('utf-8'), BLANK, K, channel_number, BLANK, ETX)
            # logger.debug(buf)
            return buf

    def unpack(self, data):
        """ AK unpack """
        # logger.debug("recv {}".format(data))
        dlen = len(data) - 10
        # dlen = len(data) - 11 # AVL

        if dlen < 0:
            # raise Exception("struct error")
            fmt = "!2b4s3b"

        else:
            # AK Response telegram !2b4s4b%ds1d
            # AVL Response maybe different from BEP, so if don't work try another 
            fmt = "!2b4s3b%ds1b" % dlen       # bep
            # fmt = "!2b4s4b%ds1b" % dlen       # AVL

        try:
            val = struct.unpack(fmt, data)

            # print(type(val))
            # tuple
            return val
        except Exception as ex:
            # logger.error(ex.message)
            b64 = binascii.b2a_base64(data)
            logger.error(b64)
            return {"error": ex, "base64": b64}
            # raise Exception("unpack exception")
