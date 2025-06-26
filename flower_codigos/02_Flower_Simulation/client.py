import flwr as fl
import os

import numpy as np

from keras.datasets import mnist

class MyClient(fl.client.NumPyClient):

    def __init__(self, cid, model, algorithm='fedavg'):
        self.cid = int(cid)
        self.x_treino, self.y_treino, self.x_teste, self.y_teste = self.load_data()
        self.modelo = model
        self.algorithm = algorithm
        print(f"Cliente {self.cid} iniciado!")

    def load_data(self):
        # Load the MNIST dataset
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        # Scale the input data to [0, 1]
        x_train, x_test = x_train/255.0, x_test/255.0
        return x_train, y_train, x_test, y_test

    # treinamento
    def fit(self, parameters, config):
        """Realiza o treinamento local do modelo."""
        if self.cid == 1:
            print(f"Cliente {self.cid}: MINHA BATERIA ESTÁ COM 90%")
        # atribui ao modelo os parâmetros agregados pelo servidor.
        if parameters != []:
            self.modelo.set_weights(parameters)

        history = self.modelo.fit(self.x_treino, self.y_treino, epochs=1, batch_size=32, verbose=1)
        metrics = {"accuracy": np.mean(history.history["accuracy"])}
        
        return self.modelo.get_weights(), len(self.x_treino), metrics

    # avaliacao
    def evaluate(self, parameters, config):
        """Realiza a avaliação local do modelo."""
        # atribui ao modelo os parâmetros agregados pelo servidor.
        self.modelo.set_weights(parameters)
        loss, accuracy = self.modelo.evaluate(self.x_teste, self.y_teste)

        # salva arquivo de log com acurácia
        if self.algorithm == 'fedavg':
            arquivo_log = "resultados_fedavg.txt"
            with open(arquivo_log, 'a') as log_evaluate_file:
                log_evaluate_file.write(f"{self.cid}, {loss}, {accuracy}\n")

        metrics = {"accuracy": accuracy}

        return loss, len(self.x_teste), metrics