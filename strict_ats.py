from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import re
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extraire_texte_pdf(chemin_pdf):
  """Extrait tout le texte d'un fichier PDF."""
  lecteur = PdfReader(chemin_pdf)
  texte = ""
  for page in lecteur.pages:
    texte += page.extract_text() or ""
  return texte


class MiniATSStrictApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Mini ATS Ultra-Strict - Testeur Avancé")
    self.root.geometry("800x750")

    self.chemin_cv = ""

    # --- Section 1 : Sélection du CV ---
    frame_cv = tk.LabelFrame(
        root, text=" 1. Sélectionner votre CV (PDF) ", padx=10, pady=10
    )
    frame_cv.pack(fill="x", padx=10, pady=5)

    self.btn_parcourir = tk.Button(
        frame_cv, text="Parcourir...", command=self.selectionner_fichier
    )
    self.btn_parcourir.pack(side="left", padx=5)

    self.lbl_chemin = tk.Label(
        frame_cv, text="Aucun fichier sélectionné", fg="gray"
    )
    self.lbl_chemin.pack(side="left", padx=5, fill="x", expand=True)

    # --- Section 2 : Offre d'emploi ---
    frame_offre = tk.LabelFrame(
        root, text=" 2. Coller la description de l'offre d'emploi ", padx=10, pady=10
    )
    frame_offre.pack(fill="both", expand=True, padx=10, pady=5)

    self.txt_offre = scrolledtext.ScrolledText(frame_offre, height=8)
    self.txt_offre.pack(fill="both", expand=True)

    # --- Section 3 : Bouton d'action ---
    self.btn_analyser = tk.Button(
        root,
        text="Lancer l'analyse Stricte (TF-IDF)",
        command=self.lancer_analyse_stricte,
        bg="#D32F2F",
        fg="white",
        font=("Arial", 11, "bold"),
        pady=8,
    )
    self.btn_analyser.pack(fill="x", padx=10, pady=10)

    # --- Section 4 : Résultats ---
    frame_resultats = tk.LabelFrame(
        root, text=" 3. Rapport d'évaluation strict ", padx=10, pady=10
    )
    frame_resultats.pack(fill="both", expand=True, padx=10, pady=5)

    self.txt_resultats = scrolledtext.ScrolledText(
        frame_resultats, height=10, bg="#f9f9f9"
    )
    self.txt_resultats.pack(fill="both", expand=True)

  def selectionner_fichier(self):
    fichier = filedialog.askopenfilename(
        title="Sélectionner le CV",
        filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
    )
    if fichier:
      self.chemin_cv = fichier
      self.lbl_chemin.config(text=fichier, fg="black")

  def lancer_analyse_stricte(self):
    if not self.chemin_cv:
      messagebox.showerror("Erreur", "Veuillez sélectionner un fichier CV PDF.")
      return

    description_poste = self.txt_offre.get("1.0", tk.END).strip()
    if not description_poste:
      messagebox.showerror(
          "Erreur", "Veuillez coller la description de l'offre d'emploi."
      )
      return

    try:
      # Extraction du CV
      texte_cv = extraire_texte_pdf(self.chemin_cv)

      if not texte_cv.strip():
        messagebox.showerror(
            "Erreur",
            "Le CV semble vide ou illisible (peut-être une image scannée ?)",
        )
        return

      # --- Moteur de calcul strict : TF-IDF et Similarité Cosinus ---
      # On utilise un Vectorizer avec les stop_words français pour ignorer les mots de liaison
      vectorizer = TfidfVectorizer(
          stop_words=[
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
              "les",
              "ces",
              "ses",
              "leur",
              "aux",
              "ou",
              "donc",
              "or",
              "ni",
              "car",
              "the",
              "and",
              "to",
              "of",
              "in",
              "for",
          ],
          lowercase=True,
          ngram_range=(1, 2),  # Prend en compte les mots seuls et les paires (ex: "admin reseau")
      )

      # Transformation des textes en matrices mathématiques
      matrice_tfidf = vectorizer.fit_transform([description_poste, texte_cv])

      # Calcul de la similarité cosinus (score de 0 à 1, converti en %)
      score_cosinus = cosine_similarity(matrice_tfidf[0:1], matrice_tfidf[1:2])[
          0][0]
      score_final = score_cosinus * 100

      # Analyse fine des mots-clés de l'offre absents du CV
      mots_offre = set(
          re.findall(r"\b[a-zA-Zàâäéèêëîïôöùûüç0-9]{3,}\b", description_poste.lower())
      )
      mots_cv = set(
          re.findall(r"\b[a-zA-Zàâäéèêëîïôöùûüç0-9]{3,}\b", texte_cv.lower())
      )
      mots_manquants = sorted(list(mots_offre - mots_cv))

      # Affichage des résultats stricts
palier_couleur = "🔴 CRITIQUE" if score_final < 40 else "🟡 MOYEN" if score_final < 70 else "🟢 EXCELLENT"

      resultat_texte = (
          f"=== SCORE DE CORRESPONDANCE STRICT : {score_final:.2f}%"
          f" ({palier_couleur}) ===\n\n"
      )

      if score_final < 40:
        resultat_texte += (
            "⚠️ Attention : Ce score est très strict. La structure lexicale de"
            " votre CV s'éloigne trop de l'attente textuelle de l'offre.\n\n"
        )
      elif score_final < 70:
        resultat_texte += (
            "💡 Votre CV passe la barre minimale, mais de nombreux"
            " co-facteurs techniques importants manquent.\n\n"
        )
      else:
        resultat_texte += (
            "🎉 Excellent alignement sémantique ! Votre CV est taillé pour"
            " passer ce type d'ATS.\n\n"
        )

      resultat_texte += (
          f"Mots-clés ou expressions de l'offre totalement absents du CV"
          f" ({len(mots_manquants)}) :\n"
      )
      resultat_texte += (
          ", ".join(mots_manquants[:35])
          + ("...\n" if len(mots_manquants) > 35 else "\n")
      )

      self.txt_resultats.insert(tk.INSERT, resultat_texte)

    except Exception as e:
      messagebox.showerror(
          "Erreur", f"Une erreur technique est survenue :\n{e}"
      )


if __name__ == "__main__":
  root = tk.Tk()
  app = MiniATSStrictApp(root)
  root.mainloop()