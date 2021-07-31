#!/usr/bin/env bash
# Expected to run as root
set -euo pipefail

TMPDIR=""

cleanup() {
    EXIT_CODE="$?"
    if [[ "$TMPDIR" != "" ]]; then
        echo '*** Unmounting...'
        umount "$BOOTDIR" "$ROOTDIR"
        rm -r "$TMPDIR"
    fi

    if [[ "$EXIT_CODE" == 0 ]]; then
        echo '*** SUCCESS (SAFE TO EJECT)'
    else
        echo '*** Exit code:' $EXIT_CODE
        echo '*** FAILURE (SAFE TO EJECT)'
    fi

}

trap cleanup EXIT

# Argument defaults

# download at: http://os.archlinuxarm.org/os/ArchLinuxARM-rpi-aarch64-latest.tar.gz
OS_ARCHIVE="ArchLinuxARM-rpi-aarch64-latest.tar.gz"
USER_SSH_KEY="/home/luke/.ssh/id_rsa.pub"

# Parse user-specified arguments

while (( "$#" )); do
  case "$1" in
    -h|--help)
      echo "Usage: mksdcard.sh -H HOSTNAME -i IP -a ARCHIVE -d DEVICE -u USER -p KEY-FILE"
      exit 0
      ;;
    -a|--archive)
      OS_ARCHIVE="$2"
      shift 2
      ;;
    -d|--device)
      SDDEV="$2"
      shift 2
      ;;
    -p|--public-key)
      USER_SSH_KEY="$2"
      shift 2
      ;;
    -i|--ip-address)
      IP_ADDR="$2"
      shift 2
      ;;
    -H|--hostname)
      IP_HOSTNAME="$2"
      shift 2
      ;;
    -r|--router-ip)
      IP_ROUTER="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Ensure required arguments were specified

SDDEV="${SDDEV?Must specify -d/--device}"
IP_ADDR="${IP_ADDR?Must specify -i/--ip-address}"
IP_ROUTER="${IP_ROUTER?Must specify -r/--router-ip}"
IP_HOSTNAME="${IP_HOSTNAME?Must specify -H/--hostname}"

echo "*** partitioning SD card..."

# Partition SD card with sfdisk
# 1. Wipe any existing partitions
# 2. Allocate first 200M to a partition
#    type=c is partition type: W95 FAT32 (LBA)
# 3. Allocate rest to a partition
#    type=83 is partition type: Linux
sfdisk "$SDDEV" << EOF
label: dos
label-id: 0x2aff57d5
device: $SDDEV
unit: sectors
sector-size: 512

size=+200MiB, type=c
type=83
EOF

# Make filesystems
mkfs.vfat "$SDDEV"1
mkfs.ext4 "$SDDEV"2


echo "*** mounting filesystems..."

# Mount filesystems in temporary directory
TMPDIR="$(mktemp -d)"
BOOTDIR="$TMPDIR/boot"
ROOTDIR="$TMPDIR/root"
mkdir -p "$BOOTDIR"
mkdir -p "$ROOTDIR"
mount "$SDDEV"1 "$BOOTDIR"
mount "$SDDEV"2 "$ROOTDIR"

echo "*** extracting OS archive..."

# Extract OS archive into root partition
bsdtar -xpf "$OS_ARCHIVE" -C "$ROOTDIR"

echo "*** doing tweaks..."

# Delete alarm user that exists by default
userdel -P "$ROOTDIR" alarm

# Lock root so password login is not possible
usermod -P "$ROOTDIR" -L root

cat >> "$ROOTDIR/etc/ssh/sshd_config" << EOF
PasswordAuthentication no
ChallengeResponseAuthentication no
PermitRootLogin without-password
EOF

# Add public key for SSH login
mkdir -p "$ROOTDIR/root/.ssh"
cp "$USER_SSH_KEY" "$ROOTDIR/root/.ssh/authorized_keys"

# update /etc/fstab for the different SD block device compared to the Raspberry Pi 3
sed -i 's/mmcblk0/mmcblk1/g' "$ROOTDIR/etc/fstab"

# set hostname
echo "$IP_HOSTNAME" > "$ROOTDIR/etc/hostname"

# Static network configuration
cat >> "$ROOTDIR/etc/dhcpcd.conf" << EOF
interface eth0
static ip_address=$IP_ADDR
static routers=$IP_ROUTER
EOF

# Enable cgroups (needed for containerd)
echo "cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1" > "$ROOTDIR/boot/cmdline.txt"

# Enable kernel modules needed for k0s
cat > "$ROOTDIR/etc/modules-load.d/k0s-modules.conf" << EOF
overlay
nf_conntrack
br_netfilter
EOF

echo "*** flushing writes..."

# flush writes
sync

echo "*** copying to boot partition..."

# Move boot stuff to boot partition
mv "$ROOTDIR/boot/"* "$BOOTDIR"

echo '*** Preparation complete!'

# # Run on the Pi after login:
# # pacman-key --init
# # pacman-key --populate archlinuxarm