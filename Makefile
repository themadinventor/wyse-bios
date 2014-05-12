.PHONY: all clean unpack pack

all:
	echo "make [unpack|pack|clean]"

clean:
	rm -rf work/ bootsplash.png

unpack:
	rm -rf work
	mkdir -p work
	./xpr.py unpack
	for f in work/*.jc; do jc/jc -i $$f -o $${f%%.jc}.bin -d ; done
	rm -f work/*.jc

pack:
	rm -f work/*.jc
	for f in work/*.bin; do jc/jc -i $$f -o $${f%%.bin}.jc -c ; done
	./xpr.py pack

patch:
	# replace splash screen
	./png_to_splash.py

	# remove bios summary
	rm work/07_IMG_00040000.bin

	# replace setup
	#rm work/05_IMG_ff120000.bin
	#cp setup/setup work/05_IMG_ff120000.bin

	# remove/replace pxe driver
	#rm work/03_IMG_000d4000.bin
	#cp ~/dev/ipxe/src/bin/10ec8139.rom work/03_IMG_000d4000.raw
