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

#include <linux/types.h>
#include <linux/device.h>
#include <ldv/common/list.h>
#include <ldv/linux/common.h>
#include <ldv/linux/device.h>
#include <ldv/linux/slab.h>
#include <ldv/verifier/color memory.h>

#include <linux/idr.h>
#include <linux/workqueue.h>
#include <linux/llist.h>
#include <drm/drm_device.h>
#include <drm/drm_modes.h>
#include <drm/drm_mode_config.h>
#include <drm/drm_managed.h>
#include <drm/drm_encoder.h>
#include <drm/drm_crtc.h>
#include <drm/drm_plane.h>

extern struct devres *ldv_color_devm_kmalloc(size_t size, gfp_t gfp);
extern void ldv_color_devm_kfree(struct devres *dr);

extern struct devres *ldv_color_drm_kmalloc(size_t size, gfp_t gfp);
extern void ldv_color_drm_kfree(struct drmres *dr);
extern void ldv_color_drm_dev_kfree(struct drm_dev *dev);

struct drm_device *drm_dev;

struct devres_node {
	struct list_head		entry;
	dr_release_t			release;
  	const char				*name;
  	size_t					size;
};

struct devres {
	struct devres_node		node;
    u8 data[];
};


struct drmres_node {
	struct list_head	entry;
	drmres_release_t	release;
	const char		*name;
	size_t			size;
};

struct drmres {
	struct drmres_node node;
	u8 data[];
};

int ldv_drmm_mode_config_init(struct drm_device *dev)
{
	INIT_LIST_HEAD(&dev->mode_config.crtc_list);
	INIT_LIST_HEAD(&dev->mode_config.encoder_list);
	INIT_LIST_HEAD(&dev->mode_config.plane_list);

	dev->mode_config.num_crtc = 0;
	dev->mode_config.num_encoder = 0;
	dev->mode_config.num_total_plane = 0;

	return 0;
}

void ldv_drm_mode_config_cleanup(struct drm_device *dev)
{
	struct drm_crtc *crtc, *ct;
	struct drm_encoder *encoder, *enct;
	struct drm_plane *plane, *plt;

	list_for_each_entry_safe(encoder, enct, &dev->mode_config.encoder_list,
				 head) {
		encoder->funcs->destroy(encoder);
	}

	list_for_each_entry_safe(plane, plt, &dev->mode_config.plane_list,
				 head) {
		plane->funcs->destroy(plane);
	}

	list_for_each_entry_safe(crtc, ct, &dev->mode_config.crtc_list, head) {
		crtc->funcs->destroy(crtc);
	}
}

void ldv_drm_crtc_cleanup(struct drm_crtc *crtc)
{
	struct drm_device *dev = crtc->dev;
	list_del(&crtc->head);
	dev->mode_config.num_crtc--;
}

int ldv_drm_crtc_init_with_planes(struct drm_device *dev, struct drm_crtc *crtc,
			      const struct drm_crtc_funcs *funcs)
{
	struct drm_mode_config *config = &dev->mode_config;
	crtc->dev = dev;
	crtc->funcs = funcs;
	list_add_tail(&crtc->head, &config->crtc_list);
	config->num_crtc++;
	return 0;
}

void ldv_drm_plane_cleanup(struct drm_plane *plane)
{
	struct drm_device *dev = plane->dev;
	list_del(&plane->head);
	dev->mode_config.num_total_plane--;
}

int ldv_drm_universal_plane_init(struct drm_device *dev, struct drm_plane *plane,
			     const struct drm_plane_funcs *funcs)
{
    struct drm_mode_config *config = &dev->mode_config;
    plane->dev = dev;
    plane->funcs = funcs;
    list_add_tail(&plane->head, &config->plane_list);
	config->num_total_plane++;
	return 0;
}

void ldv_drm_encoder_cleanup(struct drm_encoder *encoder)
{
	struct drm_device *dev = encoder->dev;
	list_del(&encoder->head);
	dev->mode_config.num_encoder--;
}

int ldv_drm_encoder_init(struct drm_device *dev,
		     struct drm_encoder *encoder,
		     const struct drm_encoder_funcs *funcs)
{
	encoder->dev = dev;
	encoder->funcs = funcs;
	list_add_tail(&encoder->head, &dev->mode_config.encoder_list);
	dev->mode_config.num_encoder++;
	return 0;
}

static const struct drm_encoder_funcs ldv_drm_simple_encoder_funcs_cleanup = {
	.destroy = ldv_drm_encoder_cleanup,
};

