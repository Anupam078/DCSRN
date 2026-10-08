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


