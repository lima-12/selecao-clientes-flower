import flwr as fl

from keras.models import Sequential
from keras.layers import Dense, Flatten, Dropout
from keras.datasets import mnist
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--id', type=int, metavar='N', default=0)
args = parser.parse_args()

client_id = args.id

arquivo_saida = open('resultado_' + str(client_id) + '.txt', 'w')

class FlowerClient(fl.client.NumPyClient):

    def __init__(self):
        self.x_treino, self.y_treino, self.x_teste, self.y_teste = self.load_data()
        self.modelo = self.create_model()

    def load_data(self):
        # Load the MNIST dataset
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        # Scale the input data to [0, 1]
        x_train, x_test = x_train/255.0, x_test/255.0
        return x_train, y_train, x_test, y_test

    def create_model(self):

        modelo = Sequential()
        modelo.add(Flatten(input_shape=(self.x_treino.shape[1:])))
        modelo.add(Dense(128, activation='relu'))
        modelo.add(Dropout(0.2))
        modelo.add(Dense(10, activation='softmax'))
        modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['acc'])
        return modelo

    # treinamento com o modelo global e dados locais
    def fit(self, parameters, config):
        # copy parameters sent by the server into client's local model
        if parameters != []:
            self.modelo.set_weights(parameters)

        history = self.modelo.fit(self.x_treino, self.y_treino, epochs=1, batch_size=32, verbose=1)
        print(f"Acurácia local: {history.history['acc']}")

        # envia ao servidor
        return self.modelo.get_weights(), len(self.x_treino), {}

    # avaliacao com dados locais do cliente
    def evaluate(self, parameters, config):
        self.modelo.set_weights(parameters)
        loss, accuracy = self.modelo.evaluate(self.x_teste, self.y_teste)

        print(f"Acurácia atual {accuracy}")
        arquivo_saida.write(str(accuracy) + '\n')
        return loss, len(self.x_teste), {}

# comentar para funcionar o simulation
fl.client.start_numpy_client(server_address='127.0.0.1:9090', client=FlowerClient())

arquivo_saida.close()