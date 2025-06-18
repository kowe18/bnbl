# evaluate_fatigue_model.py
# -------------------------
# Uporabi že naučen MLP (joblib.pkl) in izračunaj verjetnosti
# za vsak vektor v output_vectors_with_label.txt

import numpy as np
import csv, joblib, sys, os
def MLP():
    # poti (po potrebi spremeni)
    MODEL_PATH   = "mlp_fatigue_model.pkl"
    VECTORS_PATH = "output_vectors_with_label.txt"
    OUT_CSV      = "fatigue_predictions.csv"

    label_map = {0: "budan", 1: "umoran", 2: "uspavan"}

    # --- 1) preveri model ---
    if not os.path.exists(MODEL_PATH):
        sys.exit(f"❌  Model {MODEL_PATH} ne obstaja – najprej ga nauči.")

    clf = joblib.load(MODEL_PATH)
    print("✅ Model naložen")

    # --- 2) vektorji ---
    with open(VECTORS_PATH) as f:
        vectors = [
            [int(num) for num in ln.strip("[] \n").split()]
            for ln in f if ln.strip()
        ]
    vectors = np.asarray(vectors)

    if vectors.size == 0:
        sys.exit("❌  V datoteki ni vektorjev.")

    # --- 3) verjetnosti + trda etiketa ---
    probs = clf.predict_proba(vectors)
    hard  = probs.argmax(1)

    # --- 4) zapis v CSV ---
    with open(OUT_CSV, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["Frame", "p_budan", "p_umoran", "p_uspavan", "label"])
        for i, (p0, p1, p2) in enumerate(probs):
            wr.writerow([i, round(p0,3), round(p1,3), round(p2,3),
                         label_map[hard[i]]])

    print(f"✔ Rezultati zapisani v {OUT_CSV}")
