import os
import google.generativeai as genai
from typing import Optional
from google.generativeai.types import HarmCategory, HarmBlockThreshold


os.environ['GOOGLE_API_KEY'] = 'AIzaSyBj6ykG4KrQq2bWH53F8OJY_zI3lm4yx9A'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])


SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}


def translate_with_context(PATH_IMAGE: str, PATH_TXT: str, TO_TRANSLATE: str) -> Optional[str]:
    """
    Translates a specific term/phrase using context from both an image and text file.
    
    Args:
        PATH_IMAGE (str): Path to the image file
        PATH_TXT (str): Path to the text file
        TO_TRANSLATE (str): Specific term/phrase to translate
    
    Returns:
        str: Translation response from Gemini model
        None: If an error occurs during processing
    
    Raises:
        FileNotFoundError: If either image or text file is not found
        Exception: For other unexpected errors
    """
    try:
        if not os.path.exists(PATH_IMAGE):
            raise FileNotFoundError(f"Image file not found: {PATH_IMAGE}")
        if not os.path.exists(PATH_TXT):
            raise FileNotFoundError(f"Text file not found: {PATH_TXT}")
        

        image_file = genai.upload_file(PATH_IMAGE)
        

        with open(PATH_TXT, 'r', encoding='utf-8') as file:
            TXT_VALUE = file.read().strip()
        

        model = genai.GenerativeModel("gemini-1.5-flash", safety_settings=SAFETY_SETTINGS)
        

        prompt = f"I am Vietnamese so you REPONSE TO ME USING VIETNAMESE. Your task is to translate the word \"{TO_TRANSLATE}\" into Vietnamese which is found in [{TXT_VALUE}] and have the background in the image so that user can understand the word in Vietnamese. And then you reason why \"{TO_TRANSLATE}\" mean that but not other meaning."
        

        response = model.generate_content([image_file, "\n\n", prompt])
        
        return response.text
    
    except FileNotFoundError as e:
        print(f"File error: {str(e)}")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

print(translate_with_context(r"C:\Users\binh\Desktop\ainhscrape\scraped_images\comic_1150.png",
                           r"C:\Users\binh\Desktop\ainhscrape\ocr_results\comic_1150.txt",
                           "STORAGE BUSINESS"))

