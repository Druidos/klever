#ifndef __LINUX_LDV_LIST_H
#define __LINUX_LDV_LIST_H
#include <linux/types.h>
void ldv__list_add(struct list_head *new, struct list_head *prev, struct list_head *next);
void ldv__list_del(struct list_head * prev, struct list_head * next);
void ldv__list_del_entry(struct list_head *entry);
static inline bool ldv__list_add_valid(struct list_head *new, struct list_head *prev, struct list_head *next);
static inline bool ldv__list_del_entry_valid(struct list_head *entry);

#endif /* __LINUX_LDV_LIST_H */