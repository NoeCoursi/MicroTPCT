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


class MicroTPCTGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroTPCT")

        # Input and output variables
        self.fasta_path = tk.StringVar()
        self.xlsx_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.algorithm = tk.StringVar(value=ALGORITHMS[0])
        self.wildcard_enabled = tk.BooleanVar(value=False)
        self.wildcard_choice = tk.StringVar(value="X")  # Default "X" wildcard

        # --- Input FASTA ---
        tk.Label(root, text="Proteome FASTA file").pack()
        tk.Entry(root, textvariable=self.fasta_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_fasta).pack()

        # --- Input Excel ---
        tk.Label(root, text="Peptide XLSX file").pack()
        tk.Entry(root, textvariable=self.xlsx_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_xlsx).pack()

        # --- Output directory ---
        tk.Label(root, text="Output directory").pack()
        tk.Entry(root, textvariable=self.output_dir, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_output).pack()

        # --- Algorithm selection ---
        tk.Label(root, text="Choose matching algorithm").pack()
        tk.OptionMenu(root, self.algorithm, *ALGORITHMS).pack()

        # --- Wildcard ---
        tk.Checkbutton(root, text="Enable wildcard?", variable=self.wildcard_enabled).pack()
        tk.Label(root, text="Wildcard character").pack()
        tk.Entry(root, textvariable=self.wildcard_choice, width=10).pack()

        # --- Run button ---
        tk.Button(root, text="Run Pipeline", command=self.run).pack(pady=10)


    # --- Browse functions ---
    def browse_fasta(self):
        self.fasta_path.set(filedialog.askopenfilename(filetypes=[("FASTA files", "*.fasta *.fa")]))
    
    def browse_xlsx(self):
        self.xlsx_path.set(filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")]))
    
    def browse_output(self):
        self.output_dir.set(filedialog.askdirectory())


    # --- Run function ---
    def run(self):
        try:
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

def main():
    root = tk.Tk()
    app = MicroTPCTGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

