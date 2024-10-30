import pandas as pd
import os
import re
from collections import defaultdict  

word_frequencies = defaultdict(int)


for ocr_file in os.listdir('./ocr_results/'):

    if not ocr_file.endswith('.txt'):
        continue
        
    ocr_path = os.path.join('./ocr_results/', ocr_file)
    
    try:
        with open(ocr_path, 'r', encoding='utf-8') as f:

            text = f.read()
            

            words = text.split()  
            for word in words:

                word_clean = re.sub(r'[^a-zA-Z0-9]', '', word.lower())
                

                if len(word_clean) >= 2:
                    word_frequencies[word_clean] += 1
                    
    except Exception as e:
        print(f'Error processing {ocr_file}: {str(e)}')
        continue

df = pd.DataFrame([
    {'word': word, 'frequency': freq}
    for word, freq in word_frequencies.items()
])


df.sort_values(['frequency', 'word'], 
               ascending=[False, True], 
               inplace=True)


df.to_csv('extracted_words.csv', index=False)
