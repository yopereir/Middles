import os
from dotenv import load_dotenv
load_dotenv()

MODEL = os.getenv("MODEL")
MODEL_URL = os.getenv("MODEL_URL")
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
ML_FLOW_ENDPOINT = os.getenv("ML_FLOW_ENDPOINT")