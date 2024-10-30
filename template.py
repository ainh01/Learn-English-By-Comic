import os
import google.generativeai as genai


os.environ['GOOGLE_API_KEY'] = 'AIzaSyCCmKnCi3Iu385hIztzELbuKMvp9ai7DEU'
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

myfile = genai.upload_file("Cajun_instruments.png")
print(f"{myfile=}")

model = genai.GenerativeModel("gemini-1.5-flash")
result = model.generate_content(
    [myfile, "\n\n", "what funny about this meme?"]
)
print(f"{result.text=}")
