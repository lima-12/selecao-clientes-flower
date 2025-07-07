# Testes com Múltiplas Execuções

Este diretório contém scripts para executar o mesmo teste múltiplas vezes, garantindo resultados estatisticamente confiáveis e eliminando a variabilidade aleatória.

## 🎯 **Por que múltiplas execuções?**

Em aprendizado federado, uma única execução pode não ser representativa devido a:
- **Inicialização aleatória** dos pesos do modelo
- **Seleção aleatória** de clientes (no FedAvg)
- **Particionamento não-determinístico** dos dados
- **Variações de hardware** e timing

Múltiplas execuções permitem:
- **Resultados estatisticamente confiáveis**
- **Análise de variabilidade** entre execuções
- **Teste de significância** das diferenças
- **Identificação de padrões** consistentes

---

## 📁 **Scripts Disponíveis**

### 1. `teste_multiplas_execucoes.py` - **Script Completo**
- **Análise estatística detalhada**
- **Gráficos com intervalos de confiança**
- **Teste de significância (Z-score)**
- **Configuração totalmente personalizável**

### 2. `teste_rapido_multiplas.py` - **Script Rápido**
- **Configurações pré-definidas**
- **Análise simplificada**
- **Resultados rápidos**
- **Ideal para testes preliminares**

---

## 🚀 **Como Usar**

### **Opção 1: Teste Rápido (Recomendado para começar)**
```bash
cd jeffersonmatheus
python teste_rapido_multiplas.py
```

**Configurações disponíveis:**
- **1. Teste rápido**: 4 clientes, 10 rodadas, 5 execuções (~25 min)
- **2. Teste médio**: 6 clientes, 10 rodadas, 5 execuções (~30 min)
- **3. Teste completo**: 4 clientes, 20 rodadas, 5 execuções (~50 min)
- **4. Personalizado**: Você escolhe todas as configurações

### **Opção 2: Teste Completo**
```bash
cd jeffersonmatheus
python teste_multiplas_execucoes.py
```

**Você define:**
- Número de clientes por rodada (2, 4, 6, 8)
- Número de rodadas (10, 20, 30)
- Número de execuções (recomendado: 10)

---

## 📊 **Análise dos Resultados**

### **Gráficos Gerados**

#### **Gráfico 1: Todas as Execuções**
- Mostra **cada execução individual**
- Permite ver a **variabilidade** entre execuções
- Identifica **outliers** ou execuções anômalas

#### **Gráfico 2: Média com Desvio Padrão**
- **Linha sólida**: Média das execuções
- **Barras de erro**: Desvio padrão
- **Intervalo de confiança** visual

### **Estatísticas Calculadas**

#### **Por Estratégia:**
- **Média final** de todas as execuções
- **Desvio padrão** (medida de variabilidade)
- **Valor mínimo** e **máximo**
- **Mediana** (valor central)

#### **Comparação:**
- **Diferença absoluta** entre estratégias
- **Diferença percentual**
- **Z-score** para teste de significância

---

## 📈 **Interpretação dos Resultados**

### **Z-Score (Teste de Significância)**
- **Z > 2**: Diferença estatisticamente significativa ✅
- **Z ≤ 2**: Diferença não significativa ❌

### **Desvio Padrão**
- **Baixo (< 0.02)**: Resultados consistentes
- **Médio (0.02-0.05)**: Variabilidade moderada
- **Alto (> 0.05)**: Alta variabilidade

### **Diferença Percentual**
- **> +5%**: Performance-Based é melhor
- **< -5%**: FedAvg é melhor
- **Entre ±5%**: Resultados similares

---

## ⏱️ **Tempo Estimado**

| Configuração | Execuções | Tempo Total |
|-------------|-----------|-------------|
| 4 clientes, 10 rodadas | 5 | ~25 minutos |
| 6 clientes, 10 rodadas | 5 | ~30 minutos |
| 4 clientes, 20 rodadas | 5 | ~50 minutos |
| 4 clientes, 10 rodadas | 10 | ~50 minutos |
| 6 clientes, 20 rodadas | 10 | ~100 minutos |

---

## 📋 **Exemplo de Saída**

```
=== TESTE RÁPIDO: 5 execuções ===
Config: 4 clientes, 10 rodadas

--- Execução 1/5 ---
  Exec 1: FedAvg
    Extraídas 10 rodadas. Final: 0.5746
  Exec 1: Performance-Based
    Extraídas 10 rodadas. Final: 0.5804
    FedAvg: 0.5746, Perf: 0.5804, Diff: +1.01%

[... mais execuções ...]

==================================================
RESUMO RÁPIDO (5 execuções)
==================================================
FedAvg Final: 0.5723 (min: 0.5604, max: 0.5847)
Perf-Based Final: 0.5789 (min: 0.5678, max: 0.5901)
Diferença: +0.0066 (+1.15%)
✅ Performance-Based é significativamente melhor
```

---

## 🔍 **Análise Avançada**

### **Consistência dos Resultados**
- **Baixa variabilidade**: Resultados confiáveis
- **Alta variabilidade**: Pode precisar de mais execuções

### **Convergência**
- **Curvas suaves**: Boa convergência
- **Curvas instáveis**: Problemas de treinamento

### **Robustez**
- **Performance consistente**: Estratégia robusta
- **Performance variável**: Estratégia sensível

---

## 📝 **Arquivos Gerados**

### **Gráficos:**
- `teste_rapido_Xclientes_Yrodadas_Zexec_TIMESTAMP.png`
- `multiplas_execucoes_Xclientes_Yrodadas_Zexec_TIMESTAMP.png`

### **Dados:**
- `teste_rapido_Xclientes_Yrodadas_Zexec_TIMESTAMP.json`
- `resultados_multiplas_execucoes_Xclientes_Yrodadas_Zexec_TIMESTAMP.json`

### **Logs:**
- `results_fedavg_Xclients_exec_Y.txt`
- `results_performance_based_Xclients_exec_Y.txt`

---

## ⚠️ **Dicas Importantes**

1. **Comece com testes rápidos** (5 execuções) para validar
2. **Use 10+ execuções** para resultados definitivos
3. **Monitore a variabilidade** - se for alta, aumente o número de execuções
4. **Compare desvios padrão** entre estratégias
5. **Considere o tempo** - testes completos podem levar horas

---

## 🎯 **Próximos Passos**

Após executar os testes:
1. **Analise a significância estatística**
2. **Compare com outros cenários** (diferentes clientes/rodadas)
3. **Documente os padrões** encontrados
4. **Otimize parâmetros** baseado nos resultados
5. **Publique resultados** com análise estatística completa 