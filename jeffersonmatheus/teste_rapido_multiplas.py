"""Script rápido para múltiplas execuções com configurações pré-definidas."""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import json
import os
import re
import statistics
from datetime import datetime
from typing import List

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
    """Modifica a configuração do servidor."""
    server_app_path, pyproject_path = get_file_paths()
    
    with open(server_app_path, "r") as f:
        content = f.read()
    
    content = re.sub(r'clients_per_round = \d+', f'clients_per_round = {clients_per_round}', content)
    fraction_fit = clients_per_round / 10.0
    content = re.sub(r'fraction_fit=0\.\d+', f'fraction_fit={fraction_fit}', content)
    
    with open(server_app_path, "w") as f:
        f.write(content)
    
    with open(pyproject_path, "r") as f:
        pyproject_content = f.read()
    
    pyproject_content = re.sub(r'num-server-rounds = \d+', f'num-server-rounds = {num_rounds}', pyproject_content)
    
    with open(pyproject_path, "w") as f:
        f.write(pyproject_content)

def run_experiment(strategy_name: str, clients_per_round: int, num_rounds: int, execution_id: int) -> List[float]:
    """Executa um experimento e retorna as accuracies."""
    print(f"  Exec {execution_id}: {strategy_name}")
    
    server_app_path, _ = get_file_paths()
    
    with open(server_app_path, "r") as f:
        content = f.read()
    
    if strategy_name == "FedAvg":
        new_content = content.replace("USE_PERFORMANCE_BASED = True", "USE_PERFORMANCE_BASED = False")
    else:
        new_content = content.replace("USE_PERFORMANCE_BASED = False", "USE_PERFORMANCE_BASED = True")
    
    with open(server_app_path, "w") as f:
        f.write(new_content)
    
    result_file = f"results_{strategy_name.lower().replace('-', '_')}_{clients_per_round}clients_exec_{execution_id}.txt"
    with open(result_file, "w") as f:
        subprocess.run(["flwr", "run"], stdout=f, stderr=f)
    
    accuracies = []
    with open(result_file, "r") as f:
        content = f.read()
        
    if "'accuracy': [" in content:
        start_marker = "'accuracy': ["
        end_marker = "]}"
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            start_idx += len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            
            if end_idx != -1:
                metrics_section = content[start_idx:end_idx]
                pattern = r'\((\d+),\s*([\d.]+)\)'
                matches = re.findall(pattern, metrics_section)
                matches.sort(key=lambda x: int(x[0]))
                accuracies = [float(match[1]) for match in matches]
    
    return accuracies

def run_quick_test(clients_per_round: int = 4, num_rounds: int = 10, num_executions: int = 5):
    """Executa um teste rápido com configurações pré-definidas."""
    print(f"\n=== TESTE RÁPIDO: {num_executions} execuções ===")
    print(f"Config: {clients_per_round} clientes, {num_rounds} rodadas")
    
    modify_server_config(clients_per_round, num_rounds)
    
    fedavg_results = []
    perf_results = []
    
    for exec_id in range(1, num_executions + 1):
        print(f"\n--- Execução {exec_id}/{num_executions} ---")
        
        fedavg_acc = run_experiment("FedAvg", clients_per_round, num_rounds, exec_id)
        fedavg_results.append(fedavg_acc)
        
        perf_acc = run_experiment("Performance-Based", clients_per_round, num_rounds, exec_id)
        perf_results.append(perf_acc)
        
        if fedavg_acc and perf_acc:
            diff = ((perf_acc[-1] - fedavg_acc[-1]) / fedavg_acc[-1] * 100)
            print(f"    FedAvg: {fedavg_acc[-1]:.4f}, Perf: {perf_acc[-1]:.4f}, Diff: {diff:+.2f}%")
    
    return fedavg_results, perf_results

