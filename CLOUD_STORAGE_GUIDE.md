# Using Cloud Storage (Google Drive, etc.) with Docker

This guide explains how to use datasets stored on cloud storage services (Google Drive, Dropbox, OneDrive, etc.) with your Docker setup.

**⚠️ Important: This guide uses NO SUDO commands** - everything is installed and run in user space.

---

## Overview

There are two main approaches:
1. **Sync to Local**: Download/sync cloud storage to local directory, then mount into Docker (Recommended - no FUSE needed)
2. **Mount Directly**: Mount cloud storage as filesystem (requires FUSE, may need permissions)
3. **Direct Download**: Download files directly when needed

For large datasets (like your 39GB `synthetic_train.zip`), **syncing to local** is recommended as it:
- Doesn't require FUSE permissions
- Works faster (local access)
- Works offline after initial sync
- No sudo needed

---

## Method 1: Using rclone (Recommended - No sudo)

`rclone` is a powerful tool that can sync or mount many cloud storage services. **We recommend using sync (no FUSE needed)** instead of mount.

### Step 1: Install rclone (No sudo required)

**⚠️ IMPORTANT: Do this on the HOST system (outside Docker container)**

```bash
# Exit Docker container if you're inside it
exit

# On host system (not in Docker)
# Download and install to user directory (no sudo needed)
cd ~
curl https://rclone.org/install.sh | bash

# This installs to ~/.local/bin/rclone
# Add to PATH if not already there:
export PATH="$HOME/.local/bin:$PATH"

# Or manually download binary
mkdir -p ~/bin
cd ~/bin
wget https://github.com/rclone/rclone/releases/latest/download/rclone-v1.65.0-linux-amd64.zip
unzip rclone-*.zip
cd rclone-*-linux-amd64
cp rclone ~/bin/
export PATH="$HOME/bin:$PATH"

# Add to ~/.bashrc to make permanent:
echo 'export PATH="$HOME/bin:$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Step 2: Configure rclone for Google Drive

**On HOST system (outside container):**

```bash
# Make sure you're on the host, not inside Docker
# If inside container, type: exit

# Start configuration
rclone config

# Follow the prompts:
# n) New remote
# name: gdrive (or any name you want)
# Storage: Google Drive (option 15 or type "drive")
# client_id: (press Enter for default)
# client_secret: (press Enter for default)
# scope: 1 (full access)
# root_folder_id: (press Enter for root, or specify folder ID)
# service_account_file: (press Enter to skip)
# y) Yes, this is OK
# n) No, don't configure advanced settings
# y) Yes, auto config (will open browser for authentication)
# y) Yes, this is OK
```

### Step 3: Test the Connection

**On HOST system:**

```bash
# List files in your Google Drive
rclone lsd gdrive:

# List files in a specific folder
rclone lsd gdrive:path/to/datasets

# Copy a file to test
rclone copy gdrive:path/to/file.zip /tmp/
```

### Step 4: Sync Google Drive to Local Directory (Recommended - No FUSE)

**⚠️ On HOST system (outside container):**

**This method downloads files to a local directory on your HOST - no FUSE/mounting needed!**

```bash
# Make sure you're on the host system
# Create local directory on HOST
mkdir -p ~/gdrive_sync

# Sync entire Google Drive (or specific folder)
rclone sync gdrive: ~/gdrive_sync --progress

# Or sync a specific folder (recommended for large datasets)
rclone sync gdrive:datasets ~/gdrive_sync --progress

# Check synced files
ls ~/gdrive_sync
```

**Benefits:**
- ✅ No FUSE permissions needed
- ✅ Works offline after sync
- ✅ Faster access (local files)
- ✅ No sudo required

**To update files later:**
```bash
# Re-sync to get latest changes
rclone sync gdrive:datasets ~/gdrive_sync --progress
```

### Step 4b: Alternative - Mount Google Drive (Requires FUSE)

**Only use this if you need real-time sync and have FUSE permissions:**

```bash
# Create mount point
mkdir -p ~/gdrive_mount

# Mount Google Drive
rclone mount gdrive: ~/gdrive_mount --daemon --vfs-cache-mode writes

