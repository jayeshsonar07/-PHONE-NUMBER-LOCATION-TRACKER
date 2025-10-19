# ----------------------------------------------------------
# 📱 PHONE NUMBER LOCATION TRACKER USING PYTHON
# Developed by Jayesh Sonar🚀
# ----------------------------------------------------------

import tkinter as tk
from tkinter import messagebox, ttk
import phonenumbers
from phonenumbers import geocoder, carrier, timezone, region_code_for_number
import requests
import emoji
import csv
import pyttsx3
import os

# ---------------- INITIAL SETUP -----------------
try:
    engine = pyttsx3.init()
except Exception:
    print("pyttsx3 driver not found. Voice output will be disabled.")
    engine = None

CSV_FILE = "tracked_numbers.csv"
ADMIN_PASSWORD = "Jayesh5604" # Your admin password
CSV_HEADER = [
    "Phone Number", "Registered Region", "Original Carrier",
    "Region Timezone", "User's IP Location"
]

# --- THEME (Sky Blue & White) ---
BG_COLOR = "#FFFFFF"        # White
FRAME_COLOR = "#F0F4F7"     # Very Light Blue/Grey
TEXT_COLOR = "#000000"      # Black
ACCENT_COLOR = "#007BFF"    # A strong, clean blue
SKY_BLUE_COLOR = "#87CEEB"  # Sky Blue
BUTTON_TEXT_COLOR = "#000000" 
HEADER_BG_COLOR = SKY_BLUE_COLOR
HEADER_TEXT_COLOR = "#000000"
DELETE_COLOR = "#D8000C"     # Red for delete button

# ---------------- HELPER FUNCTIONS -----------------

def setup_csv_file():
    """Checks if the CSV file exists. If not, creates it with a header."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

def get_user_ip_location():
    """Fetches the user's current IP location."""
    try:
        res = requests.get("https://ipinfo.io/").json()
        city = res.get("city", "N/A")
        region = res.get("region", "N/A")
        country = res.get("country", "N/A")
        return f"{city}, {region}, {country}"
    except requests.RequestException:
        return "Location fetch error"

def speak(text):
    """Safely attempts to speak the given text."""
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error during speech: {e}")

# ---------------- MAIN APPLICATION CLASS -----------------

class PhoneTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🛰️ Phone Number Inspector (Admin Mode)")
        self.root.geometry("600x650")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Fonts
        self.font_header = ("Arial", 20, "bold")
        self.font_label = ("Arial", 12, "bold")
        self.font_entry = ("Arial", 13)
        self.font_result = ("Arial", 11)
        self.font_footer = ("Arial", 11, "bold")
        
        # Style for Tabs
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[10, 5])
        style.configure("TNotebook", background=BG_COLOR)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=25, font=("Arial", 9))

        self._create_widgets()

    def _create_widgets(self):
        # --- Header ---
        header = tk.Label(self.root, text="📞 Phone Number Inspector", font=self.font_header, bg=HEADER_BG_COLOR, fg=HEADER_TEXT_COLOR, pady=10)
        header.pack(fill="x")

        # --- Tab Control (Notebook) ---
        self.notebook = ttk.Notebook(self.root)
        
        # --- Tab 1: Inspector (Always visible) ---
        self.inspector_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.inspector_tab, text="Inspector")
        
        # --- Tab 2: Admin Login (Hides on login) ---
        self.admin_login_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_login_tab, text="Admin Login")

        # --- Tab 3: History (Created but hidden) ---
        self.history_tab_frame = ttk.Frame(self.notebook)
        # We do NOT add it to the notebook yet.

        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # --- Populate Tabs ---
        self._create_inspector_tab()
        self._create_admin_login_tab()
        self._create_history_tab()
        
        # --- Footer ---
        footer = tk.Label(self.root, text="Developed by Jayesh Sonar 🚀", font=self.font_footer, bg=BG_COLOR, fg=ACCENT_COLOR, pady=10)
        footer.pack(side="bottom", fill="x")

    def _create_inspector_tab(self):
        """Populates the Inspector tab."""
        input_frame = tk.Frame(self.inspector_tab, bg=BG_COLOR)
        input_frame.pack(pady=20, padx=20, fill="x")

        tk.Label(input_frame, text="Enter Phone Number (+CountryCode):", font=self.font_label, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(0, 5))
        self.entry_number = tk.Entry(input_frame, font=self.font_entry, width=30, justify="center", bg=FRAME_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, bd=2, relief="flat")
        self.entry_number.insert(0, "+91")
        self.entry_number.pack(ipady=8, fill="x") 

        button_frame = tk.Frame(self.inspector_tab, bg=BG_COLOR)
        button_frame.pack(pady=10)

        track_button = tk.Button(button_frame, text="🔍 INSPECT", font=self.font_label, bg=SKY_BLUE_COLOR, fg=BUTTON_TEXT_COLOR, command=self.track_number, relief="flat", activebackground="#A0DFFF", activeforeground=BUTTON_TEXT_COLOR, padx=10, pady=5)
        track_button.pack(side="left", padx=10)
        
        clear_button = tk.Button(button_frame, text="❌ CLEAR", font=self.font_label, bg=FRAME_COLOR, fg=BUTTON_TEXT_COLOR, command=self.clear_fields, relief="flat", activebackground="#E0E0E0", activeforeground=BUTTON_TEXT_COLOR, padx=10, pady=5)
        clear_button.pack(side="left", padx=10)

        result_frame = tk.Frame(self.inspector_tab, bg=FRAME_COLOR, bd=1, relief="solid")
        result_frame.pack(pady=10, padx=20, fill="x", ipady=10)

        self.location_var = tk.StringVar(value="-- N/A --")
        self.carrier_var = tk.StringVar(value="-- N/A --")
        self.timezone_var = tk.StringVar(value="-- N/A --")
        self.userloc_var = tk.StringVar(value="-- N/A --")

        self.create_result_row(result_frame, "📍 Registered Region:", self.location_var, 0)
        self.create_result_row(result_frame, "📡 Original Carrier (No MNP):", self.carrier_var, 1)
        self.create_result_row(result_frame, "⏰ Region's Timezone:", self.timezone_var, 2)
        self.create_result_row(result_frame, "🌐 Your (User's) IP Location:", self.userloc_var, 3)

    def _create_admin_login_tab(self):
        """Populates the Admin Login tab."""
        login_frame = tk.Frame(self.admin_login_tab, bg=BG_COLOR)
        login_frame.pack(pady=50, padx=30)
        
        tk.Label(login_frame, text="Enter Admin Password to View History", font=self.font_label, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(10, 10))
        self.password_entry = tk.Entry(login_frame, font=self.font_entry, justify="center", bg=FRAME_COLOR, fg=TEXT_COLOR, show="*", bd=2, relief="flat")
        self.password_entry.pack(ipady=8, fill="x", pady=10)
        login_button = tk.Button(login_frame, text="🔓 LOGIN", font=self.font_label, bg=ACCENT_COLOR, fg="#FFFFFF", command=self.check_admin_login, relief="flat", padx=10, pady=5)
        login_button.pack(pady=20)

    def _create_history_tab(self):
        """Populates the (initially hidden) History tab frame."""
        # --- NEW: Button Frame for admin actions ---
        admin_button_frame = tk.Frame(self.history_tab_frame, bg=BG_COLOR)
        admin_button_frame.pack(pady=10, fill="x")

        refresh_button = tk.Button(admin_button_frame, text="🔄 Refresh Data", font=("Arial", 10, "bold"), bg=ACCENT_COLOR, fg="#FFFFFF", relief="flat", command=self.load_csv_data)
        refresh_button.pack(side="left", padx=10)
        
        delete_button = tk.Button(admin_button_frame, text="Delete Selected", font=("Arial", 10, "bold"), bg=FRAME_COLOR, fg=DELETE_COLOR, relief="flat", command=self.delete_selected_history)
        delete_button.pack(side="left", padx=10)
        
        clear_all_button = tk.Button(admin_button_frame, text="Clear All History", font=("Arial", 10, "bold"), bg=DELETE_COLOR, fg="#FFFFFF", relief="flat", command=self.clear_all_history)
        clear_all_button.pack(side="left", padx=10)

        # --- Treeview for displaying CSV data ---
        tree_frame = tk.Frame(self.history_tab_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        tree_scroll_y = tk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = tk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.history_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode='extended' # Allow multi-select
        )
        self.history_tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=self.history_tree.yview)
        tree_scroll_x.config(command=self.history_tree.xview)

        self.history_tree["columns"] = ("Number", "Region", "Carrier", "Timezone", "IP Location")
        self.history_tree.column("#0", width=0, stretch=tk.NO)
        self.history_tree.column("Number", anchor=tk.W, width=100)
        self.history_tree.column("Region", anchor=tk.W, width=100)
        self.history_tree.column("Carrier", anchor=tk.W, width=80)
        self.history_tree.column("Timezone", anchor=tk.W, width=100)
        self.history_tree.column("IP Location", anchor=tk.W, width=120)

        self.history_tree.heading("#0", text="", anchor=tk.W)
        self.history_tree.heading("Number", text="Phone Number", anchor=tk.W)
        self.history_tree.heading("Region", text="Region", anchor=tk.W)
        self.history_tree.heading("Carrier", text="Carrier", anchor=tk.W)
        self.history_tree.heading("Timezone", text="Timezone", anchor=tk.W)
        self.history_tree.heading("IP Location", text="User IP", anchor=tk.W)

    def check_admin_login(self):
        """Checks the entered password."""
        entered_password = self.password_entry.get()
        if entered_password == ADMIN_PASSWORD:
            messagebox.showinfo("Login Success", "Welcome, Admin! Access granted.")
            self.notebook.forget(self.admin_login_tab)
            self.notebook.add(self.history_tab_frame, text="View History 🔏")
            self.notebook.select(self.history_tab_frame)
            self.load_csv_data()
        else:
            messagebox.showerror("Login Failed", "Incorrect Password. Please try again.")
            self.password_entry.delete(0, tk.END)

    def create_result_row(self, parent, label_text, var, row):
        """Helper function to create a result row in the grid."""
        label = tk.Label(parent, text=label_text, font=self.font_label, bg=FRAME_COLOR, fg=ACCENT_COLOR)
        label.grid(row=row, column=0, padx=10, pady=8, sticky="w")
        value = tk.Label(parent, textvariable=var, font=self.font_result, bg=FRAME_COLOR, fg=TEXT_COLOR)
        value.grid(row=row, column=1, padx=10, pady=8, sticky="w")

    def clear_fields(self):
        """Resets the input and output fields."""
        self.entry_number.delete(0, tk.END)
        self.entry_number.insert(0, "+91")
        self.location_var.set("-- N/A --")
        self.carrier_var.set("-- N/A --")
        self.timezone_var.set("-- N/A --")
        self.userloc_var.set("-- N/A --")

    def load_csv_data(self):
        """Loads data from the CSV file into the Treeview."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        try:
            with open(CSV_FILE, "r", newline="", encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for i, row in enumerate(reader):
                    if row: # Ensure row is not empty
                        self.history_tree.insert(parent="", index="end", iid=i, text="", values=row)
        except FileNotFoundError:
            speak("History file not found. It will be created on the first track.")
        except StopIteration:
            print("History file is empty.") # CSV file is empty
        except Exception as e:
            print(f"Error reading CSV: {e}")

    # --- NEW: Delete Selected History ---
    def delete_selected_history(self):
        """Deletes selected rows from the Treeview and the CSV file."""
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select one or more rows to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected_items)} selected row(s)?"):
            return

        # Get the values of the rows to be deleted
        rows_to_delete = set()
        for item in selected_items:
            rows_to_delete.add(tuple(self.history_tree.item(item)['values']))

        try:
            # Read all data from CSV
            with open(CSV_FILE, "r", newline="", encoding='utf-8') as f:
                reader = csv.reader(f)
                all_data = list(reader)
            
            # Filter out the rows to be deleted
            rows_to_keep = [row for row in all_data[1:] if tuple(row) not in rows_to_delete]
            
            # Write the remaining data back to the CSV
            with open(CSV_FILE, "w", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADER)
                writer.writerows(rows_to_keep)

            messagebox.showinfo("Success", "Selected rows have been deleted.")
            self.load_csv_data() # Refresh the table

        except Exception as e:
            messagebox.showerror("Error", f"Could not write to CSV file: {e}")

    # --- NEW: Clear All History ---
    def clear_all_history(self):
        """Deletes all history from the Treeview and CSV file."""
        if not messagebox.askyesno("Confirm Clear All", "Are you sure you want to delete ALL history? This cannot be undone."):
            return
        
        try:
            # Overwrite the CSV file with only the header
            with open(CSV_FILE, "w", newline="", encoding='utf-T8') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADER)
            
            messagebox.showinfo("Success", "All history has been cleared.")
            self.load_csv_data() # Refresh the table (it will be empty)
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not clear CSV file: {e}")

    def track_number(self):
        """Main function to track the phone number."""
        number = self.entry_number.get()

        if not number:
            messagebox.showwarning("Input Error", "Please enter a phone number.")
            return

        try:
            parsed_number = phonenumbers.parse(number)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number format!")

            location = geocoder.description_for_number(parsed_number, "en") or "N/A"
            sim_carrier = carrier.name_for_number(parsed_number, "en") or "N/A"
            time_zones = ", ".join(timezone.time_zones_for_number(parsed_number)) or "N/A"
            
            country_code = region_code_for_number(parsed_number)
            flag = ""
            try:
                flag = emoji.emojize(f":{country_code.lower()}:", language='alias')
            except:
                pass 

            user_loc = get_user_ip_location()

            # --- 1. FIRST: Update the GUI ---
            self.location_var.set(f"{location} {flag}")
            self.carrier_var.set(sim_carrier)
            self.timezone_var.set(time_zones)
            self.userloc_var.set(user_loc)
            self.root.update_idletasks() 

            # --- 2. Save to CSV file (FIXED) ---
            with open(CSV_FILE, "a", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([number, location, sim_carrier, time_zones, user_loc])
            
            # --- 3. SECOND: Give Voice Output ---
            speak(f"Inspection complete. Number is registered in {location}. Original Carrier is {sim_carrier}.")
            
            # --- 4. LAST: Popup is REMOVED ---
            # (No success popup here as requested)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.location_var.set("-- Error --")
            self.carrier_var.set("-- Error --")
            self.timezone_var.set("-- Error --")
            self.userloc_var.set("-- Error --")
            
            self.root.update_idletasks()
            speak("Error! Please check the number and try again.")

# ---------------- SCRIPT EXECUTION -----------------
if __name__ == "__main__":
    setup_csv_file()
    root = tk.Tk()
    app = PhoneTrackerApp(root)
    root.mainloop()