def plot_quick_results(fedavg_results, perf_results, clients_per_round, num_rounds, num_executions):
    """Plota resultados do teste rápido."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    rounds = range(1, num_rounds + 1)
    
    # Gráfico 1: Todas as execuções
    ax1.set_title(f'Teste Rápido: {num_executions} execuções', fontsize=14)
    ax1.set_xlabel('Rounds')
    ax1.set_ylabel('Accuracy')
    
    for i, execution in enumerate(fedavg_results):
        if len(execution) == num_rounds:
            alpha = 0.4
            ax1.plot(rounds, execution, 'b-', alpha=alpha, linewidth=1)
    
    for i, execution in enumerate(perf_results):
        if len(execution) == num_rounds:
            alpha = 0.4
            ax1.plot(rounds, execution, 'r-', alpha=alpha, linewidth=1)
    
    ax1.plot([], [], 'b-', label='FedAvg', linewidth=2)
    ax1.plot([], [], 'r-', label='Performance-Based', linewidth=2)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Médias
    ax2.set_title('Médias das execuções', fontsize=14)
    ax2.set_xlabel('Rounds')
    ax2.set_ylabel('Accuracy')
    
    fedavg_means = []
    perf_means = []
    
    for round_idx in range(num_rounds):
        fedavg_round_values = [execution[round_idx] for execution in fedavg_results if len(execution) > round_idx]
        perf_round_values = [execution[round_idx] for execution in perf_results if len(execution) > round_idx]
        
        if fedavg_round_values:
            fedavg_means.append(statistics.mean(fedavg_round_values))
        
        if perf_round_values:
            perf_means.append(statistics.mean(perf_round_values))
    
    if fedavg_means:
        ax2.plot(rounds[:len(fedavg_means)], fedavg_means, 'b-o', label='FedAvg', linewidth=2)
    
    if perf_means:
        ax2.plot(rounds[:len(perf_means)], perf_means, 'r-s', label='Performance-Based', linewidth=2)
    
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'teste_rapido_{clients_per_round}clientes_{num_rounds}rodadas_{num_executions}exec_{timestamp}.png', 
                dpi=300, bbox_inches='tight')
    plt.close()

def print_quick_summary(fedavg_results, perf_results):
    """Imprime resumo rápido dos resultados."""
    if not fedavg_results or not perf_results:
        print("Erro: Nenhum resultado para analisar")
        return
    
    fedavg_finals = [execution[-1] for execution in fedavg_results if execution]
    perf_finals = [execution[-1] for execution in perf_results if execution]
    
    if not fedavg_finals or not perf_finals:
        print("Erro: Não foi possível extrair resultados finais")
        return
    
    fedavg_mean = statistics.mean(fedavg_finals)
    perf_mean = statistics.mean(perf_finals)
    diff = perf_mean - fedavg_mean
    diff_percent = (diff / fedavg_mean * 100) if fedavg_mean > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"RESUMO RÁPIDO ({len(fedavg_finals)} execuções)")
    print(f"{'='*50}")
    print(f"FedAvg Final: {fedavg_mean:.4f} (min: {min(fedavg_finals):.4f}, max: {max(fedavg_finals):.4f})")
    print(f"Perf-Based Final: {perf_mean:.4f} (min: {min(perf_finals):.4f}, max: {max(perf_finals):.4f})")
    print(f"Diferença: {diff:+.4f} ({diff_percent:+.2f}%)")
    
    if diff_percent > 5:
        print("✅ Performance-Based é significativamente melhor")
    elif diff_percent < -5:
        print("❌ FedAvg é significativamente melhor")
    else:
        print("➡️ Diferença pequena, resultados similares")

def main():
    """Função principal para teste rápido."""
    print("=== TESTE RÁPIDO COM MÚLTIPLAS EXECUÇÕES ===")
    
    # Configurações rápidas
    print("\nConfigurações disponíveis:")
    print("1. Teste rápido (4 clientes, 10 rodadas, 5 execuções)")
    print("2. Teste médio (6 clientes, 10 rodadas, 5 execuções)")
    print("3. Teste completo (4 clientes, 20 rodadas, 5 execuções)")
    print("4. Personalizado")
    
    choice = input("\nEscolha uma opção (1-4): ")
    
    if choice == "1":
        clients, rounds, execs = 4, 10, 5
    elif choice == "2":
        clients, rounds, execs = 6, 10, 5
    elif choice == "3":
        clients, rounds, execs = 4, 20, 5
    elif choice == "4":
        clients = int(input("Clientes por rodada (2-8): "))
        rounds = int(input("Número de rodadas (10-30): "))
        execs = int(input("Número de execuções (3-10): "))
    else:
        print("Opção inválida, usando configuração padrão")
        clients, rounds, execs = 4, 10, 5
    
    # Executa o teste
    fedavg_results, perf_results = run_quick_test(clients, rounds, execs)
    
    # Plota e analisa resultados
    plot_quick_results(fedavg_results, perf_results, clients, rounds, execs)
    print_quick_summary(fedavg_results, perf_results)
    
    # Salva resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        'config': {'clients': clients, 'rounds': rounds, 'executions': execs},
        'fedavg': fedavg_results,
        'performance_based': perf_results
    }
    
    with open(f"teste_rapido_{clients}clientes_{rounds}rodadas_{execs}exec_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\nArquivos gerados:")
    print(f"- teste_rapido_{clients}clientes_{rounds}rodadas_{execs}exec_{timestamp}.png")
    print(f"- teste_rapido_{clients}clientes_{rounds}rodadas_{execs}exec_{timestamp}.json")

if __name__ == "__main__":
    main() 