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
#include <ldv/test.h>

static int __init ldv_init(void)
{
	int *var;
	int i;

	var = ldv_xmalloc(10 * sizeof(*var));

	for (i = 0; i < 10; i++)
		var[i] = i + 1;

	if (var[0] == 1 &&
	    var[1] == 2 &&
	    var[2] == 3 &&
	    var[3] == 4 &&
	    var[4] == 5 &&
	    var[5] == 6 &&
	    var[6] == 7 &&
	    var[7] == 8 &&
	    var[8] == 9 &&
	    var[9] == 10)
		ldv_expected_error();

	return 0;
}

module_init(ldv_init);
