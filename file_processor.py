import os
import shutil
import argparse
from pathlib import Path

def is_valid_cleaned_file(file_path):
    """Check if a file is valid by reading its content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Check if file is not empty and doesn't contain error messages
            if content.strip() and content.strip() not in ['太长', '爬取错误']:
                return True
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return False

def process_files(source_dir, target_dir):
    """Process and copy valid files from source to target directory."""
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)
    # mkdir target_dir if not exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Process ready directory
    ready_dir = source_dir /  'ready'
    if not ready_dir.exists():
        print(f"Ready directory not found: {ready_dir}")
        return
    
    # Copy valid files from ready directory
    for file_path in ready_dir.glob('*.md'):
        if is_valid_cleaned_file(file_path):
            target_file = target_dir / file_path.name
            try:
                shutil.copy2(file_path, target_file)
                print(f"Copied: {file_path.name}")
            except Exception as e:
                print(f"Error copying {file_path}: {e}")
    
    # Move page.yml if it exists
    downloads_dir = source_dir / 'downloads'
    page_yml = downloads_dir / 'page.yml'
    if page_yml.exists():
        try:
            shutil.copy2(page_yml, target_dir / 'page.yml')
            print("Moved page.yml to target directory")
        except Exception as e:
            print(f"Error moving page.yml: {e}")

def main():
    parser = argparse.ArgumentParser(description='Process and copy cleaned files')
    parser.add_argument('source_dir', help='Source directory path')
    parser.add_argument('target_dir', help='Target directory path')
    
    args = parser.parse_args()
    
    process_files(args.source_dir, args.target_dir)

if __name__ == '__main__':
    main() 