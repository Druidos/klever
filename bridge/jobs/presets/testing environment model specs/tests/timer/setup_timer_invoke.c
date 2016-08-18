/*
 * Copyright (c) 2014-2015 ISPRAS (http://www.ispras.ru)
 * Institute for System Programming of the Russian Academy of Sciences
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
#include <linux/timer.h>
#include <linux/emg/test_model.h>
#include <verifier/nondet.h>

int flip_a_coin;
struct timer_list ldv_timer;
unsigned long data;

void ldv_handler(unsigned long data)
{
	ldv_invoke_reached();
}

static int __init ldv_init(void)
{
	setup_timer(&ldv_timer, ldv_handler, data);
	return mod_timer(&ldv_timer, jiffies + msecs_to_jiffies(200));
}

static void __exit ldv_exit(void)
{
	del_timer(&ldv_timer);
}

module_init(ldv_init);
module_exit(ldv_exit);