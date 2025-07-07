"""Script para executar múltiplas vezes o mesmo teste e comparar resultados estatisticamente."""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import json
import os
import re
from typing import Dict, List, Tuple
import statistics
from datetime import datetime

def get_file_paths():
    """Detecta automaticamente os caminhos corretos dos arquivos."""
    if os.path.exists("pyproject.toml"):
        server_app_path = "jeffersonmatheus/server_app.py"
        pyproject_path = "pyproject.toml"
    elif os.path.exists("jeffersonmatheus/pyproject.toml"):
        server_app_path = "jeffersonmatheus/jeffersonmatheus/server_app.py"
        pyproject_path = "jeffersonmatheus/pyproject.toml"
    else:
        raise FileNotFoundError("Não foi possível encontrar os arquivos necessários.")
    
    return server_app_path, pyproject_path

def modify_server_config(clients_per_round: int, num_rounds: int = 10):
    """Modifica a configuração do servidor para usar diferentes quantidades de clientes."""
    server_app_path, pyproject_path = get_file_paths()
    
    with open(server_app_path, "r") as f:
        content = f.read()
    
    # Atualiza o número de clientes por rodada
    content = re.sub(
        r'clients_per_round = \d+',
        f'clients_per_round = {clients_per_round}',
        content
    )
    
    # Atualiza o fraction_fit baseado no número de clientes
    fraction_fit = clients_per_round / 10.0
    content = re.sub(
        r'fraction_fit=0\.\d+',
        f'fraction_fit={fraction_fit}',
        content
    )
    
    with open(server_app_path, "w") as f:
        f.write(content)
    
    # Atualiza o pyproject.toml para o número de rodadas
    with open(pyproject_path, "r") as f:
        pyproject_content = f.read()
    
    pyproject_content = re.sub(
        r'num-server-rounds = \d+',
        f'num-server-rounds = {num_rounds}',
        pyproject_content
    )
    
    with open(pyproject_path, "w") as f:
        f.write(pyproject_content)

def run_experiment(strategy_name: str, clients_per_round: int, num_rounds: int = 10, execution_id: int = 1) -> List[float]:
    """Executa o experimento com uma estratégia específica e retorna os resultados."""
    print(f"  Execução {execution_id}: {strategy_name} com {clients_per_round} clientes por rodada...")
    
    server_app_path, _ = get_file_paths()
    
    # Configura a estratégia no arquivo server_app.py
    with open(server_app_path, "r") as f:
        content = f.read()
    
    if strategy_name == "FedAvg":
        new_content = content.replace("USE_PERFORMANCE_BASED = True", "USE_PERFORMANCE_BASED = False")
    else:  # Performance-Based
        new_content = content.replace("USE_PERFORMANCE_BASED = False", "USE_PERFORMANCE_BASED = True")
    
    with open(server_app_path, "w") as f:
        f.write(new_content)
    
    # Executa o experimento
    result_file = f"results_{strategy_name.lower().replace('-', '_')}_{clients_per_round}clients_exec_{execution_id}.txt"
    with open(result_file, "w") as f:
        subprocess.run(["flwr", "run"], stdout=f, stderr=f)
    
    # Extrai as métricas do arquivo de resultado
    accuracies = []
    with open(result_file, "r") as f:
        content = f.read()
        
    # Procura pela seção de métricas no final do arquivo
    if "'accuracy': [" in content:
        start_marker = "'accuracy': ["
        end_marker = "]}"
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            start_idx += len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            
            if end_idx != -1:
                metrics_section = content[start_idx:end_idx]
                
                # Extrai os pares (round, accuracy) usando regex mais robusto
                pattern = r'\((\d+),\s*([\d.]+)\)'
                matches = re.findall(pattern, metrics_section)
                
                # Ordena por número da rodada e extrai apenas as accuracies
                matches.sort(key=lambda x: int(x[0]))
                accuracies = [float(match[1]) for match in matches]
                
                print(f"    Extraídas {len(accuracies)} rodadas. Final: {accuracies[-1]:.4f}")
    
    return accuracies

def run_multiple_executions(clients_per_round: int, num_rounds: int, num_executions: int = 10):
    """Executa múltiplas vezes o mesmo teste e retorna estatísticas."""
    print(f"\n=== EXECUTANDO {num_executions} VEZES ===")
    print(f"Configuração: {clients_per_round} clientes por rodada, {num_rounds} rodadas")
    
    # Modifica configuração do servidor
    modify_server_config(clients_per_round, num_rounds)
    
    # Listas para armazenar resultados
    fedavg_executions = []
    perf_executions = []
    
    # Executa múltiplas vezes
    for execution in range(1, num_executions + 1):
        print(f"\n--- Execução {execution}/{num_executions} ---")
        
        # Executa FedAvg
        fedavg_results = run_experiment("FedAvg", clients_per_round, num_rounds, execution)
        fedavg_executions.append(fedavg_results)
        
        # Executa Performance-Based
        perf_results = run_experiment("Performance-Based", clients_per_round, num_rounds, execution)
        perf_executions.append(perf_results)
    
    return fedavg_executions, perf_executions

