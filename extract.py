import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pytesseract
from PIL import Image
import os
import re
import pandas as pd
from openpyxl import Workbook
import threading
import base64
import requests
import json
from PIL import ImageEnhance, ImageOps
import io

class IDCardProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesator de buletine")
        self.root.geometry("700x500")
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_file = tk.StringVar()
        self.api_key = tk.StringVar()
        self.processing = False
        self.processing_method = tk.StringVar(value="tesseract")
        
        self._create_gui()
    
    def _create_gui(self):
        # Processing method selection
        method_frame = ttk.LabelFrame(self.root, text="Processing Method", padding="10")
        method_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Radiobutton(method_frame, text="Tesseract OCR", value="tesseract", 
                       variable=self.processing_method).pack(side="left", padx=20)
        ttk.Radiobutton(method_frame, text="GPT-4o-mini", value="gpt-4o-mini", 
                       variable=self.processing_method).pack(side="left", padx=20)
        
        # API Key input (for GPT-4V)
        api_frame = ttk.LabelFrame(self.root, text="OpenAI API Key (for GPT-4o-mini)", padding="10")
        api_frame.pack(fill="x", padx=10, pady=5)
        ttk.Entry(api_frame, textvariable=self.api_key, show="*", width=50).pack(fill="x")
        
        # Input folder selection
        input_frame = ttk.LabelFrame(self.root, text="Input", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Input Folder:").pack(side="left")
        ttk.Entry(input_frame, textvariable=self.input_folder, width=50).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Browse", command=self._browse_input).pack(side="left")
        
        # Output file selection
        output_frame = ttk.LabelFrame(self.root, text="Output", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(output_frame, text="Output Excel:").pack(side="left")
        ttk.Entry(output_frame, textvariable=self.output_file, width=50).pack(side="left", padx=5)
        ttk.Button(output_frame, text="Browse", command=self._browse_output).pack(side="left")
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress_bar.pack(fill="x")
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack()
        
        # Process button
        self.process_button = ttk.Button(self.root, text="Process ID Cards", command=self._start_processing)
        self.process_button.pack(pady=20)
    
    def _browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
    
    def _browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file:
            self.output_file.set(file)
    
    def _start_processing(self):
        if not self.input_folder.get() or not self.output_file.get():
            messagebox.showerror("Error", "Please select both input folder and output file")
            return
        
        if self.processing_method.get() == "gpt-4o-mini" and not self.api_key.get():
            messagebox.showerror("Error", "Please enter OpenAI API key for GPT-4o-mini processing")
            return
        
        if self.processing:
            return
        
        self.processing = True
        self.process_button.state(['disabled'])
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self._process_files)
        thread.start()
    
    def _process_files(self):
        try:
            # Get list of image files
            image_files = [f for f in os.listdir(self.input_folder.get())
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not image_files:
                messagebox.showinfo("Info", "No image files found in the selected folder")
                self._reset_processing()
                return
            
            # Initialize Excel workbook
            wb = Workbook()
            ws = wb.active
            ws.append(["Filename", "Nume", "Domiciliu", "CNP"])
            
            # Process each file
            for i, filename in enumerate(image_files):
                # Update progress
                progress = (i + 1) / len(image_files) * 100
                self.root.after(0, self._update_progress, progress, f"Processing {filename}...")
                
                # Process image
                image_path = os.path.join(self.input_folder.get(), filename)
                
                if self.processing_method.get() == "tesseract":
                    data = self._process_with_tesseract(image_path)
                else:
                    data = self._process_with_gpt4o_mini(image_path)
                
                # Add to Excel
                ws.append([filename] + data)
            
            # Save Excel file
            wb.save(self.output_file.get())
            
            messagebox.showinfo("Success", "Processing completed successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            self._reset_processing()
    
    def _process_with_tesseract(self, image_path):
        """Process image using Tesseract OCR"""
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance image
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Perform OCR
        text = pytesseract.image_to_string(image, lang='ron+eng')
        
        # Extract information
        nume_pattern = r'Nume[le]*/?\s*[Ss]ur\s*name\s*(?P<nume>[A-ZĂÂÎȘȚ][a-zăâîșț\-]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț\-]+)*)'
        domiciliu_pattern = r'Domiciliu[l]*/?\s*[Aa]ddress\s*(?P<domiciliu>.*?)(?=\n|\Z)'
        cnp_pattern = r'(?P<cnp>\d{13})'
        
        nume_match = re.search(nume_pattern, text)
        domiciliu_match = re.search(domiciliu_pattern, text)
        cnp_match = re.search(cnp_pattern, text)
        
        nume = nume_match.group('nume') if nume_match else "N/A"
        domiciliu = domiciliu_match.group('domiciliu') if domiciliu_match else "N/A"
        cnp = cnp_match.group('cnp') if cnp_match else "N/A"
        
        return [nume, domiciliu, cnp]
    
    def _process_with_gpt4o_mini(self, image_path):
        """Process image using GPT-4o-mini"""
        # Read and encode image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key.get()}"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a Romanian ID card. Make sure to give me the full name (both first and last name) and full address. Please extract and return ONLY these fields in this EXACT format: NUME: [value] ; DOMICILIU: [value] ; CNP: [value]"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            return ["Error", "Error", "Error"]
        
        # Parse GPT-4V response
        response_text = response.json()["choices"][0]["message"]["content"]
        
        # Extract fields using regex
        nume_match = re.search(r'NUME:\s*([^;]+)', response_text)
        domiciliu_match = re.search(r'DOMICILIU:\s*([^;]+)', response_text)
        cnp_match = re.search(r'CNP:\s*([^;]+)', response_text)
        
        nume = nume_match.group(1).strip() if nume_match else "N/A"
        domiciliu = domiciliu_match.group(1).strip() if domiciliu_match else "N/A"
        cnp = cnp_match.group(1).strip() if cnp_match else "N/A"
        
        return [nume, domiciliu, cnp]
    
    def _update_progress(self, value, status):
        self.progress_bar["value"] = value
        self.status_label["text"] = status
    
    def _reset_processing(self):
        self.processing = False
        self.progress_bar["value"] = 0
        self.status_label["text"] = "Ready"
        self.process_button.state(['!disabled'])

if __name__ == "__main__":
    # Initialize Tesseract path (adjust this based on your installation)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    root = tk.Tk()
    app = IDCardProcessor(root)
    root.mainloop()