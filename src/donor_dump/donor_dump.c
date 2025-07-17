/* donor_dump.c  - expose donor PCI-e device parameters via /proc/donor_dump
 *
 * Build:  make         (in donor_dump directory)
 * Load :  insmod donor_dump.ko bdf=0000:03:00.0
 *
 * Fields exported (one "key:value" per line):
 *   mpc               - 3-bit Max-Payload-Capable  (0-5)
 *   mpr               - 3-bit Max-ReadReq-InEffect (0-5)
 *   vendor_id, device_id, subvendor_id, subsystem_id, revision_id
 *   class_code        - 24-bit (class<<16 | subclass<<8 | progIF)
 *   bar_size          - byte length of BAR0
 *   dsn_hi / dsn_lo   - 64-bit Device Serial Number (0 if absent)
 *   extended_config   - Full 4KB configuration space (hex encoded)
 *   power_mgmt        - Power management capabilities
 *   aer_caps          - Advanced Error Reporting capabilities
 *   vendor_caps       - Vendor-specific capabilities
 *
 * Compatible with Linux kernel versions 4.x and 5.x, GPL-compatible.
 */
#include <linux/module.h>
#include <linux/version.h>
#include <linux/pci.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

static char *bdf = "";          /* passed as 0000:03:00.0 */
module_param(bdf, charp, 000);

/* Configuration options for enhanced features */
static bool enable_extended_config = true;
module_param(enable_extended_config, bool, 0444);
MODULE_PARM_DESC(enable_extended_config, "Enable extended configuration space extraction");

static bool enable_enhanced_caps = true;
module_param(enable_enhanced_caps, bool, 0444);
MODULE_PARM_DESC(enable_enhanced_caps, "Enable enhanced capability analysis");

static struct pci_dev        *pdev;
static struct proc_dir_entry *pe;

