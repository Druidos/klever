/*
 * Copyright (c) 2018 ISP RAS (http://www.ispras.ru)
 * Ivannikov Institute for System Programming of the Russian Academy of Sciences
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <linux/module.h>
#include <linux/usb.h>
#include <ldv/verifier/common.h>
#include <ldv/verifier/nondet.h>

static int __init ldv_init(void)
{
	struct usb_device *dev = ldv_undef_ptr_non_null();
	size_t size = ldv_undef_uint();
	gfp_t mem_flags = ldv_undef_uint();
	dma_addr_t dma;
	char *buf;

	buf = usb_alloc_coherent(dev, size, mem_flags, &dma);
	ldv_assume(buf != NULL);
	usb_free_coherent(dev, size, buf, dma);
	usb_free_coherent(dev, size, buf, dma);

	return 0;
}

module_init(ldv_init);
