Steps to run the new omni parser with out the need of docker. Yes we did it :)

1. Installation

   1. Install conda and python
      1.1 Create a venv omni
      command: conda create -n "omni" python==3.12
      1.2 Activate venv omni
      command: conda activate omni

   2. Clone the repo:
      command: git clone https://github.com/ShreyX24/OmniParser.git

   3. install requirements (do not remove gradio)
      command: pip install -r requirements.txt

      3.1 Removed torch and torchvision from requirements.txt, because you need to install the updated version manually
      command: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

      3.2 Intall Cuda Toolkit from Nvidia
      Link: https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local

      3.3 Install jupyter
      command pip install jupyter

2. Navigate to omnitool/omniparserserver and start the server
   command (no there is no .py at the end of omniparserserver): python -m omniparserserver

3. Navigate to omnitool/gradio/app.py and start gradio
   command: python app.py --omniparser_server_url localhost:8000

(You're backend is up and running)

4. Go to root folder i.e. /OmniParser
   4.1 Open demo.ipynb in jupyter notebook
   4.2 Click on Run all