/* ───── /proc show ─────────────────────────────────────────────────────── */
static int show(struct seq_file *m, void *v)
{
    u16 vid, did, svid, ssid;  u8 rev;  u32 cls;
    int ret;
    
    /* Comprehensive device state validation before operations */
    if (!pdev) {
        seq_printf(m, "error:device_null\n");
        return 0;
    }
    
    if (pdev->error_state != pci_channel_io_normal) {
        seq_printf(m, "error:device_unavailable\n");
        return 0;
    }
    
    /* Check if device is still enabled */
    if (!pci_is_enabled(pdev)) {
        seq_printf(m, "error:device_disabled\n");
        return 0;
    }
    
    /* Validate device is still present on the bus */
    #if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 0, 0)
    if (!pci_device_is_present(pdev)) {
        seq_printf(m, "error:device_not_present\n");
        return 0;
    }
    #else
    /* For older kernels, check vendor ID */
    u16 test_vid;
    if (pci_read_config_word(pdev, PCI_VENDOR_ID, &test_vid) != PCIBIOS_SUCCESSFUL || test_vid == 0xFFFF) {
        seq_printf(m, "error:device_not_present\n");
        return 0;
    }
    #endif
    
    /* Safe PCI config space reads with error checking */
    ret = pci_read_config_word(pdev, PCI_VENDOR_ID, &vid);
    if (ret != PCIBIOS_SUCCESSFUL) {
        seq_printf(m, "error:config_read_failed\n");
        return 0;
    }
    
    /* Validate vendor ID is not 0xFFFF (indicates device removal) */
    if (vid == 0xFFFF) {
        seq_printf(m, "error:device_removed\n");
        return 0;
    }
    
    pci_read_config_word (pdev, PCI_DEVICE_ID,            &did);
    pci_read_config_word (pdev, PCI_SUBSYSTEM_VENDOR_ID,  &svid);
    pci_read_config_word (pdev, PCI_SUBSYSTEM_ID,         &ssid);
    pci_read_config_byte (pdev, PCI_REVISION_ID,          &rev);
    pci_read_config_dword(pdev, PCI_CLASS_REVISION,       &cls);

    /* ── walk legacy capability list for PCI-Express cap (ID 0x10) with bounds checking ── */
    u8 cap_ptr;
    ret = pci_read_config_byte(pdev, PCI_CAPABILITY_LIST, &cap_ptr);
    if (ret != PCIBIOS_SUCCESSFUL) {
        seq_printf(m, "error:capability_read_failed\n");
        return 0;
    }
    
    u8 mpc = 0, mpr = 0;
    int cap_count = 0;  /* Prevent infinite loops */
    while (cap_ptr && cap_count < 64) {  /* Max 64 capabilities to prevent infinite loop */
        /* Validate capability pointer is within config space bounds */
        if (cap_ptr < 0x40 || cap_ptr > 0xFC || (cap_ptr & 0x3)) {
            pr_debug("donor_dump: Invalid capability pointer 0x%02x\n", cap_ptr);
            break;  /* Invalid capability pointer */
        }
        
        u8 cap_id;
        ret = pci_read_config_byte(pdev, cap_ptr, &cap_id);
        if (ret != PCIBIOS_SUCCESSFUL) {
            pr_debug("donor_dump: Failed to read capability ID at 0x%02x\n", cap_ptr);
            break;
        }
        
        if (cap_id == PCI_CAP_ID_EXP) {
            /* Validate we have enough space for PCIe capability structure */
            if (cap_ptr + 0x8 <= 0xFF) {
                u32 devcap, devctl;
                ret = pci_read_config_dword(pdev, cap_ptr + 0x4, &devcap);
                if (ret != PCIBIOS_SUCCESSFUL) break;
                ret = pci_read_config_dword(pdev, cap_ptr + 0x8, &devctl);
                if (ret != PCIBIOS_SUCCESSFUL) break;
                mpc =  devcap & 0x7;
                mpr = (devctl >> 5) & 0x7;
            }
            break;
        }
        
        ret = pci_read_config_byte(pdev, cap_ptr + 1, &cap_ptr);  /* next ptr */
        if (ret != PCIBIOS_SUCCESSFUL) {
            pr_debug("donor_dump: Failed to read next capability pointer\n");
            break;
        }
        cap_count++;
    }

    /* ── Extended configuration space extraction (4KB) ── */
    u8 *extended_config = NULL;
    if (enable_extended_config) {
        extended_config = kmalloc(4096, GFP_KERNEL);
        if (!extended_config) {
            pr_warn("donor_dump: Failed to allocate memory for extended config space\n");
            seq_printf(m, "error:memory_allocation_failed\n");
            return 0;
        }
        
        /* Read full 4KB configuration space with error handling */
        for (int i = 0; i < 4096; i += 4) {
            u32 data;
            ret = pci_read_config_dword(pdev, i, &data);
            if (ret != PCIBIOS_SUCCESSFUL) {
                /* Fill with 0xFF for inaccessible regions */
                data = 0xFFFFFFFF;
                pr_debug("donor_dump: Config space read failed at offset 0x%03x\n", i);
            }
            memcpy(extended_config + i, &data, 4);
        }
        pr_info("donor_dump: Successfully extracted 4KB extended configuration space\n");
    }
    
    /* ── Enhanced extended capability analysis ── */
    u32 dsn_lo = 0, dsn_hi = 0;
    u32 power_mgmt_caps = 0;
    u32 aer_caps = 0;
    u32 vendor_caps = 0;
    u32 ecap_ptr = 0x100;   /* extended caps start at 0x100 */
    int ecap_count = 0;     /* Prevent infinite loops */
    
    while (ecap_ptr && ecap_count < 64) {  /* Max 64 extended capabilities */
        /* Validate extended capability pointer bounds */
        if (ecap_ptr < 0x100 || ecap_ptr > 0xFFC || (ecap_ptr & 0x3)) {
            break;  /* Invalid extended capability pointer */
        }
        
        u32 hdr;
        ret = pci_read_config_dword(pdev, ecap_ptr, &hdr);
        if (ret != PCIBIOS_SUCCESSFUL || !hdr) {
            pr_debug("donor_dump: Failed to read extended capability header at 0x%03x\n", ecap_ptr);
            break;
        }
        
        u16 cap_id = hdr & 0xffff;
        u16 next   = hdr >> 20;
        
        switch (cap_id) {
            case PCI_EXT_CAP_ID_DSN:            /* 0x0003 - Device Serial Number */
                if (ecap_ptr + 0x8 <= 0xFFF) {
                    ret = pci_read_config_dword(pdev, ecap_ptr + 0x4, &dsn_lo);
                    if (ret != PCIBIOS_SUCCESSFUL) break;
                    ret = pci_read_config_dword(pdev, ecap_ptr + 0x8, &dsn_hi);
                    if (ret != PCIBIOS_SUCCESSFUL) break;
                }
                break;
                
            case PCI_EXT_CAP_ID_PWR:            /* 0x0001 - Power Budgeting */
                if (ecap_ptr + 0x4 <= 0xFFF) {
                    ret = pci_read_config_dword(pdev, ecap_ptr + 0x4, &power_mgmt_caps);
                    if (ret != PCIBIOS_SUCCESSFUL) power_mgmt_caps = 0;
                }
                break;
                
            case PCI_EXT_CAP_ID_ERR:            /* 0x0001 - Advanced Error Reporting */
                if (ecap_ptr + 0x4 <= 0xFFF) {
                    ret = pci_read_config_dword(pdev, ecap_ptr + 0x4, &aer_caps);
                    if (ret != PCIBIOS_SUCCESSFUL) aer_caps = 0;
                }
                break;
                
            case PCI_EXT_CAP_ID_VNDR:           /* 0x000B - Vendor Specific */
                if (ecap_ptr + 0x4 <= 0xFFF) {
                    ret = pci_read_config_dword(pdev, ecap_ptr + 0x4, &vendor_caps);
                    if (ret != PCIBIOS_SUCCESSFUL) vendor_caps = 0;
                }
                break;
        }
        
        ecap_ptr = next;
        ecap_count++;
    }

    /* ── size of BAR0 (bytes) with validation ── */
    resource_size_t bar_size = 0;
    if (pci_resource_flags(pdev, 0) & IORESOURCE_MEM) {
        bar_size = pci_resource_len(pdev, 0);
    }

    /* ── print one key:value per line (no leading spaces) ── */
    seq_printf(m,
        "mpc:0x%X\n"
        "mpr:0x%X\n"
        "vendor_id:0x%04X\n"
        "device_id:0x%04X\n"
        "subvendor_id:0x%04X\n"
        "subsystem_id:0x%04X\n"
        "revision_id:0x%02X\n"
        "class_code:0x%06X\n"
        "bar_size:0x%llX\n"
        "dsn_hi:0x%08X\n"
        "dsn_lo:0x%08X\n"
        "power_mgmt:0x%08X\n"
        "aer_caps:0x%08X\n"
        "vendor_caps:0x%08X\n",
        mpc, mpr,
        vid, did, svid, ssid, rev, cls >> 8,
        (unsigned long long)bar_size,
        dsn_hi, dsn_lo,
        power_mgmt_caps, aer_caps, vendor_caps);

    /* ── Output extended configuration space as hex-encoded string ── */
    if (enable_extended_config && extended_config) {
        seq_printf(m, "extended_config:");
        for (int i = 0; i < 4096; i++) {
            seq_printf(m, "%02x", extended_config[i]);
        }
        seq_printf(m, "\n");
        kfree(extended_config);
    } else {
        seq_printf(m, "extended_config:disabled\n");
    }
    
    return 0;
}

