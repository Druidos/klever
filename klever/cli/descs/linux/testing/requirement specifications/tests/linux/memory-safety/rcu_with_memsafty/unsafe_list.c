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
#include <linux/rcupdate.h>
#include <linux/rculist.h>

struct local_str{
	int x;
	struct rcu_head rcu;
	struct hlist_node node;
}

static void local_str_reclaim(struct rcu_head *head)
{
	struct local_str *old = container_of(head, struct local_str, rcu);
	ldv_free(old);
}

static int __init ldv_init(void)
{
	int x = ldv_undef_int();
	struct local_str *local_ptr;

	struct hlist_head *info_head = ldv_undef_ptr_non_null();

	local_ptr = ldv_malloc(sizeof(*local_ptr));
	local_ptr->x = x;

	hlist_for_each_entry_rcu(key, info_head, node) {
		call_rcu(&local_ptr->rcu, local_str_reclaim);
	}

	return 0;
}

module_init(ldv_init);

MODULE_LICENSE("GPL");
