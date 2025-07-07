import csv
import os
import heapq
import tempfile
from typing import List

def merge_sort(lista: List[list], indice_chave: int, crescente=True):
    """
    Algoritmo de merge sort em memória para ordenar listas de listas.
    (list[list], int, bool) -> list[list]
    """
    if len(lista) <= 1:
        return lista

    meio = len(lista) // 2
    esquerda = merge_sort(lista[:meio], indice_chave, crescente)
    direita = merge_sort(lista[meio:], indice_chave, crescente)

    return intercalar(esquerda, direita, indice_chave, crescente)

def intercalar(esq: List[list], dir: List[list], indice: int, crescente=True):
    """
    Função auxiliar para intercalar duas listas ordenadas.
    (list, list, int, bool) -> list
    """
    resultado = []
    i = j = 0

    while i < len(esq) and j < len(dir):
        cond = esq[i][indice] <= dir[j][indice] if crescente else esq[i][indice] >= dir[j][indice]
        if cond:
            resultado.append(esq[i])
            i += 1
        else:
            resultado.append(dir[j])
            j += 1

    resultado.extend(esq[i:])
    resultado.extend(dir[j:])
    return resultado

def criar_runs_ordenados(arquivo_csv, coluna_chave, crescente=True, buffer_max_linhas=10000):
    """
    Divide o CSV em runs (partes) ordenadas e salva em arquivos temporários.
    (str, str, bool, int) -> list[str]
    """
    arquivos_runs = []
    with open(arquivo_csv, newline='', encoding='utf-8') as f:
        leitor = csv.reader(f)
        cabecalho = next(leitor)
        indice_chave = cabecalho.index(coluna_chave)

        buffer = []
        for linha in leitor:
            buffer.append(linha)
            if len(buffer) >= buffer_max_linhas:
                buffer_ordenado = merge_sort(buffer, indice_chave, crescente)
                temp = salvar_run_temporario(buffer_ordenado)
                arquivos_runs.append(temp)
                buffer = []

        if buffer:
            buffer_ordenado = merge_sort(buffer, indice_chave, crescente)
            temp = salvar_run_temporario(buffer_ordenado)
            arquivos_runs.append(temp)

    return arquivos_runs, cabecalho, indice_chave

def salvar_run_temporario(linhas: List[list]) -> str:
    """
    Salva um run ordenado em arquivo temporário.
    (list) -> str
    """
    temp = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='', encoding='utf-8', suffix=".csv")
    escritor = csv.writer(temp)
    for linha in linhas:
        escritor.writerow(linha)
    temp.close()
    return temp.name

def merge_externo(arquivos_runs: List[str], cabecalho: List[str], indice_chave: int, crescente=True, nome_saida="saida_ordenada.csv"):
    """
    Realiza o merge externo de todos os runs e salva resultado no arquivo final.
    (list, list, int, bool, str) -> None
    """
    arquivos = [open(nome, newline='', encoding='utf-8') for nome in arquivos_runs]
    leitores = [csv.reader(f) for f in arquivos]

    heap = []
    for i, leitor in enumerate(leitores):
        try:
            linha = next(leitor)
            chave = linha[indice_chave]
            if not crescente:
                chave = inverter_chave(chave)
            heapq.heappush(heap, (chave, i, linha))
        except StopIteration:
            pass

    with open(nome_saida, 'w', newline='', encoding='utf-8') as saida:
        escritor = csv.writer(saida)
        escritor.writerow(cabecalho)

        while heap:
            _, origem, menor_linha = heapq.heappop(heap)
            escritor.writerow(menor_linha)
            try:
                nova = next(leitores[origem])
                chave = nova[indice_chave]
                if not crescente:
                    chave = inverter_chave(chave)
                heapq.heappush(heap, (chave, origem, nova))
            except StopIteration:
                pass

    for f in arquivos:
        f.close()
    for nome in arquivos_runs:
        os.remove(nome)

def inverter_chave(chave):
    """
    Inverte valor para ordenação decrescente no heap.
    """
    try:
        return -float(chave)
    except ValueError:
        return ''.join(chr(255 - ord(c)) for c in chave)

def ordenacao_externa(csv_entrada: str, coluna_chave: str, ordem_crescente: bool, arquivo_saida: str):
    """
    Função principal que organiza a execução da ordenação externa.
    (str, str, bool, str) -> None
    """
    print("Criando runs ordenados...")
    runs, cabecalho, indice_chave = criar_runs_ordenados(csv_entrada, coluna_chave, ordem_crescente)
    print(f"{len(runs)} runs criados.")
    print("Fazendo merge externo...")
    merge_externo(runs, cabecalho, indice_chave, ordem_crescente, arquivo_saida)
    print(f"Ordenação completa! Arquivo gerado: {arquivo_saida}")

# Exemplo de uso:
# Um CSV chamado "grande.csv" com uma coluna "cpf"
if _name_ == "_main_":
    ordenacao_externa(
        csv_entrada="grande.csv",
        coluna_chave="cpf",
        ordem_crescente=True,
        arquivo_saida="saida_ordenada.csv"
    )