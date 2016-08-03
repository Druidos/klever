#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/spinlock.h>
#include <linux/atomic.h>

static int __init my_init(void)
{
	spinlock_t *lock_1;
	atomic_t *atomic;
	int is_locked;

	is_locked = atomic_dec_and_lock(atomic, lock_1);
	/* successfully ignore is_locked */
	spin_unlock(lock_1);

	return 0;
}

module_init(my_init);
