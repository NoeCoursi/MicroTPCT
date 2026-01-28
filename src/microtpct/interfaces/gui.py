import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from datetime import datetime
from PIL import Image, ImageTk #Logo and image handling

from microtpct.core.pipeline import run_pipeline
from microtpct.core.match import list_available_engines, user_friendly_mapped_engine_names


ALGORITHMS = list_available_engines()
ENGINE_NAMES = user_friendly_mapped_engine_names()
ALGORITHMS_DISPLAY = list(ENGINE_NAMES.values())


# Color Scheme
PRIMARY_COLOR = "#2C3E50"
SECONDARY_COLOR = "#3498DB"
SUCCESS_COLOR = "#27AE60"
ERROR_COLOR = "#E74C3C"
BG_COLOR = "#ECF0F1"
TEXT_COLOR = "#2C3E50"
LIGHT_TEXT = "#FFFFFF"

# --- GUI ---
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
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(900, 400)

        # Store matching results for saving
        self.matching_results = None

        # Input and output variables
        self.proteome_path = tk.StringVar() # Path to Proteome (Target) FASTA file
        self.peptide_path = tk.StringVar() # Path to Peptide (Query) XLSX/CSV file
        self.output_dir = tk.StringVar() # Path to output directory
        self.algorithm = tk.StringVar(value=ALGORITHMS[0]) 
        self.wildcard_enabled = tk.BooleanVar(value=True) # Default : enabled wildcard matching
        self.wildcard_choice = tk.StringVar(value="X")
        self.save_excel = tk.BooleanVar(value=True) # Default : save as Excel
        self.save_csv = tk.BooleanVar(value=False)
        #self.include_timestamp = tk.BooleanVar(value=True) # Default : include timestamp in filename
        self.filename_custom = tk.StringVar(value="results") 

        # --- HEADER ---
        header_frame = tk.Frame(root, bg=PRIMARY_COLOR, height=60)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        
        title_label = tk.Label(header_frame, text="MicroTPCT", 
        title_label = tk.Label(header_frame, text="MicroTPCT", 
                               font=("Helvetica", 24, "bold"), 
                               fg=LIGHT_TEXT, bg=PRIMARY_COLOR)
        title_label.pack(pady=10)

        # --- LEFT COLUMN: Input Files & MicroTPCT logo ---
        left_frame = tk.Frame(root, bg=BG_COLOR)
        left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # --- Input Files section ---
        input_frame = tk.LabelFrame(left_frame, text="Input Files", padx=15, pady=15,
                            font=("Helvetica", 11, "bold"),
                            fg=TEXT_COLOR, bg=BG_COLOR,
                            relief=tk.RIDGE, borderwidth=2)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self._create_file_input(input_frame, "Proteome FASTA", self.proteome_path, 
                        self.browse_proteome, 0)
        self._create_file_input(input_frame, "Peptide (XLSX/CSV)", self.peptide_path, 
                        self.browse_peptide, 1)
        self._create_file_input(input_frame, "Output Directory", self.output_dir, 
                        self.browse_output, 2)

        # --- Image display section ---
        image_frame = tk.LabelFrame(left_frame, text="", padx=5, pady=5,
                            font=("Helvetica", 11, "bold"),
                            fg=TEXT_COLOR, bg=BG_COLOR,
                            relief=tk.RIDGE, borderwidth=0,
                            width=250, height=250)
        image_frame.pack(fill=tk.NONE, expand=False, pady=5)

        self.logo_label = tk.Label(image_frame, bg=BG_COLOR)
        self.logo_label.pack(fill=tk.BOTH, expand=True)

        # Charger le logo PNG ici, après la création de left_frame
        logo_path = "../../../assets/logo0.png"
        logo_img = Image.open(logo_path)

        logo_img = logo_img.resize((270, 270), Image.LANCZOS)

        self.tk_logo = ImageTk.PhotoImage(logo_img)
        self.logo_label.config(image=self.tk_logo)

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

        self.algorithm_display = tk.StringVar(value=ALGORITHMS_DISPLAY[0])
        algo_menu = tk.OptionMenu(config_frame, self.algorithm_display, *ALGORITHMS_DISPLAY)
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

        #tk.Checkbutton(save_frame, text="Add Timestamp", variable=self.include_timestamp,
                      #font=("Helvetica", 9), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=5, column=0, columnspan=2, sticky="w", pady=3)

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
        self.run_btn.grid(row=0, column=0, sticky="ew", pady=5)


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

    def browse_proteome(self):
        """
        Open a file dialog to select a FASTA file.
        
        Updates self.proteome_path with the selected file path.
        Filters for .fasta and .fa file extensions.
        """
        self.proteome_path.set(filedialog.askopenfilename(filetypes=[("FASTA", "*.fasta *.fa")]))
    
    def browse_peptide(self):
        """
        Open a file dialog to select a peptide file (Excel or CSV).
        
        Updates self.peptide_path with the selected file path.
        Filters for .xlsx and .csv file extensions.
        """
        self.peptide_path.set(filedialog.askopenfilename(filetypes=[("Peptide", "*.xlsx *.csv")]))

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
        self.proteome_path.set("")
        self.peptide_path.set("")
        self.output_dir.set("")
        self.algorithm.set(ALGORITHMS[0])
        self.wildcard_enabled.set(False)
        self.wildcard_choice.set("X")
        self.matching_results = None

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
        
        Calls pipeline to:
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
            
            # Get the key corresponding to the displayed name
            selected_display_name = self.algorithm_display.get()
            matching_engine_key = next(
                key for key, name in ENGINE_NAMES.items() if name == selected_display_name
            )

            if self.save_csv.get():
                output_format = "csv"
            else:
                output_format = "excel"

            print(self.wildcard_choice.get())

            result_file, stats_file = run_pipeline(
                target_file=Path(self.proteome_path.get()),
                query_file=Path(self.peptide_path.get()),

                output_path=Path(self.output_dir.get()),
                output_format=output_format,

                matching_engine=matching_engine_key,
                wildcards=self.wildcard_choice.get() if self.wildcard_choice.get() else None,

                analysis_name = self.filename_custom.get(),
                allow_wildcard = self.wildcard_enabled.get()
                )

            if result_file and stats_file:
                messagebox.showinfo(f"Info", f"Pipeline completed, results saved automatically to {self.output_dir.get()}.")
            else:
                self.matching_results = result_file
            
            self.status_label.config(text="Status: Complete ✓", fg=SUCCESS_COLOR)
            
        except Exception as e:
            self.status_label.config(text="Status: Error ✗", fg=ERROR_COLOR)
            messagebox.showerror("Error", f"✗ Error: {str(e)}")
        finally:
            self.run_btn.config(state=tk.NORMAL)

    def _save_results(self, result_file, stats_file):
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
        output_path = Path(self.output_dir.get())
        filename = self.filename_custom.get()

        # if self.include_timestamp.get():
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     filename = f"{filename}_{timestamp}"
        
        # try:
        #     # Convert results to DataFrame
        #     if hasattr(matching_results, 'to_dataframe'):
        #         df = matching_results.to_dataframe()
        #     else:
        #         df = pd.DataFrame([vars(matching_results)])
        try:
            saved_files = [result_file, stats_file]

        #     if self.save_excel.get():
        #         file_xlsx = output_path / f"{filename}.xlsx"
        #         df.to_excel(file_xlsx, index=False)
        #         saved_files.append(file_xlsx.name)

        #     if self.save_csv.get():
        #         file_csv = output_path / f"{filename}.csv"
        #         df.to_csv(file_csv, index=False)
        #         saved_files.append(file_csv.name)

            self.status_label.config(
                text=f"Status: Saved to {', '.join(saved_files)}",
                fg=SUCCESS_COLOR
                )

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
        if not self.proteome_path.get():
            messagebox.showerror("Error", "Select FASTA file")
            return False
        if not Path(self.proteome_path.get()).exists():
            messagebox.showerror("Error", "FASTA file not found")
            return False
        if not self.peptide_path.get():
            messagebox.showerror("Error", "Select peptide file")
            return False
        if not Path(self.peptide_path.get()).exists():
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