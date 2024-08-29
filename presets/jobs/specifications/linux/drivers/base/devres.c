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
#include <ldv/verifier/memory.h>

#include <linux/idr.h>
#include <linux/workqueue.h>
#include <linux/llist.h>
#include <drm/drm_modes.h>

extern struct devres *ldv_color_devm_kmalloc(size_t size, gfp_t gfp);
extern void ldv_color_devm_kfree(struct devres *dr);

extern struct devres *ldv_color_drm_kmalloc(size_t size, gfp_t gfp);
extern void ldv_color_drm_kfree(struct drmres *dr);
extern void ldv_color_drm_dev_kfree(struct drm_dev *dev);

enum switch_power_state {
	/** @DRM_SWITCH_POWER_ON: Power state is ON */
	DRM_SWITCH_POWER_ON = 0,

	/** @DRM_SWITCH_POWER_OFF: Power state is OFF */
	DRM_SWITCH_POWER_OFF = 1,

	/** @DRM_SWITCH_POWER_CHANGING: Power state is changing */
	DRM_SWITCH_POWER_CHANGING = 2,

	/** @DRM_SWITCH_POWER_DYNAMIC_OFF: Suspended */
	DRM_SWITCH_POWER_DYNAMIC_OFF = 3,
};

struct drm_open_hash {
	struct hlist_head *table;
	u8 order;
};

struct drm_modeset_lock {

	struct ww_mutex mutex;
	struct list_head head;
};

struct drm_mode_config {
	struct mutex mutex;
    struct drm_modeset_lock connection_mutex;
	struct drm_modeset_acquire_ctx *acquire_ctx;
	struct mutex idr_mutex;
	struct idr object_idr;
	struct idr tile_idr;
	struct mutex fb_lock;
	int num_fb;
	struct list_head fb_list;
	spinlock_t connector_list_lock;
	int num_connector;
	struct ida connector_ida;
	struct list_head connector_list;
	struct llist_head connector_free_list;
	struct work_struct connector_free_work;
	int num_encoder;
	struct list_head encoder_list;
	int num_total_plane;
	struct list_head plane_list;
	int num_crtc;
	struct list_head crtc_list;
	struct list_head property_list;
	struct list_head privobj_list;
	int min_width, min_height;
	int max_width, max_height;
	const struct drm_mode_config_funcs *funcs;
	resource_size_t fb_base;
	bool poll_enabled;
	bool poll_running;
	bool delayed_event;
	struct delayed_work output_poll_work;
	struct mutex blob_lock;
	struct list_head property_blob_list;
	struct drm_property *edid_property;
	struct drm_property *dpms_property;
	struct drm_property *path_property;
	struct drm_property *tile_property;
	struct drm_property *link_status_property;
	struct drm_property *plane_type_property;
	struct drm_property *prop_src_x;
	struct drm_property *prop_src_y;
	struct drm_property *prop_src_w;
	struct drm_property *prop_src_h;
	struct drm_property *prop_crtc_x;
	struct drm_property *prop_crtc_y;
	struct drm_property *prop_crtc_w;
	struct drm_property *prop_crtc_h;
	struct drm_property *prop_fb_id;
	struct drm_property *prop_in_fence_fd;
	struct drm_property *prop_out_fence_ptr;
	struct drm_property *prop_crtc_id;
	struct drm_property *prop_fb_damage_clips;
	struct drm_property *prop_active;
	struct drm_property *prop_mode_id;
	struct drm_property *prop_vrr_enabled;
	struct drm_property *dvi_i_subconnector_property;
	struct drm_property *dvi_i_select_subconnector_property;
	struct drm_property *dp_subconnector_property;
	struct drm_property *tv_subconnector_property;
	struct drm_property *tv_select_subconnector_property;
	struct drm_property *tv_mode_property;
	struct drm_property *tv_left_margin_property;
	struct drm_property *tv_right_margin_property;
	struct drm_property *tv_top_margin_property;
	struct drm_property *tv_bottom_margin_property;
	struct drm_property *tv_brightness_property;
	struct drm_property *tv_contrast_property;
	struct drm_property *tv_flicker_reduction_property;
	struct drm_property *tv_overscan_property;
	struct drm_property *tv_saturation_property;
	struct drm_property *tv_hue_property;
	struct drm_property *scaling_mode_property;
	struct drm_property *aspect_ratio_property;
	struct drm_property *content_type_property;
	struct drm_property *degamma_lut_property;
	struct drm_property *degamma_lut_size_property;
	struct drm_property *ctm_property;
	struct drm_property *gamma_lut_property;
	struct drm_property *gamma_lut_size_property;
	struct drm_property *suggested_x_property;
	struct drm_property *suggested_y_property;
	struct drm_property *non_desktop_property;
	struct drm_property *panel_orientation_property;
	struct drm_property *writeback_fb_id_property;
	struct drm_property *writeback_pixel_formats_property;
	struct drm_property *writeback_out_fence_ptr_property;
	struct drm_property *hdr_output_metadata_property;
	struct drm_property *content_protection_property;
	struct drm_property *hdcp_content_type_property;
	uint32_t preferred_depth, prefer_shadow;
	bool prefer_shadow_fbdev;
	bool fbdev_use_iomem;
	bool quirk_addfb_prefer_xbgr_30bpp;
	bool quirk_addfb_prefer_host_byte_order;
	bool async_page_flip;
	bool allow_fb_modifiers;
	bool normalize_zpos;
	struct drm_property *modifiers_property;
	uint32_t cursor_width, cursor_height;
	struct drm_atomic_state *suspend_state;
	const struct drm_mode_config_helper_funcs *helper_private;
};

