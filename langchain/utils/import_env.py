import os
from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("MODEL")
MODEL_API_KEY = os.getenv("MODEL_API_KEY")