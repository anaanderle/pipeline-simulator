# Simulador de Pipeline 

## Grupo
- Ana Clara de Oliveira Anderle
- Carolina Silva dos Santos
- Guilherme Lenzi de Oliveira
- Taimisson de Carvalho Schardosim

## Descrição do Projeto
Simulador de pipeline de processador com cinco estágios. O objetivo é demonstrar a melhoria de desempenho utilizando mecanismos de predição de desvios.

### Primeira Entrega: Predição Estática
Implementação da predição estática, assumindo que desvios não são tomados.

### Segunda Entrega: Predição Dinâmica de 1 Bit
Implementação da predição dinâmica utilizando um preditor de 1 bit.

## Resultados

### Case 1 com Predição Estática
- **Instruções**: 114
- **Instruções inválidas**: 20
- **Taxa de erros**: 17,54%

### Case 1 com Predição Dinâmica
- **Instruções**: 106
- **Instruções inválidas**: 4
- **Taxa de erros**: 3,77%

- **Melhoria**:
  - **Taxa de erros**: 78,5%
  - **Número de instruções executadas**: 7,00%

### Case 2 com Predição Estática
- **Instruções**: 87
- **Instruções inválidas**: 20
- **Taxa de erros**: 22,99%

### Case 2 com Predição Dinâmica
- **Instruções**: 79
- **Instruções inválidas**: 4
- **Taxa de erros**: 5,06%

- **Melhoria**:
  - **Taxa de erros**: 77,99%
  - **Número de instruções executadas**: 9,19%

---
**Escola Politécnica - Universidade do Vale do Rio do Sinos**  
**Arquitetura e Organização de Computadores**  
**Trabalho GA**
