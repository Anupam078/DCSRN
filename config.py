# config.py

# Network and Server Configuration
HOST = "0.0.0.0"
PORT = 5050
DEFAULT_SERVER_IP = "127.0.0.1"
BUFFER_SIZE = 4096
TIMEOUT = 5

# Storage
DATA_FOLDER = "data"
DATA_FILE = "data/registrations.csv"

# Courses and Seats
COURSES = {
    "CSE3011 Python Programming": 5,
    "CSE2001 Data Structures": 3,
    "CSE2005 Database Systems": 4
}

# Concurrency / Demo Flags
USE_LOCK = True
DEMO_DELAY = 0.0

# UI Configuration
REFRESH_MS = 500

COLOR_BG = "#EEEEE6"
COLOR_CARD = "#F8F8F2"
COLOR_INK = "#2B2D2F"
COLOR_MUTED = "#5A5C5E"
COLOR_ACCENT = "#8B5CF6"
COLOR_SUCCESS = "#2E7D32"
COLOR_ERROR = "#C62828"

FONT_TITLE = ("Georgia", 20)
FONT_BODY = ("Helvetica", 11)
FONT_BOLD = ("Helvetica", 11, "bold")
FONT_MONO = ("Courier", 10)
