# Learn-English-By-Comic

## Description  
A comprehensive tool that performs web scraping, OCR (Optical Character Recognition), and text translation to Vietnamese. The project follows a three-step pipeline: web scraping → OCR → word extraction and translation.  

## Installation  

### Dependencies  
Install required packages:  
```bash  
pip install pandas aiohttp beautifulsoup4 Pillow google-generativeai lxml
```
## Workflow

### 1. Web Scraping
- Run `step1_scrapecode.py` to collect images from target websites
- Images will be saved in the designated output directory

### 2. OCR Processing
- Run `step2_ocr.py` to perform optical character recognition on scraped images
- Generates text files containing extracted text

### 3. Word Extraction and Translation
- Run `extractwords.py` to analyze word frequency from OCR output
- Use `trainslate_api.py` to translate text to Vietnamese:
  - Accepts image path
  - Processes OCR text
  - Translates specified text to Vietnamese

## License
[[CC BY-NC 2.5]](https://creativecommons.org/licenses/by-nc/2.5/)
