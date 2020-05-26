#include <linux/ldv/list.h>

void ldv__list_add(struct list_head *new, struct list_head *prev, struct list_head *next)
{
	next->prev = new;
	new->next = next;
	new->prev = prev;
}

void ldv__list_del(struct list_head * prev, struct list_head * next)
{
  next->prev = prev;
}

void ldv__list_del_entry(struct list_head *entry)
{
	ldv__list_del(entry->prev, entry->next);
}
