#  """Script para comparar as estratégias PerformanceBasedFedAvg e FedAvg."""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import json
import os

def run_experiment(strategy_name):
    """Executa o experimento com uma estratégia específica e retorna os resultados."""
    # Configura a estratégia no arquivo server_app.py
    with open("jeffersonmatheus/server_app.py", "r") as f:
        content = f.read()
    
    if strategy_name == "FedAvg":
        new_content = content.replace("USE_PERFORMANCE_BASED = True", "USE_PERFORMANCE_BASED = False")
    else:  # Performance-Based
        new_content = content.replace("USE_PERFORMANCE_BASED = False", "USE_PERFORMANCE_BASED = True")
    
    with open("jeffersonmatheus/server_app.py", "w") as f:
        f.write(new_content)
    
    # Executa o experimento
    result_file = f"results_{strategy_name.lower().replace('-', '_')}.txt"
    with open(result_file, "w") as f:
        subprocess.run(["flwr", "run"], stdout=f, stderr=f)
    
    # Extrai as métricas do arquivo de resultado
    accuracies = []
    with open(result_file, "r") as f:
        content = f.read()
        
    # Procura pela seção de métricas no final do arquivo
    if "'accuracy': [" in content:
        metrics_section = content.split("'accuracy': [")[1].split("]")[0]
        # Extrai os pares (round, accuracy)
        pairs = metrics_section.split("),")
        for pair in pairs:
            try:
                # Extrai apenas o valor da accuracy
                accuracy = float(pair.split(",")[1].strip())
                accuracies.append(accuracy)
            except:
                continue
    
    return accuracies

def plot_comparison(fedavg_results, performance_results):
    """Plota a comparação entre as estratégias."""
    rounds = range(1, len(fedavg_results) + 1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(rounds, fedavg_results, 'b-', label='FedAvg (Baseline)', linewidth=2)
    plt.plot(rounds, performance_results, 'r-', label='Performance-Based', linewidth=2)
    
    plt.xlabel('Rounds')
    plt.ylabel('Accuracy')
    plt.title('Comparação entre Estratégias de Seleção de Clientes (non-IID)')
    plt.legend()
    plt.grid(True)
    
    # Adiciona uma grade mais detalhada
    plt.grid(True, which='both', linestyle='--', alpha=0.6)
    
    # Adiciona os valores de accuracy em cada ponto
    for i, (acc_fedavg, acc_perf) in enumerate(zip(fedavg_results, performance_results)):
        plt.annotate(f'{acc_fedavg:.3f}', 
                    (i+1, acc_fedavg), 
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center',
                    fontsize=8)
        plt.annotate(f'{acc_perf:.3f}', 
                    (i+1, acc_perf), 
                    textcoords="offset points", 
                    xytext=(0,-15), 
                    ha='center',
                    fontsize=8)
    
    plt.tight_layout()
    plt.savefig('comparacao_estrategias.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Executa experimentos
    print("Executando experimento com FedAvg...")
    fedavg_results = run_experiment("FedAvg")
    
    print("Executando experimento com Performance-Based...")
    performance_results = run_experiment("Performance-Based")
    
    # Plota resultados
    plot_comparison(fedavg_results, performance_results)
    
    # Salva resultados em um arquivo
    results = {
        "fedavg": fedavg_results,
        "performance_based": performance_results
    }
    
    with open("resultados_comparacao.json", "w") as f:
        json.dump(results, f, indent=4)
    
    # Calcula e mostra métricas comparativas
    print("\nResultados:")
    print(f"FedAvg - Accuracy Final: {fedavg_results[-1]:.4f}")
    print(f"Performance-Based - Accuracy Final: {performance_results[-1]:.4f}")
    
    melhoria = ((performance_results[-1] - fedavg_results[-1]) / fedavg_results[-1] * 100)
    print(f"\nMelhoria: {melhoria:.2f}%")
    
    # Análise adicional
    print("\nAnálise por rodada:")
    for round_num, (acc_fedavg, acc_perf) in enumerate(zip(fedavg_results, performance_results), 1):
        diff = ((acc_perf - acc_fedavg) / acc_fedavg * 100)
        print(f"Rodada {round_num:2d}: FedAvg={acc_fedavg:.4f}, Performance={acc_perf:.4f}, Diff={diff:+.2f}%")

if __name__ == "__main__":
    main()