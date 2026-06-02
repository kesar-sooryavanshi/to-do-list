import os

# Application Directory & Data Paths
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(APP_DIR), "data")
DB_FILE = os.path.join(DATA_DIR, "tasks.json")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)

# UI/Theme Palette (Hex colors for Rich TrueColor support)
# Premium palette: Black (#0D0D0D), White (#FFFFFF), Maroon (#800000), Gold (#D4AF37)
COLOR_PALETTE = {
    "bg": "#0D0D0D",
    "text": "#FFFFFF",
    "maroon": "#800000",
    "gold": "#D4AF37",
    "gray_dark": "#2A2A2A",
    "gray_light": "#B0B0B0",
    "green": "#27AE60",
    "orange": "#E67E22",
    "red": "#C0392B",
}

# Rich UI Style tags
STYLES = {
    "title": f"bold {COLOR_PALETTE['gold']}",
    "subtitle": f"italic {COLOR_PALETTE['gray_light']}",
    "header": f"bold {COLOR_PALETTE['text']} on {COLOR_PALETTE['maroon']}",
    "border": COLOR_PALETTE['maroon'],
    "highlight": COLOR_PALETTE['gold'],
    
    # Priority Styles
    "priority_high": f"bold {COLOR_PALETTE['red']}",
    "priority_medium": f"bold {COLOR_PALETTE['orange']}",
    "priority_low": f"bold {COLOR_PALETTE['gray_light']}",
    
    # Status Styles
    "status_pending": f"{COLOR_PALETTE['gray_light']}",
    "status_in_progress": f"bold {COLOR_PALETTE['orange']}",
    "status_completed": f"bold {COLOR_PALETTE['green']}",
    
    # Category Styles
    "cat_personal": "#9B59B6",
    "cat_work": "#2980B9",
    "cat_study": "#3498DB",
    "cat_health": "#2ECC71",
    "cat_finance": "#F1C40F",
    "cat_custom": COLOR_PALETTE['gold'],
}

# Default Task Categories
CATEGORIES = ["Personal", "Work", "Study", "Health", "Finance", "Custom"]

# Priority Levels
PRIORITIES = ["High", "Medium", "Low"]

# Status Levels
STATUSES = ["Pending", "In Progress", "Completed"]
