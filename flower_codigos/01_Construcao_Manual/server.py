import flwr as fl

n_rounds = 10

strategy = fl.server.strategy.FedAvg()

outputs = fl.server.start_server(
    server_address  = '127.0.0.1:9090',
    config          = fl.server.ServerConfig(num_rounds=n_rounds),
    strategy        = strategy
)

print("Output Federated Learning - Loss/Round: ", outputs.losses_distributed)