import flwr as fl

import numpy as np
import matplotlib.pyplot as plt

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--algorithm', default='fedavg')
args = parser.parse_args()

from keras.models import Sequential
from keras.layers import Dense, Flatten, Dropout

from client import MyClient
from estrategia import MyStrategy

NUM_CLIENTS = 2
NUM_ROUNDS = 10

# cria modelo
modelo = Sequential()
modelo.add(Flatten(input_shape=(28,28)))
modelo.add(Dense(128, activation='relu'))
modelo.add(Dropout(0.2))
modelo.add(Dense(10, activation='softmax'))
modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

algorithm = args.algorithm

def start_client(cid):
    return MyClient(int(cid), modelo, algorithm)

initial_parameters = modelo.get_weights()

if algorithm == 'fedavg':
    strategy = fl.server.strategy.FedAvg()
else:
    strategy = MyStrategy(initial_parameters, 1.0, 1.0, NUM_CLIENTS, NUM_CLIENTS, NUM_CLIENTS)

history = fl.simulation.start_simulation(
    client_fn        = start_client,
    num_clients      = NUM_CLIENTS,
    config           = fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
    strategy         = strategy,
    client_resources = {"num_cpus": 1, "num_gpus": 0},
)

print(history)

if algorithm != 'fedavg':
    result_loss = history.metrics_distributed['loss']
    result_acc  = history.metrics_distributed['accuracy']

    print(result_acc)

    # Salva os resultados
    arquivo_log = open('resultados_mystrategy.txt', 'a')
    for loss, acuracia in zip(result_loss, result_acc):
        arquivo_log.write(str(loss[0]) + '\t' + str(loss[1]) + '\t' + str(acuracia[1]) + '\n')
    arquivo_log.close()