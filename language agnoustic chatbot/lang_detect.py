import fasttext
import os

# Use absolute path for reliability
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "lid.176.ftz")

# Load pretrained FastText language model
lang_model = fasttext.load_model(MODEL_PATH)

def detect_language(text):
    prediction = lang_model.predict(text)
    lang_code = prediction[0][0].replace("__label__", "")
    return lang_code
