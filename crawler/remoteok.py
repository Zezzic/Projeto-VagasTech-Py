import requests
from crawler.tratamento import converter_salario, limpar_html, montar_vaga, padronizar_categoria

URL = "https://remoteok.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (projeto academico)"}


def coletar():
    try:
        resposta = requests.get(URL, headers=HEADERS, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError):
        print("Remote OK: não foi possível coletar as vagas")
        return []

    vagas = []
    for item in dados:
        if not isinstance(item, dict):
            continue
        titulo = item.get("position")
        url = item.get("url")
        if not titulo or not url:
            continue

        categoria = padronizar_categoria(titulo)
        if categoria is None:
            continue

        if url.startswith("/"):
            url = "https://remoteok.com" + url

        salario_min = converter_salario(item.get("salary_min"))
        salario_max = converter_salario(item.get("salary_max"))
        if salario_min is None:
            salario_min = salario_max
        if salario_max is None:
            salario_max = salario_min

        vaga = montar_vaga(
            titulo=titulo,
            empresa=item.get("company"),
            categoria=categoria,
            tipo_contrato=None,
            localizacao=item.get("location"),
            data_publicacao=(item.get("date") or "")[:10],
            url=url,
            fonte="Remote OK",
            descricao=limpar_html(item.get("description")),
            tags=item.get("tags") or [],
            salario_min=salario_min,
            salario_max=salario_max,
        )
        vagas.append(vaga)

    print("Remote OK:", len(vagas), "vagas de tecnologia encontradas")
    return vagas
