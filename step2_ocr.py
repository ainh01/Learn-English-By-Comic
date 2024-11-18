import os
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pathlib import Path
from math import ceil

 

TIMETOWAIT = 10

API_KEYS = [
	'AIzaSyBj6ykG4KrQq2bWH53F8OJY_zI3lm4yx9A',
	'AIzaSyBcFJ9NYxW_QlXRNvhGasrLf4BONQUL5-0',
	'AIzaSyArJ2-XTI8kcV_5C_6wPq_j7ILmhA_sNhw',
	'AIzaSyBDo9pozi-OfKXBDDcmfMi4YnopuJNbbSc',
	'AIzaSyADGpLGiHnxjGWgUHPf-3O4GVUvTiiEEsw',
	'AIzaSyDOgLddotsVp5A8_Ba5sbUfAGNAp4t3AEc',
	'AIzaSyCp6RSdu3S2-gFxvhNyRV5HhferUCGaPec',
	'AIzaSyCU-5TsLClGCd-aUbEBXYCe-RXl1PzHxWc',
	'AIzaSyC9YTzLepkJTqqnoJQUkgb78wS9_IevVCQ',
	'AIzaSyC0h9gimW6fz2nOBUB9MjxGciEF_K1fQY8',
]


SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

class APIManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.num_keys = len(api_keys)
        self.lock = threading.Lock()

        self.last_text_request_time = {key: 0 for key in self.api_keys}

    def get_api_key_for_upload(self, index):
        """
        Assign API keys for image uploads without rate limiting.
        """
        return self.api_keys[index % self.num_keys]

    def wait_for_text_request(self, api_key):
        """
        Ensure that each API key waits at least TIMETOWAIT seconds between text requests.
        """
        with self.lock:
            current_time = time.time()
            elapsed_time = current_time - self.last_text_request_time[api_key]
            if elapsed_time < TIMETOWAIT:
                wait_time = TIMETOWAIT - elapsed_time
                time.sleep(wait_time)

            self.last_text_request_time[api_key] = time.time()


class HandwritingOCR:
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.api_keys = self.api_manager.api_keys
        self.num_keys = self.api_manager.num_keys
        self.setup_directories()
        self.error_log = open('ocr_errors.log', 'a', encoding='utf-8')
        self.lock = threading.Lock()

        max_workers = min(ceil(self.num_keys * 2), 50)  
        self.upload_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.ocr_executor = ThreadPoolExecutor(max_workers=max_workers)

    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs('./ocr_results/', exist_ok=True)
        os.makedirs('./scraped_images/', exist_ok=True)  

    def upload_and_store(self, image_path, api_key, retries=3, backoff_factor=2):
        """Upload image and return uploaded data with retries."""
        attempt = 0
        while attempt < retries:
            try:
                genai.configure(api_key=api_key)
                uploaded_file = genai.upload_file(image_path)
                return {
                    'file': uploaded_file,
                    'path': image_path,
                    'api_key': api_key  
                }
            except Exception as e:
                attempt += 1
                wait_time = backoff_factor ** attempt
                error_message = f'[{datetime.now()}] Attempt {attempt}: Failed to upload {os.path.basename(image_path)}: {str(e)}\n'
                with self.lock:
                    self.error_log.write(error_message)
                print(error_message)
                if attempt < retries:
                    time.sleep(wait_time)
                else:
                    return None


    def process_text(self, uploaded_data, retries=3, backoff_factor=2):
        """Process text for an uploaded image with retries."""
        attempt = 0
        while attempt < retries:
            try:
                
                api_key = uploaded_data['api_key']
                self.api_manager.wait_for_text_request(api_key)
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash", 
                                             safety_settings=SAFETY_SETTINGS)
                
                response = model.generate_content(
                    [uploaded_data['file'], 
                     "Please extract and transcribe any text in this image, including handwritten text."],
                    safety_settings=SAFETY_SETTINGS,
                )
                
                if response.text:
                    output_path = os.path.join(
                        './ocr_results/', 
                        os.path.splitext(os.path.basename(uploaded_data['path']))[0] + '.txt'
                    )
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    return True
                else:
                    raise Exception('No text extracted from image.')
                            
            except Exception as e:
                attempt += 1
                error_message = f'[{datetime.now()}] Attempt {attempt}: Failed to process text for {os.path.basename(uploaded_data["path"])}: {str(e)}\n'
                with self.lock:
                    self.error_log.write(error_message)
                print(error_message)
                if attempt < retries:
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
                else:
                    return False


    def process_images_in_batches(self, batch_size=100):
        """Process images in batches with parallel uploading and OCR processing."""
        image_files = os.listdir('./scraped_images/')
        total_images = len(image_files)
        print(f"Total images to process: {total_images}")
        
        
        batches = [image_files[i:i + batch_size] for i in range(0, len(image_files), batch_size)]
        
        for batch_num, batch in enumerate(batches):
            print(f"\nProcessing batch {batch_num + 1}/{len(batches)} with {len(batch)} images")
            uploaded_batch = []
            

            mapped_images = [
                {
                    'image_file': image_file,
                    'api_key': self.api_manager.get_api_key_for_upload(idx)
                }
                for idx, image_file in enumerate(batch)
            ]
            

            futures_upload = {
                self.upload_executor.submit(
                    self.upload_and_store,
                    os.path.join('./scraped_images/', mapped_image['image_file']),
                    mapped_image['api_key']
                ): mapped_image['image_file']
                for mapped_image in mapped_images
            }
            

            for future in as_completed(futures_upload):
                image_file = futures_upload[future]
                try:
                    uploaded_data = future.result()
                    if uploaded_data:
                        uploaded_batch.append(uploaded_data)
                        print(f"Successfully uploaded: {image_file}")
                except Exception as e:
                    error_message = f'[{datetime.now()}] Failed to upload {image_file}: {str(e)}\n'
                    with self.lock:
                        self.error_log.write(error_message)
                    print(error_message)
            
            print(f"Upload phase completed for batch {batch_num + 1}. Starting OCR processing.")
            

            futures_ocr = {
                self.ocr_executor.submit(self.process_text, uploaded_data): uploaded_data['path']
                for uploaded_data in uploaded_batch
            }
            

            ocr_success_count = 0
            for future in as_completed(futures_ocr):
                image_path = futures_ocr[future]
                try:
                    success = future.result()
                    if success:
                        ocr_success_count += 1
                        print(f"OCR successful for: {os.path.basename(image_path)}")
                except Exception as e:
                    error_message = f'[{datetime.now()}] Failed OCR for {os.path.basename(image_path)}: {str(e)}\n'
                    with self.lock:
                        self.error_log.write(error_message)
                    print(error_message)
            
            print(f"OCR phase completed for batch {batch_num + 1}. {ocr_success_count}/{len(uploaded_batch)} successful.")
        
        print("\nAll batches processed.")

    def shutdown_executors(self):
        """Shut down the ThreadPoolExecutors."""
        self.upload_executor.shutdown(wait=True)
        self.ocr_executor.shutdown(wait=True)
        self.error_log.close()

class HandwritingOCREntryPoint:
    def __init__(self):
        api_manager = APIManager(API_KEYS)
        self.ocr_processor = HandwritingOCR(api_manager)
    
    def run(self, batch_size=100):
        try:
            self.ocr_processor.process_images_in_batches(batch_size=batch_size)
        finally:
            self.ocr_processor.shutdown_executors()

if __name__ == "__main__":
    entry_point = HandwritingOCREntryPoint()
    entry_point.run(batch_size=100)
