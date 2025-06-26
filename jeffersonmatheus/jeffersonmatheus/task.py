"""jeffersonMatheus: A Flower / TensorFlow app."""

import os

import keras
from keras import layers
from flwr_datasets import FederatedDataset
from flwr_datasets.partitioner import IidPartitioner # (IID = dados independentes e identicamente distribuídos)
from flwr_datasets.partitioner import DirichletPartitioner # (non-iid) 


# Make TensorFlow log less verbose ➡️ Oculta os logs de aviso do TensorFlow (para deixar a saída mais limpa).
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


def load_model():
    # Define a simple CNN for CIFAR-10 and set Adam optimizer
    model = keras.Sequential(
        [
            keras.Input(shape=(32, 32, 3)),
            layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(10, activation="softmax"),
        ]
    )
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
    return model


# Controlo aqui
USE_NON_IID = True  # True para non-IID, False para IID
CONCENTRATION = 0.5  # Quanto menor, mais não-iid (0.1 = bem enviesado)


fds = None  # Cache FederatedDataset ➡️ Serve para não baixar o dataset toda vez que um cliente chamar load_data().


# Essa função é chamada para cada cliente da simulação, e devolve os dados locais para ele.
def load_data(partition_id, num_partitions):
    global fds
    if fds is None:
        if USE_NON_IID:
            partitioner = DirichletPartitioner(
                partition_by="label",
                num_partitions=num_partitions,
                alpha=0.5,
                seed=42,
            )
        else:
            partitioner = IidPartitioner(num_partitions=num_partitions)

        fds = FederatedDataset(
            dataset="uoft-cs/cifar10",
            partitioners={"train": partitioner},
        )

    partition = fds.load_partition(partition_id, "train")
    partition.set_format("numpy")

    split = partition.train_test_split(test_size=0.2)
    x_train, y_train = split["train"]["img"] / 255.0, split["train"]["label"]
    x_test, y_test = split["test"]["img"] / 255.0, split["test"]["label"]
    return x_train, y_train, x_test, y_test


