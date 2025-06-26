"""Script para experimentos abrangentes de comparação entre estratégias."""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import json
import os
import re
from typing import Dict, List, Tuple

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

def plot_comparison_comprehensive(results: Dict, num_rounds: int):
    """Plota comparação abrangente entre todas as configurações."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Comparação Abrangente de Estratégias ({num_rounds} rodadas)', fontsize=16)
    
    client_configs = [8, 6, 4, 2]
    colors = ['blue', 'red', 'green', 'orange']
    
    for idx, (clients, color) in enumerate(zip(client_configs, colors)):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        rounds = range(1, num_rounds + 1)
        
        if f'fedavg_{clients}' in results and f'performance_{clients}' in results:
            fedavg_data = results[f'fedavg_{clients}']
            perf_data = results[f'performance_{clients}']
            
            # Garante que temos dados para todas as rodadas
            while len(fedavg_data) < num_rounds:
                fedavg_data.append(fedavg_data[-1] if fedavg_data else 0.0)
            while len(perf_data) < num_rounds:
                perf_data.append(perf_data[-1] if perf_data else 0.0)
            
            ax.plot(rounds, fedavg_data[:num_rounds], 'b-', label='FedAvg', linewidth=2)
            ax.plot(rounds, perf_data[:num_rounds], 'r-', label='Performance-Based', linewidth=2)
            
            ax.set_xlabel('Rounds')
            ax.set_ylabel('Accuracy')
            ax.set_title(f'{clients} clientes por rodada')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Adiciona valores finais
            if fedavg_data and perf_data:
                final_fedavg = fedavg_data[-1]
                final_perf = perf_data[-1]
                melhoria = ((final_perf - final_fedavg) / final_fedavg * 100) if final_fedavg > 0 else 0
                ax.text(0.02, 0.98, f'Melhoria: {melhoria:+.1f}%', 
                       transform=ax.transAxes, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(f'comparacao_completa_{num_rounds}rodadas.png', dpi=300, bbox_inches='tight')
    plt.close()

def run_comprehensive_experiment(num_rounds: int = 10):
    """Executa experimento abrangente com diferentes configurações."""
    print(f"\n=== EXPERIMENTO COM {num_rounds} RODADAS ===")
    
    client_configs = [8, 6, 4, 2]  # 8, 6, 4, 2 clientes de 10
    results = {}
    
    for clients_per_round in client_configs:
        print(f"\n--- Testando {clients_per_round} clientes por rodada ---")
        
        # Modifica configuração do servidor
        modify_server_config(clients_per_round, num_rounds)
        
        # Executa FedAvg
        fedavg_results = run_experiment("FedAvg", clients_per_round, num_rounds)
        results[f'fedavg_{clients_per_round}'] = fedavg_results
        
        # Executa Performance-Based
        perf_results = run_experiment("Performance-Based", clients_per_round, num_rounds)
        results[f'performance_{clients_per_round}'] = perf_results
        
        # Mostra resultados parciais
        if fedavg_results and perf_results:
            final_fedavg = fedavg_results[-1]
            final_perf = perf_results[-1]
            melhoria = ((final_perf - final_fedavg) / final_fedavg * 100) if final_fedavg > 0 else 0
            print(f"  FedAvg final: {final_fedavg:.4f}")
            print(f"  Performance final: {final_perf:.4f}")
            print(f"  Melhoria: {melhoria:+.2f}%")
    
    # Plota resultados
    plot_comparison_comprehensive(results, num_rounds)
    
    # Salva resultados
    with open(f"resultados_completos_{num_rounds}rodadas.json", "w") as f:
        json.dump(results, f, indent=4)
    
    return results

def analyze_results(results: Dict, num_rounds: int):
    """Analisa e mostra resumo dos resultados."""
    print(f"\n=== RESUMO DOS RESULTADOS ({num_rounds} rodadas) ===")
    
    client_configs = [8, 6, 4, 2]
    
    print(f"{'Clients':<8} {'FedAvg':<10} {'Perf-Based':<12} {'Melhoria':<10}")
    print("-" * 40)
    
    for clients in client_configs:
        fedavg_key = f'fedavg_{clients}'
        perf_key = f'performance_{clients}'
        
        if fedavg_key in results and perf_key in results:
            fedavg_final = results[fedavg_key][-1] if results[fedavg_key] else 0.0
            perf_final = results[perf_key][-1] if results[perf_key] else 0.0
            melhoria = ((perf_final - fedavg_final) / fedavg_final * 100) if fedavg_final > 0 else 0
            
            print(f"{clients:<8} {fedavg_final:<10.4f} {perf_final:<12.4f} {melhoria:<+10.2f}%")

def main():
    """Função principal que executa todos os experimentos."""
    print("=== EXPERIMENTO ABRANGENTE DE ESTRATÉGIAS FEDERADAS ===")
    print("Testando diferentes configurações de clientes e rodadas...")
    
    # Executa experimentos com diferentes números de rodadas
    rodadas_configs = [10, 20, 30]
    todos_resultados = {}
    
    for num_rounds in rodadas_configs:
        resultados = run_comprehensive_experiment(num_rounds)
        todos_resultados[f'{num_rounds}_rodadas'] = resultados
        analyze_results(resultados, num_rounds)
    
    # Salva todos os resultados
    with open("todos_resultados_experimento.json", "w") as f:
        json.dump(todos_resultados, f, indent=4)
    
    print("\n=== EXPERIMENTO CONCLUÍDO ===")
    print("Arquivos gerados:")
    print("- comparacao_completa_10rodadas.png")
    print("- comparacao_completa_20rodadas.png") 
    print("- comparacao_completa_30rodadas.png")
    print("- resultados_completos_10rodadas.json")
    print("- resultados_completos_20rodadas.json")
    print("- resultados_completos_30rodadas.json")
    print("- todos_resultados_experimento.json")

if __name__ == "__main__":
    main() 