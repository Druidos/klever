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
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/usb/gadget.h>
#include <ldv/verifier/common.h>
#include <ldv/verifier/nondet.h>

static int __init ldv_init(void)
{
	struct usb_gadget_driver driver;
	dev_t dev = ldv_undef_uint();
	unsigned int baseminor = ldv_undef_uint(), count = ldv_undef_uint();
	const char *name = ldv_undef_ptr();

	ldv_assume(!usb_gadget_probe_driver(&driver));
	ldv_assume(!alloc_chrdev_region(&dev, baseminor, count, name));
	unregister_chrdev_region(dev, count);
	usb_gadget_unregister_driver(&driver);

	return 0;
}

module_init(ldv_init);
