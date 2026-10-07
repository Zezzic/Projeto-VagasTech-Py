import html
import re
from datetime import datetime

TECNOLOGIAS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node", "django", "flask", "fastapi", "php", "laravel", "ruby", "rails",
    "golang", "rust", "kotlin", "swift", "flutter", "sql", "mongodb",
    "postgresql", "mysql", "redis", "graphql", "aws", "azure", "docker",
    "kubernetes", "terraform", "linux", "git", "html", "css",
]

GRUPOS_CATEGORIA = [
    ("DevOps e infraestrutura", ["devops", "sysadmin", "sre", "site reliability"]),
    ("Dados", ["data", "machine learning", "analytics"]),
    ("QA e testes", ["qa", "quality assurance", "testing", "test"]),
    ("Desenvolvimento", [
        "software", "programming", "programmer", "developer", "development",
        "engineer", "architect", "backend", "back end", "back-end", "frontend",
        "front end", "front-end", "full stack", "full-stack", "fullstack",
        "mobile", "ios", "android", "dev",
    ]),
]

NIVEIS_PALAVRAS = [
    ("estágio", ["intern", "internship", "trainee", "estagio", "estágio"]),
    ("júnior", ["junior", "jr", "entry level", "entry-level", "júnior"]),
    ("sênior", ["senior", "sr", "lead", "principal", "staff", "sênior"]),
    ("pleno", ["mid", "mid-level", "mid level", "intermediate", "pleno"]),
]

PALAVRAS_BRASIL = [
    "worldwide", "anywhere", "global", "brazil", "brasil", "latam",
    "latin america", "south america", "americas",
]


def tem_palavra(texto, palavra):
    return re.search(r"\b" + re.escape(palavra) + r"\b", texto) is not None


def limpar_html(texto):
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = html.unescape(texto)
    return re.sub(r"\s+", " ", texto).strip()


def achar_tecnologias(texto):
    texto = texto.lower()
    achadas = []
    for tecnologia in TECNOLOGIAS:
        if tem_palavra(texto, tecnologia):
            achadas.append(tecnologia)
    return achadas


def padronizar_categoria(texto):
    texto = (texto or "").lower()
    for nome, palavras in GRUPOS_CATEGORIA:
        for palavra in palavras:
            if tem_palavra(texto, palavra):
                return nome
    return None


def achar_nivel(titulo):
    titulo = titulo.lower()
    for nivel, palavras in NIVEIS_PALAVRAS:
        for palavra in palavras:
            if tem_palavra(titulo, palavra):
                return nivel
    return "não informado"


def aceita_brasil(localizacao):
    localizacao = (localizacao or "").lower()
    for palavra in PALAVRAS_BRASIL:
        if tem_palavra(localizacao, palavra):
            return True
    return False


def padronizar_tipo(tipo):
    if not tipo:
        return "não informado"
    return tipo.replace("_", " ").replace("-", " ").strip().lower()


def converter_salario(valor):
    try:
        numero = int(float(valor))
    except (TypeError, ValueError):
        return None
    if numero <= 0:
        return None
    return numero


def extrair_salario(texto):
    if not texto:
        return None, None
    texto = texto.lower().replace("401k", "")
    if "$" not in texto and "usd" not in texto:
        return None, None
    for palavra in ["hour", "/hr", "month", "week", "day"]:
        if palavra in texto:
            return None, None

    valores = []
    for numero, mil in re.findall(r"(\d[\d,]*\.?\d*)(k?)", texto):
        try:
            valor = float(numero.replace(",", ""))
        except ValueError:
            continue
        if mil:
            valor = valor * 1000
        if 10000 <= valor <= 1000000:
            valores.append(int(valor))

    if not valores:
        return None, None
    return min(valores), max(valores)


def montar_vaga(titulo, empresa, categoria, tipo_contrato, localizacao,
                data_publicacao, url, fonte, descricao, tags,
                salario_min, salario_max):
    descricao = descricao or ""
    texto_tecnologias = titulo + " " + descricao + " " + " ".join(tags)
    if len(descricao) > 2000:
        descricao = descricao[:2000] + "..."
    localizacao = (localizacao or "").strip() or "não informada"

    return {
        "titulo": titulo.strip(),
        "empresa": (empresa or "").strip() or "não informada",
        "categoria": categoria,
        "nivel": achar_nivel(titulo),
        "tecnologias": achar_tecnologias(texto_tecnologias),
        "tipo_contrato": padronizar_tipo(tipo_contrato),
        "localizacao": localizacao,
        "aceita_brasil": aceita_brasil(localizacao),
        "salario_min": salario_min,
        "salario_max": salario_max,
        "descricao": descricao,
        "data_publicacao": data_publicacao,
        "url": url.strip(),
        "fonte": fonte,
        "coletado_em": datetime.now(),
    }