struct drm_device {

	struct list_head legacy_dev_list;
    int if_version;
	struct kref ref;
	struct device *dev;

	struct {
		/** @managed.resources: managed resources list */
		struct list_head resources;
		/** @managed.final_kfree: pointer for final kfree() call */
		void *final_kfree;
		/** @managed.lock: protects @managed.resources */
		spinlock_t lock;
	} managed;
	struct drm_driver *driver;
	void *dev_private;
	struct drm_minor *primary;
	struct drm_minor *render;
	bool registered;
	struct drm_master *master;
	u32 driver_features;
	bool unplugged;
	struct inode *anon_inode;
	char *unique;
	struct mutex struct_mutex;
	struct mutex master_mutex;
	atomic_t open_count;
	struct mutex filelist_mutex;
	struct list_head filelist;
	struct list_head filelist_internal;
    struct mutex clientlist_mutex;
	struct list_head clientlist;
	bool irq_enabled;
	int irq;
	bool vblank_disable_immediate;
	struct drm_vblank_crtc *vblank;
	spinlock_t vblank_time_lock;
	spinlock_t vbl_lock;
	u32 max_vblank_count;
	struct list_head vblank_event_list;
	spinlock_t event_lock;
	struct drm_agp_head *agp;
	struct pci_dev *pdev;

#ifdef __alpha__
	struct pci_controller *hose;
#endif
	unsigned int num_crtcs;
	struct drm_mode_config mode_config;
	struct mutex object_name_lock;
	struct idr object_name_idr;
	struct drm_vma_offset_manager *vma_offset_manager;
	struct drm_vram_mm *vram_mm;
    enum switch_power_state switch_power_state;
	struct drm_fb_helper *fb_helper;
#if IS_ENABLED(CONFIG_DRM_LEGACY)
	struct list_head ctxlist;
	struct mutex ctxlist_mutex;
	struct idr ctx_idr;
	struct list_head maplist;
	struct drm_open_hash map_hash;
	struct list_head vmalist;
	struct drm_device_dma *dma;
	__volatile__ long context_flag;
	int last_context;
	spinlock_t buf_lock;
	int buf_use;
	atomic_t buf_alloc;
	struct {
		int context;
		struct drm_hw_lock *lock;
	} sigdata;
	struct drm_local_map *agp_buffer_map;
	unsigned int agp_buffer_token;
	struct drm_sg_mem *sg;
#endif
};

