# auto-archive-web

python .github/downloader/web_cleanup/config/new_config.py .github/record/2024-12-24/downloads/results.json .github/record/2024-12-24/downloads/page.yml
python .github/downloader/web_cleanup/config/add_meta.py .github/record/2024-12-24/downloads/page.yml

python .github/downloader/web_cleanup/batch.py  .github/record/2024-12-24/downloads/ .github/record/2024-12-24/cleaned .github/downloader/web_cleanup/cleaner/clean_cheerio.js HTML_CLEANER_CONFIG=.github/downloader/web_cleanup/cleaner/configs/default.json 

python .github/downloader/web_cleanup/batch.py  .github/record/2024-12-24/cleaned .github/record/2024-12-24/markdown .github/downloader/web_cleanup/markdown/html2md.js

python .github/downloader/web_cleanup/ai/process_dir.py .github/record/2024-12-24/markdown .github/record/2024-12-24/ready .github/downloader/web_cleanup/ai/prompt/clean.template
