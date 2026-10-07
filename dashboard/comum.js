const API = "http://localhost:8000";

async function buscarJson(caminho) {
  const resposta = await fetch(API + caminho);
  if (!resposta.ok) {
    throw new Error("Erro na API");
  }
  return resposta.json();
}

function mostrarErro(mensagem) {
  const caixa = document.getElementById("erro");
  caixa.textContent = mensagem;
  caixa.hidden = false;
}

function esconderErro() {
  document.getElementById("erro").hidden = true;
}

function mensagemApiFora() {
  return "Não foi possível acessar a API em " + API + ". Confira se ela está rodando.";
}

function formatarData(texto) {
  if (!texto) {
    return "-";
  }
  const partes = texto.slice(0, 10).split("-");
  return partes[2] + "/" + partes[1] + "/" + partes[0];
}

function formatarDataHora(texto) {
  if (!texto) {
    return "Sem coletas";
  }
  const data = new Date(texto);
  return data.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

function formatarSalario(minimo, maximo) {
  if (!minimo && !maximo) {
    return "-";
  }
  const menor = Math.round((minimo || maximo) / 1000);
  const maior = Math.round((maximo || minimo) / 1000);
  if (menor === maior) {
    return "US$ " + menor + " mil";
  }
  return "US$ " + menor + " a " + maior + " mil";
}