struct drm_device *drm_dev;

typedef void (*drmres_release_t)(struct drm_device *dev, void *res);



struct drm_encoder {
	struct drm_device *dev;
	struct list_head head;
	struct drm_mode_object base;
	char *name;
	int encoder_type;
	unsigned index;
	uint32_t possible_crtcs;
	uint32_t possible_clones;
	struct drm_crtc *crtc;
	struct list_head bridge_chain;
	const struct drm_encoder_funcs *funcs;
	const struct drm_encoder_helper_funcs *helper_private;
};

struct drm_encoder_funcs {
	void (*reset)(struct drm_encoder *encoder);
	void (*destroy)(struct drm_encoder *encoder);
	int (*late_register)(struct drm_encoder *encoder);
	void (*early_unregister)(struct drm_encoder *encoder);
};

struct drm_crtc_crc {
	spinlock_t lock;
	const char *source;
	bool opened, overflow;
	struct drm_crtc_crc_entry *entries;
	int head, tail;
	size_t values_cnt;
	wait_queue_head_t wq;
};

struct drm_crtc {
	struct drm_device *dev;
	struct device_node *port;
	struct list_head head;
	char *name;
	struct drm_modeset_lock mutex;
	struct drm_mode_object base;
	struct drm_plane *primary;
	struct drm_plane *cursor;
	unsigned index;
	int cursor_x;
	int cursor_y;
	bool enabled;
	struct drm_display_mode mode;
	struct drm_display_mode hwmode;
	int x;
	int y;
	const struct drm_crtc_funcs *funcs;
	uint32_t gamma_size;
	uint16_t *gamma_store;
	const struct drm_crtc_helper_funcs *helper_private;
	struct drm_object_properties properties;
	struct drm_crtc_state *state;
	struct list_head commit_list;
	spinlock_t commit_lock;
#ifdef CONFIG_DEBUG_FS
	struct dentry *debugfs_entry;
#endif
	struct drm_crtc_crc crc;
	unsigned int fence_context;
	spinlock_t fence_lock;
	unsigned long fence_seqno;
	char timeline_name[32];
	struct drm_self_refresh_data *self_refresh_data;
};

struct drm_crtc_funcs {
	void (*reset)(struct drm_crtc *crtc);
	int (*cursor_set)(struct drm_crtc *crtc, struct drm_file *file_priv,
			  uint32_t handle, uint32_t width, uint32_t height);
	int (*cursor_set2)(struct drm_crtc *crtc, struct drm_file *file_priv,
			   uint32_t handle, uint32_t width, uint32_t height,
			   int32_t hot_x, int32_t hot_y);
	int (*cursor_move)(struct drm_crtc *crtc, int x, int y);
	int (*gamma_set)(struct drm_crtc *crtc, u16 *r, u16 *g, u16 *b,
			 uint32_t size,
			 struct drm_modeset_acquire_ctx *ctx);
	void (*destroy)(struct drm_crtc *crtc);
	int (*set_config)(struct drm_mode_set *set,
			  struct drm_modeset_acquire_ctx *ctx);
	int (*page_flip)(struct drm_crtc *crtc,
			 struct drm_framebuffer *fb,
			 struct drm_pending_vblank_event *event,
			 uint32_t flags,
			 struct drm_modeset_acquire_ctx *ctx);
	int (*page_flip_target)(struct drm_crtc *crtc,
				struct drm_framebuffer *fb,
				struct drm_pending_vblank_event *event,
				uint32_t flags, uint32_t target,
				struct drm_modeset_acquire_ctx *ctx);
	int (*set_property)(struct drm_crtc *crtc,
			    struct drm_property *property, uint64_t val);
	struct drm_crtc_state *(*atomic_duplicate_state)(struct drm_crtc *crtc);
	void (*atomic_destroy_state)(struct drm_crtc *crtc,
				     struct drm_crtc_state *state);
	int (*atomic_set_property)(struct drm_crtc *crtc,
				   struct drm_crtc_state *state,
				   struct drm_property *property,
				   uint64_t val);
	int (*atomic_get_property)(struct drm_crtc *crtc,
				   const struct drm_crtc_state *state,
				   struct drm_property *property,
				   uint64_t *val);
	int (*late_register)(struct drm_crtc *crtc);
	void (*early_unregister)(struct drm_crtc *crtc);
	int (*set_crc_source)(struct drm_crtc *crtc, const char *source);
	int (*verify_crc_source)(struct drm_crtc *crtc, const char *source,
				 size_t *values_cnt);
	const char *const *(*get_crc_sources)(struct drm_crtc *crtc,
					      size_t *count);
	void (*atomic_print_state)(struct drm_printer *p,
				   const struct drm_crtc_state *state);
	u32 (*get_vblank_counter)(struct drm_crtc *crtc);
	int (*enable_vblank)(struct drm_crtc *crtc);
	void (*disable_vblank)(struct drm_crtc *crtc);
	bool (*get_vblank_timestamp)(struct drm_crtc *crtc,
				     int *max_error,
				     ktime_t *vblank_time,
				     bool in_vblank_irq);
};

