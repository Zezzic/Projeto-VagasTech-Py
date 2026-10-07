function adicionarDado(lista, nome, valor) {
  const termo = document.createElement("dt");
  termo.textContent = nome;
  const descricao = document.createElement("dd");
  descricao.textContent = valor;
  lista.appendChild(termo);
  lista.appendChild(descricao);
}

function mostrarVaga(vaga) {
  document.title = vaga.titulo;
  document.getElementById("titulo").textContent = vaga.titulo;
  document.getElementById("empresa").textContent = vaga.empresa;

  const lista = document.getElementById("dados");
  adicionarDado(lista, "Categoria", vaga.categoria);
  adicionarDado(lista, "Nível", vaga.nivel);
  adicionarDado(lista, "Tipo de contrato", vaga.tipo_contrato);
  adicionarDado(lista, "Localização", vaga.localizacao);
  adicionarDado(lista, "Aceita candidatos do Brasil", vaga.aceita_brasil ? "Sim" : "Não indicado na vaga");
  adicionarDado(lista, "Salário", formatarSalario(vaga.salario_min, vaga.salario_max));
  adicionarDado(lista, "Tecnologias", vaga.tecnologias.join(", ") || "Nenhuma encontrada");
  adicionarDado(lista, "Publicada em", formatarData(vaga.data_publicacao));
  adicionarDado(lista, "Coletada em", formatarDataHora(vaga.coletado_em));
  adicionarDado(lista, "Fonte", vaga.fonte);

  document.getElementById("descricao").textContent = vaga.descricao || "Esta vaga não tem descrição.";
  document.getElementById("nota-fonte").textContent =
    "Vaga publicada em " + vaga.fonte + ". A descrição é um resumo; o texto completo está no anúncio original.";

  const anuncio = document.getElementById("anuncio");
  if (vaga.url && vaga.url.startsWith("http")) {
    anuncio.href = vaga.url;
    anuncio.textContent = "Ver anúncio original em " + vaga.fonte;
  } else {
    anuncio.hidden = true;
  }

  document.getElementById("conteudo").hidden = false;
}

async function iniciar() {
  const id = new URLSearchParams(window.location.search).get("id");
  if (!id) {
    document.getElementById("titulo").textContent = "Vaga não encontrada";
    mostrarErro("Nenhuma vaga foi escolhida. Volte para a lista e clique em uma vaga.");
    return;
  }

  try {
    const vaga = await buscarJson("/vagas/" + encodeURIComponent(id));
    mostrarVaga(vaga);
  } catch (erro) {
    document.getElementById("titulo").textContent = "Vaga não encontrada";
    mostrarErro("Não foi possível carregar essa vaga. Confira se a API está rodando em " + API + ".");
  }
}

iniciar();
