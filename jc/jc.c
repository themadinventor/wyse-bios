/*
 * Quick and Dirty JCALG1 Compressor/Decompressor Wrapper
 * 2014-05-08 <kongo@z80.se>
 */

#include <stdio.h>
#include <unistd.h>

#include "jcalg.h"

int read_input(const char *fname, void **buf, size_t *len)
{
	FILE *f = fopen(fname, "rb");
	if (!f) {
		return 0;
	}

	fseek(f, 0, SEEK_END);
	*len = ftell(f);
	fseek(f, 0, SEEK_SET);

	*buf = malloc(*len);
	fread(*buf, *len, 1, f);
	fclose(f);

	return 1;
}

int write_output(const char *fname, void *buf, size_t len)
{
	FILE *f = fopen(fname, "wb");
	if (!f) {
		return 0;
	}

	fwrite(buf, len, 1, f);
	fclose(f);

	return 1;
}

int __attribute__((stdcall)) callback(size_t src, size_t dst)
{
	return 1;
}

void __attribute__((stdcall)) *alloc(size_t sz)
{
	return malloc(sz);
}

void __attribute__((stdcall)) *dealloc(void *ptr)
{
	free(ptr);
}

int main(int argc, char *argv[])
{
	int opt = 0, compress = 0, decompress = 0, window = 32768;
	char *in_fname = NULL, *out_fname = NULL;

	while ((opt = getopt(argc, argv, "i:o:cdw:")) != -1) {
		switch (opt) {
		case 'i':
			in_fname = optarg;
			break;

		case 'o':
			out_fname = optarg;
			break;

		case 'c':
			compress = 1;
			break;

		case 'd':
			decompress = 1;
			break;

		case 'w':
			window = atoi(optarg);
			if (window < 16 || window > 65536) {
				fprintf(stderr, "Invalid window size.\n");
				return -1;
			}
			break;

		case '?':
			fprintf(stderr, "Invalid argument. RTFM.\n");
			return -1;
		}
	}

	if (!in_fname) {
		fprintf(stderr, "Input file not specified!\n");
		return -1;
	}

	if (!out_fname) {
		fprintf(stderr, "Output file not specified!\n");
		return -1;
	}

	if (!compress && !decompress) {
		fprintf(stderr, "No operation specified!\n");
		return -1;
	}

	if (compress && decompress) {
		fprintf(stderr, "Can't both compress and decompress, retard.\n");
		return -1;
	}
	
	void *inbuf, *outbuf;
	size_t insz, outsz;
	if (!read_input(in_fname, &inbuf, &insz)) {
		perror("Unable to read input");
		return -1;
	}

	if (decompress) {
		outsz = JCALG1_GetUncompressedSizeOfCompressedBlock(inbuf);
		fprintf(stderr, "Decompressing %s -> %s (%d bytes -> %d bytes)",
				in_fname, out_fname, insz, outsz);

		outbuf = malloc(outsz);
		outsz = JCALG1_Decompress_Fast(inbuf, outbuf);
		if (!outsz) {
			fprintf(stderr, "Failed to decompress\n");
			return -1;
		}
	} else {
		outsz = JCALG1_GetNeededBufferSize(insz);
		fprintf(stderr, "Compressing %s -> %s (%d -> %d -> ",
				in_fname, out_fname, insz, outsz);
		outbuf = malloc(outsz);

		outsz = JCALG1_Compress(inbuf, insz, outbuf, window,
				alloc, dealloc, callback, 0);
		if (!outsz) {
			fprintf(stderr, "Failed to compress\n");
			return -1;
		}

		fprintf(stderr, "%d)", outsz);
	}

	if (!write_output(out_fname, outbuf, outsz)) {
		perror("Unable to write output");
		return -1;
	}

	free(inbuf);
	free(outbuf);

	fprintf(stderr, " done\n");

	return 0;
}

