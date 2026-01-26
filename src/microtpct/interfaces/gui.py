#  run GUI application for MicroTPCT
#  python3 src/microtpct/interfaces/gui.py

# pip install pyyaml
### for Linux/WSL users who do not have tkinter installed:
# sudo apt update
# sudo apt install python3-tk

import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from datetime import datetime

repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(repo_root))

from tests.minimal_pipeline import minimal_pipeline_gui
import yaml

config_path = Path(__file__).parent.parent / "config" / "defaults.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

ALGORITHMS = ["boyer_moore", 
              "match_ahocorasick", 
              "match_ahocorasick_rs", 
              "match_blast_basic", 
              "match_blast", 
              "match_find", 
              "match_in" ]

# --- Color Scheme ---
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
SUCCESS_COLOR = "#27AE60"
ERROR_COLOR = "#E74C3C"
BG_COLOR = "#ECF0F1"
TEXT_COLOR = "#2C3E50"
LIGHT_TEXT = "#FFFFFF"

class MicroTPCTGUI:
    """Main GUI class for the MicroTPCT peptide analysis pipeline."""
    
    def __init__(self, root):
        """
        Initialize the MicroTPCT GUI application.
        
        Args:
            root (tk.Tk): The root tkinter window object.
        
        Creates the main window layout with 4 columns:
        - Column 0: Input Files (FASTA, peptide, output directory)
        - Column 1: Configuration (algorithm, wildcard settings) & Save Options (format, filename, timestamp)
        - Column 2: Actions (run, save, clear, exit buttons)
        """
        self.root = root
        self.root.title("MicroTPCT")
        #self.root.geometry("1000x600")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(900, 500)

        # Store matching results for manual saving
        self.matching_results = None

        # Input and output variables
        self.fasta_path = tk.StringVar()
        self.xlsx_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.algorithm = tk.StringVar(value=ALGORITHMS[0])
        self.wildcard_enabled = tk.BooleanVar(value=False)
        self.wildcard_choice = tk.StringVar(value="X")
        self.save_excel = tk.BooleanVar(value=True)
        self.save_csv = tk.BooleanVar(value=False)
        self.include_timestamp = tk.BooleanVar(value=True)
        self.filename_custom = tk.StringVar(value="results")

        # --- HEADER ---
        header_frame = tk.Frame(root, bg=PRIMARY_COLOR, height=60)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        
        title_label = tk.Label(header_frame, text="MicroTPCT Pipeline", 
                               font=("Helvetica", 24, "bold"), 
                               fg=LIGHT_TEXT, bg=PRIMARY_COLOR)
        title_label.pack(pady=10)

        # --- LEFT COLUMN: Input Files ---
        left_frame = tk.LabelFrame(root, text="Input Files", padx=15, pady=15,
                                   font=("Helvetica", 11, "bold"),
                                   fg=TEXT_COLOR, bg=BG_COLOR,
                                   relief=tk.RIDGE, borderwidth=2)
        left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self._create_file_input(left_frame, "Proteome FASTA", self.fasta_path, 
                               self.browse_fasta, 0)
        self._create_file_input(left_frame, "Peptide (XLSX/CSV)", self.xlsx_path, 
                               self.browse_xlsx, 1)
        self._create_file_input(left_frame, "Output Directory", self.output_dir, 
                               self.browse_output, 2)

        # --- MIDDLE COLUMN: Algorithm, Configuration & Save Options ---
        middle_frame = tk.Frame(root, bg=BG_COLOR)
        middle_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Configuration section
        config_frame = tk.LabelFrame(middle_frame, text="Configuration", padx=15, pady=15,
                                     font=("Helvetica", 11, "bold"),
                                     fg=TEXT_COLOR, bg=BG_COLOR,
                                     relief=tk.RIDGE, borderwidth=2)
        config_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        tk.Label(config_frame, text="Algorithm", font=("Helvetica", 10),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        algo_menu = tk.OptionMenu(config_frame, self.algorithm, *ALGORITHMS)
        algo_menu.config(font=("Helvetica", 10), bg=LIGHT_TEXT)
        algo_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        separator = tk.Frame(config_frame, height=2, bg=PRIMARY_COLOR)
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        wildcard_check = tk.Checkbutton(config_frame, text="Enable Wildcard?", 
                                       variable=self.wildcard_enabled,
                                       font=("Helvetica", 10), bg=BG_COLOR,
                                       fg=TEXT_COLOR)
        wildcard_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        tk.Label(config_frame, text="Wildcard Char", font=("Helvetica", 10),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=3, column=0, sticky="w", pady=5)
        wildcard_entry = tk.Entry(config_frame, textvariable=self.wildcard_choice, 
                                 width=5, font=("Helvetica", 10))
        wildcard_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # Save Options section
        save_frame = tk.LabelFrame(middle_frame, text="Save Options", padx=15, pady=15,
                                   font=("Helvetica", 11, "bold"),
                                   fg=TEXT_COLOR, bg=BG_COLOR,
                                   relief=tk.RIDGE, borderwidth=2)
        save_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Format selection
        tk.Label(save_frame, text="Output Format", font=("Helvetica", 10, "bold"),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, columnspan=2, sticky="w")
        
        tk.Checkbutton(save_frame, text="Excel (.xlsx)", variable=self.save_excel,
                      font=("Helvetica", 9), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky="w", pady=3)
        tk.Checkbutton(save_frame, text="CSV (.csv)", variable=self.save_csv,
                      font=("Helvetica", 9), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=1, sticky="w", pady=3)

        separator2 = tk.Frame(save_frame, height=2, bg=PRIMARY_COLOR)
        separator2.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        # Filename options
        tk.Label(save_frame, text="Filename", font=("Helvetica", 10, "bold"),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=3, column=0, columnspan=2, sticky="w")
        
        tk.Label(save_frame, text="Custom Name", font=("Helvetica", 9),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=4, column=0, sticky="w", pady=5)
        filename_entry = tk.Entry(save_frame, textvariable=self.filename_custom, 
                                 width=20, font=("Helvetica", 9))
        filename_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Checkbutton(save_frame, text="Add Timestamp", variable=self.include_timestamp,
                      font=("Helvetica", 9), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=5, column=0, columnspan=2, sticky="w", pady=3)

        # --- RIGHT COLUMN: Actions ---
        right_frame = tk.LabelFrame(root, text="Actions", padx=15, pady=15,
                                    font=("Helvetica", 11, "bold"),
                                    fg=LIGHT_TEXT, bg=PRIMARY_COLOR,
                                    relief=tk.RIDGE, borderwidth=2)
        right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.run_btn = tk.Button(right_frame, text="Run Pipeline", command=self.run_threaded, 
                           bg=SUCCESS_COLOR, fg=LIGHT_TEXT,
                           font=("Helvetica", 12, "bold"), padx=15, pady=15,
                           relief=tk.RAISED, bd=2, cursor="hand2",
                           activebackground="#1E8449")
        self.run_btn.grid(row=0, column=0, sticky="nsew", pady=5)

        self.save_btn = tk.Button(right_frame, text="Save Results", command=self.save_manually,
                             bg="#F39C12", fg=LIGHT_TEXT,
                             font=("Helvetica", 11, "bold"), padx=15, pady=10,
                             relief=tk.RAISED, bd=1, cursor="hand2",
                             state=tk.DISABLED,
                             activebackground="#D68910")
        self.save_btn.grid(row=1, column=0, sticky="ew", pady=5)

        clear_btn = tk.Button(right_frame, text="Clear", command=self.clear,
                             bg=SECONDARY_COLOR, fg=LIGHT_TEXT,
                             font=("Helvetica", 11, "bold"), padx=15, pady=10,
                             relief=tk.RAISED, bd=1, cursor="hand2",
                             activebackground="#2874A6")
        clear_btn.grid(row=2, column=0, sticky="ew", pady=5)

        exit_btn = tk.Button(right_frame, text="Exit", command=self.root.quit,
                            bg=ERROR_COLOR, fg=LIGHT_TEXT,
                            font=("Helvetica", 11, "bold"), padx=15, pady=10,
                            relief=tk.RAISED, bd=1, cursor="hand2",
                            activebackground="#C0392B")
        exit_btn.grid(row=3, column=0, sticky="ew", pady=5)

        # --- Status Bar ---
        self.status_label = tk.Label(root, text="Status: Ready", 
                                    font=("Helvetica", 10), fg="blue",
                                    bg=BG_COLOR, relief=tk.SUNKEN, bd=1)
        self.status_label.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # Configure grid weights
        root.columnconfigure(0, weight=1)  # Inputs
        root.columnconfigure(1, weight=1)  # Config + Save
        root.columnconfigure(2, weight=1)  # Actions 
        root.rowconfigure(1, weight=1)

    def _create_file_input(self, parent, label_text, var, command, row):
        """
        Create a consistent file input row with label, entry field, and browse button.
        
        Args:
            parent (tk.Frame): The parent frame to place the input row in.
            label_text (str): The label text to display (e.g., "Proteome FASTA").
            var (tk.StringVar): The StringVar to bind the file path to.
            command (callable): The function to call when "Browse" button is clicked.
            row (int): The grid row number to place the input row at.
        
        Creates a formatted row with:
        - Label (column 0)
        - Entry field (column 1)
        - Browse button (column 2)
        """
        tk.Label(parent, text=label_text, font=("Helvetica", 10),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row, column=0, sticky="w", pady=5)
        entry = tk.Entry(parent, textvariable=var, width=25, 
                        font=("Helvetica", 10), bg=LIGHT_TEXT, fg=TEXT_COLOR)
        entry.grid(row=row, column=1, padx=5, pady=5)
        btn = tk.Button(parent, text="Browse", command=command,
                       bg=SECONDARY_COLOR, fg=LIGHT_TEXT,
                       font=("Helvetica", 9), padx=10, pady=5,
                       relief=tk.RAISED, bd=1, cursor="hand2")
        btn.grid(row=row, column=2, padx=5, pady=5)

    def browse_fasta(self):
        """
        Open a file dialog to select a FASTA file.
        
        Updates self.fasta_path with the selected file path.
        Filters for .fasta and .fa file extensions.
        """
        self.fasta_path.set(filedialog.askopenfilename(filetypes=[("FASTA", "*.fasta *.fa")]))
    
    def browse_xlsx(self):
        """
        Open a file dialog to select a peptide file (Excel or CSV).
        
        Updates self.xlsx_path with the selected file path.
        Filters for .xlsx and .csv file extensions.
        """
        self.xlsx_path.set(filedialog.askopenfilename(filetypes=[("Peptide", "*.xlsx *.csv")]))

    def browse_output(self):
        """
        Open a directory dialog to select the output directory.
        
        Updates self.output_dir with the selected directory path.
        """
        self.output_dir.set(filedialog.askdirectory())

    def clear(self):
        """
        Clear all input fields and reset to default values.
        
        Resets:
        - File paths (FASTA, peptide, output directory)
        - Algorithm selection to first option
        - Wildcard settings to disabled
        - Matching results to None
        - Save button state to disabled
        """
        self.fasta_path.set("")
        self.xlsx_path.set("")
        self.output_dir.set("")
        self.algorithm.set(ALGORITHMS[0])
        self.wildcard_enabled.set(False)
        self.wildcard_choice.set("X")
        self.matching_results = None
        self.save_btn.config(state=tk.DISABLED)

    def run_threaded(self):
        """
        Launch the pipeline execution in a separate thread.
        
        This prevents the UI from freezing during pipeline processing.
        Validates inputs before starting the thread.
        Disables the Run button and updates status during execution.
        """
        if not self._validate_inputs():
            return
        
        self.run_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Running...", fg="orange")
        self.root.update()
        
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        """
        Execute the MicroTPCT pipeline with selected parameters.
        
        Calls minimal_pipeline_gui() to:
        1. Read FASTA proteome file
        2. Read peptide file (XLSX or CSV)
        3. Run peptide matching algorithm
        4. Store results for manual saving
        
        Updates status label and enables Save button on success.
        Shows error dialog if pipeline fails.
        """
        try:
            self.status_label.config(text="Status: Processing...", fg="orange")
            self.root.update()
            
            self.matching_results = minimal_pipeline_gui(
                fasta_path=Path(self.fasta_path.get()),
                peptide_path=Path(self.xlsx_path.get()),
                output_path=Path(self.output_dir.get()),
                algorithm=self.algorithm.get(),
                wildcard=self.wildcard_choice.get() if self.wildcard_enabled.get() else None,
                config=config,
            )
            
            self.status_label.config(text="Status: Complete ✓ (Save results manually)", fg=SUCCESS_COLOR)
            self.save_btn.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "✓ Pipeline completed!\nClick 'Save Results' to save.")
            
        except Exception as e:
            self.status_label.config(text="Status: Error ✗", fg=ERROR_COLOR)
            messagebox.showerror("Error", f"✗ Error: {str(e)}")
        finally:
            self.run_btn.config(state=tk.NORMAL)

    def save_manually(self):
        """
        Manually save pipeline results with user-specified options.
        
        Validates that:
        - Results exist (pipeline has been run)
        - Save options are valid (format and filename)
        
        Uses settings from Save Options panel:
        - Output format (Excel, CSV, or both)
        - Custom filename
        - Timestamp inclusion
        
        Shows success or error dialog after saving.
        """
        if not self.matching_results:
            messagebox.showerror("Error", "No results to save. Run pipeline first.")
            return
        
        if not self._validate_save_inputs():
            return
        
        try:
            self._save_results(self.matching_results)
            messagebox.showinfo("Success", "✓ Results saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"✗ Failed to save: {str(e)}")

    def _save_results(self, matching_results):
        """
        Convert matching results to requested file formats and save.
        
        Args:
            matching_results: The MatchResult object from the pipeline.
        
        Saves to output directory with:
        - Filename: custom name + optional timestamp
        - Formats: Excel (.xlsx) and/or CSV (.csv) as selected
        
        Converts MatchResult object to pandas DataFrame before saving.
        Updates status label with saved filename.
        
        Raises:
            Exception: If conversion or saving fails.
        """
        import pandas as pd
        
        output_path = Path(self.output_dir.get())
        
        # Build filename
        filename = self.filename_custom.get()
        if self.include_timestamp.get():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}"
        
        try:
            # Convert results to DataFrame
            if hasattr(matching_results, 'to_dataframe'):
                df = matching_results.to_dataframe()
            else:
                df = pd.DataFrame([vars(matching_results)])
            
            # Save as Excel
            if self.save_excel.get():
                excel_file = output_path / f"{filename}.xlsx"
                df.to_excel(excel_file, index=False)
                self.status_label.config(text=f"Status: Saved to {excel_file.name}", fg=SUCCESS_COLOR)
                print(f"✓ Saved: {excel_file}")
            
            # Save as CSV
            if self.save_csv.get():
                csv_file = output_path / f"{filename}.csv"
                df.to_csv(csv_file, index=False)
                self.status_label.config(text=f"Status: Saved to {csv_file.name}", fg=SUCCESS_COLOR)
                print(f"✓ Saved: {csv_file}")
        
        except Exception as e:
            raise Exception(f"Could not save results: {e}")
    
    def _validate_inputs(self):
        """
        Validate that all required input files exist and are selected.
        
        Returns:
            bool: True if all inputs are valid, False otherwise.
        
        Checks:
        - FASTA file is selected and exists
        - Peptide file is selected and exists
        - Output directory is selected
        
        Shows error dialogs for missing or invalid inputs.
        """
        if not self.fasta_path.get():
            messagebox.showerror("Error", "Select FASTA file")
            return False
        if not Path(self.fasta_path.get()).exists():
            messagebox.showerror("Error", "FASTA file not found")
            return False
        if not self.xlsx_path.get():
            messagebox.showerror("Error", "Select peptide file")
            return False
        if not Path(self.xlsx_path.get()).exists():
            messagebox.showerror("Error", "Peptide file not found")
            return False
        if not self.output_dir.get():
            messagebox.showerror("Error", "Select output directory")
            return False
        return True

    def _validate_save_inputs(self):
        """
        Validate that save options are valid before saving.
        
        Returns:
            bool: True if save options are valid, False otherwise.
        
        Checks:
        - At least one output format is selected (Excel or CSV)
        - Custom filename is provided (not empty)
        
        Shows error dialogs for invalid save options.
        """
        if not (self.save_excel.get() or self.save_csv.get()):
            messagebox.showerror("Error", "Select at least one output format")
            return False
        if not self.filename_custom.get():
            messagebox.showerror("Error", "Enter filename")
            return False
        return True


def main():
    """
    Initialize and run the MicroTPCT GUI application.
    
    Creates the root tkinter window and starts the main event loop.
    """
    root = tk.Tk()
    app = MicroTPCTGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()