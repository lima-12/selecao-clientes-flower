import matplotlib.pyplot as plt

# comparacao do fedAvg com round-robin

# Dados por rodada
rounds = [1, 2, 3]

# Resultados da estratégia Round-Robin
rr_loss = [1.7993, 1.5443, 1.4291]
rr_acc = [0.4041, 0.4531, 0.4978]

# Resultados da estratégia Aleatória (FedAvg)
fedavg_loss = [1.7880, 1.5473, 1.4574]
fedavg_acc = [0.3927, 0.4589, 0.4853]

# Criar gráfico comparando Loss
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(rounds, fedavg_loss, label="FedAvg (Aleatória)", marker='o')
plt.plot(rounds, rr_loss, label="Round-Robin", marker='o')
plt.title("Perda (Loss) por Rodada")
plt.xlabel("Rodada")
plt.ylabel("Loss")
plt.legend()
plt.grid(True)

# Criar gráfico comparando Acurácia
plt.subplot(1, 2, 2)
plt.plot(rounds, fedavg_acc, label="FedAvg (Aleatória)", marker='o')
plt.plot(rounds, rr_acc, label="Round-Robin", marker='o')
plt.title("Acurácia por Rodada")
plt.xlabel("Rodada")
plt.ylabel("Acurácia")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
