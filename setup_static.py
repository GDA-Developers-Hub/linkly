import os
import shutil
import stat

# Define the paths
STATIC_ROOT = '/mnt/c/Users/ISMAEL/Desktop/Linkly/staticfiles'
STATIC_DIR = '/mnt/c/Users/ISMAEL/Desktop/Linkly/static'
ADMIN_CSS_DIR = os.path.join(STATIC_DIR, 'admin', 'css')

def ensure_directory(path):
    """Create directory and ensure proper permissions."""
    if os.path.exists(path):
        # Remove directory and its contents
        shutil.rmtree(path)
    
    # Create directory
    os.makedirs(path, exist_ok=True)
    
    # Set permissions (rwxrwxrwx)
    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    print(f"Created directory with full permissions: {path}")

# Create directories with proper permissions
for directory in [STATIC_ROOT, STATIC_DIR, ADMIN_CSS_DIR]:
    ensure_directory(directory)

print("\nStatic directories setup completed!")
print(f"STATIC_ROOT: {STATIC_ROOT}")
print(f"STATIC_DIR: {STATIC_DIR}")
print(f"ADMIN_CSS_DIR: {ADMIN_CSS_DIR}") 