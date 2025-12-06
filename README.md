# Dwello PDF Form Filler - Take Home Assignment


---


**Command**:
```bash
python main.py input.json output/filled_form.pdf
```

---

## JSON Input Format

```json
{
  "date_prepared": "2025-01-15",
  "property_address": "1234 Main St, Dublin, CA 94568",
  "buyer_name": "John Doe",
  "seller_name": "Jane Smith",
  "agreement_date": "2024-12-01",
  "repairs": [
    {
      "item": "HVAC System",
      "issue": "Not heating properly",
      "requested_action": "Repair or replace",
      "estimated_cost": 3500
    }
  ]
}
```

All JSON fields should map to their corresponding PDF form fields.

---

## Requirements

### Must Have
- Read JSON and fill PDF form
- Handle basic fields: date_prepared, property_address, buyer_name, seller_name, agreement_date
- Handle repairs array (Section 1A on the form)
- Error handling for missing files/malformed JSON
- Save valid PDF output

### Bonus (Optional)
- Mark checkboxes
- Format dates (ISO → MM/DD/YYYY)
- Handle multiple repair items elegantly
- Command-line help

---

## Implementation

The PDF is at `resources/request_for_repair.pdf`. You need to:
1. Load the JSON
2. Map JSON fields to PDF form locations
3. Fill the fields
4. Save the output

**Recommended libraries**: `pypdf`, `PyPDF2`, `reportlab`

---

## Deliverables

1. **main.py** - Your implementation (single file)
2. **output/** - At least one filled PDF example
3. **WRITEUP.md** - 300 words max covering:
   - Your approach and library choice
   - Challenges you faced
   - What you'd do differently for production

---

## Evaluation

| Criteria | Weight |
|----------|--------|
| Functionality | 40% |
| Code Quality | 30% |
| Problem Solving | 15% |
| Documentation | 15% |

**Minimum**: Fill basic text fields successfully  
**To impress**: Handle repairs + clean code + thoughtful write-up

---

## Submission

```bash
zip -r dwello-submission-yourname.zip main.py WRITEUP.md requirements.txt output/ resources/ README.md
```

Email to: `[email]` with subject: "Dwello Take-Home - [Your Name]"

---

**Note**: We value honest write-ups about what you completed vs what you didn't. Quality over quantity.
