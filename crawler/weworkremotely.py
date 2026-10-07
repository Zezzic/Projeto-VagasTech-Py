import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import requests
from crawler.tratamento import limpar_html, montar_vaga, padronizar_categoria

HEADERS = {"User-Agent": "Mozilla/5.0 (projeto academico)"}
FEEDS = [
    ("https://weworkremotely.com/remote-jobs.rss", ""),
    ("https://weworkremotely.com/categories/remote-programming-jobs.rss", "Programming"),
    ("https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss", "DevOps and Sysadmin"),
]


def pegar_texto(item, nome):
    elemento = item.find(nome)
    if elemento is None or elemento.text is None:
        return ""
    return elemento.text.strip()


def converter_data(texto):
    try:
        return parsedate_to_datetime(texto).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return ""


def separar_titulo(titulo):
    if ": " in titulo:
        empresa, cargo = titulo.split(": ", 1)
        return empresa, cargo
    return "", titulo


def coletar():
    vagas = []
    urls_vistas = []

    for endereco, categoria_padrao in FEEDS:
        try:
            resposta = requests.get(endereco, headers=HEADERS, timeout=30)
            resposta.raise_for_status()
            raiz = ET.fromstring(resposta.content)
        except (requests.RequestException, ET.ParseError):
            print("We Work Remotely: não foi possível ler", endereco)
            continue

        for item in raiz.iter("item"):
            url = pegar_texto(item, "link") or pegar_texto(item, "guid")
            titulo_completo = pegar_texto(item, "title")
            categoria = padronizar_categoria(pegar_texto(item, "category") or categoria_padrao)

            if not url or not titulo_completo or url in urls_vistas or categoria is None:
                continue

            urls_vistas.append(url)
            empresa, cargo = separar_titulo(titulo_completo)

            vaga = montar_vaga(
                titulo=cargo,
                empresa=empresa,
                categoria=categoria,
                tipo_contrato=pegar_texto(item, "type"),
                localizacao=pegar_texto(item, "region"),
                data_publicacao=converter_data(pegar_texto(item, "pubDate")),
                url=url,
                fonte="We Work Remotely",
                descricao=limpar_html(pegar_texto(item, "description")),
                tags=[],
                salario_min=None,
                salario_max=None,
            )
            vagas.append(vaga)

    print("We Work Remotely:", len(vagas), "vagas de tecnologia encontradas")
    return vagas
