"""jeffersonMatheus: A Flower / TensorFlow app."""

import numpy as np
import random
from flwr.common import Context, ndarrays_to_parameters
from flwr.server import ServerApp, ServerAppComponents, ServerConfig
from flwr.server.strategy import FedAvg
from typing import List, Tuple, Dict, Optional
from flwr.common.typing import Parameters, Scalar

from jeffersonmatheus.task import load_model


# ✅ Alternador de estratégia
USE_PERFORMANCE_BASED = True  # True para usar a estratégia baseada em performance, False para FedAvg padrão


# ✅ Função de agregação de acurácia
def aggregate_accuracy(results):
    accuracies = [metrics["accuracy"] for _, metrics in results if "accuracy" in metrics]
    if not accuracies:
        return {}
    return {"accuracy": float(sum(accuracies) / len(accuracies))}


# ✅ Estratégia personalizada: Performance-Based Selection
class PerformanceBasedFedAvg(FedAvg):
    def __init__(
        self,
        total_clients: int,
        clients_per_round: int,
        performance_window: int = 5,  # Mantém histórico das últimas 5 rodadas
        exploration_prob: float = 0.3,  # 30% de chance de exploração inicial
        **kwargs
    ):
        super().__init__(**kwargs)
        self.total_clients = total_clients
        self.clients_per_round = clients_per_round
        self.performance_window = performance_window
        self.exploration_prob = exploration_prob
        self.client_performances = {}
        self.round = 0
        
    def aggregate_fit(self, server_round, results, failures):
        """Agrega os resultados e atualiza o histórico de performance."""
        self.round = server_round
        
        # Atualiza o histórico de performance dos clientes
        for client_proxy, fit_res in results:
            if client_proxy.cid not in self.client_performances:
                self.client_performances[client_proxy.cid] = []
            
            metrics = fit_res.metrics if fit_res.metrics is not None else {}
            
            # Calcula pontuação combinando accuracy e loss (se disponíveis)
            performance_score = 1.0
            if "accuracy" in metrics and "loss" in metrics:
                # Combina accuracy e loss em uma única pontuação
                accuracy = metrics["accuracy"]
                loss = metrics["loss"]
                performance_score = accuracy * (1.0 / (1.0 + loss))
            elif "accuracy" in metrics:
                performance_score = metrics["accuracy"]
            elif "loss" in metrics:
                performance_score = 1.0 / (1.0 + metrics["loss"])
            
            # Adiciona um pequeno bônus para clientes que participaram mais recentemente
            recency_bonus = 0.01 * (self.round / 10)  # Ajustado para 10 rodadas
            performance_score *= (1.0 + recency_bonus)
            
            history = self.client_performances[client_proxy.cid]
            history.append(performance_score)
            
            # Mantém apenas as últimas performance_window pontuações
            if len(history) > self.performance_window:
                history = history[-self.performance_window:]
            self.client_performances[client_proxy.cid] = history
            
        return super().aggregate_fit(server_round, results, failures)
    
    def configure_fit(self, server_round, parameters, client_manager):
        """Seleciona clientes com base no histórico de performance."""
        all_clients = client_manager.all()
        
        # Calcula scores médios para cada cliente
        client_scores = {}
        for cid in all_clients.keys():
            if cid in self.client_performances and len(self.client_performances[cid]) > 0:
                # Usa média ponderada, dando mais peso para resultados recentes
                weights = np.linspace(0.5, 1.0, len(self.client_performances[cid]))
                client_scores[cid] = np.average(self.client_performances[cid], weights=weights)
            else:
                client_scores[cid] = 0.0
        
        # Ajusta exploration_prob com base no progresso do treinamento
        current_exploration_prob = self.exploration_prob * (1.0 - (server_round / 10))  # Ajustado para 10 rodadas
        
        if random.random() < current_exploration_prob:
            selected_cids = random.sample(list(all_clients.keys()), self.clients_per_round)
        else:
            # Seleciona os clientes com melhores scores
            sorted_clients = sorted(
                client_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            selected_cids = [cid for cid, _ in sorted_clients[:self.clients_per_round]]
        
        selected_clients = [all_clients[cid] for cid in selected_cids if cid in all_clients]
        
        return super().configure_fit(server_round, parameters, client_manager)


# ✅ Função principal do servidor
def server_fn(context: Context):
    num_rounds = context.run_config["num-server-rounds"]
    parameters = ndarrays_to_parameters(load_model().get_weights())

    # Configurações comuns para todas as estratégias
    total_clients = 10
    clients_per_round = 6  # Usando 60% dos clientes por rodada em todas as estratégias

    if USE_PERFORMANCE_BASED:
        strategy = PerformanceBasedFedAvg(
            total_clients=total_clients,
            clients_per_round=clients_per_round,  # Mesmo número de clientes que o FedAvg
            performance_window=5,
            exploration_prob=0.3,
            fraction_fit=0.6,
            min_available_clients=total_clients,
            initial_parameters=parameters,
            evaluate_metrics_aggregation_fn=aggregate_accuracy,
        )
    else:
        strategy = FedAvg(
            fraction_fit=0.6,  # 60% dos clientes por rodada
            fraction_evaluate=0.6,
            min_available_clients=total_clients,
            initial_parameters=parameters,
            evaluate_metrics_aggregation_fn=aggregate_accuracy,
        )

    config = ServerConfig(num_rounds=num_rounds)
    return ServerAppComponents(strategy=strategy, config=config)


# Create ServerApp
app = ServerApp(server_fn=server_fn) 