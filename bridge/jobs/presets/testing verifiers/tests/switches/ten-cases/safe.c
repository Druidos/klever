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
 * ee the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <linux/module.h>
#include <ldv-test.h>
#include <verifier/nondet.h>

static int __init ldv_init(void)
{
	int var1 = ldv_undef_int(), var2 = ldv_undef_int(),
	    var3 = ldv_undef_int(), var4 = ldv_undef_int(),
	    var5 = ldv_undef_int(), var6 = ldv_undef_int(),
	    var7 = ldv_undef_int(), var8 = ldv_undef_int(),
	    var9 = ldv_undef_int(), var10 = ldv_undef_int(),
	    var11 = ldv_undef_int();

	switch (1) {
	case 1:
		var11 = var1;
	case 2:
		var11 += var2;
	case 3:
		var11 += var3;
	case 4:
		var11 += var4;
	case 5:
		var11 += var5;
	case 6:
		var11 += var6;
	case 7:
		var11 += var7;
	case 8:
		var11 += var8;
	case 9:
		var11 += var9;
	case 10:
		var11 += var10;
	}

	if (var11 != var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 +
	    var9 + var10)
		ldv_error();

	return 0;
}

module_init(ldv_init);
