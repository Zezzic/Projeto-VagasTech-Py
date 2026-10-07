import json
import sys
from datetime import datetime
from banco.conexao import colecao
from banco.vagas import criar_indice, salvar_vaga

ARQUIVO = "backup_vagas.json"


def exportar():
    vagas = []
    for vaga in colecao.find({}, {"_id": 0}):
        vaga["coletado_em"] = vaga["coletado_em"].isoformat()
        vagas.append(vaga)
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(vagas, arquivo, ensure_ascii=False, indent=2)
    print(len(vagas), "vagas salvas em", ARQUIVO)


def importar():
    criar_indice()
    with open(ARQUIVO, encoding="utf-8") as arquivo:
        vagas = json.load(arquivo)
    novas = 0
    for vaga in vagas:
        vaga["coletado_em"] = datetime.fromisoformat(vaga["coletado_em"])
        if salvar_vaga(vaga):
            novas += 1
    print(novas, "vagas importadas de", ARQUIVO)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "exportar":
        exportar()
    elif len(sys.argv) > 1 and sys.argv[1] == "importar":
        importar()
    else:
        print("Use: python -m banco.backup exportar   ou   python -m banco.backup importar")
