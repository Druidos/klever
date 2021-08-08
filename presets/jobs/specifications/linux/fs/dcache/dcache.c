#include <linux/fs.h>
#include <linux/dcache.h>
#include <ldv/linux/common.h>
#include <ldv/linux/list.h>
#include <ldv/verifier/common.h>
#include <ldv/verifier/nondet.h>
#include <ldv/verifier/memory.h>

struct dentry *root_dentry;

/* Get rid of this function when macro WRITE_ONCE() will be hanled properly (https://forge.ispras.ru/issues/10896). */
static void ldv_init_list_head(struct list_head *list)
{
       list->next = list;
       list->prev = list;
}

struct dentry *ldv_d_alloc_pseudo(struct super_block *sb, const struct qstr *name)
{
	struct dentry *dentry;
	size_t size;

	if (ldv_undef_int())
		return NULL;
	else {
		dentry = ldv_zalloc(sizeof(struct dentry));
		/* Set the string */
		dentry->d_sb = sb;
		dentry->d_parent = dentry;
		dentry->d_op = dentry->d_sb->s_d_op;

		/* Init lists */
		ldv_init_list_head(&dentry->d_subdirs);
		INIT_HLIST_NODE(&dentry->d_u.d_alias);
		ldv_init_list_head(&dentry->d_child);

		return dentry;
	}
}


struct dentry *ldv_d_make_root(struct inode *root_inode)
{
	struct dentry *res = root_dentry;
	struct qstr root_name;
	char *name;

	if (root_inode && !res) {
		if (ldv_undef_int())
			return 0;
		else {
			/* TODO: Fix after CPAchecker SMG will support string assignment */
			root_name.name = ldv_xzalloc(2);
			name = (char *)root_name.name;
			name[0] = '/';
			name[1] = '\0';
			root_name.len = 1;
			root_dentry = ldv_d_alloc_pseudo(root_inode->i_sb, & root_name);
			ldv_free(root_name.name);
			ldv_assume(root_dentry != NULL);
			root_dentry->d_name.name = 0;
			root_dentry->d_name.len = 0;
			root_dentry->d_inode = root_inode;
			res = root_dentry;
		}
	}

	return res;
}
