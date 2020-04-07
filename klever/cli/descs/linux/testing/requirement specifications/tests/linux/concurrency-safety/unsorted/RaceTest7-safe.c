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
#include <linux/mutex.h>
#include <ldv/verifier/nondet.h>
#include <ldv/verifier/thread.h>

static DEFINE_MUTEX(ldv_lock);
static int _ldv_false_unsafe;
static int _ldv_false_unsafe2;
static int _ldv_true_unsafe;
static int _ldv_lockLevel;

static int ldv_func1(void)
{
	if (_ldv_lockLevel) {
		mutex_lock(&ldv_lock);
		_ldv_false_unsafe = 0;
		mutex_unlock(&ldv_lock);
	} else {
		mutex_lock(&ldv_lock);
		_ldv_false_unsafe2 = 1;
		_ldv_true_unsafe = 0;
		mutex_unlock(&ldv_lock);
	}

	return 0;
}

static int ldv_func2(void)
{
	mutex_lock(&ldv_lock);
	_ldv_false_unsafe = 1;
	_ldv_false_unsafe2 = 1;
	mutex_unlock(&ldv_lock);

	return 0;
}

static void *ldv_main(void *arg)
{
	ldv_func1();
	ldv_func2();

	return NULL;
}

static int __init ldv_init(void)
{
	pthread_t thread;
	pthread_attr_t const *attr = ldv_undef_ptr();
	void *arg1 = ldv_undef_ptr(), *arg2 = ldv_undef_ptr();

	pthread_create(&thread, attr, &ldv_main, arg1);
	ldv_main(arg2);

	return 0;
}

module_init(ldv_init);
