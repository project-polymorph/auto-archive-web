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

def execute_searches(date_dir: Path) -> None:
    """Execute searches for each query in template file."""
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
    """Process JSON search results into daily YAML file."""
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
    """Generate consolidated links.yml from all daily results."""
    gen_link_script = Path(".github/downloader/search/gen_link.py")
    output_file = date_dir / "links.yml"
    
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
    """Process links.yml through check_related.py to classify articles."""
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

def main() -> None:
    """Run the daily update process."""
    # Setup directories
    record_dir = Path(".github/record")
    today = datetime.now().strftime("%Y-%m-%d")
    date_dir = record_dir / today
    search_dir = date_dir / "search_result"
    search_dir.mkdir(parents=True, exist_ok=True)

    # Execute pipeline
    # execute_searches(search_dir)
    # process_daily_results(search_dir, date_dir)
    # links_file = date_dir / "links.yml"
    # generate_consolidated_links(date_dir)
    # process_check_related(links_file)

if __name__ == "__main__":
    main()
