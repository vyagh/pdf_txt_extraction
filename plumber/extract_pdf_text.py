import pdfplumber
import re
import json
import os
import time

# Constants
KEYWORDS = ["StatementPeriod", "CustRef#", "PrimaryAccount#"]
PDF_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PDF_FILENAME = 'tdbank.pdf'


def extract_customer_info(lines):
    for i, line in enumerate(lines):
        if 'Page:' in line:
            name = line.split('Page:')[0].strip()
            address = []
            for l in lines[i+1:]:
                l = l.strip()
                if not l: break
                for kw in KEYWORDS:
                    if kw in l:
                        l = l.split(kw)[0].strip()
                        break
                if not l: break
                address.append(l)
            return name, address
    return None, []


def extract_statement_period(lines):
    for line in lines:
        m = re.search(r'StatementPeriod: ([^\n]+)', line)
        if m: return m.group(1).strip()
    return None


def extract_account_summary(lines):
    summary, in_summary = {}, False
    for line in lines:
        if 'ACCOUNTSUMMARY' in line.replace(' ', ''): in_summary = True; continue
        if in_summary:
            if 'DAILYACCOUNTACTIVITY' in line.replace(' ', ''): break
            for part in re.split(r'(?<=[0-9]) (?=[A-Za-z])| (?=[A-Z][a-z])', line):
                m = re.match(r'([A-Za-z]+[A-Za-z ]*[A-Za-z]+) ([0-9,.%-]+)', part.strip())
                if m: summary[m.group(1).replace(' ', '')] = m.group(2)
    return summary


def extract_daily_balance_summary(lines):
    summary = []
    in_section = False
    for line in lines:
        if 'DAILYBALANCESUMMARY' in line.replace(' ', '').upper():
            in_section = True
            continue
        if in_section:
            if not line.strip() or line.strip().startswith('Call '):
                break
            # Skip header line
            if 'DATE' in line and 'BALANCE' in line:
                continue
            # Parse two columns per line
            m = re.findall(r'(\d{2}/\d{2})\s+([0-9,.-]+)', line)
            for date, balance in m:
                summary.append({'date': date, 'balance': balance})
    return summary


def extract_pdf_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        lines = [l for page in pdf.pages for l in (page.extract_text() or '').splitlines()]
    name, address = extract_customer_info(lines)
    return {
        'customer_name': name,
        'customer_address': address,
        'statement_period': extract_statement_period(lines),
        'account_summary': extract_account_summary(lines),
        'daily_balance_summary': extract_daily_balance_summary(lines)
    }


if __name__ == "__main__":
    start = time.time()
    pdf_path = os.path.join(PDF_DIR, PDF_FILENAME)
    print(json.dumps(extract_pdf_data(pdf_path), indent=2, ensure_ascii=False))
    elapsed = time.time() - start
    print(f"\n[plumber] Extraction completed in {elapsed:.2f} seconds.") 