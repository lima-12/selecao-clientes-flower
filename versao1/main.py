from flwr.simulation import start_simulation
from versao1.client_app import MnistClient
import flwr as fl

def client_fn(cid: str):
    return MnistClient(int(cid))

if __name__ == "__main__":
    strategy = fl.server.strategy.FedAvg()

    start_simulation(
        client_fn=client_fn,
        num_clients=5,
        config={"num_rounds": 3},
        strategy=strategy,
    )
