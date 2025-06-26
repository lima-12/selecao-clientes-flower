"""Script para testar uma configuração específica de clientes e rodadas."""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import json
import os
import re
from typing import Dict, List

def get_file_paths():
    """Detecta automaticamente os caminhos corretos dos arquivos."""
    # Verifica se estamos no diretório jeffersonmatheus ou no diretório pai
    if os.path.exists("pyproject.toml"):
        # Estamos no diretório jeffersonmatheus
        server_app_path = "jeffersonmatheus/server_app.py"
        pyproject_path = "pyproject.toml"
    elif os.path.exists("jeffersonmatheus/pyproject.toml"):
        # Estamos no diretório pai
        server_app_path = "jeffersonmatheus/jeffersonmatheus/server_app.py"
        pyproject_path = "jeffersonmatheus/pyproject.toml"
    else:
        raise FileNotFoundError("Não foi possível encontrar os arquivos necessários. Execute o script de dentro do diretório jeffersonmatheus ou do diretório pai.")
    
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
    fraction_fit = clients_per_round / 10.0  # Assumindo 10 clientes totais
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

def run_experiment(strategy_name: str, clients_per_round: int, num_rounds: int = 10) -> List[float]:
    """Executa o experimento com uma estratégia específica e retorna os resultados."""
    print(f"  Executando {strategy_name} com {clients_per_round} clientes por rodada...")
    
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
    result_file = f"results_{strategy_name.lower().replace('-', '_')}_{clients_per_round}clients.txt"
    with open(result_file, "w") as f:
        subprocess.run(["flwr", "run"], stdout=f, stderr=f)
    
    # Extrai as métricas do arquivo de resultado
    accuracies = []
    with open(result_file, "r") as f:
        content = f.read()
        
    # Procura pela seção de métricas no final do arquivo
    if "'accuracy': [" in content:
        # Extrai a seção completa de accuracy
        start_marker = "'accuracy': ["
        end_marker = "]}"
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            start_idx += len(start_marker)
            end_idx = content.find(end_marker, start_idx)
            
            if end_idx != -1:
                metrics_section = content[start_idx:end_idx]
                
                # Extrai os pares (round, accuracy) usando regex mais robusto
                import re
                pattern = r'\((\d+),\s*([\d.]+)\)'
                matches = re.findall(pattern, metrics_section)
                
                # Ordena por número da rodada e extrai apenas as accuracies
                matches.sort(key=lambda x: int(x[0]))
                accuracies = [float(match[1]) for match in matches]
                
                print(f"    Extraídas {len(accuracies)} rodadas: {accuracies}")
    
    return accuracies

def plot_single_comparison(fedavg_results, performance_results, clients_per_round, num_rounds):
    """Plota comparação para uma configuração específica."""
    rounds = range(1, len(fedavg_results) + 1)
    
    plt.figure(figsize=(12, 8))
    plt.plot(rounds, fedavg_results, 'b-', label='FedAvg (Baseline)', linewidth=2, marker='o')
    plt.plot(rounds, performance_results, 'r-', label='Performance-Based', linewidth=2, marker='s')
    
    plt.xlabel('Rounds', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    plt.title(f'Comparação: {clients_per_round} clientes por rodada ({num_rounds} rodadas)', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Adiciona valores de accuracy em pontos importantes
    for i, (acc_fedavg, acc_perf) in enumerate(zip(fedavg_results, performance_results)):
        if i % 2 == 0 or i == len(fedavg_results) - 1:  # Mostra a cada 2 rodadas e na última
            plt.annotate(f'{acc_fedavg:.3f}', 
                        (i+1, acc_fedavg), 
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center',
                        fontsize=9)
            plt.annotate(f'{acc_perf:.3f}', 
                        (i+1, acc_perf), 
                        textcoords="offset points", 
                        xytext=(0,-15), 
                        ha='center',
                        fontsize=9)
    
    # Adiciona estatísticas finais
    final_fedavg = fedavg_results[-1]
    final_perf = performance_results[-1]
    melhoria = ((final_perf - final_fedavg) / final_fedavg * 100) if final_fedavg > 0 else 0
    
    plt.text(0.02, 0.98, f'FedAvg Final: {final_fedavg:.4f}\nPerf-Based Final: {final_perf:.4f}\nMelhoria: {melhoria:+.2f}%', 
             transform=plt.gca().transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
             fontsize=11)
    
    plt.tight_layout()
    plt.savefig(f'comparacao_{clients_per_round}clientes_{num_rounds}rodadas.png', dpi=300, bbox_inches='tight')
    plt.close()

def test_single_configuration(clients_per_round: int, num_rounds: int = 10):
    """Testa uma configuração específica."""
    print(f"\n=== TESTANDO {clients_per_round} CLIENTES POR RODADA ({num_rounds} RODADAS) ===")
    
    # Modifica configuração do servidor
    modify_server_config(clients_per_round, num_rounds)
    
    # Executa FedAvg
    print("Executando FedAvg...")
    fedavg_results = run_experiment("FedAvg", clients_per_round, num_rounds)
    
    # Executa Performance-Based
    print("Executando Performance-Based...")
    perf_results = run_experiment("Performance-Based", clients_per_round, num_rounds)
    
    # Plota resultados
    plot_single_comparison(fedavg_results, perf_results, clients_per_round, num_rounds)
    
    # Salva resultados
    results = {
        "fedavg": fedavg_results,
        "performance_based": perf_results,
        "config": {
            "clients_per_round": clients_per_round,
            "num_rounds": num_rounds
        }
    }
    
    with open(f"resultados_{clients_per_round}clientes_{num_rounds}rodadas.json", "w") as f:
        json.dump(results, f, indent=4)
    
    # Mostra resultados
    print(f"\n=== RESULTADOS ===")
    print(f"FedAvg - Accuracy Final: {fedavg_results[-1]:.4f}")
    print(f"Performance-Based - Accuracy Final: {perf_results[-1]:.4f}")
    
    melhoria = ((perf_results[-1] - fedavg_results[-1]) / fedavg_results[-1] * 100)
    print(f"Melhoria: {melhoria:+.2f}%")
    
    # Análise por rodada
    print(f"\nAnálise por rodada:")
    for round_num, (acc_fedavg, acc_perf) in enumerate(zip(fedavg_results, perf_results), 1):
        diff = ((acc_perf - acc_fedavg) / acc_fedavg * 100)
        print(f"Rodada {round_num:2d}: FedAvg={acc_fedavg:.4f}, Performance={acc_perf:.4f}, Diff={diff:+.2f}%")
    
    print(f"\nArquivos gerados:")
    print(f"- comparacao_{clients_per_round}clientes_{num_rounds}rodadas.png")
    print(f"- resultados_{clients_per_round}clientes_{num_rounds}rodadas.json")

def main():
    """Função principal."""
    print("=== TESTE DE CONFIGURAÇÃO ÚNICA ===")
    
    # Configurações para testar
    clients_per_round = int(input("Digite o número de clientes por rodada (2, 4, 6, 8): "))
    num_rounds = int(input("Digite o número de rodadas (10, 20, 30): "))
    
    if clients_per_round not in [2, 4, 6, 8]:
        print("Erro: Número de clientes deve ser 2, 4, 6 ou 8")
        return
    
    if num_rounds not in [10, 20, 30]:
        print("Erro: Número de rodadas deve ser 10, 20 ou 30")
        return
    
    test_single_configuration(clients_per_round, num_rounds)

if __name__ == "__main__":
    main() 