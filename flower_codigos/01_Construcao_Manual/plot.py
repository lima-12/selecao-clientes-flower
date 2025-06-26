import matplotlib.pyplot as plt
import numpy as np

tamanho_fonte = 15

dados = []

for i in open('resultado_0.txt'):
	dados.append(float(i))

fig = plt.gcf()

plt.plot(dados, marker='o', color='r', linewidth=3, markersize=10)

xticks = np.arange(0,10,1)
labels = np.arange(1,11,1)
plt.xticks(xticks, labels, fontsize=tamanho_fonte)


yticks = np.arange(0.91, 1.01, 0.01)
plt.yticks(yticks, fontsize=tamanho_fonte)

plt.xlim(-0.5,9.5)

plt.xlabel("Rodada de treinamento", fontsize=tamanho_fonte)
plt.ylabel("Acurácia média", fontsize=tamanho_fonte)

plt.grid(color='grey', linestyle='--', linewidth=2, axis='both', alpha=0.1)
plt.title("FedAvg com dataset MNIST")
fig.savefig('MNIST.png', dpi=200, bbox_inches = 'tight', pad_inches = 0.05)

plt.close()