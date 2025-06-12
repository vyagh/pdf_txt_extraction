# Bank Statement PDF Extractor

This project helps you extract important information from bank statement PDFs (like TD Bank) using Python. You can use it for both digital and scanned PDFs.

## Two Ways to Extract Data

- **plumber/**: Best for digital PDFs. Uses `pdfplumber` to read text directly.
- **tesseract_spacy/**: Best for scanned or image PDFs. Uses OCR (Tesseract) to read text from images.

Both methods will extract:
- Customer Name
- Customer Address
- Statement Period
- Account Summary
- Checks (date, amount, description)

## How to Use

1. Put your PDF(s) in the `data/` folder.
2. To use the digital PDF method:
   - Go to the `plumber/` folder in your terminal.
   - Run:
     ```bash
     python extract_pdf_text.py
     ```
3. To use the scanned PDF method:
   - Go to the project root or `tesseract_spacy/` folder in your terminal.
   - Run:
     ```bash
     python tesseract_spacy/extract_pdf_text.py
     ```
4. The results will be shown as JSON in your terminal.

## Which Should I Use?
- Use **plumber** for regular, digital PDFs (text can be selected/copied).
- Use **tesseract_spacy** for scanned or photographed PDFs (text cannot be selected/copied).

## Quick Comparison

|                | plumber (pdfplumber) | tesseract_spacy (OCR) |
|----------------|----------------------|-----------------------|
| Best for       | Digital/text PDFs    | Scanned/image PDFs    |
| Speed          | ~0.23 seconds        | ~7.86 seconds         |
| Accuracy       | High, exact fields   | Good, may abbreviate  |

---

You can easily extend these scripts to handle more banks or more fields if needed. 