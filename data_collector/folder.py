import os
import json

def dwg_por_pasta(diretorio_base, arquivo_saida="dwg_por_pasta.json"):
    pastas_com_dwg = {}
    pastas_sem_dwg = []
    
    print(f"🔍 Iniciando varredura em: {diretorio_base}\n")
    
    for raiz, dirs, arquivos in os.walk(diretorio_base):
        # Lista somente arquivos .dwg
        dwg_arquivos = [arquivo for arquivo in arquivos if arquivo.lower().endswith(".dwg")]
        
        if dwg_arquivos:
            print(f"📂 {raiz} - Contém {len(dwg_arquivos)} arquivo(s) .dwg")
            print(f"   Arquivos: {dwg_arquivos}\n")
            pastas_com_dwg[raiz] = dwg_arquivos
        else:
            print(f"📂 {raiz} - ❌ NÃO contém arquivos .dwg\n")
            pastas_sem_dwg.append(raiz)
    
    # Cria o JSON final
    resultado_json = {
        "pastas_sem_dwg": pastas_sem_dwg,
        "pastas_com_dwg": pastas_com_dwg
    }
    
    # Salva em arquivo JSON
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(resultado_json, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Varredura finalizada. Arquivo JSON gerado: {arquivo_saida}\n")
    return resultado_json


base = r"G:\Meu Drive\server\PROJETOS\COPA ENERGIA\CPL"  # caminho da pasta principal
resultado = dwg_por_pasta(base)

# Exibe resumo
print("📋 Pastas que NÃO têm arquivos .dwg:")
for pasta in resultado["pastas_sem_dwg"]:
    print(" -", pasta)

print("\n📋 Pastas que têm arquivos .dwg:")
for pasta, arquivos in resultado["pastas_com_dwg"].items():
    print(f"{pasta}: {arquivos}")

