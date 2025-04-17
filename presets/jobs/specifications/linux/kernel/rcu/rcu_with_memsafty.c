/*
 * Copyright (c) 2020 ISP RAS (http://www.ispras.ru)
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

//заголовочные файлы со структурами
#include <linux/types.h>

int ldv_rcu_counter = 0;
int ldv_rcu_callbacks_num = 0;
int ldv_kfree_rcu_callbacks_num = 0;

// локальная структура-список узлов для осовбождения (call_rcu)
struct rcu_head *old_rcu_heads;
// указатель для удаляемого в текущий момент узла (call_rcu)
struct rcu_head *curr_rcu_head;

// локальная структура-список узлов для осовбождения (kfree_rcu)
struct rcu_head *old_kfree_rcu_heads;
// указатель для удаляемого в текущий момент узла (kfree_rcu)
struct rcu_head *curr_kfree_rcu_heads;

void ldv_rcu_read_lock( void )
{
	ldv_rcu_counter += 1;
}

void ldv_rcu_read_unlock( void )
{
	ldv_rcu_counter -= 1;

	if ((ldv_rcu_callbacks_num > 0) && (ldv_rcu_counter == 0))
	{
		// callback
		while(old_rcu_heads != NULL) {
			curr_rcu_head = old_rcu_heads;
			old_rcu_heads = curr_rcu_head->next;
			(*curr_rcu_head->func)(curr_rcu_head);
		}
		ldv_rcu_callbacks_num = 0;
	}

	if ((ldv_kfree_rcu_callbacks_num > 0) && (ldv_rcu_counter == 0))
	{
		// callback
		while(old_kfree_rcu_heads != NULL) {
			curr_kfree_rcu_heads = old_kfree_rcu_heads;
			old_kfree_rcu_heads = curr_kfree_rcu_heads->next;
			ldv_free(ptr);
		}
		ldv_kfree_rcu_callbacks_num = 0;
	}
}

void ldv_call_rcu(struct rcu_head *head, rcu_callback_t func)
{
	if (ldv_rcu_counter)
	{
		if(ldv_rcu_callbacks_num == 0)
			old_rcu_heads = NULL;

		ldv_rcu_callbacks_num += 1;
		head->func = func;
		head->next = old_rcu_heads;
		old_rcu_heads = head;
	}
	else
	{
		// callback
		(*func)(head);
	}
}

void ldv_kvfree_call_rcu(struct rcu_head *head, void *ptr)
{
	if (head) {
        if (ldv_rcu_counter)
        {
            if(ldv_kfree_rcu_callbacks_num == 0)
                old_kfree_rcu_heads = NULL;

            ldv_kfree_rcu_callbacks_num += 1;
            head->func = ptr;
            head->next = old_kfree_rcu_heads;
            old_kfree_rcu_heads = head;
        }
        else
        {
            // callback
            ldv_free(ptr);
        }
	}
}
