# workflow : 
#GUI
 #└── collecte paramètres utilisateur
  #    └── appelle io.validators
   #        └── appelle io.converter
    #            └── appelle core.pipeline
     #                └── core.alignment / metrics / sequences
      #                    └── io.writers

### for Linux/WSL users who do not have tkinter installed:
# sudo apt update
# sudo apt install python3-tk

import tkinter as tk
from tkinter import filedialog, messagebox

from tests import minimal_pipeline #.../MicroTPCT/tests/minimal_pipeline.py
from microtpct.config import defaults

class MicroTPCTGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroTPCT")

        # Variables pour les inputs / output
        self.input1_path = tk.StringVar()
        self.input2_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.algorithm = tk.StringVar(value="Algorithm1")  # valeur par défaut
        self.wildcard = tk.BooleanVar(value=False)

        # Input 1
        tk.Label(root, text="Proteome file").pack()
        tk.Entry(root, textvariable=self.input1_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_input1).pack()

        # Input 2
        tk.Label(root, text="Peptide file").pack()
        tk.Entry(root, textvariable=self.input2_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_input2).pack()

        # Output directory
        tk.Label(root, text="Output directory").pack()
        tk.Entry(root, textvariable=self.output_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_output).pack()

        # Algorithm selection
        tk.Label(root, text="Choose matching algorithm").pack()
        tk.OptionMenu(root, self.algorithm, "Algorithm1", "Algorithm2", "Algorithm3").pack()

        # Wildcard option
        tk.Checkbutton(root, text="Enable wildcard X?", variable=self.wildcard).pack()

        # Run button
        tk.Button(root, text="Run", command=self.run).pack(pady=10)

    def browse_input1(self):
        self.input1_path.set(
            filedialog.askopenfilename()
        )

    def browse_input2(self):
        self.input2_path.set(
            filedialog.askopenfilename()
        )

    def browse_output(self):
        self.output_path.set(
            filedialog.askdirectory()
        )

    def run(self):
        try:
            minimal_pipeline(
                input_paths=[self.input1_path.get(), self.input2_path.get()],
                output_path=self.output_path.get(),
                algorithm=self.algorithm.get(),
                wildcard=self.wildcard.get(),
                config=defaults.load(),
            )
            messagebox.showinfo("Success", "Pipeline completed successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = MicroTPCTGUI(root)
    root.mainloop()

