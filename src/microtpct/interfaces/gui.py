# workflow : 
#GUI
 #└── collecte paramètres utilisateur
  #    └── appelle io.validators
   #        └── appelle io.converter
    #            └── appelle core.pipeline
     #                └── core.alignment / metrics / sequences
      #                    └── io.writers


#  run GUI application for MicroTPCT
#  python3 src/microtpct/interfaces/gui.py

### for Linux/WSL users who do not have tkinter installed:
# sudo apt update
# sudo apt install python3-tk

import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]  # MicroTPCT/
sys.path.append(str(repo_root))

#tests
from tests import minimal_pipeline #.../MicroTPCT/tests/minimal_pipeline.py
from tests.minimal_pipeline import minimal_pipeline_gui
#config
# pip install pyyaml
import yaml
from pathlib import Path

config_path = Path(__file__).parent.parent / "config" / "defaults.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

#/mnt/c/Users/Hp/Desktop/biocomp_repository/MicroTPCT/src/microtpct/config/defaults.yaml
#from microtpct.config import defaults
#from microtpct.config.defaults import load

#available matching algorithms
# from microtpct.core.alignment.algorithms import AVAILABLE_ALGORITHMS
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
    def __init__(self, root):
        self.root = root
        self.root.title("MicroTPCT")
        self.root.geometry("1200x400")
        self.root.configure(bg=BG_COLOR)

        # Set minimum window size
        self.root.minsize(800, 400)

        # Input and output variables
        self.fasta_path = tk.StringVar()
        self.xlsx_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.algorithm = tk.StringVar(value=ALGORITHMS[0])
        self.wildcard_enabled = tk.BooleanVar(value=False)
        self.wildcard_choice = tk.StringVar(value="X")  # Default "X" wildcard

         # --- HEADER ---
        header_frame = tk.Frame(root, bg=PRIMARY_COLOR, height=60)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=0, pady=0)
        
        title_label = tk.Label(header_frame, text="MicroTPCT", 
                               font=("Helvetica", 24, "bold"), 
                               fg=LIGHT_TEXT, bg=PRIMARY_COLOR)
        title_label.pack(pady=10)


         # --- LEFT COLUMN: Input Files ---
        left_frame = tk.LabelFrame(root, text="Input Files", padx=15, pady=15,
                                   font=("Helvetica", 11, "bold"),
                                   fg=TEXT_COLOR, bg=BG_COLOR,
                                   relief=tk.RIDGE, borderwidth=2)
        left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self._create_file_input(left_frame, "Proteome FASTA file", self.fasta_path, 
                               self.browse_fasta, 0)
        self._create_file_input(left_frame, "Peptide XLSX file", self.xlsx_path, 
                               self.browse_xlsx, 1)
        self._create_file_input(left_frame, "Output directory", self.output_dir, 
                               self.browse_output, 2)
 

        # --- Input FASTA ---
        #tk.Label(root, text="Proteome FASTA file").pack()
        #tk.Entry(root, textvariable=self.fasta_path, width=50).pack()
        #tk.Button(root, text="Browse", command=self.browse_fasta).pack()

        # --- Input Excel ---
        #tk.Label(root, text="Peptide XLSX file").pack()
        #tk.Entry(root, textvariable=self.xlsx_path, width=50).pack()
        #tk.Button(root, text="Browse", command=self.browse_xlsx).pack()

        # --- Output directory ---
        #tk.Label(root, text="Output directory").pack()
        #tk.Entry(root, textvariable=self.output_dir, width=50).pack()
        #tk.Button(root, text="Browse", command=self.browse_output).pack()

        # --- MIDDLE COLUMN: Algorithm & Options ---
        middle_frame = tk.LabelFrame(root, text="⚙️ Configuration", padx=15, pady=15,
                                     font=("Helvetica", 11, "bold"),
                                     fg=TEXT_COLOR, bg=BG_COLOR,
                                     relief=tk.RIDGE, borderwidth=2)
        middle_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(middle_frame, text="Matching Algorithm", font=("Helvetica", 10),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=5)
        algo_menu = tk.OptionMenu(middle_frame, self.algorithm, *ALGORITHMS)
        algo_menu.config(font=("Helvetica", 10), bg=LIGHT_TEXT, activebackground=SECONDARY_COLOR)
        algo_menu.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        separator = tk.Frame(middle_frame, height=2, bg=PRIMARY_COLOR)
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        wildcard_check = tk.Checkbutton(middle_frame, text="Enable Wildcard?", 
                                       variable=self.wildcard_enabled,
                                       font=("Helvetica", 10), bg=BG_COLOR,
                                       fg=TEXT_COLOR, activebackground=BG_COLOR)
        wildcard_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        tk.Label(middle_frame, text="Wildcard Character", font=("Helvetica", 10),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=3, column=0, sticky="w", pady=5)
        wildcard_entry = tk.Entry(middle_frame, textvariable=self.wildcard_choice, 
                                 width=5, font=("Helvetica", 10))
        wildcard_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # --- Algorithm selection ---
        #tk.Label(root, text="Choose matching algorithm").pack()
        #tk.OptionMenu(root, self.algorithm, *ALGORITHMS).pack()

        # --- Wildcard ---
        #tk.Checkbutton(root, text="Enable wildcard?", variable=self.wildcard_enabled).pack()
        #tk.Label(root, text="Wildcard character").pack()
        #tk.Entry(root, textvariable=self.wildcard_choice, width=10).pack()

        # --- RIGHT COLUMN: Actions ---
        right_frame = tk.LabelFrame(root, text="Actions", padx=15, pady=15,
                                    font=("Helvetica", 11, "bold"),
                                    fg=LIGHT_TEXT, bg=PRIMARY_COLOR,
                                    relief=tk.RIDGE, borderwidth=2)
        right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        run_btn = tk.Button(right_frame, text="Run Pipeline", command=self.run, 
                           bg=SUCCESS_COLOR, fg=LIGHT_TEXT,
                           font=("Helvetica", 12, "bold"), padx=20, pady=15,
                           relief=tk.RAISED, bd=2, cursor="hand2",
                           activebackground="#1E8449", activeforeground=LIGHT_TEXT)
        run_btn.pack(fill=tk.BOTH, expand=True, pady=5)

        clear_btn = tk.Button(right_frame, text="Clear", command=self.clear,
                             bg=SECONDARY_COLOR, fg=LIGHT_TEXT,
                             font=("Helvetica", 11, "bold"), padx=20, pady=10,
                             relief=tk.RAISED, bd=1, cursor="hand2",
                             activebackground="#2874A6", activeforeground=LIGHT_TEXT)
        clear_btn.pack(fill=tk.X, pady=5)

        exit_btn = tk.Button(right_frame, text="Exit", command=self.root.quit,
                            bg=ERROR_COLOR, fg=LIGHT_TEXT,
                            font=("Helvetica", 11, "bold"), padx=20, pady=10,
                            relief=tk.RAISED, bd=1, cursor="hand2",
                            activebackground="#C0392B", activeforeground=LIGHT_TEXT)
        exit_btn.pack(fill=tk.X, pady=5)

        # Configure grid weights for responsiveness
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.rowconfigure(1, weight=1)

    # --- Run button ---
    #tk.Button(root, text="Run Pipeline", command=self.run).pack(pady=10)

    def _create_file_input(self, parent, label_text, var, command, row):
        """Helper method to create consistent file input rows"""
        tk.Label(parent, text=label_text, font=("Helvetica", 10),
                bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row, column=0, sticky="w", pady=5)
        entry = tk.Entry(parent, textvariable=var, width=30, 
                        font=("Helvetica", 10), bg=LIGHT_TEXT, fg=TEXT_COLOR)
        entry.grid(row=row, column=1, padx=5, pady=5)
        btn = tk.Button(parent, text="Browse", command=command,
                       bg=SECONDARY_COLOR, fg=LIGHT_TEXT,
                       font=("Helvetica", 9), padx=10, pady=5,
                       relief=tk.RAISED, bd=1, cursor="hand2",
                       activebackground="#2874A6")
        btn.grid(row=row, column=2, padx=5, pady=5)

    # --- Browse functions ---
    def browse_fasta(self):
        self.fasta_path.set(filedialog.askopenfilename(filetypes=[("FASTA file", "*.fasta *.fa")]))
    
    def browse_xlsx(self):
        self.xlsx_path.set(filedialog.askopenfilename(filetypes=[("Peptide file", "*.xlsx *.csv"), 
                                                                   ("Excel files", "*.xlsx"), 
                                                                   ("CSV files", "*.csv")]))

    def browse_output(self):
        self.output_dir.set(filedialog.askdirectory())

    def clear(self):
        """Clear all input fields"""
        self.fasta_path.set("")
        self.xlsx_path.set("")
        self.output_dir.set("")
        self.algorithm.set(ALGORITHMS[0])
        self.wildcard_enabled.set(False)
        self.wildcard_choice.set("X")

    # --- Run function ---
    def run(self):
        try:
            # Validate inputs
            if not self._validate_inputs():
                return
            
            # Appel du pipeline
            minimal_pipeline_gui(
                fasta_path=Path(self.fasta_path.get()),
                peptide_path=Path(self.xlsx_path.get()),
                output_path=Path(self.output_dir.get()),
                algorithm=self.algorithm.get(),
                wildcard=self.wildcard_choice.get() if self.wildcard_enabled.get() else None,
                config=config,
            )
            messagebox.showinfo("Success", "Pipeline completed successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _validate_inputs(self):
        """Validate all input fields"""
        if not self.fasta_path.get():
            messagebox.showerror("Error", "Please select a FASTA file")
            return False
        if not Path(self.fasta_path.get()).exists():
            messagebox.showerror("Error", f"FASTA file not found")
            return False
        if not self.xlsx_path.get():
            messagebox.showerror("Error", "Please select a peptide file")
            return False
        if not Path(self.xlsx_path.get()).exists():
            messagebox.showerror("Error", f"Peptide file not found")
            return False
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return False
        return True

def main():
    root = tk.Tk()
    app = MicroTPCTGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()



