import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
from typing import List, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin


logging.basicConfig(
    filename='download_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


ACCEPTED_FORMATS = {'.jpg', '.png', '.jpeg', '.webp'}
BASE_URL = 'https://xkcd.com'
CONCURRENT_REQUESTS = 200  
SAVE_DIR = './scraped_images/'
os.makedirs(SAVE_DIR, exist_ok=True)

async def process_image(img_data: bytes, page_number: int, image_extension: str) -> bool:
    """Process and save an image using a thread pool to avoid blocking."""
    def save_image():
        try:
            img = Image.open(BytesIO(img_data))
            if img.width < 100 or img.height < 100:
                raise ValueError('Image size below minimum requirement')
            image_filename = f'comic_{page_number}{image_extension}'
            img.save(os.path.join(SAVE_DIR, image_filename))
            return True
        except Exception as e:
            logging.error(f'Error processing image {page_number}: {str(e)}')
            return False


    with ThreadPoolExecutor() as pool:
        return await asyncio.get_event_loop().run_in_executor(pool, save_image)

async def fetch_page(session: aiohttp.ClientSession, page_number: int) -> Tuple[int, bool]:
    """Fetch and process a single comic page."""
    url = f'{BASE_URL}/{page_number}/'
    try:
        async with session.get(url) as response:
            if response.status != 200:
                raise aiohttp.ClientError(f'HTTP {response.status}')
            
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            comic_div = soup.select_one('#comic > img')
            
            if not comic_div:
                raise ValueError('Comic image not found')

            image_url = comic_div['src']
            if image_url.startswith('//'):
                image_url = 'https:' + image_url

            image_extension = os.path.splitext(image_url)[1].lower()
            if image_extension not in ACCEPTED_FORMATS:
                raise ValueError(f'Unaccepted image format: {image_extension}')


            async with session.get(urljoin(BASE_URL, image_url)) as img_response:
                if img_response.status != 200:
                    raise aiohttp.ClientError(f'Image HTTP {img_response.status}')
                
                img_data = await img_response.read()
                success = await process_image(img_data, page_number, image_extension)
                return page_number, success

    except Exception as e:
        logging.error(f'Failed to process page {page_number}: {str(e)}')
        return page_number, False

async def main(start_page: int, end_page: int):
    """Main async function to coordinate the scraping process."""
    async with aiohttp.ClientSession() as session:
        tasks = []

        for chunk_start in range(start_page, end_page + 1, CONCURRENT_REQUESTS):
            chunk_end = min(chunk_start + CONCURRENT_REQUESTS, end_page + 1)
            chunk = range(chunk_start, chunk_end)
            

            chunk_tasks = [fetch_page(session, page_num) for page_num in chunk]

            results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            

            for page_num, success in results:
                if success:
                    print(f'Successfully downloaded comic {page_num}')
                else:
                    print(f'Failed to download comic {page_num}')
            

            await asyncio.sleep(1)

if __name__ == "__main__":
    start_time = time.time()
    

    START_PAGE = 1
    END_PAGE = 3004
    

    asyncio.run(main(START_PAGE, END_PAGE))
    
    elapsed_time = time.time() - start_time
    print(f'Total time taken: {elapsed_time:.2f} seconds')
