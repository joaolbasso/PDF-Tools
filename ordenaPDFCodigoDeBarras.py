import os
from collections import defaultdict # <--- Mudança aqui para agrupar páginas
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_path, pdfinfo_from_path
from pyzbar.pyzbar import decode, ZBarSymbol

# --- CONFIGURAÇÃO ---
POPPLER_PATH = r"C:/Release-25.12.0-0/poppler-25.12.0/Library/bin"

# Configurações de Leitura
DPI_LEITURA = 150  
ALTURA_CORTE_CM = 7.0 

def gerar_relatorio_auditoria(lista_paginas, caminho_log):
    """
    Gera relatório detalhado com posições originais das ocorrências.
    """
    print(f"Gerando relatório de auditoria em: {caminho_log}")
    
    # Dicionário para mapear: Turma -> Lista de Páginas Originais
    # Ex: { 5: [10, 45], 12: [3] }
    mapa_ocorrencias = defaultdict(list)
    paginas_erro = []
    
    # 1. Processar dados
    for item in lista_paginas:
        turma = item['turma']
        pag_original = item['index_pdf'] + 1 # +1 para ficar legível para humanos
        
        if turma.isdigit():
            turma_num = int(turma)
            mapa_ocorrencias[turma_num].append(pag_original)
        else:
            paginas_erro.append(item)

    with open(caminho_log, "w", encoding="utf-8") as f:
        f.write("=== RELATÓRIO DE PROCESSAMENTO E AUDITORIA ===\n\n")
        
        turmas_encontradas = sorted(mapa_ocorrencias.keys())
        
        if turmas_encontradas:
            min_turma = turmas_encontradas[0]
            max_turma = turmas_encontradas[-1]
            total_docs = sum(len(pags) for pags in mapa_ocorrencias.values())
            
            # --- 1. Resumo ---
            f.write(f"1. INTERVALO IDENTIFICADO:\n")
            f.write(f" - Menor Turma: {min_turma:04d}\n")
            f.write(f" - Maior Turma: {max_turma:04d}\n")
            f.write(f" - Total de páginas válidas processadas: {total_docs}\n")
            
            # --- 2. Gaps (Faltantes) ---
            f.write(f"\n2. AUDITORIA DE SEQUÊNCIA (FALTANTES):\n")
            
            set_encontrados = set(turmas_encontradas)
            set_esperados = set(range(min_turma, max_turma + 1))
            faltantes = sorted(list(set_esperados - set_encontrados))
            
            if faltantes:
                f.write(f" [ALERTA] Faltam {len(faltantes)} turmas neste intervalo:\n")
                f.write(", ".join([f"{num:04d}" for num in faltantes]))
                f.write("\n")
            else:
                f.write(" [SUCESSO] Sequência completa (sem buracos).\n")

            # --- 3. Duplicidades com Posição Original (NOVO) ---
            f.write(f"\n3. ANÁLISE DE DUPLICIDADES:\n")
            
            # Filtra turmas que têm mais de 1 página na lista
            duplicados = {t: pags for t, pags in mapa_ocorrencias.items() if len(pags) > 1}
            
            if duplicados:
                f.write(f" [ATENÇÃO] Foram encontradas {len(duplicados)} turmas repetidas:\n")
                for t in sorted(duplicados.keys()):
                    pags = duplicados[t]
                    f.write(f"  - Turma {t:04d}: Aparece {len(pags)} vezes nas páginas originais {pags}\n")
            else:
                f.write(" [SUCESSO] Nenhuma duplicidade encontrada.\n")

        else:
            f.write("[CRÍTICO] Nenhum código de barras válido lido.\n")

        # --- 4. Erros ---
        f.write("\n--------------------------------------------------\n")
        f.write("4. PÁGINAS NÃO LIDAS / ERROS:\n")
        if paginas_erro:
            f.write(f" Total de páginas com erro: {len(paginas_erro)}\n")
            for erro in paginas_erro:
                f.write(f" - Página original {erro['index_pdf'] + 1}: {erro['turma']}\n")
        else:
            f.write(" Nenhuma página com erro de leitura.\n")
            
    print("Relatório gerado com sucesso.")


def ordenar_pdf_otimizado(caminho_pdf_entrada, caminho_pdf_saida):
    if not os.path.exists(caminho_pdf_entrada):
        print(f"Erro: Arquivo {caminho_pdf_entrada} não encontrado.")
        return

    print(f"Iniciando processamento: {caminho_pdf_entrada}")

    try:
        info = pdfinfo_from_path(caminho_pdf_entrada, poppler_path=POPPLER_PATH)
        total_paginas = info["Pages"]
        print(f"Total de páginas: {total_paginas}")
    except Exception as e:
         print(f"Erro no Poppler: {e}")
         return

    leitor_pdf_origem = PdfReader(caminho_pdf_entrada)
    lista_paginas = [] 

    pixels_altura_corte = int((ALTURA_CORTE_CM / 2.54) * DPI_LEITURA)

    for i in range(total_paginas):
        num_pag = i + 1
        print(f"Processando página {num_pag}/{total_paginas}...", end="\r")
        
        try:
            imagens = convert_from_path(
                caminho_pdf_entrada, 
                first_page=num_pag, 
                last_page=num_pag, 
                dpi=DPI_LEITURA,
                poppler_path=POPPLER_PATH
            )
            
            imagem_inteira = imagens[0]
            largura_img, altura_img = imagem_inteira.size

            if altura_img > pixels_altura_corte:
                box = (0, 0, largura_img, pixels_altura_corte)
                imagem_para_ler = imagem_inteira.crop(box)
                imagem_inteira.close() 
            else:
                imagem_para_ler = imagem_inteira

            codigos = decode(imagem_para_ler, symbols=[ZBarSymbol.CODE128, ZBarSymbol.CODE39, ZBarSymbol.EAN13])
            
            codigo_turma = "ZZZZ_ERRO_LEITURA" 
            
            if codigos:
                codigo_turma = codigos[0].data.decode('utf-8')
            
            imagem_para_ler.close()

            lista_paginas.append({
                "turma": codigo_turma,
                "index_pdf": i
            })
            
        except Exception as e:
            print(f"\nErro fatal na página {num_pag}: {e}")
            lista_paginas.append({"turma": "ZZZZ_ERRO_FATAL", "index_pdf": i})

    print(f"\nOrdenando e salvando...")
    lista_paginas.sort(key=lambda x: (x["turma"], x["index_pdf"]))

    # Gera relatório log atualizado
    nome_log = caminho_pdf_saida.replace(".pdf", "_relatorio.txt")
    gerar_relatorio_auditoria(lista_paginas, nome_log)

    escritor_pdf = PdfWriter()
    for item in lista_paginas:
        pagina_obj = leitor_pdf_origem.pages[item["index_pdf"]]
        escritor_pdf.add_page(pagina_obj)

    with open(caminho_pdf_saida, "wb") as f:
        escritor_pdf.write(f)

    print(f"Concluído! Arquivo: {caminho_pdf_saida}")
    print(f"Log de auditoria: {nome_log}")

if __name__ == "__main__":
    entrada = "bruto.pdf" 
    saida = "ordenado_final.pdf"
    ordenar_pdf_otimizado(entrada, saida)