/* ───── seq_file boilerplate ───────────────────────────────────────────── */
static int open_proc(struct inode *i, struct file *f)
{ return single_open(f, show, NULL); }

/* Define proc_ops or file_operations based on kernel version */
#if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 6, 0)
static const struct proc_ops fops = {
    .proc_open    = open_proc,
    .proc_read    = seq_read,
    .proc_lseek   = seq_lseek,
    .proc_release = single_release,
};
#else
static const struct file_operations fops = {
    .open    = open_proc,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = single_release,
};
#endif

/* ───── module init/exit with comprehensive error handling ───────────────────────────────────────────────── */
static int __init mod_init(void)
{
    unsigned dom, bus, dev, fn;
    int ret = 0;

    /* Validate BDF parameter format */
    if (!bdf || strlen(bdf) == 0) {
        pr_err("donor_dump: BDF parameter is required (format: 0000:03:00.0)\n");
        return -EINVAL;
    }

    if (sscanf(bdf, "%x:%x:%x.%x", &dom, &bus, &dev, &fn) != 4) {
        pr_err("donor_dump: Invalid BDF format '%s' (expected: 0000:03:00.0)\n", bdf);
        return -EINVAL;
    }

    /* Validate BDF component ranges */
    if (dom > 0xFFFF || bus > 0xFF || dev > 0x1F || fn > 0x7) {
        pr_err("donor_dump: BDF components out of range: %04x:%02x:%02x.%x\n", dom, bus, dev, fn);
        return -EINVAL;
    }

    pdev = pci_get_domain_bus_and_slot(dom, bus, PCI_DEVFN(dev, fn));
    if (!pdev) {
        pr_err("donor_dump: PCI device %s not found\n", bdf);
        return -ENODEV;
    }

    /* Comprehensive device state validation */
    if (!pci_is_enabled(pdev)) {
        pr_err("donor_dump: PCI device %s is not enabled\n", bdf);
        ret = -ENODEV;
        goto err_put_device;
    }

    /* Check if device is still present (not removed during operation) */
    if (pdev->error_state != pci_channel_io_normal) {
        pr_err("donor_dump: PCI device %s is in error state\n", bdf);
        ret = -EIO;
        goto err_put_device;
    }

    /* Verify device is actually present on the bus */
    #if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 0, 0)
    if (!pci_device_is_present(pdev)) {
        pr_err("donor_dump: PCI device %s is not present on bus\n", bdf);
        ret = -ENODEV;
        goto err_put_device;
    }
    #else
    /* For older kernels, check vendor ID instead */
    u16 vendor_id;
    if (pci_read_config_word(pdev, PCI_VENDOR_ID, &vendor_id) != PCIBIOS_SUCCESSFUL || vendor_id == 0xFFFF) {
        pr_err("donor_dump: PCI device %s is not present on bus\n", bdf);
        ret = -ENODEV;
        goto err_put_device;
    }
    #endif

    /* Test basic config space access */
    u16 vendor_id;
    if (pci_read_config_word(pdev, PCI_VENDOR_ID, &vendor_id) != PCIBIOS_SUCCESSFUL || vendor_id == 0xFFFF) {
        pr_err("donor_dump: Cannot read config space from device %s\n", bdf);
        ret = -EIO;
        goto err_put_device;
    }

    /* Create proc entry */
    pe = proc_create("donor_dump", 0444, NULL, &fops);
    if (!pe) {
        pr_err("donor_dump: Failed to create /proc/donor_dump\n");
        ret = -ENOMEM;
        goto err_put_device;
    }
    
    pr_info("donor_dump: Successfully loaded for device %s (VID:0x%04x)\n", bdf, vendor_id);
    return 0;

err_put_device:
    if (pdev) {
        pci_dev_put(pdev);
        pdev = NULL;
    }
    return ret;
}

