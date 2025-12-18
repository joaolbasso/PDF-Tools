from pypdf import PdfWriter

def juntar_pdfs(lista_arquivos, nome_saida):
    print("Iniciando a junção dos arquivos...")
    
    # Cria o objeto que vai "escrever" o novo PDF
    escritor = PdfWriter()

    for pdf in lista_arquivos:
        print(f"Adicionando: {pdf}")
        try:
            # append adiciona todas as páginas do arquivo ao final
            escritor.append(pdf)
        except FileNotFoundError:
            print(f"ERRO: O arquivo '{pdf}' não foi encontrado na pasta.")
            return

    # Salva o resultado final
    with open(nome_saida, "wb") as f_saida:
        escritor.write(f_saida)
    
    print(f"Sucesso! Arquivo completo salvo como: {nome_saida}")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # Liste aqui os arquivos que você quer juntar, na ordem que quiser
    # Exemplo: O bolão principal + a página que você escaneou agora
    arquivos_para_juntar = [
        "ordenado_final_tarde.pdf",           # Seu arquivo original grande
        "3 tarde.pdf"  # A página única que você escaneou agora
    ]
    
    arquivo_final = "bruto_completo.pdf"
    
    juntar_pdfs(arquivos_para_juntar, arquivo_final)