# Vagas remotas de tecnologia: crawler, API e dashboard

Fluxo do projeto: **Sites → Web Crawler → MongoDB → FastAPI → Dashboard**

## Sites escolhidos e dados coletados

| Site | Como é coletado | Observação |
|------|-----------------|------------|
| Remotive (remotive.com) | API pública em JSON (`/api/remote-jobs`) | Pede no máximo 4 consultas por dia, atribuição à fonte e link para a vaga |
| We Work Remotely (weworkremotely.com) | Feeds RSS públicos (geral, programação e DevOps) | Pede atribuição com link para a vaga original |
| Remote OK (remoteok.com) | API pública em JSON (`/api/`) | Pede crédito a "Remote OK" e link de volta. O logotipo do site não é usado |

Só vagas de tecnologia são salvas (desenvolvimento, dados, DevOps e QA). Não são coletados dados pessoais, apenas informações públicas do anúncio. O dashboard mostra a fonte de cada vaga e o link para o anúncio original.

## Estrutura de pastas

```
projeto/
  crawler/      coleta e tratamento dos dados (um arquivo por site)
  banco/        conexão, consultas e backup do MongoDB
  api/          API FastAPI
  dashboard/    páginas web (HTML, CSS e JS)
  requirements.txt
```

## Instalação

1. Instale o Python 3.10 ou mais novo e o MongoDB (ou rode com Docker: `docker run -d -p 27017:27017 --name mongo mongo`).
2. Na pasta do projeto:

```
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

No Linux ou Mac, ative com `source venv/bin/activate`.

O MongoDB deve estar em `mongodb://localhost:27017`. O banco usado é `vagas_remotas` e a coleção é `vagas` (configurados em `banco/conexao.py`).

## Como executar

Rode sempre a partir da pasta `projeto`.

1. Crawler (independente da API):

```
python -m crawler.main
```

Pode ser executado várias vezes. Vagas já salvas são ignoradas e nada é apagado. Cada execução faz uma consulta ao Remotive, que pede no máximo 4 por dia.

2. API:

```
python -m uvicorn api.main:app --reload
```

3. Dashboard: abra http://localhost:8000/dashboard/ no navegador.

A documentação automática da API fica em http://localhost:8000/docs.

## Dashboard

- Seis indicadores: total de vagas, tecnologia mais pedida, categoria com mais vagas, vagas que aceitam candidatos do Brasil, salário médio informado e data da última coleta.
- Cinco gráficos: tecnologias mais pedidas, vagas por categoria, vagas por nível, faixa salarial e vagas publicadas por dia.
- Indicadores e gráficos acompanham os filtros.
- Filtros: busca por cargo ou empresa, categoria, nível, tecnologia, fonte e "aceita candidatos do Brasil".
- Tabela com paginação e ordenação (clique em Cargo, Empresa, Salário ou Publicada em).
- Botão "Exportar CSV" com as vagas do filtro atual.
- Clique no cargo para abrir a página de detalhe da vaga (`vaga.html`).

## Estrutura do banco de dados

Banco `vagas_remotas`, coleção `vagas`. Cada documento é uma vaga:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `_id` | ObjectId | Identificador gerado pelo MongoDB |
| `titulo` | string | Cargo da vaga |
| `empresa` | string | Nome da empresa |
| `categoria` | string | Desenvolvimento, Dados, DevOps e infraestrutura ou QA e testes |
| `nivel` | string | estágio, júnior, pleno, sênior ou não informado (descoberto pelo título) |
| `tecnologias` | lista de strings | Tecnologias encontradas no título, nas tags e na descrição |
| `tipo_contrato` | string | Ex.: full time, contract |
| `localizacao` | string | Região em que o candidato pode morar |
| `aceita_brasil` | booleano | Verdadeiro se a localização diz worldwide, anywhere, Brazil, LATAM e similares |
| `salario_min` | inteiro ou nulo | Salário mínimo em dólares por ano, quando informado |
| `salario_max` | inteiro ou nulo | Salário máximo em dólares por ano, quando informado |
| `descricao` | string | Descrição limpa, com no máximo 2000 caracteres |
| `data_publicacao` | string | Data de publicação no formato AAAA-MM-DD |
| `url` | string | Link da vaga no site de origem |
| `fonte` | string | Remotive, We Work Remotely ou Remote OK |
| `coletado_em` | data e hora | Quando o crawler coletou a vaga |

O campo `url` tem índice único, e é assim que registros duplicados são evitados.

## Tratamento dos dados

- Remoção de HTML da descrição.
- Categorias dos três sites unificadas em quatro grupos. Vagas que não são de tecnologia são descartadas.
- Padronização do tipo de contrato (minúsculas, sem `_` e `-`).
- Valores vazios viram "não informada" ou "não informado".
- Extração das tecnologias a partir de uma lista de palavras-chave (`crawler/tratamento.py`).
- Nível da vaga pelo título e `aceita_brasil` pela localização. Os dois são estimativas por palavras-chave, e podem errar em títulos ou localizações incomuns.
- Salário: o Remote OK informa números. No Remotive o texto é lido, e só valores em dólares por ano são aceitos (valores por hora, mês ou semana e outras moedas são ignorados). Cerca de 96% das vagas do Remote OK não informam salário, então as estatísticas de salário usam poucas vagas.
- Datas convertidas para AAAA-MM-DD.

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/vagas` | Lista as vagas com paginação, filtros e ordenação |
| GET | `/vagas/{id_vaga}` | Retorna uma vaga pelo `_id` (404 se não existir) |
| GET | `/estatisticas` | Estatísticas e dados dos gráficos (aceita os mesmos filtros) |
| GET | `/filtros` | Opções disponíveis para os filtros do dashboard |
| GET | `/exportar/csv` | Baixa as vagas filtradas em CSV |

Filtros (valem para `/vagas`, `/estatisticas` e `/exportar/csv`): `busca` (cargo ou empresa), `categoria`, `nivel`, `tecnologia`, `fonte` e `aceita_brasil` (true ou false).

Outros parâmetros de `/vagas` e `/exportar/csv`: `ordenar_por` (`data`, `empresa`, `titulo` ou `salario`) e `direcao` (`asc` ou `desc`). Só `/vagas` usa `pagina` (começa em 1) e `limite` (de 1 a 100, padrão 20).

Exemplo: `/vagas?tecnologia=python&nivel=sênior&aceita_brasil=true&ordenar_por=salario&direcao=desc`

Resposta de `/vagas`: `{"total": 120, "pagina": 1, "limite": 10, "vagas": [ ... ]}`

Resposta de `/estatisticas`: `total`, `tecnologia_mais_pedida`, `categoria_com_mais_vagas`, `aceitam_brasil`, `salario_medio`, `vagas_com_salario`, `ultima_coleta`, `por_categoria`, `por_fonte`, `por_tecnologia` (10 mais pedidas), `por_nivel`, `por_faixa_salarial` e `por_dia` (últimos 30 dias).

## Nome e RM dos Integrantes

- Diego Candido Stoianof — RM570748
- Felipe Moreira Mendes — RM570807
- Lucas Zezzi Custodio — RM571161
- Romulo Mendes Souza — RM570620
