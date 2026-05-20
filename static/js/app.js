const HORARIOS = [
  "08:00","08:30","09:00","09:30","10:00","10:30",
  "11:00","11:30","13:00","13:30","14:00","14:30",
  "15:00","15:30","16:00","16:30","17:00","17:30","18:00"
];

function mostrarMsg(id, texto, tipo) {
  const el = document.getElementById(id);
  el.textContent = texto;
  el.className = "msg " + tipo;
  el.style.display = "block";
  setTimeout(() => { el.style.display = "none"; }, 4000);
}

function formatarData(data) {
  const [y, m, d] = data.split("-");
  return `${d}/${m}/${y}`;
}

function mostrarAba(aba) {
  document.querySelectorAll(".aba").forEach(el => el.classList.remove("ativa"));
  document.querySelectorAll(".nav-btn").forEach(el => el.classList.remove("active"));
  document.getElementById("aba-" + aba).classList.add("ativa");
  event.target.classList.add("active");

  if (aba === "agenda") {
    const filtro = document.getElementById("filtro-data");
    if (!filtro.value) {
      const hoje = new Date().toISOString().split("T")[0];
      filtro.value = hoje;
    }
    carregarAgenda();
  }
}

async function atualizarHorarios() {
  const data = document.getElementById("data").value;
  const select = document.getElementById("horario");

  if (!data) {
    select.innerHTML = '<option value="">Selecione uma data primeiro</option>';
    return;
  }

  const res = await fetch(`/api/agendamentos?data=${data}`);
  const ocupados = await res.json();
  const horariosOcupados = ocupados.map(a => a.horario);

  select.innerHTML = "";
  HORARIOS.forEach(h => {
    const opt = document.createElement("option");
    opt.value = h;
    opt.textContent = horariosOcupados.includes(h) ? `${h} — ocupado` : h;
    opt.disabled = horariosOcupados.includes(h);
    select.appendChild(opt);
  });

  const primeiro = HORARIOS.find(h => !horariosOcupados.includes(h));
  if (primeiro) select.value = primeiro;
}

document.getElementById("data").addEventListener("change", atualizarHorarios);

async function agendarHorario() {
  const nome = document.getElementById("nome").value.trim();
  const telefone = document.getElementById("telefone").value.trim();
  const servico = document.getElementById("servico").value;
  const data = document.getElementById("data").value;
  const horario = document.getElementById("horario").value;

  if (!nome || !data || !horario) {
    mostrarMsg("msg-form", "Preencha nome, data e horário.", "erro");
    return;
  }

  const res = await fetch("/api/agendamentos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, telefone, servico, data, horario })
  });

  if (res.ok) {
    mostrarMsg("msg-form", `✓ Agendamento confirmado para ${nome} às ${horario}!`, "sucesso");
    document.getElementById("nome").value = "";
    document.getElementById("telefone").value = "";
    document.getElementById("data").value = "";
    document.getElementById("horario").innerHTML = '<option value="">Selecione uma data primeiro</option>';
  } else {
    const err = await res.json();
    mostrarMsg("msg-form", err.detail || "Erro ao agendar.", "erro");
  }
}

async function carregarAgenda() {
  const data = document.getElementById("filtro-data").value;
  const lista = document.getElementById("lista-agendamentos");

  if (!data) { lista.innerHTML = '<p class="vazio">Selecione uma data.</p>'; return; }

  const res = await fetch(`/api/agendamentos?data=${data}`);
  const agendamentos = await res.json();

  if (agendamentos.length === 0) {
    lista.innerHTML = `<p class="vazio">Nenhum agendamento para ${formatarData(data)}.</p>`;
    return;
  }

  lista.innerHTML = agendamentos.map(a => `
    <div class="agendamento-item" id="item-${a.id}">
      <div class="horario-badge">${a.horario}</div>
      <div class="agendamento-info">
        <strong>${a.nome}</strong>
        <span>${a.servico}</span>
        ${a.telefone ? `<div class="telefone">📞 ${a.telefone}</div>` : ""}
      </div>
      <div class="agendamento-acoes">
        <button class="btn-icon edit" title="Editar" onclick="abrirModal(${JSON.stringify(a).replace(/"/g, '&quot;')})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </button>
        <button class="btn-icon del" title="Cancelar" onclick="cancelar(${a.id})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
        </button>
      </div>
    </div>
  `).join("");
}

async function cancelar(id) {
  if (!confirm("Cancelar este agendamento?")) return;

  const res = await fetch(`/api/agendamentos/${id}`, { method: "DELETE" });

  if (res.ok || res.status === 204) {
    document.getElementById("item-" + id)?.remove();
    const lista = document.getElementById("lista-agendamentos");
    if (!lista.querySelector(".agendamento-item")) {
      lista.innerHTML = '<p class="vazio">Nenhum agendamento para esta data.</p>';
    }
  } else {
    alert("Erro ao cancelar agendamento.");
  }
}

function abrirModal(a) {
  document.getElementById("edit-id").value = a.id;
  document.getElementById("edit-nome").value = a.nome;
  document.getElementById("edit-telefone").value = a.telefone || "";
  document.getElementById("edit-servico").value = a.servico;
  document.getElementById("edit-data").value = a.data;
  document.getElementById("edit-horario").value = a.horario;
  document.getElementById("modal-overlay").style.display = "flex";
}

function fecharModal(e) {
  if (e.target.id === "modal-overlay") {
    document.getElementById("modal-overlay").style.display = "none";
  }
}

async function salvarEdicao() {
  const id = document.getElementById("edit-id").value;
  const dados = {
    nome: document.getElementById("edit-nome").value.trim(),
    telefone: document.getElementById("edit-telefone").value.trim(),
    servico: document.getElementById("edit-servico").value,
    data: document.getElementById("edit-data").value,
    horario: document.getElementById("edit-horario").value
  };

  const res = await fetch(`/api/agendamentos/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados)
  });

  if (res.ok) {
    document.getElementById("modal-overlay").style.display = "none";
    carregarAgenda();
  } else {
    const err = await res.json();
    mostrarMsg("msg-modal", err.detail || "Erro ao salvar.", "erro");
  }
}

const hoje = new Date().toISOString().split("T")[0];
document.getElementById("data").min = hoje;