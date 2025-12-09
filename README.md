# Sahaj - GSTR-1 Table 13 Generator

A simple desktop tool for GST practitioners in India to generate **Table 13 of GSTR-1** (Summary of Documents Issued during the tax period).

## What Does This Do?

Every month when filing GSTR-1, you need to fill Table 13 with a summary of all invoices issued. This means:
- Finding the first and last invoice number
- Counting how many were cancelled/missing
- Doing this for each invoice series

**Sahaj does all of this automatically.** Just paste your invoice numbers, and get Table 13 ready to copy into the GST portal.

## Installation

```bash
# Clone or download the project
cd sahaj-table13-generator

# Install requirements
pip install -r requirements.txt

# Run the app
python main.py
```

## How to Use

### Step 1: Select Document Type
Choose what type of documents you're summarizing (Invoices, Credit Notes, etc.)

### Step 2: Enter Your Invoice Format
Tell the tool what your invoice numbers look like by using `[ ]` brackets to mark the serial number part.

**Examples:**

| Your Invoices | Write Format As |
|---------------|-----------------|
| GST/24-25/0001, GST/24-25/0002... | `GST/24-25/[0001]` |
| INV-001-A, INV-002-A... | `INV-[001]-A` |
| SAL001, SAL002... | `SAL[001]` |

**Multiple Series?** If you have invoices like `GST/A/001` and `GST/B/001`, use `*` for the changing part:
- Format: `GST/*/[001]`
- The tool will automatically detect and separate each series!

### Step 3: Paste Invoice Numbers
Copy invoice numbers from Excel/Tally and paste them (one per line).

### Step 4: Click Generate
Get your Table 13 output with:
- Starting and ending invoice numbers
- Total count and cancelled count
- List of missing/cancelled invoice numbers
- Ready-to-copy format for GST portal
