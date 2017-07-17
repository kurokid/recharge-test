"""
(C) Copyright 2009 kurokid
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
from ISO8583.ISOErrors import *
import socket
import sys
import time
import struct


# Configure the client
serverIP = "10.2.81.3"
serverPort = 9007

bigEndian = True
#bigEndian = False

s = None
for res in socket.getaddrinfo(serverIP, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
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

iso = ISO8583()
iso.redefineBit(41, 41, 'Card Acceptor Terminal Identification', 'N', 16, 'an')
iso.redefineBit(18, 18, 'Merchants Type', 'N', 4, 'n')
iso.setMTI('0200')
iso.setBit(2,'000')
iso.setBit(3,'503011')
iso.setBit(4,'000000010000')
iso.setBit(7,'0172162255')
iso.setBit(11,'006241')
iso.setBit(12,'162255')
iso.setBit(13,'0712')
iso.setBit(15,'0712')
iso.setBit(18,'6011')
iso.setBit(32,'515274')
iso.setBit(37,'000000000000')
iso.setBit(41,'test123         ')
iso.setBit(42,'123test        ')
iso.setBit(43,'                                  dicoba')
iso.setBit(48,'0812 94136044000000010000')
iso.setBit(49,'360')
iso.setBit(63,'131001')

if bigEndian:
	try:
		ascii = iso.getRawIso()
		message =  struct.pack('!h', len(ascii) + 2)
		message += ascii
		s.send(message)
		print ('Sending ... %s' % message)
		ans = s.recv(2048)
		print ("\nGet ASCII |%s|" % ans)
		size = len(ans)-2
		ans = ans[2:size]
		isoAns = ISO8583()
		isoAns.setIsoContent(ans)
		if isoAns.getMTI() == '0210':
			if isoAns.getBit(39) == '00':
				print ("\nTransaction Success !!!")
			else:
				print ("\nTransaction Failed Error Code " + isoAns.getBit(39))
	except InvalidIso8583, ii:
		print ii
		sys.exit(1)	
else:
	try:
		message = iso.getNetworkISO(False)
		s.send(message)
		print ('Sending ... %s' % message)
		ans = s.recv(2048)
		print ("\nInput ASCII |%s|" % ans)
		isoAns = ISO8583()
		isoAns.setNetworkISO(ans,False)
		v1 = isoAns.getBitsAndValues()
		for v in v1:
			print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
		if isoAns.getMTI() == '0810':
			print ("    That's great !!! The server understand my message !!!")
		else:
			print ("The server dosen't understand my message!")
	except InvalidIso8583, ii:
		print ii
		sys.exit(1)
s.close()
