# Kernel module build configuration
obj-m += donor_dump.o

# Get kernel release
KVER ?= $(shell uname -r)
# Get kernel source directory
KDIR ?= /lib/modules/$(KVER)/build
# Get current directory
PWD := $(shell pwd)

# Default target
all:
	@echo "Building donor_dump kernel module for kernel $(KVER)..."
	@if [ ! -d "$(KDIR)" ]; then \
		echo "Error: Kernel headers not found at $(KDIR)"; \
		echo "Please install appropriate kernel headers for your distribution"; \
		echo "For Debian/Ubuntu: apt-get install linux-headers-$(KVER)"; \
		echo "For Fedora/CentOS: dnf install kernel-devel-$(KVER)"; \
		echo "For Arch Linux: pacman -S linux-headers"; \
		echo "For openSUSE: zypper install kernel-devel-$(KVER)"; \
		exit 1; \
	fi
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Clean build artifacts
clean:
	@echo "Cleaning donor_dump build artifacts..."
	@if [ -d "$(KDIR)" ]; then \
		$(MAKE) -C $(KDIR) M=$(PWD) clean; \
	fi
	rm -f *.o *.ko *.mod.c *.mod *.order *.symvers .*.cmd
	rm -rf .tmp_versions/ .cache.mk Module.symvers modules.order

# Install module (requires root)
install: all
	@echo "Installing donor_dump module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "Error: Module installation requires root privileges"; \
		exit 1; \
	fi
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	depmod -a

# Uninstall module (requires root)
uninstall:
	@echo "Uninstalling donor_dump module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "Error: Module removal requires root privileges"; \
		exit 1; \
	fi
	rmmod donor_dump 2>/dev/null || true
	rm -f /lib/modules/$(shell uname -r)/extra/donor_dump.ko
	depmod -a

# Load module with BDF parameter
load: all
	@echo "Loading donor_dump module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "Error: Module loading requires root privileges"; \
		exit 1; \
	fi
	@if [ -z "$(BDF)" ]; then \
		echo "Error: BDF parameter required. Usage: make load BDF=0000:03:00.0"; \
		exit 1; \
	fi
	insmod ./donor_dump.ko bdf=$(BDF)

# Unload module
unload:
	@echo "Unloading donor_dump module..."
	@if [ "$(shell id -u)" != "0" ]; then \
		echo "Error: Module unloading requires root privileges"; \
		exit 1; \
	fi
	rmmod donor_dump

# Show module info
info:
	@if [ -f "./donor_dump.ko" ]; then \
		echo "Module information:"; \
		modinfo ./donor_dump.ko; \
	else \
		echo "Module not built. Run 'make' first."; \
	fi

# Help target
help:
	@echo "Available targets:"
	@echo "  all      - Build the kernel module (default)"
	@echo "  clean    - Clean build artifacts"
	@echo "  install  - Install module to system (requires root)"
	@echo "  uninstall- Remove module from system (requires root)"
	@echo "  load     - Load module with BDF parameter (requires root)"
	@echo "           Usage: make load BDF=0000:03:00.0"
	@echo "  unload   - Unload module (requires root)"
	@echo "  info     - Show module information"
	@echo "  help     - Show this help message"

.PHONY: all clean install uninstall load unload info help
