import json
import yaml
from datetime import datetime
import re
import glob
import os
import argparse

def parse_date(date_str):
    """Parse various Chinese date formats to a standard format"""
    if not date_str:
        return None
        
    # Remove common Chinese characters
    date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '').strip()
    
    # Try to parse the date
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %d, %Y')
    except:
        return None

def clean_snippet(snippet):
    """Clean and format the snippet text"""
    # Remove extra whitespace
    snippet = ' '.join(snippet.split())
    
    # Remove common unwanted patterns
    snippet = re.sub(r'\n时长：.*?\n发布时间：', ' ', snippet)
    
    return snippet

def merge_news(json_files, yaml_file):
    # Initialize empty list for all articles
    all_articles = []
    processed_links = set()
    process_count = 0  # Counter for processed articles
    skip_count = 0     # Counter for skipped articles
    
    # Load existing YAML if it exists
    if os.path.exists(yaml_file):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            existing_articles = yaml.safe_load(f) or []
            all_articles.extend(existing_articles)
            processed_links = {article['link'] for article in existing_articles}
    
    # Process each JSON file
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract news articles from each file
        for page in data['results']:
            # Handle both old format with 'organic' and new format with 'news'
            articles = page.get('organic', page.get('news', []))
            
            for article in articles:
                # Skip non-news entries or existing links
                if (not article.get('title') or 
                    not article.get('snippet') or 
                    article['link'] in processed_links):
                    print(f"skip {article['link']}")
                    skip_count += 1  # Increment skip counter
                    continue
                    
                # Create article entry
                entry = {
                    'title': article['title'],
                    'link': article['link'],
                    'snippet': clean_snippet(article['snippet'])
                }
                
                # Add date if available
                date = parse_date(article.get('date'))
                if date:
                    entry['snippet'] = f"{date} — {entry['snippet']}"
                
                all_articles.append(entry)
                processed_links.add(article['link'])
                process_count += 1  # Increment process counter
    
    print(f"Processed {process_count} articles, skipped {skip_count} articles")
    
    # Write to YAML file
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(all_articles, f, allow_unicode=True, sort_keys=False)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Merge JSON news files into YAML')
    parser.add_argument('-i', '--input-dir', required=True,
                      help='Directory containing input JSON files')
    parser.add_argument('-o', '--output-dir', required=True,
                      help='Directory for output YAML file')
    args = parser.parse_args()

    # Validate directories
    if not os.path.isdir(args.input_dir):
        raise ValueError(f"Input directory does not exist: {args.input_dir}")
    os.makedirs(args.output_dir, exist_ok=True)

    # Find all JSON files in the input directory
    json_files = glob.glob(os.path.join(args.input_dir, '*.json'))
    if not json_files:
        print(f"No JSON files found in {args.input_dir}")
        return

    # Set output YAML path
    yaml_file = os.path.join(args.output_dir, 'results.yml')
    
    # Merge news files
    merge_news(json_files, yaml_file)

if __name__ == '__main__':
    main()