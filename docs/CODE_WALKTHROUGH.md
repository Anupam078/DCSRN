# Code Walkthrough

## Phase 1: Config and Validation

### `config.py`
This file contains no logic or functions, only constant variables used throughout the project (such as the server `PORT`, `COURSES` dictionary, and Tkinter colours). Putting them in one place makes it easy to change settings without digging through logic code.

### `validation.py`
* **`validate_fields(name, roll_number, email, course)`**: Validates user inputs using basic string methods like `strip()`, `isalnum()`, and `find()`. It returns an empty string if all inputs are good, or a specific error message if any field breaks its rules. Both the client and server use this function to ensure invalid data is never sent or saved. [Unit 2: string methods]

## Phase 2: Storage (File Handling)

### `storage.py`
* **`ensure_data_file()`**: Uses `os.makedirs` to safely create the `data/` folder if it doesn't exist, and creates an empty `registrations.csv` file using write mode (`"w"`) if missing. [Unit 4: directories, file handling]
* **`append_registration(roll, name, email, course)`**: Gets the current time as a string, builds a comma-separated line, and saves it using append mode (`"a"`). Append mode guarantees we add to the bottom without deleting old records. [Unit 4: file handling]
* **`load_registrations()`**: Opens the file in read mode (`"r"`), loops through each line, and uses `split(",")` to turn it into a list. It skips any malformed lines that have fewer than 5 parts. [Unit 4: file handling]
* **`clear_registrations()`**: Instantly empties the entire file by opening it in write mode (`"w"`) and immediately closing it.
