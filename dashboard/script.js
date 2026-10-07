const POR_PAGINA = 10;
const CORES = ["#0e7c66", "#2f9e8a", "#6cbfaf", "#e2a03f", "#c97b2a", "#3d5a80", "#98a6b3", "#7a9e7e", "#b5651d", "#5e548e"];
const ORDEM_INICIAL = { data: "desc", empresa: "asc", titulo: "asc", salario: "desc" };
const NOMES_COLUNAS = { titulo: "Cargo", empresa: "Empresa", salario: "Salário", data: "Publicada em" };

let paginaAtual = 1;
let totalPaginas = 1;
let ordenarPor = "data";
let direcao = "desc";
let graficos = {};

function preencherSelect(id, valores) {
  const select = document.getElementById(id);
  for (const valor of valores) {
    const opcao = document.createElement("option");
    opcao.value = valor;
    opcao.textContent = valor;
    select.appendChild(opcao);
  }
}

function desenharGrafico(id, tipo, dados, opcoes) {
  if (graficos[id]) {
    graficos[id].destroy();
  }
  graficos[id] = new Chart(document.getElementById(id), {
    type: tipo,
    data: {
      labels: Object.keys(dados),
      datasets: [{
        data: Object.values(dados),
        backgroundColor: tipo === "line" ? "rgba(14, 124, 102, 0.15)" : CORES,
        borderColor: tipo === "line" ? "#0e7c66" : "#ffffff",
        borderWidth: tipo === "line" ? 2 : 1,
        fill: tipo === "line",
        tension: 0.25,
      }],
    },
    options: Object.assign({ responsive: true, maintainAspectRatio: false }, opcoes),
  });
}

function montarParametros() {
  const params = new URLSearchParams();
  const campos = ["busca", "categoria", "nivel", "tecnologia", "fonte"];
  for (const campo of campos) {
    const valor = document.getElementById(campo).value.trim();
    if (valor) {
      params.set(campo, valor);
    }
  }
  if (document.getElementById("brasil").checked) {
    params.set("aceita_brasil", "true");
  }
  return params;
}

function montarParametrosComOrdem() {
  const params = montarParametros();
  params.set("ordenar_por", ordenarPor);
  params.set("direcao", direcao);
  return params;
}

async function carregarOpcoes() {
  const opcoes = await buscarJson("/filtros");
  preencherSelect("categoria", opcoes.categorias);
  preencherSelect("nivel", opcoes.niveis);
  preencherSelect("tecnologia", opcoes.tecnologias);
  preencherSelect("fonte", opcoes.fontes);
}

async function carregarEstatisticas() {
  const dados = await buscarJson("/estatisticas?" + montarParametros().toString());

  document.getElementById("total").textContent = dados.total;
  document.getElementById("tecnologia-top").textContent = dados.tecnologia_mais_pedida || "-";
  document.getElementById("categoria-top").textContent = dados.categoria_com_mais_vagas || "-";
  document.getElementById("aceitam-brasil").textContent = dados.aceitam_brasil;
  document.getElementById("ultima-coleta").textContent = formatarDataHora(dados.ultima_coleta);

  if (dados.salario_medio) {
    document.getElementById("salario-medio").textContent = formatarSalario(dados.salario_medio, dados.salario_medio);
    document.getElementById("salario-nota").textContent = "por ano, em " + dados.vagas_com_salario + " vagas com salário";
  } else {
    document.getElementById("salario-medio").textContent = "-";
    document.getElementById("salario-nota").textContent = "nenhuma vaga com salário";
  }

  desenharGrafico("grafico-tecnologias", "bar", dados.por_tecnologia, {
    indexAxis: "y",
    plugins: { legend: { display: false } },
  });
  desenharGrafico("grafico-categorias", "doughnut", dados.por_categoria, {
    plugins: { legend: { position: "bottom" } },
  });
  desenharGrafico("grafico-niveis", "bar", dados.por_nivel, {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
  });
  desenharGrafico("grafico-salarios", "bar", dados.por_faixa_salarial, {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
  });
  desenharGrafico("grafico-dias", "line", dados.por_dia, {
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
  });
}

function criarCelula(texto) {
  const celula = document.createElement("td");
  celula.textContent = texto;
  return celula;
}

function criarCelulaLink(texto, endereco, novaAba) {
  const celula = document.createElement("td");
  const link = document.createElement("a");
  link.href = endereco;
  link.textContent = texto;
  if (novaAba) {
    link.target = "_blank";
    link.rel = "noopener";
  }
  celula.appendChild(link);
  return celula;
}

