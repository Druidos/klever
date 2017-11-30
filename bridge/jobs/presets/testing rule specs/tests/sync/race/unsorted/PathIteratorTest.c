/*
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

/* The test checks the work path iterator. */

#include <linux/module.h>
#include <linux/mutex.h>
#include <verifier/nondet.h>
#include <verifier/thread.h>

static DEFINE_MUTEX(ldv_lock);
static int _ldv_global_var;

static void ldv_func1(int a)
{
	/* Access to _ldv_global_var is false. */
	if (a)
		_ldv_global_var = 1;
}

static void ldv_func2(int a)
{
	/* The first call. */
	ldv_func1(1);
}

static void ldv_func3(int a)
{
	/* The second call. */
	ldv_func1(a);
}

static void ldv_func4(int a)
{
	/* One more function call. */
	ldv_func1(a);
}

static void ldv_func5(void)
{
	int p = 0;

	ldv_func3(p);
	mutex_lock(&ldv_lock);
	_ldv_global_var = 2;
	mutex_unlock(&ldv_lock);
	ldv_func2(p);
	ldv_func4(p);
}

static void *ldv_main(void *arg)
{
	ldv_func5();
	return NULL;
}

static int __init init(void)
{
	pthread_t thread;
	pthread_attr_t const *attr = ldv_undef_ptr();
	void *arg = ldv_undef_ptr();

	pthread_create(&thread, attr, &ldv_main, arg);
	ldv_main(0);

	return 0;
}

module_init(init);
