import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import cv2
import pandas as pd
from PIL import Image, ImageTk

# Create the GUI application
class StudentAuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Authentication and Attendance System")
        self.root.geometry("800x600")

        self.csv_file = ""
        self.csv_data = None
        self.scanning = False

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        self.upload_btn = tk.Button(frame, text="Upload CSV File", command=self.upload_csv, width=25)
        self.upload_btn.grid(row=0, column=0, padx=10, pady=5)

        self.qr_code_btn = tk.Button(frame, text="Start Scanning", command=self.start_scan, width=25)
        self.qr_code_btn.grid(row=1, column=0, padx=10, pady=5)

        self.stop_scan_btn = tk.Button(frame, text="Stop Scanning", command=self.stop_scan, width=25)
        self.stop_scan_btn.grid(row=2, column=0, padx=10, pady=5)

        self.status_label = tk.Label(frame, text="", width=50)
        self.status_label.grid(row=3, column=0, padx=10, pady=5)

        self.camera_label = tk.Label(self.root)
        self.camera_label.pack(pady=20)

    def upload_csv(self):
        try:
            self.csv_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if self.csv_file:
                self.csv_data = pd.read_csv(self.csv_file)
                self.csv_data.columns = self.csv_data.columns.str.strip().str.lower()  # Ensure columns are lower case
                messagebox.showinfo("Success", "CSV File Uploaded Successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload CSV file: {str(e)}")

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
                self.root.update_idletasks()
                self.root.update()
                if not self.scanning:
                    break
            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to access the camera: {str(e)}")
            self.stop_scan()

    def update_attendance(self, data):
        try:
            student_info = [item.strip().lower() for item in data.split(',')]
            print(f"QR Data Processed: {student_info}")  # Debug: Print processed QR data
            if len(student_info) < 4:
                self.status_label.config(text="Invalid QR data.")
                return
            name, year, course, subjects = student_info[:4]
            if self.csv_data is not None:
                name = name.replace(" ", "")
                self.csv_data['name'] = self.csv_data['name'].str.replace(" ", "").str.lower()
                print(self.csv_data)  # Debug: Print CSV data for comparison
                match = ((self.csv_data["name"] == name) & 
                         (self.csv_data["year"].astype(str).str.lower().str.strip() == year) & 
                         (self.csv_data["course"].str.lower().str.strip() == course) & 
                         (self.csv_data["subjects"].str.lower().str.strip() == subjects)).any()
                if match:
                    self.csv_data.loc[self.csv_data["name"] == name, "present"] = "Yes"
                    self.csv_data.to_csv(self.csv_file, index=False)
                    self.status_label.config(text="You may go now.")
                    messagebox.showinfo("Attendance Update", "Attendance marked successfully. You may go now.")
                else:
                    self.status_label.config(text="Your data not found.")
                    messagebox.showinfo("Attendance Update", "Your data not found.")
            else:
                self.status_label.config(text="CSV file not loaded.")
                messagebox.showinfo("Attendance Update", "CSV file not loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update attendance: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentAuthApp(root)
    root.mainloop()
