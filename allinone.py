import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import qrcode
import pandas as pd
import cv2
import winsound
from datetime import datetime

# Custom MessageBox with auto-close
class AutoCloseMessageBox(tk.Toplevel):
    def __init__(self, master, message, timeout=2000):
        super().__init__(master)
        self.title("Message")
        self.geometry("300x100")
        label = tk.Label(self, text=message)
        label.pack(pady=20)
        self.after(timeout, self.destroy)

# Create the main application
class CombinedApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Student QR Code Generator and Authentication System")
        self.master.geometry("800x600")

        self.csv_file = ""
        self.csv_data = None
        self.scanning = False

        # Create tab control
        self.tab_control = ttk.Notebook(master)

        # Create QR Code Generator tab
        self.qr_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.qr_tab, text="QR Code Generator")
        self.create_qr_tab(self.qr_tab)

        # Create Authentication tab
        self.auth_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.auth_tab, text="Authentication and Attendance")
        self.create_auth_tab(self.auth_tab)

        self.tab_control.pack(expand=1, fill='both')

    def create_qr_tab(self, tab):
        main_frame = tk.Frame(tab, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # CSV Section
        csv_frame = tk.LabelFrame(main_frame, text="CSV File", padx=10, pady=10)
        csv_frame.pack(fill="x", pady=5)
        
        self.qr_label = tk.Label(csv_frame, text="Select CSV File:")
        self.qr_label.pack(side="left")
        
        self.qr_upload_button = tk.Button(csv_frame, text="Upload CSV", command=self.upload_csv_qr)
        self.qr_upload_button.pack(side="left", padx=5)

        # Edit Section
        edit_frame = tk.LabelFrame(main_frame, text="Edit Student Data", padx=10, pady=10)
        edit_frame.pack(fill="x", pady=5)
        
        tk.Label(edit_frame, text="Select Student Name:").pack(side="left")
        self.student_name_var = tk.StringVar(edit_frame)
        self.student_name_var.set("")
        self.student_menu = tk.OptionMenu(edit_frame, self.student_name_var, "")
        self.student_menu.pack(side="left", padx=5)
        
        tk.Label(edit_frame, text="Field to Update:").pack(side="left")
        self.field_var = tk.StringVar(edit_frame)
        self.field_var.set("name")
        field_menu = tk.OptionMenu(edit_frame, self.field_var, "name", "class", "subject", "year")
        field_menu.pack(side="left", padx=5)
        
        tk.Label(edit_frame, text="New Value:").pack(side="left")
        self.new_value_entry = tk.Entry(edit_frame)
        self.new_value_entry.pack(side="left", padx=5)
        
        self.update_button = tk.Button(edit_frame, text="Update", command=self.update_data)
        self.update_button.pack(side="left", padx=5)

        # Add New Student Section
        add_frame = tk.LabelFrame(main_frame, text="Add New Student", padx=10, pady=10)
        add_frame.pack(fill="x", pady=5)

        tk.Label(add_frame, text="Name:").pack(side="left")
        self.new_name_entry = tk.Entry(add_frame)
        self.new_name_entry.pack(side="left", padx=5)

        tk.Label(add_frame, text="Class:").pack(side="left")
        self.new_class_entry = tk.Entry(add_frame)
        self.new_class_entry.pack(side="left", padx=5)

        tk.Label(add_frame, text="Subject:").pack(side="left")
        self.new_subject_entry = tk.Entry(add_frame)
        self.new_subject_entry.pack(side="left", padx=5)

        tk.Label(add_frame, text="Year:").pack(side="left")
        self.new_year_entry = tk.Entry(add_frame)
        self.new_year_entry.pack(side="left", padx=5)

        self.add_button = tk.Button(add_frame, text="Add Student", command=self.add_student)
        self.add_button.pack(side="left", padx=5)

        # Generate QR Codes Section
        generate_frame = tk.LabelFrame(main_frame, text="Generate QR Codes", padx=10, pady=10)
        generate_frame.pack(fill="x", pady=5)
        
        self.generate_button = tk.Button(generate_frame, text="Generate QR Codes", command=self.generate_qr_codes)
        self.generate_button.pack()

        # Status Section
        self.status_label = tk.Label(main_frame, text="Status: Ready", anchor="w")
        self.status_label.pack(fill="x", pady=5)

    def create_auth_tab(self, tab):
        frame = tk.Frame(tab)
        frame.pack(pady=20)

        self.upload_btn = tk.Button(frame, text="Upload CSV File", command=self.upload_csv_auth, width=25)
        self.upload_btn.grid(row=0, column=0, padx=10, pady=5)

        self.qr_code_btn = tk.Button(frame, text="Start Scanning", command=self.start_scan, width=25)
        self.qr_code_btn.grid(row=1, column=0, padx=10, pady=5)

        self.stop_scan_btn = tk.Button(frame, text="Stop Scanning", width=25, command=self.stop_scan)
        self.stop_scan_btn.grid(row=2, column=0, padx=10, pady=5)

        self.auth_status_label = tk.Label(frame, text="", width=50)
        self.auth_status_label.grid(row=3, column=0, padx=10, pady=5)

        self.camera_label = tk.Label(tab)
        self.camera_label.pack(pady=20)

    def upload_csv_qr(self):
        self.upload_csv_common("qr")

    def upload_csv_auth(self):
        self.upload_csv_common("auth")

    def upload_csv_common(self, caller):
        try:
            self.csv_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if self.csv_file:
                self.csv_data = pd.read_csv(self.csv_file)
                self.csv_data.columns = self.csv_data.columns.str.strip().str.lower()  # Normalize column names to lowercase
                # Ensure attendance columns exist
                if 'attendance_date' not in self.csv_data.columns:
                    self.csv_data['attendance_date'] = ""
                if 'attendance_time1' not in self.csv_data.columns:
                    self.csv_data['attendance_time1'] = ""
                if 'attendance_time2' not in self.csv_data.columns:
                    self.csv_data['attendance_time2'] = ""
                print("CSV Columns:", self.csv_data.columns.tolist())  # Debug: Print CSV column names
                self.reset_internal_state()
                if caller == "qr":
                    AutoCloseMessageBox(self.master, "CSV File Uploaded Successfully!")
                    self.update_student_menu()
                elif caller == "auth":
                    AutoCloseMessageBox(self.master, "CSV File Uploaded Successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload CSV file: {str(e)}")

    def reset_internal_state(self):
        # Reset any internal state related to the old CSV file
        self.student_name_var.set("")
        menu = self.student_menu["menu"]
        menu.delete(0, "end")

    def update_student_menu(self):
        if 'name' in self.csv_data.columns:
            self.student_name_var.set(self.csv_data['name'][0])
            menu = self.student_menu["menu"]
            menu.delete(0, "end")
            for name in self.csv_data['name']:
                menu.add_command(label=name, command=lambda value=name: self.student_name_var.set(value))
        else:
            messagebox.showerror("Invalid File", "The CSV file must contain a 'name' column.")

    def update_data(self):
        if not hasattr(self, 'csv_data') or self.csv_data is None:
            messagebox.showerror("No File Uploaded", "Please upload a CSV file first.")
            return

        student_name = self.student_name_var.get()
        field_to_update = self.field_var.get()
        new_value = self.new_value_entry.get()

        if field_to_update == "year" and not new_value.isdigit():
            messagebox.showerror("Invalid Input", "Year must be a number.")
            return
        if field_to_update == "year":
            new_value = int(new_value)

        self.csv_data.loc[self.csv_data['name'] == student_name, field_to_update] = new_value
        self.csv_data.to_csv(self.csv_file, index=False)

        self.new_value_entry.delete(0, tk.END)

        if field_to_update == "name":
            self.update_student_menu()

        self.status_label.config(text="Status: Student data updated successfully.")

    def add_student(self):
        if not hasattr(self, 'csv_data') or self.csv_data is None:
            messagebox.showerror("No File Uploaded", "Please upload a CSV file first.")
            return

        new_name = self.new_name_entry.get()
        new_class = self.new_class_entry.get()
        new_subject = self.new_subject_entry.get()
        new_year = self.new_year_entry.get()

        if not new_year.isdigit():
            messagebox.showerror("Invalid Input", "Year must be a number.")
            return

        new_year = int(new_year)

        new_student = {
            "name": new_name,
            "class": new_class,
            "subject": new_subject,
            "year": new_year
        }

        new_student_df = pd.DataFrame([new_student])

        self.csv_data = pd.concat([self.csv_data, new_student_df], ignore_index=True)
        self.csv_data.to_csv(self.csv_file, index=False)

        self.new_name_entry.delete(0, tk.END)
        self.new_class_entry.delete(0, tk.END)
        self.new_subject_entry.delete(0, tk.END)
        self.new_year_entry.delete(0, tk.END)

        self.update_student_menu()

        self.status_label.config(text="Status: New student added successfully.")

    def generate_qr_codes(self):
        if not hasattr(self, 'csv_data') or self.csv_data is None:
            messagebox.showerror("No File Uploaded", "Please upload a CSV file first.")
            return

        required_columns = {'name', 'class', 'subject', 'year'}

        if not required_columns.issubset(self.csv_data.columns):
            messagebox.showerror("Invalid Data", f"The CSV file must contain the following columns: {', '.join(required_columns)}")
            return

        for index, row in self.csv_data.iterrows():
            try:
                qr_data = f"Name: {row['name']}, Class: {row['class']}, Subject: {row['subject']}, Year: {row['year']}"
                qr = qrcode.make(qr_data)
                qr.save(f"{row['name']}_QR.png")
            except KeyError as e:
                messagebox.showerror("Data Error", f"Missing data for {e}")
                continue

        self.status_label.config(text="Status: QR codes generated successfully.")

    def start_scan(self):
        self.scanning = True
        self.scan_qr_code()

    def stop_scan(self):
        self.scanning = False

    def scan_qr_code(self):
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Using DirectShow backend
            detector = cv2.QRCodeDetector()
            while self.scanning:
                ret, frame = cap.read()
                if ret:
                    data, bbox, _ = detector.detectAndDecode(frame)
                    if data:
                        print(f"QR Data: {data}")  # Debug: Print QR code data
                        self.update_attendance(data)
                    # Resize frame for display
                    frame = cv2.resize(frame, (400, 300))
                    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    img = Image.fromarray(cv2image)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.camera_label.imgtk = imgtk
                    self.camera_label.configure(image=imgtk)
                self.master.update_idletasks()
                self.master.update()
                if not self.scanning:
                    break
            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to access the camera: {str(e)}")
            self.stop_scan()

    def update_attendance(self, data):
        try:
            student_info = [item.split(':', 1)[1].strip().lower() for item in data.split(',')]
            print(f"QR Data Processed: {student_info}")  # Debug: Print processed QR data
            if len(student_info) < 4:
                self.auth_status_label.config(text="Invalid QR data.")
                return
            name, class_, subject, year = student_info[:4]

            if self.csv_data is not None:
                self.csv_data['name'] = self.csv_data['name'].str.replace(" ", "").str.lower()
                self.csv_data['class'] = self.csv_data['class'].str.lower().str.strip()
                self.csv_data['subject'] = self.csv_data['subject'].str.lower().str.strip()
                self.csv_data['year'] = self.csv_data['year'].str.lower().str.strip()
                print(self.csv_data)  # Debug: Print CSV data for comparison

                # Get the current date and time
                current_date = datetime.now().strftime("%Y-%m-%d")
                current_time = datetime.now().strftime("%H:%M:%S")

                # Check if the student has already marked attendance today
                match = self.csv_data[(self.csv_data["name"] == name.replace(" ", "")) & 
                                      (self.csv_data["year"] == year) & 
                                      (self.csv_data["class"] == class_) & 
                                      (self.csv_data["subject"] == subject)]

                if not match.empty:
                    # Check if the student has already marked attendance twice today
                    attendance_records = match[match["attendance_date"] == current_date]

                    if not attendance_records.empty and attendance_records["attendance_time2"].iloc[0]:
                        AutoCloseMessageBox(self.master, "Attendance already marked twice for today.")
                    else:
                        # Mark attendance and update the date and time
                        if attendance_records.empty or not attendance_records["attendance_time1"].iloc[0]:
                            self.csv_data.loc[match.index, "attendance_time1"] = current_time
                            self.csv_data.loc[match.index, "attendance_date"] = current_date
                        else:
                            self.csv_data.loc[match.index, "attendance_time2"] = current_time
                        
                        self.csv_data.to_csv(self.csv_file, index=False)
                        winsound.Beep(1000, 500)  # Frequency 1000 Hz, Duration 500 ms
                        AutoCloseMessageBox(self.master, "Attendance marked successfully. You may go now.")
                else:
                    self.auth_status_label.config(text="Your data not found.")
                    AutoCloseMessageBox(self.master, "Your data not found.")
            else:
                self.auth_status_label.config(text="CSV file not loaded.")
                AutoCloseMessageBox(self.master, "CSV file not loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update attendance: {str(e)}")
            print(f"Failed to update attendance: {str(e)}")  # Debug: Print error

if __name__ == "__main__":
    root = tk.Tk()
    app = CombinedApp(root)
    root.mainloop()