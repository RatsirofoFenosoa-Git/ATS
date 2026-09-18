from collections import Counter
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pypdf import PdfReader


def extraire_texte_pdf(chemin_pdf):
  try:
    lecteur = PdfReader(chemin_pdf)
    texte = ""
    for page in lecteur.pages:
      texte += page.extract_text() or ""
    return texte
  except Exception as e:
    return ""


def nettoyer_et_tokenizer(texte):
  mots = re.findall(r"\b[a-zA-Zàâäéèêëîïôöùûüç0-9]+\b", texte.lower())
  stop_words = {
      "le",
      "la",
      "les",
      "un",
      "une",
      "des",
      "et",
      "en",
      "de",
      "du",
      "au",
      "aux",
      "pour",
      "par",
      "sur",
      "dans",
      "avec",
      "que",
      "qui",
      "est",
      "sont",
      "the",
      "and",
      "to",
      "of",
      "in",
      "for",
      "les",
  }
  return [m for m in mots if m not in stop_words and len(m) > 2]


class MiniATSApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Mini ATS - Testeur de CV")
    self.root.geometry("750x680")
    self.root.minsize(600, 500)

    self.chemin_cv = ""

    # --- Section 1 : Sélection du CV ---
    cadre_cv = tk.LabelFrame(
        root, text=" 1. Sélectionner votre CV (PDF) ", padx=10, pady=10
    )
    cadre_cv.pack(fill="x", padx=15, pady=10)

    self.lbl_chemin = tk.Label(
        cadre_cv, text="Aucun fichier sélectionné", fg="gray", anchor="w"
    )
    self.lbl_chemin.pack(side="left", fill="x", expand=True, padx=(0, 10))

    btn_parcourir = tk.Button(
        cadre_cv, text="Parcourir...", command=self.choisir_cv
    )
    btn_parcourir.pack(side="right")

    # --- Section 2 : Offre d'emploi ---
    cadre_offre = tk.LabelFrame(
        root, text=" 2. Coller la description de l'offre d'emploi ", padx=10, pady=10
    )
    cadre_offre.pack(fill="both", expand=True, padx=15, pady=5)

    self.txt_offre = scrolledtext.ScrolledText(
        cadre_offre, wrap=tk.WORD, height=8
    )
    self.txt_offre.pack(fill="both", expand=True)

    # --- Bouton d'action ---
    self.btn_analyser = tk.Button(
        root,
        text="Lancer l'analyse ATS",
        bg="#2e7d32",
        fg="white",
        font=("Arial", 11, "bold"),
        command=self.lancer_analyse,
        pady=8,
    )
    self.btn_analyser.pack(fill="x", padx=15, pady=10)

    # --- Section 3 : Résultats ---
    cadre_resultats = tk.LabelFrame(
        root, text=" 3. Rapport d'analyse et mots-clés ", padx=10, pady=10
    )
    cadre_resultats.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    self.txt_resultats = scrolledtext.ScrolledText(
        cadre_resultats, wrap=tk.WORD, height=10, bg="#f4f6f7"
    )
    self.txt_resultats.pack(fill="both", expand=True)
    self.txt_resultats.config(state=tk.DISABLED)

  def choisir_cv(self):
    chemin = filedialog.askopenfilename(
        title="Sélectionner le CV",
        filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
    )
    if chemin:
      self.chemin_cv = chemin
      self.lbl_chemin.config(text=os.path.basename(chemin), fg="black")

  def lancer_analyse(self):
    if not self.chemin_cv:
      messagebox.showwarning(
          "Attention", "Veuillez sélectionner un fichier CV au format PDF."
      )
      return

    description_poste = self.txt_offre.get("1.0", tk.END).strip()
    if not description_poste:
      messagebox.showwarning(
          "Attention", "Veuillez coller la description de l'offre d'emploi."
      )
      return

    # Extraction du texte du PDF
    texte_cv = extraire_texte_pdf(self.chemin_cv)
    if not texte_cv.strip():
      messagebox.showerror(
          "Erreur",
          "Impossible de lire le texte du PDF. Vérifiez qu'il n'est pas"
          " protégé ou scanné en image.",
      )
      return

    # Traitement textuel
    mots_cv = nettoyer_et_tokenizer(texte_cv)
    mots_cv_set = set(mots_cv)

    mots_offre = nettoyer_et_tokenizer(description_poste)
    mots_offre_set = set(mots_offre)

    mots_communs = mots_cv_set.intersection(mots_offre_set)
    mots_manquants = mots_offre_set - mots_cv_set

    # Calcul du score
    score = (
        (len(mots_communs) / len(mots_offre_set)) * 100 if mots_offre_set else 0
    )

    frequence_offre = Counter(mots_offre)
    manquants_tries = sorted(
        list(mots_manquants), key=lambda x: frequence_offre[x], reverse=True
    )

    # Affichage du rapport
    self.txt_resultats.config(state=tk.NORMAL)
    self.txt_resultats.delete("1.0", tk.END)

    rapport = f"=== SCORE DE CORRESPONDANCE ATS : {score:.2f}% ===\n\n"
    rapport += f"• Mots-clés communs trouvés ({len(mots_communs)}) :\n"
    rapport += (
        ", ".join(sorted(list(mots_communs))[:30])
        + ("...\n\n" if len(mots_communs) > 30 else "\n\n")
    )

    rapport += f"• Mots-clés importants manquants dans votre CV (à ajouter) :\n"
    rapport += ", ".join(manquants_tries[:25]) + "\n"

    self.txt_resultats.insert(tk.END, rapport)
    self.txt_resultats.config(state=tk.DISABLED)


if __name__ == "__main__":
  root = tk.Tk()
  app = MiniATSApp(root)
  root.mainloop()