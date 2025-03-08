# Install Omni Parser without Docker

Yes, we did it! :)

## Steps to Run the New Omni Parser Without Docker

### 1. Installation

#### 1.1 Install Conda and Python

- Create a virtual environment named `omni`:
  ```sh
  conda create -n "omni" python==3.12
  ```
- Activate the virtual environment:
  ```sh
  conda activate omni
  ```

#### 1.2 Clone the Repository
```sh
git clone https://github.com/ShreyX24/Custom-Omni.git
```

#### 1.3 Install Requirements (Do not remove Gradio)
```sh
pip install -r requirements.txt
```

- **Note:** `torch` and `torchvision` have been removed from `requirements.txt`. Install the updated versions manually:
  ```sh
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
  ```

- **Install CUDA Toolkit from NVIDIA**  
  [Download CUDA Toolkit](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local)

- **Install Jupyter**
  ```sh
  pip install jupyter
  ```

---

### 2. Start Omni Parser Server
Navigate to `omnitool/omniparserserver` and start the server:
```sh
python -m omniparserserver
```

*(Note: There is no `.py` at the end of `omnibackendserver`)*

---

### 3. Start Gradio UI
Navigate to `omnitool/gradio/app.py` and start Gradio:
```sh
python app.py --omniparser_server_url localhost:8000
```

*(Your backend is up and running!)*

---

### 4. Run the Demo
Navigate to the root folder `/OmniParser`:

#### 4.1 Open Jupyter Notebook
```sh
jupyter notebook
```

#### 4.2 Open `demo.ipynb` and Click **Run All**

---

You're all set! 🎉