int ldv_drm_simple_encoder_init(struct drm_device *dev,
			    struct drm_encoder *encoder)
{
	return ldv_drm_encoder_init(dev, encoder, &ldv_drm_simple_encoder_funcs_cleanup);
}


void *ldv_devres_dev_get_drvdata(const struct device *dev)
{
	return dev->driver_data;
}

void ldv_devres_dev_set_drvdata(struct device *dev, void *data)
{
    dev->driver_data = data;
}


void *ldv_devm_kmalloc_array(size_t n, size_t size, gfp_t flags)
{
	void *res;

	ldv_check_alloc_flags(flags);
	res = ldv_malloc(n * size);
	ldv_save_allocated_memory_to_list(res);

	return res;
}

void *ldv_devm_kcalloc(size_t n, size_t size, gfp_t flags)
{
	void *res;

	ldv_check_alloc_flags(flags);
	res = ldv_calloc(n, size);
	ldv_save_allocated_memory_to_list(res);

	return res;
}

struct devres * ldv_devm_alloc_dr(size_t size, gfp_t gfp, int flag)
{
	struct devres *dr;

	dr = ldv_color_devm_kmalloc(size + sizeof(struct devres), gfp);
	if (!dr)
		return NULL;

    if(flag)
        memset(dr, 0, offsetof(struct devres, data));

	INIT_LIST_HEAD(&dr->node.entry);
	return dr;
}

void ldv_devres_add(struct device *dev, struct devres *dr)
{
	struct devres_node *node = &dr->node;
  	list_add_tail(&node->entry, &dev->devres_head);
}

void *ldv_devm_kmalloc(struct device *dev, size_t size, gfp_t gfp)
{
	struct devres *dr;

	dr = ldv_devm_alloc_dr(size, gfp, 0);
	if (!dr)
		return NULL;

	dr->node.size = size;

	ldv_devres_add(dev, dr);
    struct devres_node *node = &dr->node;
    if (list_empty(&dev->devres_head)) {
        dev->devres_head.next = &node->entry;
        node->entry.prev = &dev->devres_head;
    }
	return dr->data;
}

void *ldv_devm_kzalloc(struct device *dev, size_t size, gfp_t gfp)
{
	struct devres *dr;

	dr = ldv_devm_alloc_dr(size, gfp, 1);
	if (!dr)
		return NULL;

	dr->node.size = size;

	ldv_devres_add(dev, dr);
    struct devres_node *node = &dr->node;
    if (list_empty(&dev->devres_head)) {
        dev->devres_head.next = &node->entry;
        node->entry.prev = &dev->devres_head;
    }
	return dr->data;
}

void ldv_release_nodes(struct device *dev, struct list_head *todo)
{
	struct devres *dr, *tmp;

	list_for_each_entry_safe_reverse(dr, tmp, todo, node.entry) {
		ldv_color_devm_kfree(dr);
	}
}

int ldv_devres_release_all(struct device *dev)
{

	struct list_head todo = LIST_HEAD_INIT(todo);

	if (list_empty(&dev->devres_head))
		return 0;
	ldv_release_nodes(dev, &todo);

	return 0;
}

static struct drmres * ldv_drmm_alloc_dr(drmres_release_t release,
                                         size_t size, gfp_t gfp, int flag)
{
	struct drmres *dr;
	if (!dr)
		return NULL;

	dr = ldv_color_drm_kmalloc(size + sizeof(*dr), gfp);
	if (!dr)
		return NULL;

    if(flag)
        memset(dr, 0, offsetof(struct drmres, data));

	INIT_LIST_HEAD(&dr->node.entry);
	dr->node.release = release;
	dr->node.size = size;
	return dr;
}

void *ldv_drmm_kmalloc(struct drm_device *dev, size_t size, gfp_t gfp)
{
	struct drmres *dr;
	unsigned long flags;

	dr = ldv_drmm_alloc_dr(NULL, size, gfp, 0);
	if (!dr)
		return NULL;

	list_add(&dr->node.entry, &dev->managed.resources);

	return dr->data;
}

void *ldv_drmm_kzalloc(struct drm_device *dev, size_t size, gfp_t gfp)
{
	struct drmres *dr;
	unsigned long flags;

	dr = ldv_drmm_alloc_dr(NULL, size, gfp, 1);
	if (!dr)
		return NULL;

	list_add(&dr->node.entry, &dev->managed.resources);

	return dr->data;
}

static void ldv_free_dr(struct drmres *dr)
{
	free(dr);
}

