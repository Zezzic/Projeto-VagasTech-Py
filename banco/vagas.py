import re
from collections import Counter
from bson import ObjectId
from bson.errors import InvalidId
from banco.conexao import colecao

NIVEIS = ["estágio", "júnior", "pleno", "sênior", "não informado"]
FAIXAS = ["até 60 mil", "60 a 100 mil", "100 a 140 mil", "acima de 140 mil"]
CAMPOS_ORDEM = {
    "data": "data_publicacao",
    "empresa": "empresa",
    "titulo": "titulo",
    "salario": "salario_max",
}


def criar_indice():
    colecao.create_index("url", unique=True)


def salvar_vaga(vaga):
    if colecao.find_one({"url": vaga["url"]}):
        return False
    colecao.insert_one(vaga)
    return True


def converter(vaga):
    vaga["_id"] = str(vaga["_id"])
    return vaga


def montar_filtro(categoria, tecnologia, fonte, busca, nivel, aceita_brasil):
    filtro = {}
    if categoria:
        filtro["categoria"] = categoria
    if tecnologia:
        filtro["tecnologias"] = tecnologia.lower()
    if fonte:
        filtro["fonte"] = fonte
    if nivel:
        filtro["nivel"] = nivel
    if aceita_brasil:
        filtro["aceita_brasil"] = True
    if busca:
        texto = {"$regex": re.escape(busca), "$options": "i"}
        filtro["$or"] = [{"titulo": texto}, {"empresa": texto}]
    return filtro


def montar_ordem(ordenar_por, direcao):
    campo = CAMPOS_ORDEM.get(ordenar_por, "data_publicacao")
    sentido = 1 if direcao == "asc" else -1
    return [(campo, sentido), ("coletado_em", -1)]


def contar_vagas(filtro):
    return colecao.count_documents(filtro)


def listar_vagas(filtro, pagina, limite, ordem):
    pular = (pagina - 1) * limite
    cursor = colecao.find(filtro).sort(ordem).skip(pular).limit(limite)
    return [converter(vaga) for vaga in cursor]


def listar_todas(filtro, ordem):
    return list(colecao.find(filtro).sort(ordem))


def buscar_vaga(id_vaga):
    try:
        objeto_id = ObjectId(id_vaga)
    except InvalidId:
        return None
    vaga = colecao.find_one({"_id": objeto_id})
    if vaga is None:
        return None
    return converter(vaga)


def opcoes_filtros():
    niveis_existentes = colecao.distinct("nivel")
    return {
        "categorias": sorted(colecao.distinct("categoria")),
        "tecnologias": sorted(colecao.distinct("tecnologias")),
        "fontes": sorted(colecao.distinct("fonte")),
        "niveis": [nivel for nivel in NIVEIS if nivel in niveis_existentes],
    }


def faixa_salarial(valor):
    if valor < 60000:
        return FAIXAS[0]
    if valor < 100000:
        return FAIXAS[1]
    if valor < 140000:
        return FAIXAS[2]
    return FAIXAS[3]


def estatisticas(filtro):
    campos = {
        "categoria": 1, "fonte": 1, "tecnologias": 1, "data_publicacao": 1,
        "nivel": 1, "aceita_brasil": 1, "salario_min": 1, "salario_max": 1,
    }
    todas = list(colecao.find(filtro, campos))

    categorias = Counter()
    fontes = Counter()
    tecnologias = Counter()
    niveis = Counter()
    faixas = Counter()
    dias = Counter()
    salarios = []
    aceitam_brasil = 0

    for vaga in todas:
        categorias[vaga.get("categoria", "não informada")] += 1
        fontes[vaga.get("fonte", "não informada")] += 1
        niveis[vaga.get("nivel", "não informado")] += 1
        tecnologias.update(vaga.get("tecnologias", []))
        if vaga.get("data_publicacao"):
            dias[vaga["data_publicacao"]] += 1
        if vaga.get("aceita_brasil"):
            aceitam_brasil += 1
        if vaga.get("salario_min") and vaga.get("salario_max"):
            medio = (vaga["salario_min"] + vaga["salario_max"]) / 2
            salarios.append(medio)
            faixas[faixa_salarial(medio)] += 1

    por_categoria = dict(categorias.most_common())
    por_fonte = dict(fontes.most_common())
    por_tecnologia = dict(tecnologias.most_common(10))
    por_nivel = {nivel: niveis[nivel] for nivel in NIVEIS if nivel in niveis}
    por_faixa = {faixa: faixas[faixa] for faixa in FAIXAS if faixa in faixas}
    por_dia = dict(sorted(dias.items())[-30:])

    ultima = colecao.find_one(filtro, sort=[("coletado_em", -1)])

    return {
        "total": len(todas),
        "tecnologia_mais_pedida": list(por_tecnologia)[0] if por_tecnologia else None,
        "categoria_com_mais_vagas": list(por_categoria)[0] if por_categoria else None,
        "aceitam_brasil": aceitam_brasil,
        "salario_medio": int(sum(salarios) / len(salarios)) if salarios else None,
        "vagas_com_salario": len(salarios),
        "ultima_coleta": ultima["coletado_em"] if ultima else None,
        "por_categoria": por_categoria,
        "por_fonte": por_fonte,
        "por_tecnologia": por_tecnologia,
        "por_nivel": por_nivel,
        "por_faixa_salarial": por_faixa,
        "por_dia": por_dia,
    }
