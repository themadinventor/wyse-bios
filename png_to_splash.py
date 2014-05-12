#!/usr/bin/env python
# png2splash
# 2014 kongo@etf.nu

import Image, ImagePalette

png = Image.open('puc.png')

if png.mode != 'P':
	print 'Bootsplash must be in palette mode'
	exit(-1)

if png.size != (800, 600):
	print 'Bootsplash must be 800x600'
	exit(-1)
pal = png.palette.getdata()[1]

palette = ""
for i in xrange(256):
    palette += pal[i*3:i*3+3][::-1]+'\0'

file('work/06_BMP_00100000.bin', 'wb').write(''.join(map(chr, list(png.getdata()))))
file('work/12_PAL_00000000.raw', 'wb').write(palette)
