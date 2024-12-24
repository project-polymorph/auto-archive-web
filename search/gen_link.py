import os
import yaml
import argparse
from pathlib import Path

def process_results(input_dir: Path = Path('.github/downloader'), 
                   output_file: Path = Path('.github/links.yml'),
                   verbose: bool = False):
    """Process YAML results files and generate consolidated links file.
    
    Args:
        input_dir: Directory containing results.yml files
        output_file: Output path for consolidated links
        verbose: Whether to print detailed progress
    """
    # Initialize dictionary with existing links if file exists
    all_links = {}
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            all_links = yaml.safe_load(f) or {}
    
    duplicate_count = 0
    new_count = 0
    
    # Walk through all subdirectories in input directory
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file == 'results.yml':
                file_path = Path(root) / file
                
                if verbose:
                    print(f"Processing {file_path}")
                
                # Read the results.yml file
                with open(file_path, 'r', encoding='utf-8') as f:
                    results = yaml.safe_load(f)
                
                # Process each result
                for result in results:
                    link = result.get('link')
                    if link:
                        if link in all_links:
                            duplicate_count += 1
                            continue
                        
                        # Create entry for new link
                        all_links[link] = {
                            'title': result.get('title'),
                            'snippet': result.get('snippet'),
                            'is_related': result.get('is_related', 'unknown'),
                        }
                        new_count += 1

    if duplicate_count > 0 or verbose:
        print(f"\nTotal existing links skipped: {duplicate_count}")
    if new_count > 0 or verbose:
        print(f"Total new links added: {new_count}")
        
    # Save the updated links.yml file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(all_links, f, allow_unicode=True, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(description='Generate consolidated links file from results.yml files')
    parser.add_argument('-i', '--input-dir', type=Path, default=Path('.github/downloader'),
                      help='Input directory containing results.yml files')
    parser.add_argument('-o', '--output-file', type=Path, default=Path('.github/links.yml'),
                      help='Output path for consolidated links file')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Print detailed processing information')
    
    args = parser.parse_args()
    process_results(args.input_dir, args.output_file, args.verbose)

if __name__ == '__main__':
    main()
