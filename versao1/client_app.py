import flwr as fl
import tensorflow as tf
from typing import Dict, Tuple
from versao1.model_utils import get_model, get_client_data

class MnistClient(fl.client.NumPyClient):
    def __init__(self, cid: int):
        self.model = get_model()
        self.cid = cid
        self.x_train, self.y_train = get_client_data(cid)
        (_, _), (self.x_test, self.y_test) = tf.keras.datasets.mnist.load_data()
        self.x_test = self.x_test / 255.0

    def get_parameters(self, config: Dict = {}) -> list:
        return self.model.get_weights()

    def fit(self, parameters, config: Dict) -> Tuple[list, int, Dict]:
        self.model.set_weights(parameters)
        self.model.fit(self.x_train, self.y_train, epochs=1, verbose=0)
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters, config: Dict) -> Tuple[float, int, Dict]:
        self.model.set_weights(parameters)
        loss, accuracy = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        return loss, len(self.x_test), {"accuracy": float(accuracy)}
