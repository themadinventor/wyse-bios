#ifndef JCALG_H
#define JCALG_H

#include <stdlib.h>

extern size_t __attribute__((stdcall)) JCALG1_Compress(const void *src, size_t len, void *dst, size_t wndsz, void *alloc, void *dealloc, void *callback, int dischksum);
extern size_t __attribute__((stdcall)) JCALG1_Decompress_Small(const void *src, void *dst);
extern size_t __attribute__((stdcall)) JCALG1_Decompress_Fast(const void *src, void *dst);
extern size_t __attribute__((stdcall)) JCALG1_GetUncopressedSizeOfCompressedBlock(const void *block);
extern size_t __attribute__((stdcall)) JCALG1_GetNeededBufferSize(size_t size);

#endif
