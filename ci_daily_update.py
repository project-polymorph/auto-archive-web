"""Daily news update script for automated news collection and processing.

This script performs three main tasks:
1. Executes news searches using queries from a template file
2. Processes JSON results into daily YAML files
3. Consolidates all daily results of today into a master links.yml file

Directory structure:
    .github/
    ├── prompts/
    │   └── search.md.template    # Contains search queries
    ├── record/
    │   └── YYYY-MM-DD/          # Daily results directory
    │       ├── search_result/    # Raw JSON search results
    │       └── results.yml       # Processed daily results
    ├── links.yml                 # Consolidated links file
    └── downloader/
        └── search/
            ├── serper.py         # Search execution script
            ├── results.py        # Results processing script
            └── gen_link.py       # Link consolidation script
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

def output_exists(paths) -> bool:
    """Check if output files/directories exist."""
    if isinstance(paths, (str, Path)):
        paths = [paths]
    return all(Path(p).exists() for p in paths)

def execute_searches(date_dir: Path) -> None:
    search_dir = date_dir / "search_result"
    if output_exists(search_dir) and any(search_dir.iterdir()):
        print(f"Search results already exist in {search_dir}, skipping...")
        return

    template_path = Path(".github/prompts/search.md.template")
    script_path = Path(".github/downloader/search/serper.py")
    
    # Read search queries
    with open(template_path, 'r', encoding='utf-8') as file:
        queries = file.readlines()

    # Execute each search query
    for query in queries:
        query = query.strip()
        if query:
            output_file = date_dir / f"{query.replace(' ', '_')}_zh-cn_cn_search.json"
            subprocess.run(["python3", script_path, query, "--endpoint", "/news", "--output", output_file], check=True)

    print(f"Search results saved in {date_dir}")

def process_daily_results(search_dir: Path, output_dir: Path) -> None:
    results_file = output_dir / "results.yml"
    if output_exists(results_file):
        print(f"Daily results already exist in {results_file}, skipping...")
        return

    results_script = Path(".github/downloader/search/results.py")
    
    try:
        subprocess.run([
            "python3", results_script,
            "-i", str(search_dir),
            "-o", str(output_dir)
        ], check=True)
        print(f"Daily results processed and saved to {output_dir / 'results.yml'}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing daily results: {e}")
        raise

def generate_consolidated_links(date_dir: Path) -> None:
    output_file = date_dir / "links.yml"
    if output_exists(output_file):
        print(f"Consolidated links already exist in {output_file}, skipping...")
        return

    gen_link_script = Path(".github/downloader/search/gen_link.py")
    
    try:
        subprocess.run([
            "python3", gen_link_script,
            "-i", str(date_dir),
            "-o", str(output_file),
            "-v"
        ], check=True)
        print(f"Consolidated links saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating consolidated links: {e}")
        raise

def process_check_related(input_file: Path) -> None:
    if not output_exists(input_file):
        print(f"Input file {input_file} not found, skipping...")
        return

    check_related_script = Path(".github/downloader/ai/check_related.py")
    template_path = Path(".github/prompts/check_related.md.template")
    gen_struct_path = Path(".github/scripts/ai/gen_struct.py")
    
    try:
        subprocess.run([
            "python3", check_related_script,
            "-i", str(input_file),
            "-t", str(template_path),
            "-g", str(gen_struct_path)
        ], check=True)
        print(f"Links processed and classified in {input_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error classifying links: {e}")
        raise

def download_webpage(links_file: Path, date_dir: Path) -> None:
    """Download webpage content for links in links.yml."""
    download_script = Path(".github/downloader/download/download.py")
    output_dir = date_dir / "downloads"
    if output_exists(output_dir):
        print(f"Daily results already exist in {output_dir}, skipping...")
        return
    try:
        subprocess.run([
            "python3", download_script,
            "--yaml-path", str(links_file),
            "--output-dir", str(output_dir),
            "--download-type", "webpage",
            "--pattern", ".*"
        ], check=True)
        print(f"Webpages downloaded to {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading webpages: {e}")
        raise

def process_webpages(date_dir: Path) -> None:
    """Process downloaded webpages through cleanup pipeline."""
    downloads_dir = date_dir / "downloads"
    cleaned_dir = date_dir / "cleaned" 
    markdown_dir = date_dir / "markdown"
    ready_dir = date_dir / "ready"
    
    try:
        # Configure new settings
        subprocess.run([
            "python3", ".github/downloader/web_cleanup/config/new_config.py",
            str(downloads_dir / "results.json"),
            str(downloads_dir / "page.yml")
        ], check=True)

        # Add metadata
        subprocess.run([
            "python3", ".github/downloader/web_cleanup/config/add_meta.py",
            str(downloads_dir / "page.yml")
        ], check=True)

        # Clean HTML
        subprocess.run([
            "python3", ".github/downloader/web_cleanup/batch.py",
            str(downloads_dir),
            str(cleaned_dir),
            ".github/downloader/web_cleanup/cleaner/clean_cheerio.js"
        ], env={
            "HTML_CLEANER_CONFIG": ".github/downloader/web_cleanup/cleaner/configs/default.json"
        }, check=True)

        # Convert to Markdown
        subprocess.run([
            "python3", ".github/downloader/web_cleanup/batch.py",
            str(cleaned_dir),
            str(markdown_dir),
            ".github/downloader/web_cleanup/markdown/html2md.js"
        ], check=True)

        # Process with AI
        subprocess.run([
            "python3", ".github/downloader/web_cleanup/ai/process_dir.py",
            str(markdown_dir),
            str(ready_dir),
            ".github/downloader/web_cleanup/ai/prompt/clean.template"
        ], check=True)

        # Copy to workspace
        subprocess.run([
            "python3", ".github/downloader/file_processor.py",
            str(date_dir),
            "workspace"
        ], check=True)

        print(f"Webpages processed and saved to {ready_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing webpages: {e}")
        raise

def main() -> None:
    """Run the daily update process."""
    # Setup directories
    record_dir = Path(".github/record")
    today = datetime.now().strftime("%Y-%m-%d")
    date_dir = record_dir / today
    search_dir = date_dir / "search_result"
    search_dir.mkdir(parents=True, exist_ok=True)

    # Execute pipeline
    execute_searches(search_dir)
    process_daily_results(search_dir, date_dir)
    links_file = date_dir / "links.yml"
    generate_consolidated_links(date_dir)
    process_check_related(links_file)
    download_webpage(links_file, date_dir)
    process_webpages(date_dir)

if __name__ == "__main__":
    main()
