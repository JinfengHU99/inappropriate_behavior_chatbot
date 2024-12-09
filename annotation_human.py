import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import json
import os
from settings import ANNOTATION_HUMAN_PATH

class LabelingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Outil d'annotation de texte avec les étiquettes")
        self.data = pd.DataFrame()
        self.current_index = 0
        self.progress_file = "labeling_progress.json"

        # Create UI components
        self.create_widgets()
        self.load_progress()

    def create_widgets(self):
        # Buttons
        self.load_button = tk.Button(self.root, text="Charger les fichiers CSV", command=self.load_csv)
        self.load_button.pack()

        # Added Export Button
        self.export_button = tk.Button(self.root, text="Exporter CSV Fusionné", command=self.export_combined_csv)
        self.export_button.pack()

        self.label_frame = tk.Frame(self.root)
        self.label_frame.pack(pady=10)

        self.insécurité_personnelle_button = tk.Button(self.label_frame, text="Insécurité personnelle", command=lambda: self.label("Insécurité personnelle"))
        self.insécurité_personnelle_button.pack(side=tk.LEFT, padx=5)

        self.insécurité_tiers_button = tk.Button(self.label_frame, text="Insécurité envers les tiers", command=lambda: self.label("Insécurité envers les tiers"))
        self.insécurité_tiers_button.pack(side=tk.LEFT, padx=5)

        self.comportement_approprie_button = tk.Button(self.label_frame, text="Comportement approprié", command=lambda: self.label("Comportement approprié"))
        self.comportement_approprie_button.pack(side=tk.LEFT, padx=5)

        self.supprimer_button = tk.Button(self.label_frame, text="Supprimer", command=self.delete_row)
        self.supprimer_button.pack(side=tk.LEFT, padx=5)

        # Text Area
        self.text_area = tk.Text(self.root, wrap=tk.WORD, height=10, width=50)
        self.text_area.pack(pady=10)

        # Status Bar
        self.status_label = tk.Label(self.root, text="État: Aucun fichier chargé")
        self.status_label.pack(pady=5)

    def load_csv(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("Fichiers CSV", "*.csv")])
        if filepaths:
            data_frames = []
            for filepath in filepaths:
                try:
                    df = pd.read_csv(filepath, sep=';', quotechar='"', escapechar='\\')
                    data_frames.append(df)
                except pd.errors.ParserError as e:
                    messagebox.showerror("Erreur", f"Erreur lors du chargement du fichier {filepath}: {e}")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Une erreur est survenue lors du chargement du fichier {filepath}: {e}")

            if data_frames:
                self.data = pd.concat(data_frames, ignore_index=True)
                self.data["Label"] = None
                self.data = self.data[["ID", "Text", "Date", "URL", "Label"]]  # Réorganiser les colonnes
                self.current_index = 0
                self.show_current_text()
                self.status_label.config(text=f"État: {len(self.data)} enregistrements chargés")

    def show_current_text(self):
        if not self.data.empty and self.current_index < len(self.data):
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.data.iloc[self.current_index]["Text"])
        else:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "Plus de texte disponible")

    def label(self, label_value):
        if not self.data.empty and self.current_index < len(self.data):
            self.data.at[self.current_index, "Label"] = label_value
            self.next_record()

    def delete_row(self):
        if not self.data.empty and self.current_index < len(self.data):
            self.data.drop(self.current_index, inplace=True)
            self.data.reset_index(drop=True, inplace=True)
            self.next_record()

    def next_record(self):
        self.current_index = min(self.current_index + 1, len(self.data) - 1)
        self.show_current_text()

    def save_progress(self):
        progress = {
            "current_index": self.current_index,
            "data": self.data.to_dict(orient="records")
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f)
        print(f"Progression enregistrée dans {self.progress_file}")

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
                self.data = pd.DataFrame(progress["data"])
                
                required_columns = ['ID', 'Text', 'Date', 'URL', 'Label']
                for col in required_columns:
                    if col not in self.data.columns:
                        self.data[col] = None
                self.data = self.data[required_columns]
                
                self.current_index = progress.get("current_index", 0)
                self.show_current_text()
                self.status_label.config(text=f"État: Reprise de l'annotation")

    def save_csv(self):
        if not self.data.empty:
            save_path = ANNOTATION_HUMAN_PATH
            if save_path:
                self.data.to_csv(save_path, index=False)
                messagebox.showinfo("Sauvegarde réussie", f"Les résultats d'annotation ont été sauvegardés dans {save_path}")

    # Added method to export combined CSV
    def export_combined_csv(self):
        if not self.data.empty:
            save_path = ANNOTATION_HUMAN_PATH
            if save_path:
                self.data.to_csv(save_path, index=False)
                messagebox.showinfo("Exportation réussie", f"Les données combinées ont été exportées vers {save_path}")

    def on_close(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous sauvegarder les modifications avant de quitter ?"):
            self.save_progress()
            self.save_csv()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelingTool(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
