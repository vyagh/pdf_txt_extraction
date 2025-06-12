import os
import json
import re
from docling.document_converter import DocumentConverter
import time

PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'tdbank.pdf')

SUMMARY_KEYS = [
    'Beginning Balance', 'Average Collected Balance', 'Electronic Deposits',
    'Interest Earned This Period', 'Interest Paid Year-to-Date', 'Electronic Payments',
    'Annual Percentage Yield Earned', 'Service Charges', 'Days in Period', 'Ending Balance'
]

SUMMARY_HEADER = 'ACCOUNT SUMMARY'
ACTIVITY_HEADER = 'DAILY ACCOUNT ACTIVITY'
SECTION_HEADERS = [
    'ACCOUNT SUMMARY', 'DAILY ACCOUNT ACTIVITY', 'STATEMENT OF ACCOUNT',
    'Electronic Deposits', 'Electronic Payments', 'Service Charges', 'DAILY BALANCE SUMMARY'
]

SECTION_HEADER_SET = set([h.upper() for h in SECTION_HEADERS])
def is_section_header(line):
    return line.strip().upper() in SECTION_HEADER_SET

def is_name_candidate(line):
    l = line.strip()
    return l.isupper() and 'STATEMENT' not in l and not is_section_header(l) and len(l.split()) >= 2

def is_money(val):
    # Accept only plausible monetary values: must have decimal, be <12 chars, and only digits, commas, or dot
    return bool(re.match(r'^[0-9,.]+$', val)) and '.' in val and len(val) < 12

def extract_customer_info(lines):
    if 'Page:' in lines:
        idx = lines.index('Page:')
        name = None
        for i in range(idx-1, -1, -1):
            l = lines[i].strip()
            if is_name_candidate(l):
                name = l
                break
        address = [lines[j].strip() for j in range(0, i)]
        address = [l for l in address if l and l != name and 'TD Business Convenience Plus' not in l and not is_name_candidate(l)]
        print(f"[DEBUG] Full address list before processing: {address!r}")
        out_address = []
        # If address is empty or only contains 'KAZAKHSTAN', try to extract from the name line
        if not address or (len(address) == 1 and address[0].upper() == 'KAZAKHSTAN'):
            # Search for a line that starts with the name and has more content
            for line in lines:
                if name and line.startswith(name) and len(line) > len(name) + 5:
                    rest = line[len(name):].strip()
                    print(f"[DEBUG] Fallback: extracting address from name line: {rest!r}")
                    tokens = rest.split()
                    # Try to find a zip code or token with digits
                    split_idx = None
                    for idx, t in enumerate(tokens):
                        if (t.isdigit() and len(t) >= 5) or any(c.isdigit() for c in t):
                            split_idx = idx
                            break
                    if split_idx is not None and split_idx > 0:
                        street = ' '.join(tokens[:split_idx])
                        cityzip = ' '.join(tokens[split_idx:])
                        if street:
                            out_address.append(street)
                        if cityzip:
                            out_address.append(cityzip)
                    elif len(tokens) >= 4:
                        street = ' '.join(tokens[:-2])
                        cityzip = ' '.join(tokens[-2:])
                        if street:
                            out_address.append(street)
                        if cityzip:
                            out_address.append(cityzip)
                    else:
                        if rest:
                            out_address.append(rest)
                    break
            # Add 'KAZAKHSTAN' if present in lines
            for l in lines:
                if l.strip().upper() == 'KAZAKHSTAN' and l.strip() not in out_address:
                    out_address.append(l.strip())
        else:
            if address:
                first = address[0]
                print(f"[DEBUG] First address line: {first!r}")
                if name and first.startswith(name):
                    rest = first[len(name):].strip()
                    print(f"[DEBUG] Raw address line after removing name: {rest!r}")
                    # Regex: street, city, zip
                    m = re.match(r'(.+?) ([A-Z ]+) (\d{5,})$', rest)
                    if m:
                        street = m.group(1).strip()
                        city = m.group(2).strip()
                        zip_code = m.group(3).strip()
                        if street:
                            out_address.append(street)
                        if city and zip_code:
                            out_address.append(f"{city} {zip_code}")
                    else:
                        tokens = rest.split()
                        # Try to find a zip code or token with digits
                        split_idx = None
                        for idx, t in enumerate(tokens):
                            if (t.isdigit() and len(t) >= 5) or any(c.isdigit() for c in t):
                                split_idx = idx
                                break
                        if split_idx is not None and split_idx > 0:
                            street = ' '.join(tokens[:split_idx])
                            cityzip = ' '.join(tokens[split_idx:])
                            if street:
                                out_address.append(street)
                            if cityzip:
                                out_address.append(cityzip)
                        elif len(tokens) >= 4:
                            street = ' '.join(tokens[:-2])
                            cityzip = ' '.join(tokens[-2:])
                            if street:
                                out_address.append(street)
                            if cityzip:
                                out_address.append(cityzip)
                        else:
                            if rest:
                                out_address.append(rest)
                else:
                    out_address.append(first)
                for l in address[1:]:
                    if l and l not in out_address:
                        out_address.append(l)
        return name, out_address
    return None, []

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

