import os
from pypdf import PdfReader, PdfWriter

def deletar_paginas(caminho_entrada, caminho_saida, paginas_para_deletar):
    """
    Remove páginas específicas de um PDF.
    paginas_para_deletar: Lista de números inteiros (ex: [5] ou [5, 10, 12])
    Nota: Usa numeração humana (começa em 1).
    """
    
    if not os.path.exists(caminho_entrada):
        print(f"Erro: Arquivo '{caminho_entrada}' não encontrado.")
        return

    print(f"Lendo arquivo: {caminho_entrada}")
    leitor = PdfReader(caminho_entrada)
    escritor = PdfWriter()
    
    total_paginas = len(leitor.pages)
    
    # Validação básica para não tentar deletar página que não existe
    for p in paginas_para_deletar:
        if p < 1 or p > total_paginas:
            print(f"ERRO: A página {p} não existe! O documento tem apenas {total_paginas} páginas.")
            return

    # Convertendo para conjunto para busca rápida
    # E ajustando índice (Humano diz página 1, Python entende índice 0)
    indices_para_remover = {p - 1 for p in paginas_para_deletar}

    paginas_mantidas = 0
    
    print("Processando...")
    for i in range(total_paginas):
        # Se o índice atual NÃO estiver na lista de remoção, adiciona no novo PDF
        if i not in indices_para_remover:
            escritor.add_page(leitor.pages[i])
            paginas_mantidas += 1
        else:
            print(f" - Deletando a página {i + 1}...")

    # Salva o arquivo final
    with open(caminho_saida, "wb") as f:
        escritor.write(f)

    print("-" * 30)
    print(f"Sucesso! PDF salvo em: {caminho_saida}")
    print(f"Original tinha {total_paginas} páginas. Novo tem {paginas_mantidas} páginas.")

# --- CONFIGURAÇÃO E EXECUÇÃO ---
if __name__ == "__main__":
    arquivo_origem = "ordenado_final_manha.pdf"
    arquivo_destino = "bruto.pdf"
    
    paginas_alvo = [228, 230, 232] 

    deletar_paginas(arquivo_origem, arquivo_destino, paginas_alvo)