def calculate_statistics(executions: List[List[float]], strategy_name: str):
    """Calcula estatísticas dos resultados de múltiplas execuções."""
    if not executions or not executions[0]:
        return {}
    
    num_rounds = len(executions[0])
    stats = {
        'strategy': strategy_name,
        'num_executions': len(executions),
        'num_rounds': num_rounds,
        'final_accuracies': [],
        'round_stats': []
    }
    
    # Estatísticas por rodada
    for round_idx in range(num_rounds):
        round_accuracies = [execution[round_idx] for execution in executions if len(execution) > round_idx]
        
        if round_accuracies:
            round_stat = {
                'round': round_idx + 1,
                'mean': statistics.mean(round_accuracies),
                'std': statistics.stdev(round_accuracies) if len(round_accuracies) > 1 else 0,
                'min': min(round_accuracies),
                'max': max(round_accuracies),
                'median': statistics.median(round_accuracies)
            }
            stats['round_stats'].append(round_stat)
    
    # Estatísticas das acurácias finais
    final_accuracies = [execution[-1] for execution in executions if execution]
    stats['final_accuracies'] = final_accuracies
    stats['final_mean'] = statistics.mean(final_accuracies)
    stats['final_std'] = statistics.stdev(final_accuracies) if len(final_accuracies) > 1 else 0
    stats['final_min'] = min(final_accuracies)
    stats['final_max'] = max(final_accuracies)
    stats['final_median'] = statistics.median(final_accuracies)
    
    return stats

