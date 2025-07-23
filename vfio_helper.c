/*
 * vfio_helper.c - Extract VFIO ioctl constants from kernel headers
 * 
 * This program opens /dev/vfio/vfio to verify VFIO subsystem availability,
 * then prints the numeric values of VFIO ioctl constants that are computed
 * from kernel headers at compile time. This ensures the constants match
 * the exact kernel version being used.
 * 
 * The program does NOT actually execute any ioctls - it only prints the
 * constant values that would be used for ioctl calls.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <linux/vfio.h>

int main(void) {
    int vfio_fd;
    
    /* 
     * Open /dev/vfio/vfio to verify VFIO subsystem is available.
     * We don't actually use this fd for ioctls - just verification.
     * This ensures we're running on a system with VFIO support.
     */
    vfio_fd = open("/dev/vfio/vfio", O_RDWR);
    if (vfio_fd < 0) {
        fprintf(stderr, "Warning: Cannot open /dev/vfio/vfio: %s\n", 
                strerror(errno));
        fprintf(stderr, "Warning: VFIO may not be available, but continuing...\n");
        /* Continue anyway - we just want the constants */
    } else {
        close(vfio_fd);
    }
    
    /*
     * Print all VFIO ioctl constants, one per line.
     * These values are computed at compile-time from the kernel headers,
     * ensuring they match the running kernel exactly.
     * 
     * Format: CONSTANT_NAME=numeric_value
     * This makes parsing easier for the Python patcher script.
     */
    
    /* Container/API level ioctls */
    printf("VFIO_GET_API_VERSION=%lu\n", (unsigned long)VFIO_GET_API_VERSION);
    printf("VFIO_CHECK_EXTENSION=%lu\n", (unsigned long)VFIO_CHECK_EXTENSION);
    printf("VFIO_SET_IOMMU=%lu\n", (unsigned long)VFIO_SET_IOMMU);
    
    /* Group management ioctls */
    printf("VFIO_GROUP_GET_STATUS=%lu\n", (unsigned long)VFIO_GROUP_GET_STATUS);
    printf("VFIO_GROUP_SET_CONTAINER=%lu\n", (unsigned long)VFIO_GROUP_SET_CONTAINER);
    printf("VFIO_GROUP_GET_DEVICE_FD=%lu\n", (unsigned long)VFIO_GROUP_GET_DEVICE_FD);
    
    /* Device-level ioctls */
    printf("VFIO_DEVICE_GET_INFO=%lu\n", (unsigned long)VFIO_DEVICE_GET_INFO);
    printf("VFIO_DEVICE_GET_REGION_INFO=%lu\n", (unsigned long)VFIO_DEVICE_GET_REGION_INFO);
    printf("VFIO_DEVICE_GET_IRQ_INFO=%lu\n", (unsigned long)VFIO_DEVICE_GET_IRQ_INFO);
    printf("VFIO_DEVICE_SET_IRQS=%lu\n", (unsigned long)VFIO_DEVICE_SET_IRQS);
    printf("VFIO_DEVICE_RESET=%lu\n", (unsigned long)VFIO_DEVICE_RESET);
    printf("VFIO_DEVICE_GET_PCI_HOT_RESET_INFO=%lu\n", (unsigned long)VFIO_DEVICE_GET_PCI_HOT_RESET_INFO);
    
    /* IOMMU management ioctls */
    printf("VFIO_IOMMU_GET_INFO=%lu\n", (unsigned long)VFIO_IOMMU_GET_INFO);
    printf("VFIO_IOMMU_MAP_DMA=%lu\n", (unsigned long)VFIO_IOMMU_MAP_DMA);
    printf("VFIO_IOMMU_UNMAP_DMA=%lu\n", (unsigned long)VFIO_IOMMU_UNMAP_DMA);
    printf("VFIO_IOMMU_ENABLE=%lu\n", (unsigned long)VFIO_IOMMU_ENABLE);
    printf("VFIO_IOMMU_DISABLE=%lu\n", (unsigned long)VFIO_IOMMU_DISABLE);
    
    return 0;
}