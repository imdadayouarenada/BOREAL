## **Selenium-Based Automation for Atmospheric Data Retrieval**

---

### **Description**
This project automates the retrieval of atmospheric data from the BOREAL website using Selenium. The script:
1. Configures parameters for extinction, backscatter, and depolarization.
2. Run all the possible combinations of input parameters.
3. Generates multiple realizations to simulate retrieval uncertainty.
4. Saves the results for further analysis.
5. Generate a custom Decision Tree to evaluate input parameters importance.

---

### **Features**
- Automates data input and retrieval.
- Generates uncertainty realizations.
- Saves results in a structured directory.
- Allows customization of input values and error margins.

---

### **Dependencies**
The following Python packages are required:
- **selenium**: Web automation.
- **tqdm**: Progress bar for iterative tasks.
- **numpy**: Array manipulations and data generation.
- **matplotlib**: Plotting distributions and results.
- **scipy**: Advanced scientific computations.
- **graphviz**: Workflow representation.

Make sure Graphviz software is installed on your system (required for the `graphviz` Python package).

---

### **Installation**

#### **Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd <repository-directory>
```

#### **Step 2: Set Up Virtual Environment**
Create and activate a Python virtual environment:
```bash
python3 -m venv boreal-env
source boreal-env/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

#### **Step 3: Install Dependencies**
Install the required Python packages:
```bash
pip install -r requirements.txt
```

Ensure Graphviz is installed:
- On Ubuntu/Debian:
  ```bash
  sudo apt-get install graphviz
  ```
- On MacOS:
  ```bash
  brew install graphviz
  ```
- On Windows:
  Download Graphviz from the [official site](https://graphviz.gitlab.io/_pages/Download/Download_windows.html) and add it to your PATH.

---

### **Usage**
1. **Set Up Input Values**: Update extinction, backscatter, and depolarization parameters in the script.
2. **Run the Script**:
   ```bash
   python script_name.py
   ```
3. **Outputs**:
   - Results will be saved in the specified directory (e.g., `Retrieval_Uncertainty`).

---

### **Directory Structure**
```
project/
│
├── script_name.py         # Main script
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── outputs/               # Folder for saved results
└── README.md              # Project documentation
```

---

### **Customization**
To modify:
- **Input Parameters**: Update the extinction, backscatter, or depolarization dictionaries.
- **Number of Realizations**: Change the value of `n` in the script.
- **Browser Options**: Adjust ChromeDriver options (e.g., headless mode).

---

### **Contributors**
- **Your Name** – Carlotta Gilè

---

### **Contact**
For questions or support, please contact:
- **Email**: carlotta.gile@estudiantat.upc.edu
