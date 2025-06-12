# Bank Statement PDF Extractor

Extracts key information from bank statement PDFs (like TD Bank) using Python. Supports both digital and scanned PDFs with multiple extraction methods.

## Methods

- **plumber/** (pdfplumber): Digital/text PDFs. Fast, reliable text extraction.
- **pymupdf_method/** (PyMuPDF): Digital/text PDFs. Very fast, robust for complex layouts.
- **tesseract_spacy/** (OCR): Scanned/image PDFs. Uses OCR, slower and less accurate.

**Extracted fields:**
- Customer Name
- Customer Address
- Statement Period
- Account Summary
- Daily Balance Summary (not available in OCR)

## Usage

1. Place PDFs in `data/`.
2. Run one of:
   - `python plumber/extract_pdf_text.py`
   - `python pymupdf_method/extract_pdf_text.py`
   - `python tesseract_spacy/extract_pdf_text.py`
3. Output is shown as JSON in the terminal.

## Comparison

| Method                | Best for             | Speed         | Accuracy  | Features Extracted                |
|----------------------|---------------------|---------------|-----------|-----------------------------------|
| pdfplumber           | Digital/text PDFs   | 0.35 seconds  | High      | All fields incl. daily balances   |
| PyMuPDF (fitz)       | Digital/text PDFs   | 0.03 seconds  | High      | All fields incl. daily balances   |
| tesseract_spacy (OCR)| Scanned/image PDFs  | 14.82 seconds | Moderate  | Most fields (no daily balances)   |

## Recommendations

- **Digital PDFs:** Use **pdfplumber** or **PyMuPDF**. Try both if needed.
- **Scanned PDFs:** Use **tesseract_spacy** (OCR).
- **Best overall:** **pdfplumber** for most digital statements; **PyMuPDF** for speed or complex layouts; **tesseract_spacy** only for scanned/image files.

---

Easily extendable for more banks or fields. 