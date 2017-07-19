"""
(C) Copyright 2017 kurokid
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from ISO8583.ISO8583 import ISO8583
from ISO8583.ISOErrors import InvalidIso8583
import socket
import sys
import time
import struct


# Configure the client
serverIP = "10.2.81.3"
serverPort = 9007
# numberEcho = 5
timeBetweenEcho = 10  # in seconds

bigEndian = True
# bigEndian = False

s = None
for res in socket.getaddrinfo(serverIP, serverPort, socket.AF_UNSPEC,
                              socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error, msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error, msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print ('Could not connect :(')
    sys.exit(1)

while True:
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7, '6062307470')
    iso.setBit(11, '000573')
    iso.setBit(70, '301')
    if bigEndian:
        try:
            ascii = iso.getRawIso()
            message = struct.pack('!h', len(ascii) + 2)
            message += ascii
            s.send(message)
            # print ('Sending ... %s' % message)
            ans = s.recv(2048)
            # print ("\nGet ASCII |%s|" % ans)
            size = len(ans)-2
            ans = ans[2:size]
            isoAns = ISO8583()
            isoAns.setIsoContent(ans)
            if isoAns.getMTI() == '0810':
                if isoAns.getBit(39) == '00':
                    print ("Echo Success !!!")
                else:
                    print ("Echo Failed")
        except InvalidIso8583, ii:
            print ii
            break
        time.sleep(timeBetweenEcho)
    else:
        try:
            message = iso.getNetworkISO(False)
            s.send(message)
            print ('Sending ... %s' % message)
            ans = s.recv(2048)
            print ("\nInput ASCII |%s|" % ans)
            isoAns = ISO8583()
            isoAns.setNetworkISO(ans, False)
            v1 = isoAns.getBitsAndValues()
            for v in v1:
                print ('Bit %s of type %s with value = %s' % (v['bit'],
                       v['type'], v['value']))
            if isoAns.getMTI() == '0810':
                print ("That's great !!! The server understand my message !!!")
            else:
                print ("The server dosen't understand my message!")
        except InvalidIso8583, ii:
            print ii
            break
        time.sleep(timeBetweenEcho)

print ('Closing...')
s.close()
