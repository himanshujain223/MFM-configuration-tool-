import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import zipfile
import hashlib
import shutil


class EntryLabelPair(tk.Frame):
    def __init__(self, parent, label_text):
        super().__init__(parent)
        
        self.label = tk.Label(self, text=label_text)
        self.label.pack(side=tk.TOP, padx=5, pady=5)
        
        self.entry = tk.Entry(self)
        self.entry.pack(side=tk.BOTTOM, padx=5, pady=5)

class SensorConfigurationPopup(tk.Toplevel):
    def __init__(self, parent, default_values):
        super().__init__(parent)
        self.title("Sensor Configuration")
        
        # Create a frame to hold label and entry pairs
        self.labels_entries_frame = tk.Frame(self)
        self.labels_entries_frame.pack()
        
        labels = ["Name", "Position", "BSD Type ID", "BSD Adap ID"]
        self.entry_pairs = []
        for label_text in labels:
            pair = EntryLabelPair(self.labels_entries_frame, label_text)
            pair.pack(side=tk.LEFT, padx=5, pady=5)
            self.entry_pairs.append(pair)
        
        # Initialize entry values with default values
        for pair, default_value in zip(self.entry_pairs, default_values):
            pair.entry.insert(tk.END, default_value)
        
        self.btn_edit = tk.Button(self, text="Edit", command=self.edit_row)
        self.btn_edit.pack(pady=10)

        self.btn_remove = tk.Button(self, text="Remove", command=self.remove_row)
        self.btn_remove.pack(pady=10)

        self.btn_save = tk.Button(self, text="Save", command=self.save)
        self.btn_save.pack(pady=10)
        
    def edit_row(self):
        for pair in self.entry_pairs:
            pair.entry.config(state=tk.NORMAL)

    def remove_row(self):
        for pair in self.entry_pairs:
            pair.entry.delete(0, tk.END)
            
    def save(self):
        values = [pair.entry.get() for pair in self.entry_pairs]
        # Perform save operation with values

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Label and Entry Demo")
        self.geometry("400x200")

        self.btn_configure_sensor = tk.Button(self, text="Configure Sensor", command=self.configure_sensor)
        self.btn_configure_sensor.pack(pady=10)
        
    def configure_sensor(self):
        default_values = ["", "", "", ""]  # Example default values
        popup = SensorConfigurationPopup(self, default_values)
        popup.grab_set()  # Prevent interaction with main window
        popup.focus_set()  # Focus on the popup window
        popup.wait_window()  # Wait until popup window is closed

class BpscfgConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bpscfg Configurator")
        self.geometry("800x600")

        self.txt_editor = scrolledtext.ScrolledText(self, width=100, height=30)
        self.txt_editor.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)

        btn_open_bpscfg = tk.Button(btn_frame, text="Open .bpscfg File", command=self.open_bpscfg)
        btn_open_bpscfg.pack(side=tk.LEFT, padx=5, pady=5)

        btn_sensor_config = tk.Button(btn_frame, text="Sensor Configuration", command=self.open_sensor_configuration)
        btn_sensor_config.pack(side=tk.LEFT, padx=5, pady=5)

        btn_save = tk.Button(btn_frame, text="Save", command=self.save_file)
        btn_save.pack(side=tk.LEFT, padx=5, pady=5)

        self.bpscfg_file_path = None

    def open_bpscfg(self):
        bpscfg_file_path = filedialog.askopenfilename(filetypes=[("Bpscfg Files", "*.bpscfg"), ("All Files", "*.*")])
        if bpscfg_file_path:
            self.bpscfg_file_path = bpscfg_file_path
            self.extract_bpscfg_file()

    def extract_bpscfg_file(self):
        # Change .bpscfg extension to .zip
        zip_file_path = os.path.splitext(self.bpscfg_file_path)[0] + ".zip"
        os.rename(self.bpscfg_file_path, zip_file_path)

        dir_path = os.path.dirname(zip_file_path)
        extractedfile_path = os.path.join(dir_path, 'temp')

        # Unzip the .zip file
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(path=extractedfile_path)

        # Change .mfm extension to .zip
        mfm_file_path = os.path.join(extractedfile_path, "Currencies", "Config.mfm")
        mfm_zip_file_path = os.path.splitext(mfm_file_path)[0] + ".zip"
        os.rename(mfm_file_path, mfm_zip_file_path)
        mfm_extractedpath = os.path.join(extractedfile_path, 'Currencies', 'Config')

        # Unzip the .zip file
        with zipfile.ZipFile(mfm_zip_file_path, "r") as zip_ref:
            zip_ref.extractall(path=mfm_extractedpath)

        os.remove(os.path.join(extractedfile_path, "Currencies", "Config.zip"))

        mfm_config_file_path = os.path.join(mfm_extractedpath, "MFMConfig.xml")
        with open(mfm_config_file_path, "r") as mfm_config_file:
            self.txt_editor.delete(1.0, tk.END)
            self.txt_editor.insert(tk.END, mfm_config_file.read())

    def save_file(self):
        if self.bpscfg_file_path:
            # Get the content of the text box
            text_content = self.txt_editor.get(1.0, tk.END)

            # Write the content to the MFMConfig.xml file
            mfm_config_file_path = os.path.join(os.path.dirname(self.bpscfg_file_path), "temp", "Currencies", "Config", "MFMConfig.xml")
            with open(mfm_config_file_path, "w") as mfm_config_file:
                mfm_config_file.write(text_content)

            h = hashlib.sha1()
            with open(mfm_config_file_path, 'rb') as file:
                chunk = 0
                while chunk != b'':
                    chunk = file.read(1024)
                    h.update(chunk)
            hash_code = h.hexdigest()

            # Update hash code in Manifest.xml
            manifest_file_path = os.path.join(os.path.dirname(self.bpscfg_file_path), "temp", "Currencies",
                                               "Config", "Manifest.xml")
            with open(manifest_file_path, "r") as manifest_file:
                manifest_content = manifest_file.read()
                hash_start_index = manifest_content.find("hash=") + len("hash=")
                hash_end_index = manifest_content.find("\n", hash_start_index)
                manifest_content = manifest_content[:hash_start_index] + hash_code + manifest_content[hash_end_index:]

            with open(manifest_file_path, "w") as manifest_file:
                manifest_file.write(manifest_content)

            # Convert Config folder to .zip
            config_folder_path = os.path.join(os.path.dirname(self.bpscfg_file_path), "temp", "Currencies", "Config")
            output_zip_path = os.path.join(os.path.dirname(self.bpscfg_file_path), "temp", "Currencies", "Config")

            # You can call the function to convert to zip here
            # convert_to_zip(config_folder_path, output_zip_path)

    def open_sensor_configuration(self):
        # Read default values from the uploaded file
        mfm_config_file = ["","", "", ""]

        # Open Sensor Configuration Popup
        SensorConfigurationPopup(self,mfm_config_file)


if __name__ == "__main__":
    app = BpscfgConfigurator()
    app.mainloop()
