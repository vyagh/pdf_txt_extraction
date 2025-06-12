import fitz  # PyMuPDF
import re
import os
import json
import time

PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'tdbank.pdf')

SUMMARY_KEYS = [
    'Beginning Balance', 'Average Collected Balance', 'Electronic Deposits',
    'Interest Earned This Period', 'Interest Paid Year-to-Date', 'Electronic Payments',
    'Annual Percentage Yield Earned', 'Service Charges', 'Days in Period', 'Ending Balance'
]

SUMMARY_HEADER = 'ACCOUNT SUMMARY'
ACTIVITY_HEADER = 'DAILY ACCOUNT ACTIVITY'


def extract_customer_info(lines):
    # Search for a block of 3-4 consecutive lines: name (all uppercase), street, city/zip, country
    for i in range(len(lines)-3):
        l0 = lines[i].strip()
        l1 = lines[i+1].strip()
        l2 = lines[i+2].strip()
        l3 = lines[i+3].strip() if i+3 < len(lines) else ''
        # Heuristic: name is all uppercase, next lines are plausible address
        if l0.isupper() and len(l0.split()) >= 2 and l1 and l2 and (l3.isupper() or l3.istitle() or l3.isdigit() or l3):
            # Check for country in l3 or l2
            if any(x in l3.upper() for x in ['KAZAKHSTAN', 'USA', 'INDIA']) or any(x in l2.upper() for x in ['KAZAKHSTAN', 'USA', 'INDIA']):
                return l0, [l1, l2, l3] if l3 else [l1, l2]
    # Fallback to previous logic
    return '', []

def extract_statement_period(lines):
    date_pattern = re.compile(r'([A-Za-z]{3,9} \d{1,2} \d{4}-[A-Za-z]{3,9} \d{1,2} \d{4})')
    for i, line in enumerate(lines):
        if 'Statement Period:' in line:
            for j in range(i+1, len(lines)):
                val = lines[j].strip()
                if not val or val in ('Cust Ref #:', 'Primary Account #:'):
                    continue
                m = date_pattern.search(val)
                if m:
                    return m.group(1)
    return None

def extract_account_summary(lines):
    summary = {}
    in_summary = False
    for i, line in enumerate(lines):
        if SUMMARY_HEADER in line:
            in_summary = True
            continue
        if in_summary:
            if ACTIVITY_HEADER in line:
                break
            for key in SUMMARY_KEYS:
                if key in line:
                    # Take the next non-empty line as value
                    for j in range(i+1, len(lines)):
                        val = lines[j].strip()
                        if val and re.match(r'^[0-9,.%-]+$', val):
                            summary[key.replace(' ', '')] = val
                            break
    return summary

def extract_daily_balance_summary(lines, last_lines=None):
    summary = []
    in_section = False
    search_lines = last_lines if last_lines is not None else lines
    found_header = False
    date_list = []
    balance_list = []
    for line in search_lines:
        if 'DAILYBALANCESUMMARY' in line.replace(' ', '').upper():
            in_section = True
            found_header = True
            continue
        if in_section:
            if not line.strip() or line.strip().startswith('Call '):
                break
            # Skip header lines
            if 'DATE' in line.upper() or 'BALANCE' in line.upper():
                continue
            # Collect dates and balances
            date_match = re.match(r'\d{2}/\d{2}', line.strip())
            balance_match = re.match(r'^[0-9,.-]+$', line.strip())
            if date_match:
                date_list.append(line.strip())
            elif balance_match:
                balance_list.append(line.strip())
    # Pair dates and balances in order
    for date, balance in zip(date_list, balance_list):
        summary.append({'date': date, 'balance': balance})
    return summary

def main():
    start = time.time()
    doc = fitz.open(PDF_PATH)
    lines = []
    all_pages = []
    for page in doc:
        text = page.get_text()
        page_lines = text.splitlines()
        lines.extend(page_lines)
        all_pages.append(page_lines)
    # Use only the last 2 pages for daily balance summary
    last_lines = []
    for page_lines in all_pages[-2:]:
        last_lines.extend(page_lines)
    name, address = extract_customer_info(lines)
    statement_period = extract_statement_period(lines)
    account_summary = extract_account_summary(lines)
    daily_balance_summary = extract_daily_balance_summary(lines, last_lines=last_lines)
    result = {
        'customer_name': name,
        'customer_address': address,
        'statement_period': statement_period,
        'account_summary': account_summary,
        'daily_balance_summary': daily_balance_summary
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    elapsed = time.time() - start
    print(f"\n[pymupdf] Extraction completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main() 