void ldv_drm_managed_release(struct drm_device *dev)
{
	struct drmres *dr, *tmp;

	list_for_each_entry_safe(dr, tmp, &dev->managed.resources, node.entry) {
		if (dr->node.release)
			dr->node.release(dev, dr->node.size ? *(void **)&dr->data : NULL);

		list_del(&dr->node.entry);
      	ldv_color_drm_kfree(dr);
	}
}

static void ldv_del_dr(struct drm_device *dev, struct drmres *dr)
{
	list_del(&dr->node.entry);
}

void ldv_drmm_add_final_kfree(struct drm_device *dev, void *container)
{
	dev->managed.final_kfree = container;
}

int __ldv_drmm_add_action(struct drm_device *dev,
		      drmres_release_t action,
		      void *data)
{
	struct drmres *dr;

	dr = ldv_drmm_alloc_dr(action, 0, GFP_KERNEL, 0);
	if (!dr)
		return NULL;

	list_add(&dr->node.entry, &dev->managed.resources);

	return 0;
}

int __ldv_drmm_add_action_or_reset(struct drm_device *dev,
			       drmres_release_t action,
			       void *data)
{
	int ret;

	ret = __ldv_drmm_add_action(dev, action, data);

	return ret;
}

void ldv_drmm_kfree(struct drm_device *dev, void *data)
{
	struct drmres *dr_match = NULL, *dr;

	if (!data)
		return;

	list_for_each_entry(dr, &dev->managed.resources, node.entry) {
		if (dr->data == data) {
			dr_match = dr;
			ldv_del_dr(dev, dr_match);
			break;
		}
	}
  	ldv_color_drm_kfree(dr);
}


void ldv_kref_init(struct kref *kref)
{
	kref->refcount.refs.counter = 1;
}

struct device *ldv_get_device(struct device *dev)
{
	struct kobject *kobj = &dev->kobj;
	struct kref *kref = &kobj->kref;
	kref->refcount.refs.counter = kref->refcount.refs.counter + 1;
	return dev;
}

void ldv_put_device(struct device *dev)
{
    struct kobject *kobj = &dev->kobj;
	struct kref *kref = &kobj->kref;
	kref->refcount.refs.counter = kref->refcount.refs.counter - 1;
}

static void ldv_drm_dev_init_release(struct drm_device *dev, void *res)
{
	ldv_put_device(dev->dev);
	dev->dev = NULL;
}

static int ldv_drm_dev_init(struct drm_device *dev,
			const struct drm_driver *driver,
			struct device *parent)
{
	int ret = 0;

	ldv_kref_init(&dev->ref);
	dev->dev = ldv_get_device(parent);

	INIT_LIST_HEAD(&dev->managed.resources);

	ret = __ldv_drmm_add_action_or_reset(dev, ldv_drm_dev_init_release, NULL);

	return ret;
}

struct drm_device *ldv_drm_dev_alloc(struct drm_driver *driver,
				 struct device *parent)
{
	struct drm_device *dev;

	dev = ldv_color_drm_kmalloc(sizeof(*dev), GFP_KERNEL);
	if (!dev)
		return NULL;
    drm_dev = dev;

  	ldv_devres_dev_set_drvdata(parent, dev);

	ldv_drm_dev_init(dev, driver, parent);

	ldv_drmm_add_final_kfree(dev, dev);

	return dev;
}

static void ldv_drm_dev_release(struct kref *ref)
{
	struct drm_device *dev = container_of(ref, struct drm_device, ref);

    if(drm_dev) {
         ldv_drm_managed_release(dev);
         ldv_color_drm_dev_kfree(dev->managed.final_kfree);
    }

}

int ldv_kref_put(struct kref *kref, void (*release)(struct kref *kref))
{
	kref->refcount.refs.counter = kref->refcount.refs.counter - 1;
	if (!(kref->refcount.refs.counter)) {
		release(kref);
		return 1;
	}
	return 0;
}

void ldv_drm_dev_put(struct drm_device *dev)
{
	if (dev)
		ldv_kref_put(&dev->ref, ldv_drm_dev_release);
}

void *__ldv_devm_drm_dev_alloc(struct device *parent, struct drm_driver *driver, size_t size)
{
    struct drm_device *dev;

	dev = ldv_color_drm_kmalloc(size, GFP_KERNEL);
	if (!dev)
		return NULL;
    drm_dev = dev;

  	ldv_devres_dev_set_drvdata(parent, dev);

	ldv_drm_dev_init(dev, driver, parent);

	ldv_drmm_add_final_kfree(dev, dev);

	return dev;
}

const void *ldv_devres_of_device_get_match_data(const struct device *dev) {
    int ret = 1;
    return ret;
}
