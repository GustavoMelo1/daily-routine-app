const BASE_URL = "http://localhost:8000";

export function formatarDataISO(date) {
  const ano = date.getFullYear();
  const mes = String(date.getMonth() + 1).padStart(2, "0");
  const dia = String(date.getDate()).padStart(2, "0");
  return `${ano}-${mes}-${dia}`;
}

export async function listarDiasDoMes(ano, mes) {
  const resposta = await fetch(`${BASE_URL}/dias?ano=${ano}&mes=${mes}`);
  if (!resposta.ok) throw new Error("Falha ao listar os dias do mês");
  const lista = await resposta.json();
  const marcadores = {};
  for (const item of lista) {
    if (item.marcador) marcadores[item.data] = item.marcador;
  }
  return marcadores;
}

export async function buscarDia(dataISO) {
  const resposta = await fetch(`${BASE_URL}/dias/${dataISO}`);
  if (resposta.status === 404) return null;
  if (!resposta.ok) throw new Error("Falha ao buscar o dia");
  return resposta.json();
}

export async function criarDia(payload) {
  const resposta = await fetch(`${BASE_URL}/dias`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resposta.ok) throw new Error("Falha ao criar o dia");
  return resposta.json();
}

export async function criarTarefa(payload) {
  const resposta = await fetch(`${BASE_URL}/tarefas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resposta.ok) throw new Error("Falha ao criar a tarefa");
  return resposta.json();
}

export async function atualizarTarefa(id, cumprida) {
  const resposta = await fetch(`${BASE_URL}/tarefas/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cumprida }),
  });
  if (!resposta.ok) throw new Error("Falha ao atualizar a tarefa");
  return resposta.json();
}
