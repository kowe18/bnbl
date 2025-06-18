import numpy as np
from sklearn.neural_network import MLPClassifier
import csv, random, joblib

label_map = {0: "budan", 1: "umoran", 2: "uspavan"}

# ------ branje vektorjev ------
with open("output_vectors_with_label.txt") as f:
    vectors = [
        [int(num) for num in ln.strip("[] \n").split()]
        for ln in f if ln.strip()
    ]

vectors = np.asarray(vectors)
if len(vectors) < 15:
    raise SystemExit("❌  Premalo vektorjev v datoteki.")

# ------ ročno označevanje ------
num_select = 10
start_idxs = random.sample(range(0, len(vectors)//3), num_select//2)
end_idxs   = random.sample(range(len(vectors)*2//3, len(vectors)), num_select//2)
selected_idxs = start_idxs + end_idxs
random.shuffle(selected_idxs)

X_train = vectors[selected_idxs]
y_train = []

print("0=budan, 1=umoran, 2=uspavan")
for i, vec in enumerate(X_train):
    while True:
        try:
            lbl = int(input(f"{i+1}. {vec} -> "))
            if lbl in (0,1,2):
                y_train.append(lbl); break
        except ValueError:
            pass
        print("   ✖ vpiši 0/1/2")

# ------ MLP ------
clf = MLPClassifier(hidden_layer_sizes=(8,), max_iter=2000, random_state=42)
clf.fit(X_train, y_train)
joblib.dump(clf, "mlp_fatigue_model.pkl")
print("✔ Model shranjen v mlp_fatigue_model.pkl")

# ------ predikcija ------
mask = np.ones(len(vectors), bool); mask[selected_idxs] = False
probs = clf.predict_proba(vectors[mask])
hard  = probs.argmax(1)

with open("fatigue_predictions.csv", "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["Frame", "p_budan", "p_umoran", "p_uspavan", "label"])
    test_i = 0
    for i in range(len(vectors)):
        if mask[i]:
            p0,p1,p2 = probs[test_i]; lab = hard[test_i]; test_i += 1
            wr.writerow([i, round(p0,3), round(p1,3), round(p2,3), label_map[lab]])
        else:
            wr.writerow([i, "train","train","train",
                         label_map[y_train[selected_idxs.index(i)]]])

print("✔ Rezultati zapisani v fatigue_predictions.csv")
