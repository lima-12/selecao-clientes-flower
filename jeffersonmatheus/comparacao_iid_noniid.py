import matplotlib.pyplot as plt

# Dados obtidos das execuções
rounds = [1, 2, 3]

# Accuracy
accuracy_iid = [0.4004, 0.4727, 0.5077]
accuracy_noniid = [0.2940, 0.3938, 0.4080]

# Loss
loss_iid = [1.7922, 1.5110, 1.4152]
loss_noniid = [2.0604, 1.7016, 1.6288]

# Configura o layout da figura
plt.figure(figsize=(12, 5))

# --- Accuracy ---
plt.subplot(1, 2, 1)
plt.plot(rounds, accuracy_iid, marker='o', label='IID', color='green')
plt.plot(rounds, accuracy_noniid, marker='o', label='non-IID', color='orange')
plt.title("Comparação de Accuracy")
plt.xlabel("Rodadas")
plt.ylabel("Accuracy")
plt.ylim(0.2, 0.6)
plt.grid(True)
plt.legend()

# --- Loss ---
plt.subplot(1, 2, 2)
plt.plot(rounds, loss_iid, marker='o', label='IID', color='blue')
plt.plot(rounds, loss_noniid, marker='o', label='non-IID', color='red')
plt.title("Comparação de Loss")
plt.xlabel("Rodadas")
plt.ylabel("Loss")
plt.grid(True)
plt.legend()

# Exibe o gráfico
# plt.savefig("comparacao_iid_noniid.png", dpi=300, bbox_inches='tight')
plt.tight_layout()
plt.show()