# Or mount a specific folder
rclone mount gdrive:datasets ~/gdrive_mount --daemon --vfs-cache-mode writes

# Check if mounted
ls ~/gdrive_mount
```

**Note:** The `--daemon` flag runs it in the background. To unmount:
```bash
fusermount -u ~/gdrive_mount
# Or if that doesn't work:
pkill -f "rclone mount"
```

**Note:** If you get "permission denied" for FUSE, use the sync method (Step 4) instead.

### Step 5: Add to Docker Compose

Edit `docker-compose.yml`:

**If using sync (recommended):**
```yaml
volumes:
  # Mount synced Google Drive (local directory)
  - ~/gdrive_sync:/workspace/data_cloud
  
  # Existing mounts
  - ./data:/workspace/data
  - "./:/workspace"
```

**If using mount:**
```yaml
volumes:
  # Mount Google Drive (FUSE mount)
  - ~/gdrive_mount:/workspace/data_cloud
  
  # Existing mounts
  - ./data:/workspace/data
  - "./:/workspace"
```

### Step 6: Restart Docker

**On HOST system:**

```bash
docker-compose down
docker-compose up -d
```

### Step 7: Access in Container

**Now you can access the synced files INSIDE the container:**

```bash
# Enter container
docker exec -it lego_release-jeremy bash

# Now you're INSIDE the container
# The synced files from ~/gdrive_sync on host are available at /workspace/data_cloud
ls /workspace/data_cloud/  # See your Google Drive files
```

**Summary:**
- ✅ Install/configure rclone: **HOST** (outside container)
- ✅ Sync files: **HOST** (creates ~/gdrive_sync on host)
- ✅ Use files: **INSIDE container** (at /workspace/data_cloud)

---

## Method 2: Using gdrive CLI (Simple Download)

For one-time downloads or when you don't need real-time sync.

### Step 1: Install gdrive (No sudo required)

```bash
# Create bin directory in home
mkdir -p ~/bin

# Download gdrive
cd ~/bin
wget https://github.com/glotlabs/gdrive/releases/download/3.9.0/gdrive_linux-x64.tar.gz
tar -xzf gdrive_linux-x64.tar.gz
chmod +x gdrive

# Or use the newer version directly
wget -O ~/bin/gdrive https://github.com/glotlabs/gdrive/releases/download/3.9.0/gdrive_linux-x64
chmod +x ~/bin/gdrive

# Add to PATH
export PATH="$HOME/bin:$PATH"
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
```

### Step 2: Authenticate

```bash
gdrive about
# This will open a browser for authentication
```

### Step 3: Download Files

```bash
# List files
gdrive list

# Download a file by ID
gdrive download <file-id>

# Download to specific location
gdrive download <file-id> --path /mnt/datasets/

# Download entire folder
gdrive download --recursive <folder-id> --path /mnt/datasets/
```

### Step 4: Use in Docker

Once downloaded, mount the local directory:

```yaml
volumes:
  - /mnt/datasets:/workspace/data_cloud
```

---

## Method 3: Using Google Drive File Stream (Official)

Google Drive File Stream creates a virtual drive that syncs on-demand.

### Step 1: Install Google Drive File Stream (Alternative: Use rclone instead)

**Note:** Google Drive File Stream for Linux typically requires system-level installation. For a no-sudo solution, use **rclone** (Method 1) instead.

If you still want to try:
```bash
# Download (check latest version)
cd ~/Downloads
wget https://dl.google.com/drive-file-stream/GoogleDriveFUSE.deb

# Extract manually (no sudo)
dpkg-deb -x GoogleDriveFUSE.deb ~/gdrive-fuse
# Then manually configure paths
```

**Recommended:** Use rclone (Method 1) which works without sudo.

### Step 2: Authenticate

```bash
google-drive-ocamlfuse ~/gdrive
# Opens browser for authentication
```

### Step 3: Mount

```bash
# Mount to directory
google-drive-ocamlfuse ~/gdrive

