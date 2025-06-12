import os
from pdf2image import convert_from_path
import pytesseract
import re
import json
import time

# Paths
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'tdbank.pdf')

# Helper functions for extraction

def normalize(s):
    return re.sub(r'\s+', '', s).lower()

def extract_customer_info(lines):
    name = None
    address = []
    for i, line in enumerate(lines):
        if 'Page:' in line:
            name = line.split('Page:')[0].strip()
            for l in lines[i+1:]:
                l = l.strip()
                if not l: break
                if any(kw in l for kw in ["Statement Period", "Cust Ref #", "Primary Account #"]):
                    l = l.split("Statement Period")[0].split("Cust Ref #")[0].split("Primary Account #")[0].strip()
                if not l: break
                address.append(l)
            break
    return name, address

def extract_statement_period(lines):
    for line in lines:
        m = re.search(r'Statement Period: ([^\n]+)', line)
        if m:
            return m.group(1).strip()
    return None

def extract_account_summary(lines):
    summary = {}
    in_summary = False
    for line in lines:
        if normalize('ACCOUNT SUMMARY') in normalize(line):
            in_summary = True
            continue
        if in_summary:
            if normalize('DAILY ACCOUNT ACTIVITY') in normalize(line):
                break
            parts = re.split(r'(?<=[0-9]) (?=[A-Za-z])| (?=[A-Z][a-z])', line)
            for part in parts:
                m = re.match(r'([A-Za-z]+[A-Za-z ]*[A-Za-z]+) ([0-9,.%-]+)', part.strip())
                if m:
                    key = m.group(1).replace(' ', '')
                    value = m.group(2)
                    summary[key] = value
    return summary

def extract_checks(lines):
    checks = []
    in_activity = False
    for line in lines:
        if normalize('DAILY ACCOUNT ACTIVITY') in normalize(line):
            in_activity = True
        if in_activity and ('CHECK DEPOSIT' in line):
            m = re.match(r'(\d{2}/\d{2}) .*CHECK DEPOSIT.* ([0-9,.]+)', line)
            if m:
                checks.append({
                    'date': m.group(1),
                    'amount': m.group(2),
                    'description': line.strip()
                })
    return checks

def ocr_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    texts = [pytesseract.image_to_string(img) for img in images]
    return texts

def main():
    start = time.time()
    texts = ocr_pdf(PDF_PATH)
    all_lines = []
    for text in texts:
        all_lines.extend(text.splitlines())
    # Debug: print all lines for tuning
    # for i, line in enumerate(all_lines):
    #     print(f"{i:03}: {repr(line)}")
    name, address = extract_customer_info(all_lines)
    statement_period = extract_statement_period(all_lines)
    account_summary = extract_account_summary(all_lines)
    checks = extract_checks(all_lines)
    result = {
        'customer_name': name,
        'customer_address': address,
        'statement_period': statement_period,
        'account_summary': account_summary,
        'checks': checks
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    elapsed = time.time() - start
    print(f"\n[tesseract_spacy] Extraction completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main() 