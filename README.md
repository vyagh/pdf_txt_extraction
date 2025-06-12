# Bank Statement PDF Extractor

This project helps you extract important information from bank statement PDFs (like TD Bank) using Python. It supports both digital and scanned PDFs, and provides multiple extraction methods for flexibility and accuracy.

## Extraction Methods

### 1. plumber/ (pdfplumber)
- **Best for:** Digital/text PDFs (where text can be selected/copied)
- **How it works:** Uses `pdfplumber` to extract text directly from the PDF.
- **Extracts:**
  - Customer Name
  - Customer Address
  - Statement Period
  - Account Summary
  - Daily Balance Summary

### 2. pymupdf_method/ (PyMuPDF)
- **Best for:** Digital/text PDFs (alternative to pdfplumber)
- **How it works:** Uses `PyMuPDF` (imported as `fitz`) to extract text and layout information from the PDF.
- **Extracts:**
  - Customer Name
  - Customer Address
  - Statement Period
  - Account Summary
  - Daily Balance Summary

### 3. tesseract_spacy/ (OCR)
- **Best for:** Scanned/image PDFs (where text cannot be selected/copied)
- **How it works:** Uses `pdf2image` to convert PDF pages to images, then `pytesseract` (OCR) to extract text from images.
- **Extracts:**
  - Customer Name
  - Customer Address
  - Statement Period
  - Account Summary

## How to Use

1. Put your PDF(s) in the `data/` folder.
2. To use the digital PDF methods:
   - **pdfplumber:**
     ```bash
     python plumber/extract_pdf_text.py
     ```
   - **PyMuPDF:**
     ```bash
     python pymupdf_method/extract_pdf_text.py
     ```
3. To use the scanned PDF (OCR) method:
   ```bash
   python tesseract_spacy/extract_pdf_text.py
   ```
4. The results will be shown as JSON in your terminal.

## Method Comparison

| Method                | Best for             | Speed (approx) | Accuracy         | Features Extracted                |
|----------------------|---------------------|----------------|------------------|-----------------------------------|
| pdfplumber           | Digital/text PDFs   | 0.35 seconds   | High             | All fields incl. daily balances   |
| PyMuPDF (fitz)       | Digital/text PDFs   | 0.03 seconds   | High             | All fields incl. daily balances   |
| tesseract_spacy (OCR)| Scanned/image PDFs  | 14.82 seconds  | Moderate         | Most fields (no daily balances)   |

- **pdfplumber** and **PyMuPDF** both work well for digital PDFs, with similar speed and accuracy. PyMuPDF may be more robust for some complex layouts.
- **tesseract_spacy** is necessary for scanned/image PDFs, but is slower and may be less accurate, especially for tables or fine details.

## Conclusion & Recommendations

- **For digital/text PDFs:** Use either **pdfplumber** or **PyMuPDF**. Both extract all key fields, including the daily balance summary, quickly and accurately. If you encounter extraction issues with one, try the other.
- **For scanned/image PDFs:** Use **tesseract_spacy** (OCR). It is slower and may miss some structured data, but is the only option for non-selectable PDFs.
- **Overall best:** For most users with standard digital bank statements, **pdfplumber** is recommended for its simplicity and reliability. Use **PyMuPDF** as a strong alternative. Use **tesseract_spacy** only when dealing with scanned or photographed documents.

---

You can easily extend these scripts to handle more banks or more fields if needed. 