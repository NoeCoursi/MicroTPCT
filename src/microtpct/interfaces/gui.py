# workflow : 
#GUI
 #└── collecte paramètres utilisateur
  #    └── appelle io.validators
   #        └── appelle io.converter
    #            └── appelle core.pipeline
     #                └── core.alignment / metrics / sequences
      #                    └── io.writers


import tkinter as tk
from tkinter import filedialog, messagebox

from microtpct.core.pipeline import run_pipeline
from microtpct.config import defaults

class MicroTPCTGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MicroTPCT")

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        tk.Label(root, text="Input file").pack()
        tk.Entry(root, textvariable=self.input_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_input).pack()

        tk.Label(root, text="Output directory").pack()
        tk.Entry(root, textvariable=self.output_path, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_output).pack()

        tk.Button(root, text="Run", command=self.run).pack(pady=10)

    def browse_input(self):
        self.input_path.set(
            filedialog.askopenfilename()
        )

    def browse_output(self):
        self.output_path.set(
            filedialog.askdirectory()
        )

    def run(self):
        try:
            run_pipeline(
                input_path=self.input_path.get(),
                output_path=self.output_path.get(),
                config=defaults.load(),
            )
            messagebox.showinfo("Success", "Pipeline completed successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = MicroTPCTGUI(root)
    root.mainloop()

