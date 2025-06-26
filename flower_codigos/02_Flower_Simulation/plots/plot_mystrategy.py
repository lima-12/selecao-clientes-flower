import matplotlib.pyplot as plt
import numpy as np

tamanho_fonte = 15

def plot_acc():
	dados = []
	for i in open('../resultados_mystrategy.txt'):
		acuracia = float(i.split("\t")[2])
		dados.append(acuracia)
	
	fig = plt.gcf()

	plt.plot(dados, marker='o', color='r', linewidth=3, markersize=10)

	xticks = np.arange(0,10,1)
	labels = np.arange(1,11,1)
	plt.xticks(xticks, labels, fontsize=tamanho_fonte)

	plt.xlim(-0.5,9.5)

	yticks = np.arange(0.91, 1.01, 0.01)
	plt.yticks(yticks, fontsize=tamanho_fonte)

	plt.xlabel("Rodada de treinamento", fontsize=tamanho_fonte)
	plt.ylabel("Acurácia média", fontsize=tamanho_fonte)

	plt.grid(color='grey', linestyle='--', linewidth=2, axis='both', alpha=0.1)
	plt.title("MyStrategy com dataset MNIST")
	fig.savefig('Acuracia_MyStrategy.png', dpi=200, bbox_inches = 'tight', pad_inches = 0.05)

	plt.close()

def plot_loss():
	dados = []
	for i in open('../resultados_mystrategy.txt'):
		loss = float(i.split("\t")[1])
		dados.append(loss)
	
	fig = plt.gcf()

	plt.plot(dados, marker='o', color='b', linewidth=3, markersize=10)

	xticks = np.arange(0,10,1)
	labels = np.arange(1,11,1)
	plt.xticks(xticks, labels, fontsize=tamanho_fonte)

	plt.xlim(-0.5,9.5)

	# yticks = np.arange(0.91, 1.01, 0.01)
	plt.yticks(fontsize=tamanho_fonte)

	plt.xlabel("Rodada de treinamento", fontsize=tamanho_fonte)
	plt.ylabel("Loss", fontsize=tamanho_fonte)

	plt.grid(color='grey', linestyle='--', linewidth=2, axis='both', alpha=0.1)
	plt.title("MyStrategy com dataset MNIST")
	fig.savefig('Loss_MyStrategy.png', dpi=200, bbox_inches = 'tight', pad_inches = 0.05)

	plt.close()

plot_acc()
plot_loss()
