from dotenv import load_dotenv
load_dotenv() # before other imports so os.getenv will include .env values

import sys
import os
sys.path.insert(0, os.getcwd()) # allow modules in subdirectories to be imported

from app import app

if __name__ == '__main__':
  PORT = int(os.getenv('PORT', 5000))
  app.run(host="localhost", port=PORT, debug=True)

