#!/usr/bin/env python
# (re)pack XpressROM bios
# 140508 <kongo@z80.se>

import struct
import sys
import os
import re

class XRFragment:

    def __init__(self):
        self.data = ''
        self.address = 0
        self.tag = 0
        self.mode = 0
        self.imsize = 0
        self.realsize = 0
        self.padsize = 0

    def load(self, fname, tag, address):
        self.data = file(fname, 'rb').read()
        self.address = address
        self.tag = tag
        self.mode = 3
        self.imsize = len(self.data)
        self.realsize = self.imsize
	if self.data[0:2] == 'JC':
	    (self.realsize, ) = struct.unpack('<I', self.data[2:6])
	    self.mode = 4
        self.padsize = 32 + self.imsize
        if self.padsize % 16 > 0:
            self.padsize += 16 - self.padsize % 16
        return self

    def save(self, fname):
        file(fname, 'wb').write(self.data)
        
    def padding(self, size):
        self.imsize = size-32
        self.realsize = self.imsize
        self.address = 0
        self.tag = 'PAD'
        self.mode = 3
        self.data = '\0'*self.imsize
        self.padsize = self.imsize
        return self

    def parse(self, f):
        hdr = f.read(32)
        if len(hdr) < 32:
            return False
        (self.tag, self.mode, self.address, self.realsize, self.imsize, r1,r2,r3,r4,r5,r6) = struct.unpack('<4sBIIIIIIBBB', hdr)
        self.tag = self.tag[1:]
        self.data = f.read(self.imsize)
        self.padsize = 32 + self.imsize
        if self.padsize % 16 > 0:
            self.padsize += 16 - self.padsize % 16
        f.read(self.padsize-32-self.imsize)
        return True

    def write(self, f):
        f.write(struct.pack('<4sBIIIIIIBBB', '$'+self.tag, self.mode,
            self.address, self.realsize, self.imsize, 0,0,0,0,0,0))
        f.write(self.data)
        f.write('\0'*(self.padsize-32-self.imsize))

class XRBIOS:

	def __init__(self):
		self.images = []

        def load(self, fname):
            f = file(fname, 'rb')
            while True:
                im = XRFragment()
                if im.parse(f):
                    self.images.append(im)
                else:
                    break
	
        def dump(self):
            for im in self.images:
                print '%s\t%08x\t%08x\t%08x' % (im.tag, im.address, im.realsize, im.imsize)
            print 'Data size:\t%6d' % sum(im.imsize for im in self.images)
            print 'Data+OH size:\t%6d' % sum(im.padsize for im in self.images)

	def add(self, tag, address, fname):
            self.images.append(XRFragment().load(fname, tag, address))

	def write(self, fname, romsize=256*1024):
		print 'ROM size:\t%6d' % romsize
		padsize = romsize - sum(im.padsize for im in self.images)
		if padsize <= 32:
			raise Exception('Overflowing ROM')
		print 'Padding:\t%6d' % padsize

		f = file(fname, 'wb')
                XRFragment().padding(padsize).write(f)

		for im in self.images:
                    im.write(f)
	
	def read(self, fname):
		self.images = []
		f = file(fname, 'rb')
		while True:
			hdr = f.read(32)
			if len(hdr) < 32:
				break
			(tag, imtype, address, ramsize, imsize, r1,r2,r3,r4,r5,r6) = struct.unpack("<4sBIIIIIIBBB", hdr)
			if imsize & 0xf:
				imsize += 16
				imsize &= 0xfffffff0
			data = f.read(imsize)
			self.images.append((tag[1:], address, data, imsize, ramsize, imtype))

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('pack','unpack'):
        print 'usage: xpr.py [pack|unpack]'
        sys.exit(-1)

    if sys.argv[1] == 'unpack':
        img = XRBIOS()
        img.load('original.rom')
        #img.dump()
        for (idx, im) in enumerate(img.images):
            im.save('work/%02d_%s_%08x.%s' % (idx, im.tag, im.address, 'jc' if im.mode ==4 else 'raw'))
    elif sys.argv[1] == 'pack':
        img = XRBIOS()
        r = re.compile('[0-9]{1,5}_(IMG|XPR|BMP|PAL)_([0-9a-f]{8,8})\.(jc|raw)$')
        for f in sorted(os.listdir('work/')):
            m = r.match(f)
            if m:
                img.add(m.group(1), int(m.group(2), 16), 'work/'+f)
        img.dump()
        img.write('puc.rom')
