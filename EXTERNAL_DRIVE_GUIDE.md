# Using External Drives with Docker

This guide explains how to mount and use external drives (USB drives, external hard drives, network drives) with your Docker setup.

## Current System Status

From your system, I can see:
- `/storage` - A 7.3TB drive (sda) already mounted
- `sdb` - A 7.3TB drive (not currently mounted)

---

## Method 1: Mount External Drive to Host System

### Step 1: Find Your External Drive

```bash
# List all block devices
lsblk

# Or with more details
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,UUID
```

### Step 2: Create Mount Point

```bash
# Create a directory to mount the drive
sudo mkdir -p /mnt/external_drive

# Or use a more descriptive name
sudo mkdir -p /mnt/data_drive
```

### Step 3: Mount the Drive

**For a drive that's already formatted:**

```bash
# Find the device (e.g., /dev/sdb1)
sudo mount /dev/sdb1 /mnt/external_drive

# Check if it's mounted
df -h | grep external_drive
```

**For a drive that needs formatting (WARNING: This will erase all data):**

```bash
# Format as ext4 (Linux native)
sudo mkfs.ext4 /dev/sdb1

# Then mount it
sudo mount /dev/sdb1 /mnt/external_drive
```

### Step 4: Set Permissions

```bash
# Make it accessible to your user
sudo chown -R jeremy.siburian:gci /mnt/external_drive

# Or make it writable by all
sudo chmod 755 /mnt/external_drive
```

### Step 5: Make Mount Permanent (Optional)

Add to `/etc/fstab` to mount automatically on boot:

```bash
# First, get the UUID
sudo blkid /dev/sdb1

# Edit fstab
sudo nano /etc/fstab

# Add a line like this (replace UUID with your actual UUID):
UUID=your-uuid-here /mnt/external_drive ext4 defaults,user 0 2
```

---

## Method 2: Use Existing Mounted Drive (/storage)

If you want to use the drive already mounted at `/storage`:

### Option A: Symlink to Project Directory

```bash
# Create symlinks in your project
cd /home/jeremy.siburian/lego_release
ln -s /storage/data ./data_external
ln -s /storage/checkpoints ./checkpoints_external
```

### Option B: Mount Directly in Docker Compose

Update `docker-compose.yml` to mount `/storage`:

```yaml
volumes:
  # Mount external drive
  - /storage/data:/workspace/data_external
  - /storage/checkpoints:/workspace/checkpoints_external
  # ... other volumes
```

---

## Method 3: Mount External Drive in Docker Compose

### Direct Mount in docker-compose.yml

Edit `docker-compose.yml` to add external drive volumes:

```yaml
services:
  lego_release:
    # ... other config ...
    volumes:
      # Mount external drive directories
      - /mnt/external_drive/data:/workspace/data_external
      - /mnt/external_drive/checkpoints:/workspace/checkpoints_external
      - /mnt/external_drive/results:/workspace/results_external
      
      # Or use /storage if already mounted
      - /storage/data:/workspace/data_external
      - /storage/checkpoints:/workspace/checkpoints_external
      
      # Existing mounts
      - ./data:/workspace/data
      - ./results:/workspace/results
      - ./checkpoints:/workspace/checkpoints
      - "./:/workspace"
```

### Restart Docker Compose

```bash
# Stop containers
docker-compose down

# Start with new mounts
docker-compose up -d
```

---

## Method 4: Mount Network Drives (NFS, SMB/CIFS)

### Mount NFS Share

```bash
# Install NFS client (if not already installed)
sudo apt-get install nfs-common

# Create mount point
sudo mkdir -p /mnt/nfs_share

# Mount NFS
sudo mount -t nfs server:/path/to/share /mnt/nfs_share

# Or add to /etc/fstab for permanent mount
# server:/path/to/share /mnt/nfs_share nfs defaults 0 0
```

### Mount SMB/CIFS Share (Windows/Network Share)

```bash
# Install SMB client
sudo apt-get install cifs-utils

# Create mount point
sudo mkdir -p /mnt/smb_share

# Mount SMB share
sudo mount -t cifs //server/share /mnt/smb_share -o username=user,password=pass

# Or with credentials file (more secure)
sudo mount -t cifs //server/share /mnt/smb_share -o credentials=/path/to/.smbcredentials
```

Then add to `docker-compose.yml` as shown in Method 3.

---

## Practical Examples

### Example 1: Using /storage for Large Datasets

If `/storage` has your large datasets:

```yaml
# docker-compose.yml
volumes:
  # Use external storage for large datasets
  - /storage/synthetic_train:/workspace/data/synthetic_train
  - /storage/synthetic_val:/workspace/data/synthetic_val
  - /storage/checkpoints:/workspace/checkpoints
  # Keep local for smaller files
  - ./data:/workspace/data
  - "./:/workspace"
```

### Example 2: Separate Data and Results on External Drive

```yaml
volumes:
  # Data on external drive
  - /mnt/external_drive/datasets:/workspace/data
  # Results on external drive (for large outputs)
  - /mnt/external_drive/results:/workspace/results
  # Checkpoints on external drive
  - /mnt/external_drive/checkpoints:/workspace/checkpoints
  # Code stays local
  - "./:/workspace"
```

### Example 3: Multiple External Locations

```yaml
volumes:
  # Training data from one drive
  - /storage/training_data:/workspace/data/training
  # Evaluation data from another location
  - /mnt/usb_drive/eval_data:/workspace/data/eval
  # Checkpoints from network share
  - /mnt/nfs_share/checkpoints:/workspace/checkpoints
  # Local project code
  - "./:/workspace"
```

---

## Accessing Files in Container

Once mounted, access files from inside the container:

```bash
# Enter container
docker exec -it lego_release-jeremy bash

# Check mounted volumes
ls -la /workspace/

# Access external drive data
ls -la /workspace/data_external/
ls -la /workspace/checkpoints_external/

# Use in your code
python script.py --data_path /workspace/data_external/synthetic_train
```

---

## Troubleshooting

### Permission Denied Errors

```bash
# Fix ownership
sudo chown -R jeremy.siburian:gci /mnt/external_drive

# Or make it world-readable
sudo chmod -R 755 /mnt/external_drive
```

### Drive Not Showing in Container

1. **Check if drive is mounted on host:**
   ```bash
   df -h | grep external
   mount | grep external
   ```

2. **Check docker-compose.yml syntax:**
   ```bash
   docker-compose config  # Validates YAML
   ```

3. **Check container logs:**
   ```bash
   docker-compose logs lego_release
   ```

### Drive Unmounts After Reboot

Add to `/etc/fstab` for permanent mounting (see Method 1, Step 5).

### Docker Can't Access Mounted Drive

Ensure the drive is mounted **before** starting Docker containers:

```bash
# Mount drive first
sudo mount /dev/sdb1 /mnt/external_drive

# Then start containers
docker-compose up -d
```

---

## Best Practices

1. **Mount drives before starting Docker** - Ensure external drives are mounted on the host before running `docker-compose up`

2. **Use absolute paths** - Always use absolute paths in `docker-compose.yml` volumes (e.g., `/mnt/drive` not `~/drive`)

3. **Check permissions** - Make sure your user has read/write access to mounted drives

4. **Organize by purpose** - Keep datasets, checkpoints, and results in separate directories

5. **Backup important data** - External drives can fail; keep backups of critical data

6. **Monitor disk space** - Large datasets can fill drives quickly:
   ```bash
   df -h  # Check disk usage
   du -sh /mnt/external_drive/*  # Check directory sizes
   ```

---

## Quick Reference

### Check Mounted Drives
```bash
df -h                    # Show all mounted filesystems
lsblk                    # Show all block devices
mount | grep external     # Show external mounts
```

### Mount/Unmount
```bash
sudo mount /dev/sdb1 /mnt/external_drive    # Mount
sudo umount /mnt/external_drive              # Unmount
```

### Docker Volume Commands
```bash
docker volume ls                              # List volumes
docker-compose config                         # Validate config
docker-compose down && docker-compose up -d   # Restart with new mounts
```

---

## Example: Complete Setup for Large Dataset

```bash
# 1. Mount external drive
sudo mkdir -p /mnt/datasets
sudo mount /dev/sdb1 /mnt/datasets
sudo chown -R jeremy.siburian:gci /mnt/datasets

# 2. Organize directories
mkdir -p /mnt/datasets/{synthetic_train,synthetic_val,checkpoints,results}

# 3. Copy or move data
# (if data is elsewhere, move it here)

# 4. Update docker-compose.yml
# Add volumes:
#   - /mnt/datasets/synthetic_train:/workspace/data/synthetic_train
#   - /mnt/datasets/synthetic_val:/workspace/data/synthetic_val
#   - /mnt/datasets/checkpoints:/workspace/checkpoints
#   - /mnt/datasets/results:/workspace/results

# 5. Restart containers
docker-compose down
docker-compose up -d

# 6. Verify in container
docker exec -it lego_release-jeremy bash
ls -la /workspace/data/
```

---

For more information, see:
- `DOCKER.md` - Docker setup documentation
- `docker-compose.yml` - Current volume configuration