# Check
ls ~/gdrive
```

### Step 4: Add to Docker Compose

```yaml
volumes:
  - ~/gdrive:/workspace/data_cloud
```

---

## Method 4: Direct Download Script

For automated downloads when container starts.

### Create Download Script

Create `scripts/download_from_gdrive.sh`:

```bash
#!/bin/bash
# Download large files from Google Drive

# Method 1: Using gdrive CLI
gdrive download <file-id> --path /workspace/data/

# Method 2: Using wget with direct link (if you have it)
# wget --no-check-certificate 'https://drive.google.com/uc?export=download&id=FILE_ID' -O /workspace/data/file.zip

# Method 3: Using rclone
# rclone copy gdrive:datasets/synthetic_train.zip /workspace/data/
```

### Use in Dockerfile or docker-compose

```yaml
# In docker-compose.yml, add as command or in entrypoint
command: bash -c "bash scripts/download_from_gdrive.sh && bash"
```

---

## Method 5: Using Shared Links (Public Files)

If your Google Drive files are shared publicly or you have a direct download link.

### Get Direct Download Link

1. Share file/folder on Google Drive
2. Get shareable link
3. Convert to direct download link:
   - For files: `https://drive.google.com/uc?export=download&id=FILE_ID`
   - Use tools like `gdown` Python package

### Download with gdown

```bash
# Install gdown
pip install gdown

# Download file
gdown https://drive.google.com/uc?id=FILE_ID -O /path/to/save/file.zip

# Or in Python script
import gdown
gdown.download('https://drive.google.com/uc?id=FILE_ID', 'output.zip', quiet=False)
```

### Add to Docker

```yaml
# Mount download directory
volumes:
  - ./downloads:/workspace/downloads
```

Then download inside container or before starting.

---

## Best Practices

### 1. Cache Large Files Locally

For very large datasets (39GB+), download once and cache locally:

```bash
# Create cache directory
mkdir -p ~/datasets_cache

# Download once
rclone copy gdrive:datasets/synthetic_train.zip ~/datasets_cache/

# Mount cache in Docker
# In docker-compose.yml:
volumes:
  - ~/datasets_cache:/workspace/data_cache
```

### 2. Use Read-Only Mounts for Safety

```yaml
volumes:
  - ~/gdrive_mount:/workspace/data_cloud:ro  # Read-only
```

### 3. Sync Only What You Need

Instead of mounting entire Google Drive, sync specific folders:

```bash
# Sync only datasets folder
rclone sync gdrive:datasets ~/local_datasets --progress
```

### 4. Handle Large Files

For files >15GB, Google Drive may require special handling:

```bash
# Use rclone with resume support
rclone copy gdrive:large_file.zip ~/datasets/ --progress --transfers 1

# Or use gdown with resume
gdown --resume https://drive.google.com/uc?id=FILE_ID
```

### 5. Background Sync (No sudo)

Keep rclone mount running in background:

**Option A: Use screen or tmux**
```bash
# Start in screen session
screen -S rclone
rclone mount gdrive: ~/gdrive_mount --vfs-cache-mode writes
# Press Ctrl+A then D to detach

# Reattach later
screen -r rclone
```

**Option B: Use nohup**
```bash
# Run in background
nohup rclone mount gdrive: ~/gdrive_mount --vfs-cache-mode writes > ~/rclone.log 2>&1 &

# Check if running
ps aux | grep rclone

# Stop it
pkill -f "rclone mount"
```

**Option C: User systemd (if available without sudo)**
```bash
# Create user systemd service directory
mkdir -p ~/.config/systemd/user

# Create service file
nano ~/.config/systemd/user/rclone-gdrive.service
```

```ini
[Unit]
Description=rclone mount Google Drive
After=network.target

[Service]
Type=simple
ExecStart=%h/.local/bin/rclone mount gdrive: %h/gdrive_mount --vfs-cache-mode writes
Restart=on-failure

[Install]
WantedBy=default.target
```

```bash
# Enable and start (user systemd, no sudo)
systemctl --user enable rclone-gdrive
systemctl --user start rclone-gdrive
```

---

## Complete Example: docker-compose.yml

