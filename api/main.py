import csv
import io
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from banco import vagas

app = FastAPI(title="API de vagas remotas de tecnologia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/vagas")
def listar(
    categoria: str = None,
    tecnologia: str = None,
    fonte: str = None,
    busca: str = None,
    nivel: str = None,
    aceita_brasil: bool = False,
    ordenar_por: str = "data",
    direcao: str = "desc",
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
):
    filtro = vagas.montar_filtro(categoria, tecnologia, fonte, busca, nivel, aceita_brasil)
    ordem = vagas.montar_ordem(ordenar_por, direcao)
    total = vagas.contar_vagas(filtro)
    lista = vagas.listar_vagas(filtro, pagina, limite, ordem)
    return {"total": total, "pagina": pagina, "limite": limite, "vagas": lista}


@app.get("/vagas/{id_vaga}")
def consultar(id_vaga: str):
    vaga = vagas.buscar_vaga(id_vaga)
    if vaga is None:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga


@app.get("/estatisticas")
def estatisticas(
    categoria: str = None,
    tecnologia: str = None,
    fonte: str = None,
    busca: str = None,
    nivel: str = None,
    aceita_brasil: bool = False,
):
    filtro = vagas.montar_filtro(categoria, tecnologia, fonte, busca, nivel, aceita_brasil)
    return vagas.estatisticas(filtro)


@app.get("/filtros")
def filtros():
    return vagas.opcoes_filtros()


@app.get("/exportar/csv")
def exportar_csv(
    categoria: str = None,
    tecnologia: str = None,
    fonte: str = None,
    busca: str = None,
    nivel: str = None,
    aceita_brasil: bool = False,
    ordenar_por: str = "data",
    direcao: str = "desc",
):
    filtro = vagas.montar_filtro(categoria, tecnologia, fonte, busca, nivel, aceita_brasil)
    ordem = vagas.montar_ordem(ordenar_por, direcao)
    lista = vagas.listar_todas(filtro, ordem)

    saida = io.StringIO()
    escritor = csv.writer(saida)
    escritor.writerow([
        "titulo", "empresa", "categoria", "nivel", "tecnologias", "tipo_contrato",
        "localizacao", "aceita_brasil", "salario_min", "salario_max",
        "data_publicacao", "fonte", "url", "coletado_em",
    ])
    for vaga in lista:
        escritor.writerow([
            vaga["titulo"], vaga["empresa"], vaga["categoria"], vaga["nivel"],
            "; ".join(vaga["tecnologias"]), vaga["tipo_contrato"],
            vaga["localizacao"], "sim" if vaga["aceita_brasil"] else "não",
            vaga["salario_min"] or "", vaga["salario_max"] or "",
            vaga["data_publicacao"], vaga["fonte"], vaga["url"], vaga["coletado_em"],
        ])

    conteudo = "\ufeff" + saida.getvalue()
    return Response(
        content=conteudo,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=vagas.csv"},
    )


pasta_dashboard = os.path.join(os.path.dirname(__file__), "..", "dashboard")
app.mount("/dashboard", StaticFiles(directory=pasta_dashboard, html=True), name="dashboard")
