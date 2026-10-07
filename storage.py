import os
import time
from config import DATA_FOLDER, DATA_FILE

def ensure_data_file():
    """
    Ensures the data directory and file exist.
    Creates an empty file if it doesn't exist.
    """
    # [Unit 4: directories]
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        # [Unit 4: file handling] open with 'w' to create an empty file
        with open(DATA_FILE, "w") as f:
            pass

def append_registration(roll, name, email, course):
    """
    Appends a new registration as a comma-separated line.
    May raise OSError.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{roll},{name},{email},{course},{timestamp}"
    
    # [Unit 4: file handling] 'a' mode appends without overwriting
    with open(DATA_FILE, "a") as f:
        f.write(line + "\n")

def load_registrations():
    """
    Reads all registrations from the file.
    Skips lines with fewer than 5 fields.
    Returns a list of lists.
    """
    registrations = []
    if not os.path.exists(DATA_FILE):
        return registrations

    # [Unit 4: file handling] 'r' mode for reading
    with open(DATA_FILE, "r") as f:
        for line in f:
            fields = line.strip().split(",")
            if len(fields) >= 5:
                registrations.append(fields)
    
    return registrations

def clear_registrations():
    """
    Empties the data file for testing or resetting.
    """
    # [Unit 4: file handling] 'w' mode overwrites and clears the file
    with open(DATA_FILE, "w") as f:
        pass

# TEMP TEST: remove in Phase 10
if __name__ == "__main__":
    print("Testing storage...")
    ensure_data_file()
    clear_registrations()
    
    append_registration("24BCE10354", "Asmi Chakne", "asmi@example.com", "CSE3011 Python Programming")
    append_registration("25BOE10105", "Niharika Tanwi", "niharika@example.com", "CSE2001 Data Structures")
    
    records = load_registrations()
    for rec in records:
        print("Loaded:", rec)
        
    clear_registrations()
    print("File cleared.")