def extract_account_summary_from_lines(lines):
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
                    after = line.split(key, 1)[-1].strip()
                    if after and re.match(r'^[0-9,.%-]+$', after.split()[0]):
                        summary[key.replace(' ', '')] = after.split()[0]
                        continue
                    for j in range(i+1, len(lines)):
                        val = lines[j].strip()
                        if val and re.match(r'^[0-9,.%-]+$', val.split()[0]):
                            summary[key.replace(' ', '')] = val.split()[0]
                            break
    return summary

def extract_account_summary_from_tables(tables):
    summary = {}
    for table in tables:
        for row in table.get('rows', []):
            for i, cell in enumerate(row):
                for key in SUMMARY_KEYS:
                    if key in cell:
                        if i+1 < len(row):
                            val = row[i+1].strip()
                            if re.match(r'^[0-9,.%-]+$', val):
                                summary[key.replace(' ', '')] = val
    return summary

def extract_checks_from_lines(lines):
    checks = []
    if ACTIVITY_HEADER in lines:
        idx = lines.index(ACTIVITY_HEADER)
        section = lines[idx:]
        try:
            amount_idx = section.index('AMOUNT')
        except ValueError:
            amount_idx = None
        amounts = []
        if amount_idx is not None:
            for l in section[amount_idx+1:]:
                if is_money(l.strip()):
                    amounts.append(l.strip())
        # For each ATM CHECK DEPOSIT line, look backwards for the nearest unused date line
        date_indices = [i for i, l in enumerate(section[:amount_idx if amount_idx is not None else len(section)]) if re.match(r'\d{2}/\d{2}', l.strip())]
        used_dates = set()
        pairs = []
        for i, l in enumerate(section[:amount_idx if amount_idx is not None else len(section)]):
            if 'ATM CHECK DEPOSIT' in l:
                # Look backwards for nearest unused date line
                for j in reversed(date_indices):
                    if j < i and j not in used_dates:
                        date = section[j].strip()
                        desc = l.strip()
                        pairs.append((date, desc))
                        used_dates.add(j)
                        break
        # Pair in order with amounts
        for (date, desc), amount in zip(pairs, amounts):
            checks.append({
                'date': date,
                'amount': amount,
                'description': f"{date} {desc} {amount}"
            })
    return checks

def extract_checks_from_tables(tables):
    checks = []
    for table in tables:
        for row in table.get('rows', []):
            if len(row) >= 3:
                date, desc, amount = row[0], row[1], row[2]
                if re.match(r'\d{2}/\d{2}', date) and 'CHECK DEPOSIT' in desc:
                    # Prefer the first number after the description as amount
                    amt_match = re.search(r'([0-9,.]+)', amount)
                    amt_val = amt_match.group(1) if amt_match and is_money(amt_match.group(1)) else (amount.strip() if is_money(amount.strip()) else None)
                    checks.append({
                        'date': date,
                        'amount': amt_val,
                        'description': desc.strip()
                    })
    return checks

def get_tables(docling_tables):
    tables = []
    for t in docling_tables:
        if hasattr(t, 'data') and hasattr(t.data, 'grid'):
            grid = t.data.grid
            rows = []
            for row in grid:
                rows.append([getattr(cell, 'text', '') for cell in row])
            tables.append({'rows': rows})
    return tables

def main():
    start = time.time()
    converter = DocumentConverter()
    result = converter.convert(PDF_PATH)
    lines = [item.text for item in result.document.texts if hasattr(item, 'text')]
    name, address = extract_customer_info(lines)
    statement_period = extract_statement_period(lines)
    account_summary = extract_account_summary_from_lines(lines)
    checks = extract_checks_from_lines(lines)
    if not account_summary or all(v is None for v in account_summary.values()):
        tables = get_tables(getattr(result.document, 'tables', []))
        table_summary = extract_account_summary_from_tables(tables)
        if table_summary:
            account_summary = table_summary
    if not checks or any(c['amount'] is None for c in checks):
        tables = get_tables(getattr(result.document, 'tables', []))
        table_checks = extract_checks_from_tables(tables)
        if table_checks:
            checks_out = []
            for c in checks:
                if c['amount'] is not None:
                    checks_out.append(c)
                else:
                    match = next((tc for tc in table_checks if tc['date'] == c['date'] and tc['description'] == c['description'] and tc['amount']), None)
                    if match:
                        checks_out.append(match)
            for tc in table_checks:
                if not any(c['date'] == tc['date'] and c['description'] == tc['description'] for c in checks_out):
                    checks_out.append(tc)
            checks = checks_out if checks_out else table_checks
    result_json = {
        'customer_name': name,
        'customer_address': address,
        'statement_period': statement_period,
        'account_summary': account_summary,
        'checks': checks
    }
    print(json.dumps(result_json, indent=2, ensure_ascii=False))
    elapsed = time.time() - start
    print(f"\n[docling_v2] Extraction completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main() 