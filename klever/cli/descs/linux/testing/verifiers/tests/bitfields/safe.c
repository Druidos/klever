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
#include <ldv/common/test.h>
#include "bitfields.h"

static int __init ldv_init(void)
{
	union ldv_union var1 = {.field1 = {1, 2, 3}},
	                var2 = {.field2 = 123};

	if (var1.field2 != 29)
		ldv_unexpected_error();

	if (var2.field1.bitfield1 != 1)
		ldv_unexpected_error();

	if (var2.field1.bitfield2 != 1)
		ldv_unexpected_error();

	if (var2.field1.bitfield3 != 7)
		ldv_unexpected_error();

	return 0;
}

module_init(ldv_init);
