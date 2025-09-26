# Solution to the [Investment Adviser For Stocks](https://zh.swiss-ai-weeks.ch/challenges/vz3) challenge
### Rename PDF Files (Recommended)
The PDF files come with technical ISIN-based names like `DE0005140008-EUR-DE-en.pdf`. To make them more readable, run the renaming script:

```bash
chmod +x rename_all_pdfs.sh
./rename_all_pdfs.sh
```

This will rename files to beautiful company names:
- `DE0005140008-EUR-DE-en.pdf` → `DEUTSCHE BANK_EN.pdf`
- `DE0005200000-EUR-DE-de.pdf` → `BEIERSDORF_DE.pdf`
- `GB00B1YW4409-GBp-GB-de.pdf` → `3I GROUP PLC..pdf`

**Language Indicators:**
- `_EN` = English version
- `_DE` = German version  
- No suffix = Default version (usually German)

### 3. Data Structure
- **CSV Files**: `data/2025-09-23_data_EN.csv` contains company information with ISIN, names, sectors, etc.
- **PDF Files**: `data/2025-09-23/` contains investment reports for each company
- **Multiple Languages**: Each company may have reports in German and English