import tensorflow as tf
from typing import Tuple, Dict

def get_model() -> tf.keras.Model:
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation="relu"),
        tf.keras.layers.Dense(10, activation="softmax"),
    ])
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

def load_data() -> Tuple[Tuple, Tuple]:
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    # Normalização simples
    x_train, x_test = x_train / 255.0, x_test / 255.0
    return (x_train, y_train), (x_test, y_test)

def get_client_data(cid: int, num_clients: int = 5) -> Tuple:
    (x_train, y_train), _ = load_data()
    # Divide de forma simples e IID
    size = len(x_train) // num_clients
    start = cid * size
    end = start + size
    return (x_train[start:end], y_train[start:end])
