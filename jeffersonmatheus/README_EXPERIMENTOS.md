# Experimentos Abrangentes de Estratégias Federadas

Este diretório contém scripts para executar experimentos abrangentes comparando as estratégias **FedAvg** e **Performance-Based** em diferentes configurações.

## 📁 Arquivos Criados

### 1. `experimento_completo.py`
**Script principal** que executa todos os experimentos automaticamente:
- Testa **4 configurações** de clientes: 8, 6, 4, 2 clientes por rodada
- Testa **3 configurações** de rodadas: 10, 20, 30 rodadas
- Total: **12 experimentos** (4 clientes × 3 rodadas × 2 estratégias)

### 2. `teste_unico.py`
**Script para teste individual** de uma configuração específica:
- Permite escolher quantos clientes e rodadas testar
- Útil para testes rápidos ou debug

### 3. `comparacao_estrategias.py`
**Script original** (mantido para compatibilidade):
- Testa apenas 6 clientes por rodada
- 10 rodadas fixas

## 🚀 Como Usar

### Opção 1: Experimento Completo (Recomendado)
```bash
cd jeffersonmatheus
python experimento_completo.py
```

**O que acontece:**
1. Executa automaticamente todos os 12 experimentos
2. Gera gráficos comparativos para cada configuração
3. Salva todos os resultados em arquivos JSON
4. Mostra resumo final com todas as métricas

**Arquivos gerados:**
- `comparacao_completa_10rodadas.png`
- `comparacao_completa_20rodadas.png`
- `comparacao_completa_30rodadas.png`
- `resultados_completos_10rodadas.json`
- `resultados_completos_20rodadas.json`
- `resultados_completos_30rodadas.json`
- `todos_resultados_experimento.json`

### Opção 2: Teste Individual
```bash
cd jeffersonmatheus
python teste_unico.py
```

**O que acontece:**
1. Solicita o número de clientes (2, 4, 6, 8)
2. Solicita o número de rodadas (10, 20, 30)
3. Executa apenas essa configuração
4. Gera gráfico e resultados específicos

### Opção 3: Script Original
```bash
cd jeffersonmatheus
python comparacao_estrategias.py
```

## 📊 Configurações Testadas

| Clientes por Rodada | Fraction Fit | Descrição |
|-------------------|--------------|-----------|
| 8 de 10 | 0.8 (80%) | Quase todos os clientes |
| 6 de 10 | 0.6 (60%) | Maioria dos clientes |
| 4 de 10 | 0.4 (40%) | Menos da metade |
| 2 de 10 | 0.2 (20%) | Poucos clientes |

## 🔧 Modificações Automáticas

Os scripts modificam automaticamente:

### `server_app.py`
- `clients_per_round = X` (onde X é 8, 6, 4 ou 2)
- `fraction_fit = Y` (onde Y é 0.8, 0.6, 0.4 ou 0.2)

### `pyproject.toml`
- `num-server-rounds = Z` (onde Z é 10, 20 ou 30)

## 📈 Análise dos Resultados

### Gráficos Gerados
- **Comparação lado a lado** das duas estratégias
- **Valores de acurácia** em cada rodada
- **Percentual de melhoria** da estratégia Performance-Based
- **Análise por rodada** com diferenças percentuais

### Métricas Calculadas
- **Acurácia final** de cada estratégia
- **Melhoria percentual** da Performance-Based sobre FedAvg
- **Evolução temporal** da performance
- **Consistência** dos resultados

## 🎯 Cenários de Teste

### Cenário 1: 10 Rodadas
- **Objetivo**: Teste rápido, validação inicial
- **Tempo**: ~30-45 minutos
- **Uso**: Verificar se as estratégias funcionam corretamente

### Cenário 2: 20 Rodadas
- **Objetivo**: Teste intermediário, análise de convergência
- **Tempo**: ~1-1.5 horas
- **Uso**: Verificar estabilidade e tendências

### Cenário 3: 30 Rodadas
- **Objetivo**: Teste completo, resultados definitivos
- **Tempo**: ~1.5-2.5 horas
- **Uso**: Análise final e publicação de resultados

## 🔍 Interpretação dos Resultados

### Quantidade de Clientes
- **Mais clientes (8)**: Maior diversidade, convergência mais lenta
- **Menos clientes (2)**: Menos diversidade, convergência mais rápida
- **Meio termo (4-6)**: Equilíbrio entre diversidade e eficiência

### Número de Rodadas
- **10 rodadas**: Resultados preliminares
- **20 rodadas**: Tendências claras
- **30 rodadas**: Resultados estáveis e confiáveis

### Estratégias
- **FedAvg**: Baseline, seleção aleatória
- **Performance-Based**: Seleção inteligente baseada em histórico

## ⚠️ Observações Importantes

1. **Tempo de execução**: O experimento completo pode levar 3-4 horas
2. **Recursos**: Certifique-se de ter memória suficiente
3. **Backup**: Os scripts modificam arquivos automaticamente
4. **Interrupção**: Pode interromper a qualquer momento (Ctrl+C)

## 🛠️ Troubleshooting

### Problema: "Arquivo não encontrado"
- Verifique se está no diretório correto (`jeffersonmatheus/`)
- Confirme se os arquivos `server_app.py` e `pyproject.toml` existem

### Problema: "Erro de permissão"
- Verifique se tem permissão de escrita no diretório
- Execute com privilégios adequados se necessário

### Problema: "Resultados incompletos"
- Verifique se o comando `flwr run` está funcionando
- Confirme se o ambiente virtual está ativado

## 📝 Próximos Passos

Após executar os experimentos, você pode:

1. **Analisar os gráficos** gerados
2. **Comparar os resultados** entre diferentes configurações
3. **Identificar padrões** de comportamento das estratégias
4. **Otimizar parâmetros** baseado nos resultados
5. **Documentar descobertas** para relatórios ou artigos 