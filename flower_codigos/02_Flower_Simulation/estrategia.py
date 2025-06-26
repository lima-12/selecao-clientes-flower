from typing import Callable, Union

import tensorflow as tf
import flwr as fl
from flwr_datasets import FederatedDataset
import pandas as pd

from flwr.common import (
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    MetricsAggregationFn,
    NDArrays,
    Parameters,
    Scalar,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
)

from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy.aggregate import aggregate, weighted_loss_avg

class MyStrategy(fl.server.strategy.FedAvg):
    def __init__(self,
        initial_parameters,
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=2,
        min_evaluate_clients=2,
        min_available_clients=2,
    ):
        super().__init__(
            fraction_fit=fraction_fit,
            fraction_evaluate=fraction_evaluate,
            min_fit_clients=min_fit_clients,
            min_evaluate_clients=min_evaluate_clients,
            min_available_clients=min_available_clients
        )
        self.initial_parameters = initial_parameters

    def initialize_parameters(self, client_manager):
        """Inicializa os parâmetros do modelo global."""
        initial_parameters = self.initial_parameters
        # limpa da memória os parâmetros
        self.initial_parameters = None
        return fl.common.ndarrays_to_parameters(initial_parameters)

    def configure_fit(self, server_round, parameters, client_manager):
        """Configura a próxima rodada de treinamento."""
        # obtém informações referentes a amostragem dos clientes.
        sample_size, min_num_clients = self.num_fit_clients(
            client_manager.num_available()
        )
        # informações de configuração a serem enviadas para os clientes.
        config = {}

        # faz a amostragem dos clientes para o treinamento na rodada atual.
        clients = client_manager.sample(
            num_clients=sample_size, min_num_clients=min_num_clients
        )

        # retorna os parâmetros agregados e informações de configuração
        return [(client, FitIns(parameters, config)) for client in clients]

    def aggregate_fit(self, server_round, results, failures):
        """Agrega os resultados da rodada de treinamento."""

        # os parâmetros retornados pelos clientes estão em formato hexadecimal.
        # Para que seja possível tratá-los utilizando funções do python,
        # utilizamos funções built-in do python para convertê-los em arrays.
        weights_results = [
            (parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples)
            for _, fit_res in results
        ]

        # convertendo os parâmetros para hexadecimal.
        parameters_aggregated = ndarrays_to_parameters(
            aggregate(weights_results))

        # métricas globais de treinamento.
        metrics_aggregated = {}

        return parameters_aggregated, metrics_aggregated

    def configure_evaluate(self, server_round, parameters,
                           client_manager):
        """Configura a próxima rodada de avaliação."""
        config = {}

        evaluate_ins = EvaluateIns(parameters, config)

        # amostragem dos clientes utilizados para avaliação.
        sample_size, min_num_clients = self.num_evaluation_clients(
            client_manager.num_available()
        )
        clients = client_manager.sample(
            num_clients=sample_size, min_num_clients=min_num_clients
        )

        # retorna os parâmetros agregados e informações de configuração.
        return [(client, evaluate_ins) for client in clients]

    def aggregate_evaluate(self, server_round, results, failures):
        """Agrega os resultados da rodada de avaliação."""
        # loss ponderada pelo tamanho do dataset de treino de cada cliente.

        loss_aggregated = weighted_loss_avg(
            [
                (evaluate_res.num_examples, evaluate_res.loss)
                for _, evaluate_res in results
            ]
        )
        # obtém as métricas personalizadas do cliente.
        acc_aggregated = [r.metrics["accuracy"] * r.num_examples for _, r in results]
        examples = [r.num_examples for _, r in results]
        # métricas globais de avaliação.
        metrics_aggregated = {'loss': loss_aggregated,
                              'accuracy': sum(acc_aggregated) / sum(examples)}
        return loss_aggregated, metrics_aggregated