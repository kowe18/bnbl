import pandas as pd
def puttingTogether():
    csv_path    = "output/headdrop_log.csv"                 # CSV s kolono D (0 / 1 / 2 …)
    vectors_in  = "output_vectors.txt"         # izvirni vektorji brez oznake
    vectors_out = "output_vectors_with_label.txt"

    # 1) D-kolona iz CSV-ja
    df = pd.read_csv(csv_path)                 # če CSV nima glave -> header=None
    labels = df.iloc[:, 3].tolist()            # kolona D (indeks 3)

    # 2) preberi vektorje
    with open(vectors_in, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    if len(lines) != len(labels):
        raise ValueError("Različno število vrstic med TXT in CSV!")

    # 3) združi in zapiši – BREZ vejic, z dodatnim presledkom
    with open(vectors_out, "w") as f:
        for vec_line, lab in zip(lines, labels):
            # odstrani oglate oklepaje in odvečne presledke na robu
            core = vec_line.strip("[] ").strip()
            f.write(f"[{core} {int(lab)}]\n")

    print("✔  Končano – rezultat v", vectors_out)
