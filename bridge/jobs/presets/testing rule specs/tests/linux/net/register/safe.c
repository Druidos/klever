/*
 * Copyright (c) 2014-2016 ISPRAS (http://www.ispras.ru)
 * Institute for System Programming of the Russian Academy of Sciences
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
 * ee the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <linux/module.h>
#include <linux/usb.h>
#include <linux/netdevice.h>
#include <verifier/nondet.h>

static int ldv_usb_probe(struct usb_interface *intf,
                         const struct usb_device_id *id)
{
	struct net_device *dev = ldv_undef_ptr();

	if (register_netdev(dev) < 0)
		return ldv_undef_int_negative();

	unregister_netdev(dev);

	return 0;
}

static struct usb_driver ldv_usb_driver = {
	.probe = ldv_usb_probe
};

static int __init ldv_init(void)
{
	if (usb_register(&ldv_usb_driver) < 0)
		return ldv_undef_int_negative();

	usb_deregister(&ldv_usb_driver);

	return 0;
}

module_init(ldv_init);
