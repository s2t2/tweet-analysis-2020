
import os

from dotenv import load_dotenv

load_dotenv()

MU = float(os.getenv("MU", default="1"))
ALPHA_PERCENTILE = float(os.getenv("ALPHA_PERCENTILE", default="0.999"))

LAMBDA_00 = float(os.getenv("LAMBDA_1", default="0.61")) # TODO: interpretation of what this means
LAMBDA_11 = float(os.getenv("LAMBDA_2", default="0.83")) # TODO: interpretation of what this means
