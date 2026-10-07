import requests
from crawler.tratamento import extrair_salario, limpar_html, montar_vaga, padronizar_categoria

URL = "https://remotive.com/api/remote-jobs"
HEADERS = {"User-Agent": "Mozilla/5.0 (projeto academico)"}


def coletar():
    try:
        resposta = requests.get(URL, headers=HEADERS, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError):
        print("Remotive: não foi possível coletar as vagas")
        return []

    vagas = []
    for item in dados.get("jobs", []):
        titulo = item.get("title")
        url = item.get("url")
        categoria = padronizar_categoria(item.get("category"))
        if not titulo or not url or categoria is None:
            continue

        salario_min, salario_max = extrair_salario(item.get("salary"))

        vaga = montar_vaga(
            titulo=titulo,
            empresa=item.get("company_name"),
            categoria=categoria,
            tipo_contrato=item.get("job_type"),
            localizacao=item.get("candidate_required_location"),
            data_publicacao=(item.get("publication_date") or "")[:10],
            url=url,
            fonte="Remotive",
            descricao=limpar_html(item.get("description")),
            tags=item.get("tags") or [],
            salario_min=salario_min,
            salario_max=salario_max,
        )
        vagas.append(vaga)

    print("Remotive:", len(vagas), "vagas de tecnologia encontradas")
    return vagas
