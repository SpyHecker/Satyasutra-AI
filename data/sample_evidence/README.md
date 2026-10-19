# Sample Evidence Dataset

This directory contains **synthetic, fictional** investigation documents designed for development and testing of the SatyaSutra pipeline. No real case data is used.

## Files

| File | Type | Purpose |
| --- | --- | --- |
| `fir_report.txt` | FIR (First Information Report) | Primary complaint with names, locations, dates, stolen objects, and suspect info |
| `witness_statement_1.txt` | Witness Statement | Corroborates FIR details; adds vehicle plate and physical descriptions |
| `witness_statement_2.txt` | Witness Statement | Introduces deliberate contradictions (vehicle color, number of suspects, timeline) |
| `case_notes.txt` | Investigator Notes | Summarizes key persons, evidence, timeline gaps, and contradictions |

## Expected Entities (for NER testing)

| Entity Type | Examples |
| --- | --- |
| **Person** | Rajesh Kumar Verma, Sunil Patil, Priya Sharma, Vikram Deshmukh, SI Meera Joshi |
| **Location** | Shivajinagar PS, 45 FC Road, 47 FC Road, Karve Nagar, Camp Pune, JM Road |
| **Time** | 14-July-2026 11:45 PM, 15-July-2026 8:30 AM, 12:30 AM, 1:10 AM |
| **Object** | Dell Inspiron laptops (serial numbers), Samsung Galaxy S24 phones, CCTV hard drive, white Maruti van (MH-12 XX 7856) |

## Built-in Contradictions (for contradiction detection testing)

1. **Vehicle color**: White (Witness 1 / FIR) vs. dark grey/black (Witness 2)
2. **Number of suspects**: Two (Witness 1) vs. three (Witness 2)
3. **Timeline overlap**: 10:45 PM observation vs. 12:30 AM observation — 1.5-hour gap

These contradictions are intentional and designed to test the system's ability to flag conflicting information across sources.
