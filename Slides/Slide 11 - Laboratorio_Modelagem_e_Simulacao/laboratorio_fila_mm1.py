#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Laboratório de modelagem e simulação de eventos discretos: fila M/M/1.

Autor do material didático: Professor Msc Elionai Magalhães.
Disciplina: Avaliação e Desempenho de Sistemas Computacionais.

Requisitos: Python 3.9+; nenhuma biblioteca externa.

Exemplos:
    python laboratorio_fila_mm1.py
    python laboratorio_fila_mm1.py --comparar
    python laboratorio_fila_mm1.py --taxa-chegada 5.5 --taxa-servico 6 --clientes 20000
    python laboratorio_fila_mm1.py --clientes 200 --csv eventos.csv --mostrar-eventos 12
"""

from __future__ import annotations

import argparse
import csv
import heapq
import random
from collections import deque
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Resultado:
    taxa_chegada: float
    taxa_servico: float
    clientes: int
    duracao: float
    utilizacao: float
    espera_media: float
    permanencia_media: float
    fila_media: float
    sistema_medio: float
    taxa_efetiva: float
    eventos: list[tuple[float, str, int, int, int]]


def simular_fila_mm1(
    taxa_chegada: float = 4.0,
    taxa_servico: float = 6.0,
    clientes: int = 20000,
    semente: int = 42,
    guardar_eventos: bool = False,
) -> Resultado:
    """Simula clientes com chegadas e serviços exponenciais, um servidor e fila FIFO.

    Tempo em MINUTOS, taxas em CLIENTES/MINUTO.
    A simulação começa vazia e encerra após atender todos os clientes gerados.
    Médias são estimativas de um experimento finito, não valores exatos.
    """
    if taxa_chegada <= 0 or taxa_servico <= 0:
        raise ValueError("As taxas de chegada e serviço devem ser positivas.")
    if clientes < 1:
        raise ValueError("A quantidade de clientes deve ser pelo menos 1.")

    sorteio_chegada = random.Random(semente)
    sorteio_servico = random.Random(semente + 101)
    agenda: list[tuple[float, int, str, int]] = []
    proximo_seq = 0

    def agendar(tempo: float, tipo: str, identificador: int) -> None:
        nonlocal proximo_seq
        heapq.heappush(agenda, (tempo, proximo_seq, tipo, identificador))
        proximo_seq += 1

    fila: deque[tuple[int, float]] = deque()
    servidor_ocupado = False
    ultimo_tempo = 0.0
    area_fila = 0.0
    area_sistema = 0.0
    area_ocupacao = 0.0
    soma_esperas = 0.0
    soma_permanencias = 0.0
    chegadas_geradas = 0
    saidas = 0
    instantes_chegada: dict[int, float] = {}
    historico: list[tuple[float, str, int, int, int]] = []

    agendar(sorteio_chegada.expovariate(taxa_chegada), "CHEGADA", 1)

    while agenda:
        instante, _ordem, tipo, cliente = heapq.heappop(agenda)
        delta = instante - ultimo_tempo
        if delta < -1e-10:
            raise RuntimeError("Agenda de eventos fora da ordem temporal.")
        area_fila += len(fila) * delta
        area_sistema += (len(fila) + int(servidor_ocupado)) * delta
        area_ocupacao += int(servidor_ocupado) * delta
        ultimo_tempo = instante

        if tipo == "CHEGADA":
            chegadas_geradas += 1
            instantes_chegada[cliente] = instante
            if chegadas_geradas < clientes:
                agendar(
                    instante + sorteio_chegada.expovariate(taxa_chegada),
                    "CHEGADA", cliente + 1,
                )
            if servidor_ocupado:
                fila.append((cliente, instante))
            else:
                servidor_ocupado = True
                agendar(
                    instante + sorteio_servico.expovariate(taxa_servico),
                    "SAIDA", cliente,
                )
        else:  # SAIDA
            saidas += 1
            soma_permanencias += instante - instantes_chegada.pop(cliente)
            if fila:
                proximo_cliente, instante_chegada = fila.popleft()
                soma_esperas += instante - instante_chegada
                agendar(
                    instante + sorteio_servico.expovariate(taxa_servico),
                    "SAIDA", proximo_cliente,
                )
            else:
                servidor_ocupado = False

        if guardar_eventos:
            historico.append((instante, tipo, cliente, len(fila), int(servidor_ocupado)))

    assert saidas == clientes and not fila and not servidor_ocupado
    return Resultado(
        taxa_chegada=taxa_chegada,
        taxa_servico=taxa_servico,
        clientes=clientes,
        duracao=ultimo_tempo,
        utilizacao=area_ocupacao / ultimo_tempo,
        espera_media=soma_esperas / clientes,
        permanencia_media=soma_permanencias / clientes,
        fila_media=area_fila / ultimo_tempo,
        sistema_medio=area_sistema / ultimo_tempo,
        taxa_efetiva=clientes / ultimo_tempo,
        eventos=historico,
    )


def teoria_mm1(taxa_chegada: float, taxa_servico: float) -> dict[str, float] | None:
    """Valores de equilíbrio teóricos; exigem taxa_chegada < taxa_servico."""
    if taxa_chegada >= taxa_servico:
        return None
    rho = taxa_chegada / taxa_servico
    w = 1 / (taxa_servico - taxa_chegada)
    wq = rho / (taxa_servico - taxa_chegada)
    return {"rho": rho, "wq": wq, "w": w, "lq": taxa_chegada * wq, "l": taxa_chegada * w}


def imprimir_resultado(resultado: Resultado) -> None:
    r = resultado
    print(f"\nCENÁRIO: chegada={r.taxa_chegada:g}/min; serviço={r.taxa_servico:g}/min; clientes={r.clientes:,}")
    print(f"Tempo simulado: {r.duracao:.2f} min | taxa efetiva: {r.taxa_efetiva:.3f}/min")
    print(f"Utilização observada: {r.utilizacao:.3f} ({100*r.utilizacao:.1f}%)")
    print(f"Espera média na fila (Wq): {r.espera_media:.3f} min = {60*r.espera_media:.1f} s")
    print(f"Tempo médio total (W):   {r.permanencia_media:.3f} min = {60*r.permanencia_media:.1f} s")
    print(f"Clientes médios na fila (Lq): {r.fila_media:.3f}")
    print(f"Clientes médios no sistema (L): {r.sistema_medio:.3f}")
    print(f"Verificação de Little: Lq={r.fila_media:.3f} e λef·Wq={r.taxa_efetiva*r.espera_media:.3f}")
    teoria = teoria_mm1(r.taxa_chegada, r.taxa_servico)
    if teoria is None:
        print("ATENÇÃO: λ ≥ μ; não existe equilíbrio estacionário M/M/1.")
    else:
        print(f"Teoria M/M/1 (equilíbrio): ρ={teoria['rho']:.3f}; Wq={teoria['wq']:.3f} min; W={teoria['w']:.3f} min")
        print("Diferenças entre teoria e simulação são esperadas devido à amostra finita e ao início vazio.")


def salvar_csv(eventos: list[tuple[float, str, int, int, int]], arquivo: str) -> None:
    caminho = Path(arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        gravador = csv.writer(f, delimiter=";")
        gravador.writerow(["tempo_min", "evento", "cliente", "tamanho_fila", "servidor_ocupado"])
        for tempo, evento, cliente, fila, ocupado in eventos:
            gravador.writerow([f"{tempo:.6f}", evento, cliente, fila, ocupado])
    print(f"Arquivo CSV criado: {caminho.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Laboratório de simulação de eventos discretos M/M/1.")
    parser.add_argument("--taxa-chegada", type=float, default=4.0, help="λ: clientes por minuto (padrão: 4)")
    parser.add_argument("--taxa-servico", type=float, default=6.0, help="μ: clientes por minuto (padrão: 6)")
    parser.add_argument("--clientes", type=int, default=20000, help="número de clientes (padrão: 20000)")
    parser.add_argument("--semente", type=int, default=42, help="semente para reproduzir os sorteios")
    parser.add_argument("--comparar", action="store_true", help="comparar cenário normal (4/6) e sobrecarga (5,5/6)")
    parser.add_argument("--csv", type=str, default="", help="salvar agenda executada de eventos em CSV")
    parser.add_argument("--mostrar-eventos", type=int, default=0, help="exibir os primeiros N eventos")
    args = parser.parse_args()

    if args.comparar:
        resultados = [
            simular_fila_mm1(4.0, 6.0, args.clientes, args.semente),
            simular_fila_mm1(5.5, 6.0, args.clientes, args.semente),
        ]
        for r in resultados:
            imprimir_resultado(r)
        print("\nCONCLUSÃO: compare as esperas; quando λ se aproxima de μ, a fila cresce muito.")
    else:
        r = simular_fila_mm1(
            args.taxa_chegada, args.taxa_servico, args.clientes, args.semente,
            guardar_eventos=bool(args.csv or args.mostrar_eventos),
        )
        imprimir_resultado(r)
        if args.mostrar_eventos:
            print("\nPRIMEIROS EVENTOS: tempo(min) | tipo | cliente | fila | ocupado")
            for t, tipo, cliente, fila, ocupado in r.eventos[:args.mostrar_eventos]:
                print(f"{t:9.4f} | {tipo:7s} | {cliente:5d} | {fila:4d} | {ocupado}")
        if args.csv:
            salvar_csv(r.eventos, args.csv)


if __name__ == "__main__":
    main()