static void __exit mod_exit(void)
{
    /* Safe cleanup with proper ordering and error handling */
    if (pe) {
        proc_remove(pe);
        pe = NULL;
        pr_debug("donor_dump: Removed /proc/donor_dump entry\n");
    }
    
    /* Properly release device reference to prevent memory leaks */
    if (pdev) {
        /* Verify device is still valid before logging */
        #if LINUX_VERSION_CODE >= KERNEL_VERSION(5, 0, 0)
        if (pci_device_is_present(pdev) && pdev->error_state == pci_channel_io_normal) {
            pr_info("donor_dump: Releasing device %s\n", bdf);
        } else {
            pr_info("donor_dump: Releasing device reference (device may have been removed)\n");
        }
        #else
        /* For older kernels, check error state only */
        if (pdev->error_state == pci_channel_io_normal) {
            pr_info("donor_dump: Releasing device %s\n", bdf);
        } else {
            pr_info("donor_dump: Releasing device reference (device may have been removed)\n");
        }
        #endif
        pci_dev_put(pdev);
        pdev = NULL;
    }
    
    pr_info("donor_dump: Module unloaded successfully\n");
}

module_init(mod_init);
module_exit(mod_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Dump selected PCIe device parameters for DMA-FW builder");
MODULE_AUTHOR("Ramsey McGrath <ramsey@voltcyclone.info>");