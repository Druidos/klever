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
	int iso_packets = ldv_undef_int();
	gfp_t mem_flags = ldv_undef_uint();
	struct urb *urb;

	urb = usb_alloc_urb(iso_packets, mem_flags);
	ldv_assume(urb != NULL);
	usb_free_urb(urb);
	usb_free_urb(urb);

	return 0;
}

module_init(ldv_init);
