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
#include <linux/blkdev.h>
#include <ldv/verifier/common.h>
#include <ldv/verifier/nondet.h>

static int __init ldv_init(void)
{
	struct request_queue *q = ldv_undef_ptr();
	int rw = ldv_undef_int();
	gfp_t gfp_mask = ldv_undef_uint();

	ldv_assume(blk_get_request(q, rw, gfp_mask) != NULL);

	return 0;
}

module_init(ldv_init);