function criarLinha(vaga) {
  const linha = document.createElement("tr");

  linha.appendChild(criarCelulaLink(vaga.titulo, "vaga.html?id=" + encodeURIComponent(vaga._id), false));
  linha.appendChild(criarCelula(vaga.empresa));
  linha.appendChild(criarCelula(vaga.nivel));
  linha.appendChild(criarCelula(vaga.categoria));
  linha.appendChild(criarCelula(vaga.tecnologias.slice(0, 4).join(", ") || "-"));
  linha.appendChild(criarCelula(formatarSalario(vaga.salario_min, vaga.salario_max)));
  linha.appendChild(criarCelula(formatarData(vaga.data_publicacao)));
  linha.appendChild(criarCelula(vaga.fonte));

  if (vaga.url && vaga.url.startsWith("http")) {
    linha.appendChild(criarCelulaLink("Ver anúncio", vaga.url, true));
  } else {
    linha.appendChild(criarCelula("-"));
  }
  return linha;
}

function atualizarCabecalhos() {
  const botoes = document.querySelectorAll("button.ordenar");
  for (const botao of botoes) {
    const campo = botao.dataset.campo;
    let texto = NOMES_COLUNAS[campo];
    if (campo === ordenarPor) {
      texto = texto + (direcao === "asc" ? " ↑" : " ↓");
    }
    botao.textContent = texto;
  }
}

async function carregarVagas() {
  const params = montarParametrosComOrdem();
  params.set("pagina", paginaAtual);
  params.set("limite", POR_PAGINA);
  const dados = await buscarJson("/vagas?" + params.toString());

  const tabela = document.getElementById("tabela");
  tabela.innerHTML = "";

  if (dados.vagas.length === 0) {
    const linha = document.createElement("tr");
    const celula = document.createElement("td");
    celula.colSpan = 9;
    celula.className = "vazio";
    celula.textContent = "Nenhuma vaga encontrada. Mude os filtros ou rode o crawler para coletar vagas.";
    linha.appendChild(celula);
    tabela.appendChild(linha);
  }

  for (const vaga of dados.vagas) {
    tabela.appendChild(criarLinha(vaga));
  }

  totalPaginas = Math.max(1, Math.ceil(dados.total / POR_PAGINA));
  document.getElementById("info-pagina").textContent =
    "Página " + paginaAtual + " de " + totalPaginas + " (" + dados.total + " vagas)";
  document.getElementById("anterior").disabled = paginaAtual <= 1;
  document.getElementById("proxima").disabled = paginaAtual >= totalPaginas;
  atualizarCabecalhos();
}

async function atualizarLista() {
  try {
    await carregarVagas();
    esconderErro();
  } catch (erro) {
    mostrarErro(mensagemApiFora());
  }
}

async function aplicarFiltros() {
  paginaAtual = 1;
  try {
    await carregarEstatisticas();
    await carregarVagas();
    esconderErro();
  } catch (erro) {
    mostrarErro(mensagemApiFora());
  }
}

document.getElementById("filtros").addEventListener("submit", function (evento) {
  evento.preventDefault();
  aplicarFiltros();
});

const camposComMudanca = ["categoria", "nivel", "tecnologia", "fonte", "brasil"];
for (const id of camposComMudanca) {
  document.getElementById(id).addEventListener("change", aplicarFiltros);
}

document.getElementById("limpar").addEventListener("click", function () {
  document.getElementById("filtros").reset();
  aplicarFiltros();
});

document.getElementById("exportar").addEventListener("click", function () {
  window.location.href = API + "/exportar/csv?" + montarParametrosComOrdem().toString();
});

document.getElementById("anterior").addEventListener("click", function () {
  paginaAtual = paginaAtual - 1;
  atualizarLista();
});

document.getElementById("proxima").addEventListener("click", function () {
  paginaAtual = paginaAtual + 1;
  atualizarLista();
});

const botoesOrdem = document.querySelectorAll("button.ordenar");
for (const botao of botoesOrdem) {
  botao.addEventListener("click", function () {
    const campo = botao.dataset.campo;
    if (campo === ordenarPor) {
      direcao = direcao === "asc" ? "desc" : "asc";
    } else {
      ordenarPor = campo;
      direcao = ORDEM_INICIAL[campo];
    }
    paginaAtual = 1;
    atualizarLista();
  });
}

async function iniciar() {
  try {
    await carregarOpcoes();
    await carregarEstatisticas();
    await carregarVagas();
  } catch (erro) {
    mostrarErro(mensagemApiFora());
  }
}

iniciar();
