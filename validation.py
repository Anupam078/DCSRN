# validation.py

def validate_fields(name, roll_number, email, course):
    """
    Validates registration fields using plain string methods.
    Returns an empty string if valid, or an error message if invalid.
    """
    # [Unit 2: string methods] Check name
    clean_name = name.strip()
    if not (2 <= len(clean_name) <= 50) or "," in clean_name:
        return "Name must be 2-50 characters (no commas)."

    # Check roll number
    clean_roll = roll_number.strip()
    if not (5 <= len(clean_roll) <= 15) or not clean_roll.isalnum():
        return "Roll number must be 5-15 letters/digits."

    # Check email
    clean_email = email.strip()
    if len(clean_email) > 60 or " " in clean_email or "," in clean_email:
        return "Enter a valid email address."
    
    # Must have '@' and a '.' after the '@'
    at_pos = clean_email.find("@")
    if at_pos == -1 or clean_email.find(".", at_pos) == -1:
        return "Enter a valid email address."

    # Check course
    if not course or course.strip() == "":
        return "Please select a course."

    return ""

# TEMP TEST: remove in Phase 10
if __name__ == "__main__":
    tests = [
        # 1. Valid input
        ("Asmi Chakne", "24BCE10354", "asmi@example.com", "CSE3011 Python Programming"),
        # 2. 1-char name
        ("A", "24BCE10354", "asmi@example.com", "CSE3011 Python Programming"),
        # 3. Roll with a space
        ("Asmi Chakne", "24 BCE", "asmi@example.com", "CSE3011 Python Programming"),
        # 4. Email without @
        ("Asmi Chakne", "24BCE10354", "asmiexample.com", "CSE3011 Python Programming"),
        # 5. Name with a comma
        ("Asmi, Chakne", "24BCE10354", "asmi@example.com", "CSE3011 Python Programming"),
        # 6. Empty course
        ("Asmi Chakne", "24BCE10354", "asmi@example.com", "")
    ]
    
    for i, test in enumerate(tests, 1):
        result = validate_fields(*test)
        print(f"Test {i}: {result if result else 'OK'}")