def plot_multiple_executions(fedavg_executions, perf_executions, clients_per_round, num_rounds, num_executions):
    """Plota os resultados de múltiplas execuções."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    rounds = range(1, num_rounds + 1)
    
    # Gráfico 1: Todas as execuções
    ax1.set_title(f'Todas as {num_executions} Execuções ({clients_per_round} clientes, {num_rounds} rodadas)', fontsize=14)
    ax1.set_xlabel('Rounds')
    ax1.set_ylabel('Accuracy')
    
    # Plota cada execução do FedAvg
    for i, execution in enumerate(fedavg_executions):
        if len(execution) == num_rounds:
            alpha = 0.3 if i < len(fedavg_executions) - 1 else 0.8
            ax1.plot(rounds, execution, 'b-', alpha=alpha, linewidth=1)
    
    # Plota cada execução do Performance-Based
    for i, execution in enumerate(perf_executions):
        if len(execution) == num_rounds:
            alpha = 0.3 if i < len(perf_executions) - 1 else 0.8
            ax1.plot(rounds, execution, 'r-', alpha=alpha, linewidth=1)
    
    # Adiciona legendas
    ax1.plot([], [], 'b-', label='FedAvg', linewidth=2)
    ax1.plot([], [], 'r-', label='Performance-Based', linewidth=2)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Média com intervalo de confiança
    ax2.set_title(f'Média com Desvio Padrão ({num_executions} execuções)', fontsize=14)
    ax2.set_xlabel('Rounds')
    ax2.set_ylabel('Accuracy')
    
    # Calcula médias e desvios padrão por rodada
    fedavg_means = []
    fedavg_stds = []
    perf_means = []
    perf_stds = []
    
    for round_idx in range(num_rounds):
        fedavg_round_values = [execution[round_idx] for execution in fedavg_executions if len(execution) > round_idx]
        perf_round_values = [execution[round_idx] for execution in perf_executions if len(execution) > round_idx]
        
        if fedavg_round_values:
            fedavg_means.append(statistics.mean(fedavg_round_values))
            fedavg_stds.append(statistics.stdev(fedavg_round_values) if len(fedavg_round_values) > 1 else 0)
        
        if perf_round_values:
            perf_means.append(statistics.mean(perf_round_values))
            perf_stds.append(statistics.stdev(perf_round_values) if len(perf_round_values) > 1 else 0)
    
    # Plota médias com barras de erro
    if fedavg_means:
        ax2.errorbar(rounds[:len(fedavg_means)], fedavg_means, yerr=fedavg_stds, 
                    fmt='b-o', label='FedAvg', capsize=5, capthick=2)
    
    if perf_means:
        ax2.errorbar(rounds[:len(perf_means)], perf_means, yerr=perf_stds, 
                    fmt='r-s', label='Performance-Based', capsize=5, capthick=2)
    
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'multiplas_execucoes_{clients_per_round}clientes_{num_rounds}rodadas_{num_executions}exec_{timestamp}.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def print_statistical_summary(fedavg_stats, perf_stats):
    """Imprime um resumo estatístico dos resultados."""
    print(f"\n{'='*60}")
    print(f"RESUMO ESTATÍSTICO ({fedavg_stats['num_executions']} execuções)")
    print(f"{'='*60}")
    
    print(f"\n{'FedAvg':<20} {'Performance-Based':<20} {'Diferença':<15}")
    print("-" * 55)
    
    # Acurácia final
    fedavg_final = fedavg_stats['final_mean']
    perf_final = perf_stats['final_mean']
    diff = perf_final - fedavg_final
    diff_percent = (diff / fedavg_final * 100) if fedavg_final > 0 else 0
    
    print(f"Final: {fedavg_final:.4f} ± {fedavg_stats['final_std']:.4f}")
    print(f"       {perf_final:.4f} ± {perf_stats['final_std']:.4f}")
    print(f"       {diff:+.4f} ({diff_percent:+.2f}%)")
    
    print(f"\nEstatísticas detalhadas:")
    print(f"FedAvg - Min: {fedavg_stats['final_min']:.4f}, Max: {fedavg_stats['final_max']:.4f}, Mediana: {fedavg_stats['final_median']:.4f}")
    print(f"Perf-Based - Min: {perf_stats['final_min']:.4f}, Max: {perf_stats['final_max']:.4f}, Mediana: {perf_stats['final_median']:.4f}")
    
    # Teste de significância simples (se a diferença é maior que 2 desvios padrão)
    combined_std = np.sqrt(fedavg_stats['final_std']**2 + perf_stats['final_std']**2)
    if combined_std > 0:
        z_score = abs(diff) / combined_std
        print(f"\nZ-score da diferença: {z_score:.2f}")
        if z_score > 2:
            print("✅ Diferença estatisticamente significativa (Z > 2)")
        else:
            print("❌ Diferença não estatisticamente significativa (Z ≤ 2)")

def main():
    """Função principal."""
    print("=== TESTE COM MÚLTIPLAS EXECUÇÕES ===")
    
    # Configurações
    clients_per_round = int(input("Digite o número de clientes por rodada (2, 4, 6, 8): "))
    num_rounds = int(input("Digite o número de rodadas (10, 20, 30): "))
    num_executions = int(input("Digite o número de execuções (recomendado: 10): "))
    
    if clients_per_round not in [2, 4, 6, 8]:
        print("Erro: Número de clientes deve ser 2, 4, 6 ou 8")
        return
    
    if num_rounds not in [10, 20, 30]:
        print("Erro: Número de rodadas deve ser 10, 20 ou 30")
        return
    
    if num_executions < 1:
        print("Erro: Número de execuções deve ser pelo menos 1")
        return
    
    # Executa múltiplas vezes
    fedavg_executions, perf_executions = run_multiple_executions(
        clients_per_round, num_rounds, num_executions
    )
    
    # Calcula estatísticas
    fedavg_stats = calculate_statistics(fedavg_executions, "FedAvg")
    perf_stats = calculate_statistics(perf_executions, "Performance-Based")
    
    # Plota resultados
    plot_multiple_executions(fedavg_executions, perf_executions, 
                           clients_per_round, num_rounds, num_executions)
    
    # Imprime resumo estatístico
    print_statistical_summary(fedavg_stats, perf_stats)
    
    # Salva resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        'config': {
            'clients_per_round': clients_per_round,
            'num_rounds': num_rounds,
            'num_executions': num_executions,
            'timestamp': timestamp
        },
        'fedavg': {
            'executions': fedavg_executions,
            'statistics': fedavg_stats
        },
        'performance_based': {
            'executions': perf_executions,
            'statistics': perf_stats
        }
    }
    
    with open(f"resultados_multiplas_execucoes_{clients_per_round}clientes_{num_rounds}rodadas_{num_executions}exec_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nArquivos gerados:")
    print(f"- multiplas_execucoes_{clients_per_round}clientes_{num_rounds}rodadas_{num_executions}exec_{timestamp}.png")
    print(f"- resultados_multiplas_execucoes_{clients_per_round}clientes_{num_rounds}rodadas_{num_executions}exec_{timestamp}.json")

if __name__ == "__main__":
    main() 