```yaml
version: '3.8'

services:
  lego_release:
    # ... other config ...
    volumes:
      # Local project data
      - ./data:/workspace/data
      
      # Google Drive (mounted via rclone)
      - ~/gdrive_mount/datasets:/workspace/data_cloud
      
      # Or cached downloads
      - ~/datasets_cache:/workspace/data_cache
      
      # Results
      - ./results:/workspace/results
      
      # Project code
      - "./:/workspace"
```

---

## Troubleshooting

### rclone Mount Not Working

**If FUSE is not available, use rclone copy/sync instead of mount:**

```bash
# Instead of mounting, sync files locally
rclone sync gdrive:datasets ~/local_datasets --progress

# Then mount the local directory in Docker
# In docker-compose.yml:
volumes:
  - ~/local_datasets:/workspace/data_cloud
```

**Check mount status:**
```bash
# Check if rclone is running
ps aux | grep rclone

# Check logs
rclone mount gdrive: ~/gdrive_mount --vfs-cache-mode writes -v
```

### Permission Denied (FUSE)

**If you can't use FUSE without sudo, use rclone copy/sync instead:**

```bash
# Sync files to local directory (no FUSE needed)
rclone sync gdrive:datasets ~/gdrive_sync --progress

# This creates a local copy that you can mount in Docker
# Update docker-compose.yml:
volumes:
  - ~/gdrive_sync:/workspace/data_cloud
```

**Alternative: Use rclone without mounting**
- Use `rclone copy` or `rclone sync` to download files
- Then use the local directory in Docker
- No FUSE/mounting required

### Slow Performance

- Use `--vfs-cache-mode writes` for better performance
- Cache frequently accessed files locally
- Use `rclone sync` instead of mount for one-time operations

### Google Drive Quota Exceeded

- Check your Google Drive storage quota
- Consider using service account for higher limits
- Use `rclone` with `--drive-shared-with-me` for shared folders

---

## Comparison of Methods

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **rclone mount** | Real-time sync, many services | Requires FUSE, setup needed | Frequent access, multiple services |
| **gdrive CLI** | Simple, direct | One-time download | Occasional downloads |
| **gdown** | Python-friendly | Requires direct links | Python scripts, public files |
| **Direct download** | No setup | Manual, no sync | One-time use |
| **File Stream** | Official, integrated | Linux support limited | Windows/Mac primarily |

---

## Quick Start: rclone for Google Drive (No sudo)

**⚠️ IMPORTANT: Steps 1-4 are done on HOST (outside container). Step 7 is inside container.**

```bash
# ============================================
# ON HOST SYSTEM (outside Docker container)
# ============================================

# 1. Install (no sudo)
cd ~
curl https://rclone.org/install.sh | bash
export PATH="$HOME/.local/bin:$PATH"

# 2. Configure
rclone config
# Follow prompts, choose Google Drive

# 3. Test
rclone lsd gdrive:

# 4. Sync to local (no FUSE needed, recommended)
mkdir -p ~/gdrive_sync
rclone sync gdrive:datasets ~/gdrive_sync --progress

# 5. Add to docker-compose.yml (edit the file)
# Add this line under volumes:
#   - ~/gdrive_sync:/workspace/data_cloud

# 6. Restart Docker
docker-compose down && docker-compose up -d

# ============================================
# NOW INSIDE CONTAINER
# ============================================

# 7. Enter container and use files
docker exec -it lego_release-jeremy bash

# Now you're INSIDE the container
ls /workspace/data_cloud/  # See your synced Google Drive files
```

---

## Alternative: Other Cloud Services

### Dropbox

```bash
# Install dropbox-cli or use rclone
rclone config
# Choose Dropbox (option 9)
```

### OneDrive

```bash
# Use rclone
rclone config
# Choose OneDrive (option 18)
```

### AWS S3 / Azure Blob

```bash
# Use rclone or native tools
rclone config
# Choose S3 (option 5) or Azure (option 2)
```

---

For more details, see:
- `EXTERNAL_DRIVE_GUIDE.md` - Local drive mounting
- `DOCKER.md` - Docker setup

