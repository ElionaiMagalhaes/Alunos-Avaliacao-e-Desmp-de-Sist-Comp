# Laboratório — Modelagem matemática e simulação de eventos discretos

**Disciplina:** Avaliação e Desempenho de Sistemas Computacionais  
**Professor:** Msc Elionai Magalhães  
**Exemplo:** fila de atendimento M/M/1 (um servidor, chegadas e serviços exponenciais, disciplina FIFO)

## Conteúdo do pacote

- `laboratorio_fila_mm1.py` — programa completo, executável com Python 3.9+ **sem instalar bibliotecas adicionais**.
- `Laboratorio_Fila_MM1_Colab.ipynb` — caderno independente para executar no Google Colab ou Jupyter.
- `exemplo_eventos.csv` — registro de chegadas e saídas de uma execução demonstrativa com 120 clientes.
- `resultados_comparacao.csv` — comparação de dois cenários obtida com 20.000 clientes e semente 42.
- `README_LABORATORIO.md` — estas instruções.

## Opção A — Executar no Windows com Python

1. Instale Python 3, se ainda não estiver instalado: https://www.python.org/downloads/.
2. Extraia o arquivo ZIP para uma pasta local.
3. Abra a pasta no Explorador de Arquivos; na barra de endereço digite `cmd` e pressione Enter.
4. Execute o cenário-base:

   ```powershell
   py laboratorio_fila_mm1.py
   ```

   Se `py` não funcionar, use `python laboratorio_fila_mm1.py`.

5. Compare os cenários:

   ```powershell
   py laboratorio_fila_mm1.py --comparar
   ```

6. Veja eventos e crie um arquivo CSV:

   ```powershell
   py laboratorio_fila_mm1.py --clientes 120 --mostrar-eventos 12 --csv meus_eventos.csv
   ```

7. Faça um experimento com outra taxa de chegada:

   ```powershell
   py laboratorio_fila_mm1.py --taxa-chegada 5.5 --taxa-servico 6 --clientes 20000
   ```

## Opção B — Executar no Google Colab (sem instalar Python localmente)

1. Acesse https://colab.research.google.com/ e entre com sua conta Google.
2. Selecione **Arquivo > Fazer upload de notebook** e escolha `Laboratorio_Fila_MM1_Colab.ipynb`.
3. Execute as células em ordem, pelo botão de reprodução de cada célula.
4. Altere a taxa de chegada de 4 para 5,5 clientes/minuto e execute novamente.
5. Compare a utilização, a espera média na fila e a permanência média.

## Conceitos e fórmulas

- **λ (lambda):** taxa média de chegadas, em clientes/minuto.
- **μ (mi):** taxa média de atendimento de um servidor, em clientes/minuto.
- **ρ (rô):** utilização teórica do servidor, `ρ = λ/μ`.
- **Wq:** espera média antes do atendimento, em minutos.
- **W:** permanência média total, incluindo espera e atendimento, em minutos.
- **Lq:** quantidade média de clientes aguardando na fila.
- **L:** quantidade média de clientes no sistema, aguardando ou sendo atendidos.

Para uma fila M/M/1 **em equilíbrio, quando λ < μ**:

- `W = 1 / (μ - λ)`;
- `Wq = λ / [μ × (μ - λ)]`;
- `L = λ × W` e `Lq = λ × Wq` (Lei de Little).

**Cenário-base:** λ = 4 e μ = 6 clientes/minuto. Então ρ = 66,7%, W = 0,5 minuto (30 s) e Wq = 0,333 minuto (20 s). Os valores simulados variam com o tamanho da amostra e a semente; não precisam coincidir exatamente com os valores teóricos.

**Importante:** quando λ ≥ μ, a fila M/M/1 não apresenta equilíbrio estacionário; não use as fórmulas de equilíbrio para concluir que a espera será finita.

## Exercício sugerido

1. Execute o cenário-base com 20.000 clientes e registre ρ, Wq, W e Lq.
2. Execute o cenário de maior carga com λ = 5,5 e μ = 6. Compare a espera média.
3. Execute novamente com outra semente, por exemplo `--semente 123`, e explique por que os valores mudaram.
4. Responda: o servidor ficou mais rápido ou foi a taxa de chegada que aumentou? Por que a fila cresceu?
5. Registre comandos, resultados e interpretação em um pequeno relatório.

## Fontes e observações

- Plano de Ensino de Avaliação e Desempenho de Sistemas Computacionais (Multivix, 2026/2).
- Documentação Python — `random.expovariate`: https://docs.python.org/3/library/random.html#random.expovariate
- Documentação Python — `heapq`: https://docs.python.org/3/library/heapq.html
- Documentação SimPy (biblioteca gratuita opcional para estudos avançados): https://simpy.readthedocs.io/en/latest/

O programa é um **modelo didático simplificado**, com um servidor, fila ilimitada, sem desistências e sem prioridades. Para representar um sistema real, é necessário verificar se as hipóteses são adequadas e usar dados de medição.
