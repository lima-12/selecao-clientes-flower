import matplotlib.pyplot as plt
import numpy as np

tamanho_fonte = 15

def plot_acc():

	dados = {}

	for i in open('../resultados_fedavg.txt'):
		
		id = i.split(',')[0]

		if id not in dados:
			dados[id] = []
			dados[id].append(float(i.split(',')[2]))
		else:
			dados[id].append(float(i.split(',')[2]))

	fig = plt.gcf()

	plt.plot(dados['0'], marker='o', color='r', linewidth=3, markersize=10)

	xticks = np.arange(0,10,1)
	labels = np.arange(1,11,1)
	plt.xticks(xticks, labels, fontsize=tamanho_fonte)

	plt.xlim(-0.5,9.5)

	yticks = np.arange(0.91, 1.01, 0.01)
	plt.yticks(yticks, fontsize=tamanho_fonte)

	plt.xlabel("Rodada de treinamento", fontsize=tamanho_fonte)
	plt.ylabel("Acurácia média", fontsize=tamanho_fonte)

	plt.grid(color='grey', linestyle='--', linewidth=2, axis='both', alpha=0.1)
	plt.title("FedAvg com dataset MNIST")
	fig.savefig('Acuracia_FedAvg.png', dpi=200, bbox_inches = 'tight', pad_inches = 0.05)

	plt.close()

def plot_loss():

	dados = {}

	for i in open('../resultados_fedavg.txt'):
		
		id = i.split(',')[0]

		if id not in dados:
			dados[id] = []
			dados[id].append(float(i.split(',')[1]))
		else:
			dados[id].append(float(i.split(',')[1]))

	fig = plt.gcf()

	plt.plot(dados['0'], marker='o', color='b', linewidth=3, markersize=10)

	xticks = np.arange(0,10,1)
	labels = np.arange(1,11,1)
	plt.xticks(xticks, labels, fontsize=tamanho_fonte)
	plt.yticks(fontsize=tamanho_fonte)
	
	plt.xlim(-0.5,9.5)

	plt.xlabel("Rodada de treinamento", fontsize=tamanho_fonte)
	plt.ylabel("Acurácia média", fontsize=tamanho_fonte)

	plt.grid(color='grey', linestyle='--', linewidth=2, axis='both', alpha=0.1)
	plt.title("FedAvg com dataset MNIST")
	fig.savefig('Loss_FedAvg.png', dpi=200, bbox_inches = 'tight', pad_inches = 0.05)

	plt.close()

plot_acc()
plot_loss()