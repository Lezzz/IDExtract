# Romanian ID Card Processor 📝

This application automates the processing of Romanian ID cards (buletine), extracting information such as name, address, and personal numerical code (CNP). It offers two processing methods: local OCR with Tesseract (basic implementation) or cloud processing using GPT-4o-mini.

## System Requirements 💻

- Python 3.8 or newer
- Windows, Linux, or MacOS
- ~2GB free RAM for batch processing

## Installation 🔧

1. **Clone the repository** or download the Python script

2. **Install required Python packages**:
```bash
pip install pillow==10.2.0
pip install pytesseract==0.3.10
pip install pandas==2.2.0
pip install openpyxl==3.1.2
pip install requests==2.31.0
pip install tk==0.1.0
pip install numpy==1.26.3
pip install opencv-python==4.9.0.80
pip install openai==1.31.0
```

3. **Install Tesseract OCR** (only needed if using Tesseract method):

- **Windows**: 
  - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
  - Install and note installation path (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`)
  - Add to PATH or modify the path in the script

- **Linux**:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ron
```

- **MacOS**:
```bash
brew install tesseract
brew install tesseract-lang
```

## Usage 🚀

1. **Launch the application**:
```bash
python id_card_processor.py
```

2. **Choose processing method**:
   - **Tesseract OCR**: Local processing (faster but less accurate currently)
   - **GPT-4o-mini**: Cloud processing (requires OpenAI API key, more accurate)

3. **If using GPT-4o-mini**:
   - Enter your OpenAI API key in the dedicated field
   - You can get an API key from: https://platform.openai.com/api-keys

4. **Select the directory** with ID card images (.jpg, .jpeg, or .png)

5. **Choose location** for the output Excel file

6. **Click "Process ID Cards"** and wait for processing

## Important Notes ⚠️

1. **For Tesseract method**:
   - Current implementation is basic and needs tuning for better accuracy
   - Works best with clear, well-lit, properly aligned images
   - Consider this a baseline implementation for further improvements

2. **For GPT-4o-mini method**:
   - Requires internet connection
   - Check OpenAI pricing for image analysis costs
   - More accurate in information extraction
   - Rate limits apply based on your OpenAI account tier

## Troubleshooting 🔍

1. **Tesseract errors**:
   - Verify Tesseract is installed correctly
   - Check script path to Tesseract executable
   - Ensure Romanian language pack is installed

2. **GPT-4o-mini errors**:
   - Verify API key
   - Check internet connection
   - Ensure you have available API credits
   - Common status codes:
     - 429: Rate limit exceeded
     - 401: Invalid API key
     - 500: OpenAI service error

## Known Limitations ⚡

- Tesseract OCR is not optimized for Romanian ID cards in current implementation
- API rate limiting may slow down large batch processing
- Memory usage increases with batch size
- Image quality significantly affects accuracy for both methods

## Fields Extracted 📋

Currently extracts:
- NUME (Name)
- DOMICILIU (Address)
- CNP (Personal Numerical Code)

## Contact 📫

For questions or issues, please open an issue in the repository.