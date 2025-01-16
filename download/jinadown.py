import os
import subprocess
from pathlib import Path

def download_jina(url, output_dir, title):
    """Download content from URL using Jina AI and save as markdown"""
    try:
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate safe base filename from title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        base_name = safe_title.replace(' ', '_')[:100]

        # Use a specific download directory
        download_dir = os.path.join(output_dir, "download")
        print(f"Creating download directory: {download_dir}")
        if os.path.exists(download_dir):
            for file in os.listdir(download_dir):
                os.remove(os.path.join(download_dir, file))
            os.rmdir(download_dir)
        os.makedirs(download_dir, exist_ok=False)

        # Download using Jina AI endpoint
        jina_url = f"https://r.jina.ai/{url}"
        command = [
            'curl',
            '--location',
            '--no-progress-meter',
            '-v',
            '--insecure',
            jina_url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"curl failed with error: {result.stderr}")
        
        # Save the markdown content
        markdown_content = result.stdout
        new_filename = f"{base_name}.md"
        new_path = os.path.join(output_dir, new_filename)
        
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✓ Successfully saved markdown to {new_path}")
        return True, new_path
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False, str(e) 