enum drm_plane_type {
	DRM_PLANE_TYPE_OVERLAY,
	DRM_PLANE_TYPE_PRIMARY,
	DRM_PLANE_TYPE_CURSOR,
};

struct drm_plane {
	struct drm_device *dev;
	struct list_head head;
	char *name;
	struct drm_modeset_lock mutex;
	struct drm_mode_object base;
	uint32_t possible_crtcs;
	uint32_t *format_types;
	unsigned int format_count;
	bool format_default;
	uint64_t *modifiers;
	unsigned int modifier_count;
	struct drm_crtc *crtc;
	struct drm_framebuffer *fb;
	struct drm_framebuffer *old_fb;
	const struct drm_plane_funcs *funcs;
	struct drm_object_properties properties;
	enum drm_plane_type type;
	unsigned index;
	const struct drm_plane_helper_funcs *helper_private;
	struct drm_plane_state *state;
	struct drm_property *alpha_property;
	struct drm_property *zpos_property;
	struct drm_property *rotation_property;
	struct drm_property *blend_mode_property;
	struct drm_property *color_encoding_property;
	struct drm_property *color_range_property;
};

struct drm_plane_funcs {
    int (*update_plane)(struct drm_plane *plane,
			    struct drm_crtc *crtc, struct drm_framebuffer *fb,
			    int crtc_x, int crtc_y,
			    unsigned int crtc_w, unsigned int crtc_h,
			    uint32_t src_x, uint32_t src_y,
			    uint32_t src_w, uint32_t src_h,
			    struct drm_modeset_acquire_ctx *ctx);
	int (*disable_plane)(struct drm_plane *plane,
			     struct drm_modeset_acquire_ctx *ctx);
	void (*destroy)(struct drm_plane *plane);
	void (*reset)(struct drm_plane *plane);
	int (*set_property)(struct drm_plane *plane,
			    struct drm_property *property, uint64_t val);
	struct drm_plane_state *(*atomic_duplicate_state)(struct drm_plane *plane);
	void (*atomic_destroy_state)(struct drm_plane *plane,
				     struct drm_plane_state *state);
	int (*atomic_set_property)(struct drm_plane *plane,
				   struct drm_plane_state *state,
				   struct drm_property *property,
				   uint64_t val);
	int (*atomic_get_property)(struct drm_plane *plane,
				   const struct drm_plane_state *state,
				   struct drm_property *property,
				   uint64_t *val);
	int (*late_register)(struct drm_plane *plane);
	void (*early_unregister)(struct drm_plane *plane);
	void (*atomic_print_state)(struct drm_printer *p,
				   const struct drm_plane_state *state);
	bool (*format_mod_supported)(struct drm_plane *plane, uint32_t format,
				     uint64_t modifier);
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
