"""
Debug why name isn't appearing after Sincerely
"""

from utils import create_docx, create_pdf

# Test data
test_cover_letter = """Dear Hiring Manager,

I am writing to express my strong interest in the position.

I have extensive experience and would love to contribute.

Sincerely,"""

test_contact = {
    'name': 'John Smith',
    'email': 'john@email.com',
    'phone': '(555) 123-4567',
    'address': 'San Francisco, CA'
}

print("="*70)
print("DEBUG: Export Name Issue")
print("="*70)

print("\n1. Original cover letter:")
print(test_cover_letter)
print(f"\n   Ends with: '{test_cover_letter[-20:]}'")

print("\n2. Contact info:")
print(f"   Name: {test_contact['name']}")

print("\n3. Creating DOCX...")
docx_buffer = create_docx(test_cover_letter, test_contact)
print(f"   DOCX size: {len(docx_buffer.getvalue())} bytes")

print("\n4. Creating PDF...")
pdf_bytes = create_pdf(test_cover_letter, test_contact)
print(f"   PDF size: {len(pdf_bytes)} bytes")

# Save files
with open('debug_output.docx', 'wb') as f:
    f.write(docx_buffer.getvalue())
print("\n✓ Saved: debug_output.docx")

with open('debug_output.pdf', 'wb') as f:
    f.write(pdf_bytes)
print("✓ Saved: debug_output.pdf")

print("\n" + "="*70)
print("Open both files and check if 'John Smith' appears after 'Sincerely,'")
print("="*70)