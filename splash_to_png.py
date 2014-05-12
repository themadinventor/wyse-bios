#!/usr/bin/env python
# splash2png
# 2014 kongo@etf.nu

import Image, ImagePalette

bitmap = file('work/BMP_00100000.bin', 'rb').read()
pal = file('work/PAL_00000000.raw', 'rb').read()

palette = ""
for i in xrange(256):
    palette += pal[i*4:i*4+3][::-1]

im = Image.fromstring('P',(800, 600),bitmap)
im.putpalette(palette)
im.save('bootsplash.png', format='PNG')
