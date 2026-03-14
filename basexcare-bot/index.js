/**
 * ═══════════════════════════════════════════════════════
 *  BaseX Care Bot — BazeX Care
 *  Bot de acompanhamento inteligente de cuidados
 *  Versão Institucional — Hospitais, Clínicas e Home Care
 *  @BasexCareBot
 * ═══════════════════════════════════════════════════════
 */

require("dotenv").config();
const { Telegraf, Markup } = require("telegraf");
const cron = require("node-cron");
const fs = require("fs");
const path = require("path");

// ═══════════════════════════════════════════════════════
//  CONFIGURAÇÃO
// ═══════════════════════════════════════════════════════

const BOT_TOKEN = process.env.BOT_TOKEN || "8633651730:AAHnjRPM4gs6Q2XcXoTgjlSqLM-ceu3eYQQ";
const bot = new Telegraf(BOT_TOKEN);
const DB_PATH = path.join(__dirname, "data.json");

// ═══════════════════════════════════════════════════════
//  BANCO DE DADOS (JSON)
// ═══════════════════════════════════════════════════════

function loadDB() {
  try {
    const raw = fs.readFileSync(DB_PATH, "utf8");
    const data = JSON.parse(raw);
    return {
      patients: data.patients || {},
      caregivers: data.caregivers || {},
      families: data.families || {},
      nurses: data.nurses || {},
      supervisors: data.supervisors || {},
      shifts: data.shifts || {},
      checklists: data.checklists || {},
      vitals: data.vitals || {},
      incidents: data.incidents || {},
      scales: data.scales || {},
      alerts: data.alerts || [],
      discharges: data.discharges || {},
    };
  } catch {
    return { patients: {}, caregivers: {}, families: {}, nurses: {}, supervisors: {}, shifts: {}, checklists: {}, vitals: {}, incidents: {}, scales: {}, alerts: [], discharges: {} };
  }
}

function saveDB() {
  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2), "utf8");
}

let db = loadDB();

// ═══════════════════════════════════════════════════════
//  UTILITÁRIOS DE DATA/HORA
// ═══════════════════════════════════════════════════════

const TZ = "America/Sao_Paulo";

function now() {
  return new Date().toLocaleString("pt-BR", { timeZone: TZ });
}

function todayKey() {
  return new Date().toLocaleDateString("pt-BR", { timeZone: TZ }).replace(/\//g, "-");
}

function timeNow() {
  return new Date().toLocaleTimeString("pt-BR", { timeZone: TZ, hour: "2-digit", minute: "2-digit" });
}

function currentHour() {
  return parseInt(new Date().toLocaleString("pt-BR", { timeZone: TZ, hour: "2-digit", hour12: false }));
}

function getVitalPeriod() {
  const h = currentHour();
  if (h >= 6 && h < 12) return "manhã";
  if (h >= 12 && h < 18) return "tarde";
  return "noite";
}

function formatDuration(ms) {
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  return h > 0 ? `${h}h${m}min` : `${m}min`;
}

function generateCode() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let code = "CUI-";
  for (let i = 0; i < 5; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return code;
}

// ═══════════════════════════════════════════════════════
//  SINAIS VITAIS — FAIXAS NORMAIS
// ═══════════════════════════════════════════════════════

const VITAL_RANGES = {
  temperatura:   { min: 35.5, max: 37.5, unit: "°C",   emoji: "🌡️", label: "Temperatura" },
  saturacao:     { min: 92,   max: 100,  unit: "%",    emoji: "💨", label: "Saturação (SpO2)" },
  pressao_sis:   { min: 90,   max: 140,  unit: "mmHg", emoji: "🩺", label: "Pressão Sistólica" },
  pressao_dia:   { min: 60,   max: 90,   unit: "mmHg", emoji: "🩺", label: "Pressão Diastólica" },
  freq_cardiaca: { min: 50,   max: 100,  unit: "bpm",  emoji: "❤️", label: "Freq. Cardíaca" },
};

function isOutOfRange(type, value) {
  const r = VITAL_RANGES[type];
  if (!r) return false;
  return value < r.min || value > r.max;
}

function vitalStatus(type, value) {
  return isOutOfRange(type, value) ? "⚠️" : "✅";
}

// ═══════════════════════════════════════════════════════
//  NÍVEIS DE PRIORIDADE
// ═══════════════════════════════════════════════════════

const PRIORITY_LEVELS = {
  high:   { emoji: "🔴", label: "Alta dependência", desc: "Necessita assistência contínua" },
  medium: { emoji: "🟠", label: "Dependência média", desc: "Necessita supervisão e apoio parcial" },
  low:    { emoji: "🟢", label: "Independente", desc: "Necessita acompanhamento leve" },
};

// ═══════════════════════════════════════════════════════
//  ESCALAS CLÍNICAS
// ═══════════════════════════════════════════════════════

const CLINICAL_SCALES = {
  pain: {
    emoji: "😣", label: "Escala de Dor",
    options: [
      { id: "0", label: "0 — Sem dor" },
      { id: "1-3", label: "1-3 — Dor leve" },
      { id: "4-6", label: "4-6 — Dor moderada" },
      { id: "7-9", label: "7-9 — Dor intensa" },
      { id: "10", label: "10 — Dor insuportável" },
    ],
  },
  confusion: {
    emoji: "🧠", label: "Confusão Mental",
    options: [
      { id: "lucido", label: "Lúcido e orientado" },
      { id: "leve", label: "Confusão leve (desorientado no tempo)" },
      { id: "moderada", label: "Confusão moderada (desorientado tempo/espaço)" },
      { id: "grave", label: "Confusão grave (não reconhece pessoas)" },
      { id: "inconsciente", label: "Inconsciente / não responsivo" },
    ],
  },
  fall_risk: {
    emoji: "⚠️", label: "Risco de Queda",
    options: [
      { id: "baixo", label: "Baixo — Caminha estável" },
      { id: "moderado", label: "Moderado — Instável, usa apoio" },
      { id: "alto", label: "Alto — Já caiu recentemente" },
      { id: "muito_alto", label: "Muito alto — Confuso + instável" },
    ],
  },
  feeding: {
    emoji: "🍽️", label: "Alimentação",
    options: [
      { id: "normal", label: "Normal — Come sozinho" },
      { id: "assistida", label: "Assistida — Precisa de ajuda" },
      { id: "pastosa", label: "Dieta pastosa" },
      { id: "liquida", label: "Dieta líquida" },
      { id: "sonda", label: "Sonda / Enteral" },
      { id: "recusa", label: "Recusando alimentação" },
    ],
  },
};

// ═══════════════════════════════════════════════════════
//  INTERCORRÊNCIAS
// ═══════════════════════════════════════════════════════

const INCIDENT_TYPES = [
  { id: "queda", emoji: "🤕", label: "Paciente caiu" },
  { id: "vomito", emoji: "🤢", label: "Paciente vomitou" },
  { id: "recusa_med", emoji: "💊", label: "Recusou medicação" },
  { id: "agitacao", emoji: "😤", label: "Paciente agitado" },
  { id: "dispneia", emoji: "😮‍💨", label: "Falta de ar / dispneia" },
  { id: "febre", emoji: "🌡️", label: "Febre alta" },
  { id: "dor_intensa", emoji: "😣", label: "Dor intensa" },
  { id: "sangramento", emoji: "🩸", label: "Sangramento" },
  { id: "convulsao", emoji: "⚡", label: "Convulsão" },
  { id: "outro", emoji: "📝", label: "Outra intercorrência" },
];

// ═══════════════════════════════════════════════════════
//  MÁQUINA DE ESTADOS (CONVERSA)
// ═══════════════════════════════════════════════════════

const states = {};

function setState(userId, step, data = {}) {
  states[userId] = { step, data, ts: Date.now() };
}

function getState(userId) {
  return states[userId] || { step: "idle", data: {} };
}

function clearState(userId) {
  delete states[userId];
}

// ═══════════════════════════════════════════════════════
//  HELPERS DE DADOS
// ═══════════════════════════════════════════════════════

function uid(ctx) {
  return String(ctx.from.id);
}

function userName(ctx) {
  return ctx.from.first_name || "Usuário";
}

function getPatientId(userId) {
  const cg = db.caregivers[userId];
  if (cg && cg.activePatientId) return cg.activePatientId;
  if (cg && cg.patientIds && cg.patientIds.length > 0) return cg.patientIds[0];
  // Fallback: campo antigo
  if (cg && cg.patientId) return cg.patientId;
  const fam = db.families[userId];
  if (fam && fam.patientCode) {
    const entry = Object.entries(db.patients).find(([, p]) => p.code === fam.patientCode);
    return entry ? entry[0] : null;
  }
  return null;
}

function getAllPatientIds(userId) {
  const cg = db.caregivers[userId];
  if (!cg) return [];
  // Novo formato: array de pacientes
  if (cg.patientIds && cg.patientIds.length > 0) return cg.patientIds;
  // Fallback: campo antigo
  if (cg.patientId) return [cg.patientId];
  return [];
}

function getActiveShift(userId) {
  return Object.values(db.shifts).find(
    (s) => s.caregiverId === userId && s.active
  );
}

function getActiveShiftForPatient(patientId) {
  return Object.values(db.shifts).find(
    (s) => s.patientId === patientId && s.active
  );
}

// ═══════════════════════════════════════════════════════
//  FICHA CLÍNICA DO PACIENTE
// ═══════════════════════════════════════════════════════

function buildPatientCard(patient, patientId) {
  const pri = PRIORITY_LEVELS[patient.priority] || PRIORITY_LEVELS.medium;
  let card = `━━━━━━━━━━━━━━━━━━━━━\n`;
  card += `👤 *${patient.name}*`;
  if (patient.age) card += `, ${patient.age} anos`;
  card += `\n`;
  card += `${pri.emoji} *${pri.label}*\n`;
  card += `━━━━━━━━━━━━━━━━━━━━━\n`;

  if (patient.room) card += `🏥 Quarto/Leito: *${patient.room}*\n`;
  if (patient.conditions) card += `🩺 Diagnóstico: ${patient.conditions}\n`;
  if (patient.fallRisk) card += `⚠️ Risco de queda: *${patient.fallRisk}*\n`;
  if (patient.diet) card += `🍽️ Dieta: *${patient.diet}*\n`;
  if (patient.criticalMed) card += `💊 Med. crítica: *${patient.criticalMed}*\n`;
  if (patient.mobility) card += `🦯 Mobilidade: ${patient.mobility}\n`;

  if (patient.medications && patient.medications.length > 0 && patient.medicationsRaw !== "depois") {
    card += `\n💊 *Medicações:*\n`;
    patient.medications.forEach((m) => {
      card += `  • ${m}\n`;
    });
  }

  card += `\n🔑 Código: \`${patient.code}\`\n`;
  card += `━━━━━━━━━━━━━━━━━━━━━`;
  return card;
}

// ═══════════════════════════════════════════════════════
//  CHECKLIST — TAREFAS
// ═══════════════════════════════════════════════════════

function getChecklistTasks(patientId) {
  const patient = db.patients[patientId];
  if (!patient) return [];

  const tasks = [
    { id: "remedio_manha",  emoji: "💊", label: "Medicação da manhã" },
    { id: "cafe_manha",     emoji: "☕", label: "Café da manhã" },
    { id: "higiene",        emoji: "🚿", label: "Higiene pessoal / banho" },
    { id: "pressao",        emoji: "🩺", label: "Verificar pressão arterial" },
    { id: "agua_manha",     emoji: "💧", label: "Hidratação (manhã)" },
    { id: "almoco",         emoji: "🍽️", label: "Almoço" },
    { id: "remedio_tarde",  emoji: "💊", label: "Medicação da tarde" },
    { id: "caminhada",      emoji: "🚶", label: "Caminhada / exercício" },
    { id: "lanche",         emoji: "🍎", label: "Lanche da tarde" },
    { id: "agua_tarde",     emoji: "💧", label: "Hidratação (tarde)" },
    { id: "jantar",         emoji: "🍽️", label: "Jantar" },
    { id: "remedio_noite",  emoji: "💊", label: "Medicação da noite" },
    { id: "sono",           emoji: "🛏️", label: "Preparar para dormir" },
  ];

  if (patient.mobility === "Acamado") {
    const idx = tasks.findIndex((t) => t.id === "caminhada");
    if (idx >= 0) tasks[idx] = { id: "mudanca_posicao", emoji: "🔄", label: "Mudança de posição (decúbito)" };
  }

  return tasks;
}

function buildChecklistMessage(shift) {
  const patient = db.patients[shift.patientId];
  const tasks = getChecklistTasks(shift.patientId);
  const done = shift.completedTasks || [];
  const times = shift.completedTasks_times || {};

  let text = `📋 *Checklist — ${patient?.name || "Paciente"}*\n`;
  text += `━━━━━━━━━━━━━━━━━━━━━\n\n`;

  tasks.forEach((t) => {
    if (done.includes(t.id)) {
      text += `✅ ~${t.label}~ _(${times[t.id] || ""})_\n`;
    } else {
      text += `⬜ ${t.label}\n`;
    }
  });

  const pending = tasks.filter((t) => !done.includes(t.id));
  text += `\n📊 *${done.length}/${tasks.length}* concluídas`;

  if (pending.length === 0) {
    text += `\n\n🎉 *Todas as tarefas concluídas!*`;
    return { text, keyboard: null };
  }

  text += `\n\n👇 Toque para marcar como feita:`;

  const buttons = pending.map((t) => [
    Markup.button.callback(`${t.emoji} ${t.label}`, `task_${t.id}`),
  ]);

  buttons.push([
    Markup.button.callback("🧠 Humor", "btn_humor"),
    Markup.button.callback("📊 Sinais", "btn_vitals"),
  ]);
  buttons.push([
    Markup.button.callback("📏 Escalas clínicas", "btn_scales"),
    Markup.button.callback("⚠️ Intercorrência", "btn_incident"),
  ]);

  return { text, keyboard: Markup.inlineKeyboard(buttons) };
}

// ═══════════════════════════════════════════════════════
//  RELATÓRIO DO TURNO
// ═══════════════════════════════════════════════════════

function generateReport(shift) {
  const patient = db.patients[shift.patientId];
  const caregiver = db.caregivers[shift.caregiverId];
  const tasks = getChecklistTasks(shift.patientId);
  const done = shift.completedTasks || [];
  const times = shift.completedTasks_times || {};
  const duration = shift.endTimestamp
    ? formatDuration(shift.endTimestamp - shift.startTimestamp)
    : formatDuration(Date.now() - shift.startTimestamp);

  const pri = PRIORITY_LEVELS[patient?.priority] || PRIORITY_LEVELS.medium;

  let r = `━━━━━━━━━━━━━━━━━━━━━\n`;
  r += `👤 *Paciente:* ${patient?.name || "N/A"}`;
  if (patient?.room) r += ` — Quarto ${patient.room}`;
  r += `\n`;
  r += `${pri.emoji} ${pri.label}\n`;
  r += `👩‍⚕️ *Cuidador(a):* ${caregiver?.name || "N/A"}\n`;
  r += `🕐 *Início:* ${shift.startedAt}\n`;
  r += `🕐 *Fim:* ${shift.endedAt || "Em andamento"}\n`;
  r += `⏱️ *Duração:* ${duration}\n`;
  r += `━━━━━━━━━━━━━━━━━━━━━\n\n`;

  r += `📋 *Checklist:* ${done.length}/${tasks.length}\n\n`;
  tasks.forEach((t) => {
    if (done.includes(t.id)) {
      r += `✅ ${t.label} _(${times[t.id] || ""})_\n`;
    } else {
      r += `❌ ${t.label}\n`;
    }
  });

  // Escalas clínicas
  if (shift.scales && shift.scales.length > 0) {
    r += `\n📏 *Escalas Clínicas:*\n`;
    shift.scales.forEach((s) => {
      const scale = CLINICAL_SCALES[s.type];
      r += `  ${scale?.emoji || "📏"} ${scale?.label || s.type}: *${s.value}* _(${s.time})_\n`;
    });
  }

  // Sinais vitais
  if (shift.vitals && shift.vitals.length > 0) {
    r += `\n📊 *Sinais Vitais:*\n`;
    shift.vitals.forEach((v) => {
      r += `\n  _${v.period} (${v.registeredAt?.split(",")[1]?.trim() || ""})_\n`;
      r += `  🌡️ ${v.temperatura}°C ${vitalStatus("temperatura", v.temperatura)}`;
      r += ` | 💨 ${v.saturacao}% ${vitalStatus("saturacao", v.saturacao)}\n`;
      r += `  🩺 ${v.pressao_sis}/${v.pressao_dia} mmHg ${isOutOfRange("pressao_sis", v.pressao_sis) || isOutOfRange("pressao_dia", v.pressao_dia) ? "⚠️" : "✅"}`;
      r += ` | ❤️ ${v.freq_cardiaca} bpm ${vitalStatus("freq_cardiaca", v.freq_cardiaca)}\n`;
    });
  } else {
    r += `\n📊 *Sinais Vitais:* Não registrados neste turno\n`;
  }

  if (shift.humor) {
    r += `\n🧠 *Humor:* ${shift.humor} _(${shift.humorTime || ""})_\n`;
  }

  // Intercorrências
  if (shift.incidents && shift.incidents.length > 0) {
    r += `\n🚨 *Intercorrências:*\n`;
    shift.incidents.forEach((inc) => {
      const type = INCIDENT_TYPES.find((t) => t.id === inc.type);
      r += `  ${type?.emoji || "⚠️"} ${type?.label || inc.type} _(${inc.time})_\n`;
      if (inc.details) r += `     ↳ ${inc.details}\n`;
    });
  }

  if (shift.observations && shift.observations.length > 0) {
    r += `\n📝 *Observações:*\n`;
    shift.observations.forEach((o) => {
      r += `  ${o.time} — ${o.text}\n`;
    });
  }

  r += `\n━━━━━━━━━━━━━━━━━━━━━\n`;
  r += `_Relatório gerado pela BazeX Care_`;
  return r;
}

// ═══════════════════════════════════════════════════════
//  NOTIFICAR CADEIA CLÍNICA (Cuidador → Enfermeira → Supervisor → Família)
// ═══════════════════════════════════════════════════════

function notifyFamily(patientId, message) {
  notifyClinicalChain(patientId, message, "family");
}

function notifyClinicalChain(patientId, message, level = "all") {
  const patient = db.patients[patientId];
  if (!patient) return;

  // Registrar alerta no banco
  db.alerts.push({
    patientId,
    patientName: patient.name,
    message: message.replace(/[*_`]/g, "").substring(0, 200),
    timestamp: Date.now(),
    date: todayKey(),
    time: timeNow(),
    level,
    resolved: false,
  });
  // Manter apenas últimos 500 alertas
  if (db.alerts.length > 500) db.alerts = db.alerts.slice(-500);
  saveDB();

  const sent = new Set();

  // 1. Notificar enfermeira(s) vinculada(s) ao paciente
  if (level === "all" || level === "nurse" || level === "family") {
    Object.values(db.nurses).forEach((nurse) => {
      if (!nurse.chatId) return;
      const nursePatients = nurse.patientIds || [];
      if (nursePatients.includes(patientId) || nursePatients.length === 0) {
        if (!sent.has(nurse.chatId)) {
          sent.add(nurse.chatId);
          bot.telegram.sendMessage(nurse.chatId,
            `👩‍⚕️ *[ENFERMAGEM]* ` + message,
            { parse_mode: "Markdown" }
          ).catch(() => {});
        }
      }
    });
  }

  // 2. Notificar supervisor(es)
  if (level === "all" || level === "supervisor" || level === "family") {
    Object.values(db.supervisors).forEach((sup) => {
      if (!sup.chatId) return;
      if (!sent.has(sup.chatId)) {
        sent.add(sup.chatId);
        bot.telegram.sendMessage(sup.chatId,
          `🏥 *[SUPERVISÃO]* ` + message,
          { parse_mode: "Markdown" }
        ).catch(() => {});
      }
    });
  }

  // 3. Notificar família
  if (patient.familyIds && patient.familyIds.length > 0) {
    patient.familyIds.forEach((fId) => {
      const fam = db.families[fId];
      if (fam && fam.chatId && !sent.has(fam.chatId)) {
        sent.add(fam.chatId);
        bot.telegram.sendMessage(fam.chatId, message, { parse_mode: "Markdown" }).catch(() => {});
      }
    });
  }
}

// ═══════════════════════════════════════════════════════
//  COMANDO /start
// ═══════════════════════════════════════════════════════

bot.start((ctx) => {
  const name = userName(ctx);
  clearState(uid(ctx));

  ctx.reply(
    `Olá, *${name}*! 👋\n\n` +
    `Eu sou a *BazeX Care* — assistente inteligente de cuidado domiciliar e institucional.\n\n` +
    `Como você quer usar o bot?`,
    {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard([
        [Markup.button.callback("👩‍⚕️ Sou Cuidador(a)", "role_caregiver")],
        [Markup.button.callback("👨‍👩‍👧 Sou Família", "role_family")],
        [Markup.button.callback("🩺 Sou Enfermeiro(a)", "role_nurse")],
        [Markup.button.callback("🏥 Sou Supervisor(a)", "role_supervisor")],
      ]),
    }
  );
});

// ═══════════════════════════════════════════════════════
//  SELEÇÃO DE ROLE
// ═══════════════════════════════════════════════════════

bot.action("role_caregiver", (ctx) => {
  const userId = uid(ctx);
  ctx.answerCbQuery("Cadastrado como Cuidador(a)!");

  db.caregivers[userId] = db.caregivers[userId] || {};
  Object.assign(db.caregivers[userId], {
    name: userName(ctx),
    chatId: ctx.chat.id,
    role: "caregiver",
    registeredAt: now(),
  });

  // Migrar campo antigo patientId para patientIds
  if (db.caregivers[userId].patientId && !db.caregivers[userId].patientIds) {
    db.caregivers[userId].patientIds = [db.caregivers[userId].patientId];
    db.caregivers[userId].activePatientId = db.caregivers[userId].patientId;
  }
  if (!db.caregivers[userId].patientIds) {
    db.caregivers[userId].patientIds = [];
  }

  saveDB();

  const patientIds = getAllPatientIds(userId);

  if (patientIds.length > 0) {
    return showCaregiverMenu(ctx, userId);
  }

  // Sem paciente — iniciar cadastro
  setState(userId, "reg_name");
  ctx.reply(
    `Perfeito, *${userName(ctx)}*! Você está como *Cuidador(a)*. 💚\n\n` +
    `Vamos cadastrar o paciente.\n\n` +
    `*Qual o nome completo do paciente?*`,
    { parse_mode: "Markdown" }
  );
});

function showCaregiverMenu(ctx, userId) {
  const patientIds = getAllPatientIds(userId);
  const activeId = getPatientId(userId);
  const activePatient = db.patients[activeId];

  let msg = `Bem-vinda de volta, *${userName(ctx)}*! 💚\n\n`;

  if (activePatient) {
    const pri = PRIORITY_LEVELS[activePatient.priority] || PRIORITY_LEVELS.medium;
    msg += `${pri.emoji} Paciente ativo: *${activePatient.name}*`;
    if (activePatient.room) msg += ` — Quarto ${activePatient.room}`;
    msg += `\n`;
  }

  if (patientIds.length > 1) {
    msg += `📋 Você tem *${patientIds.length} pacientes* cadastrados\n`;
  }

  msg += `\nO que deseja fazer?`;

  const buttons = [
    [Markup.button.callback("▶️ Iniciar turno", "btn_start_shift")],
    [Markup.button.callback("📋 Checklist", "btn_checklist"), Markup.button.callback("📊 Sinais vitais", "btn_vitals")],
    [Markup.button.callback("📏 Escalas clínicas", "btn_scales"), Markup.button.callback("⚠️ Intercorrência", "btn_incident")],
    [Markup.button.callback("📈 Histórico", "btn_history"), Markup.button.callback("👤 Ficha do paciente", "btn_patient_card")],
  ];

  if (patientIds.length > 1) {
    buttons.push([Markup.button.callback("🔄 Trocar paciente", "btn_switch_patient")]);
  }

  buttons.push([Markup.button.callback("➕ Cadastrar novo paciente", "btn_new_patient")]);

  return ctx.reply(msg, {
    parse_mode: "Markdown",
    ...Markup.inlineKeyboard(buttons),
  });
}

bot.action("role_family", (ctx) => {
  const userId = uid(ctx);
  ctx.answerCbQuery("Cadastrado como Família!");

  db.families[userId] = db.families[userId] || {};
  Object.assign(db.families[userId], {
    name: userName(ctx),
    chatId: ctx.chat.id,
    role: "family",
    registeredAt: now(),
  });
  saveDB();
  clearState(userId);

  ctx.reply(
    `Bem-vindo(a), *${userName(ctx)}*! 💙\n\n` +
    `Você está como *Família*. Vou te enviar:\n` +
    `• Relatórios automáticos do turno\n` +
    `• Alertas de sinais vitais\n` +
    `• Alertas de intercorrências\n\n` +
    `Para vincular ao paciente, peça o *código* ao cuidador e use:\n` +
    `/vincular CODIGO\n\n` +
    `*Comandos:*\n` +
    `/vincular — Vincular ao paciente\n` +
    `/relatorio — Último relatório\n` +
    `/historico — Histórico de sinais vitais\n` +
    `/ajuda — Todos os comandos`,
    { parse_mode: "Markdown" }
  );
});

// ═══════════════════════════════════════════════════════
//  ROLE: ENFERMEIRO(A)
// ═══════════════════════════════════════════════════════

bot.action("role_nurse", (ctx) => {
  const userId = uid(ctx);
  ctx.answerCbQuery("Cadastrado como Enfermeiro(a)!");

  db.nurses[userId] = db.nurses[userId] || {};
  Object.assign(db.nurses[userId], {
    name: userName(ctx),
    chatId: ctx.chat.id,
    role: "nurse",
    registeredAt: now(),
    patientIds: db.nurses[userId]?.patientIds || [],
  });
  saveDB();
  clearState(userId);

  const patientCount = Object.keys(db.patients).length;
  const activeShifts = Object.values(db.shifts).filter((s) => s.active).length;
  const todayAlerts = db.alerts.filter((a) => a.date === todayKey()).length;

  ctx.reply(
    `Bem-vindo(a), *${userName(ctx)}*! \ud83e\ude7a\n\n` +
    `Você está como *Enfermeiro(a) Responsável*.\n\n` +
    `\ud83d\udcca *Resumo atual:*\n` +
    `\ud83d\udc65 Pacientes cadastrados: *${patientCount}*\n` +
    `\ud83d\udfe2 Turnos ativos: *${activeShifts}*\n` +
    `\ud83d\udea8 Alertas hoje: *${todayAlerts}*\n\n` +
    `Você receberá:\n` +
    `\u2022 Alertas de sinais vitais críticos\n` +
    `\u2022 Alertas de intercorrências\n` +
    `\u2022 Escalas clínicas críticas\n\n` +
    `*Comandos:*\n` +
    `/painel — Painel de supervisão\n` +
    `/vincular CODIGO — Vincular a um paciente\n` +
    `/historico — Histórico de sinais vitais\n` +
    `/relatorio — Último relatório\n` +
    `/ajuda — Todos os comandos`,
    { parse_mode: "Markdown" }
  );
});

// ═══════════════════════════════════════════════════════
//  ROLE: SUPERVISOR(A)
// ═══════════════════════════════════════════════════════

bot.action("role_supervisor", (ctx) => {
  const userId = uid(ctx);
  ctx.answerCbQuery("Cadastrado como Supervisor(a)!");

  db.supervisors[userId] = db.supervisors[userId] || {};
  Object.assign(db.supervisors[userId], {
    name: userName(ctx),
    chatId: ctx.chat.id,
    role: "supervisor",
    registeredAt: now(),
  });
  saveDB();
  clearState(userId);

  const patientCount = Object.keys(db.patients).length;
  const activeShifts = Object.values(db.shifts).filter((s) => s.active).length;
  const todayAlerts = db.alerts.filter((a) => a.date === todayKey()).length;

  ctx.reply(
    `Bem-vindo(a), *${userName(ctx)}*! \ud83c\udfe5\n\n` +
    `Você está como *Supervisor(a) de Plantão*.\n\n` +
    `\ud83d\udcca *Resumo atual:*\n` +
    `\ud83d\udc65 Pacientes cadastrados: *${patientCount}*\n` +
    `\ud83d\udfe2 Turnos ativos: *${activeShifts}*\n` +
    `\ud83d\udea8 Alertas hoje: *${todayAlerts}*\n\n` +
    `Você receberá *todos os alertas* de todos os pacientes.\n\n` +
    `*Comandos:*\n` +
    `/painel — Painel de supervisão completo\n` +
    `/historico — Histórico de sinais vitais\n` +
    `/relatorio — Último relatório\n` +
    `/ajuda — Todos os comandos`,
    { parse_mode: "Markdown" }
  );
});

// ═══════════════════════════════════════════════════════
//  BOTÕES DE NAVEGAÇÃO RÁPIDA
// ═══════════════════════════════════════════════════════

bot.action("btn_start_shift", (ctx) => {
  ctx.answerCbQuery();
  handleStartShift(ctx, uid(ctx));
});

bot.action("btn_checklist", (ctx) => {
  ctx.answerCbQuery();
  handleChecklist(ctx, uid(ctx));
});

bot.action("btn_vitals", (ctx) => {
  ctx.answerCbQuery();
  handleVitalsStart(ctx, uid(ctx));
});

bot.action("btn_history", (ctx) => {
  ctx.answerCbQuery();
  handleHistory(ctx, uid(ctx));
});

bot.action("btn_patient_card", (ctx) => {
  ctx.answerCbQuery();
  const patientId = getPatientId(uid(ctx));
  if (!patientId || !db.patients[patientId]) {
    return ctx.reply("Nenhum paciente ativo. Use /start");
  }
  ctx.reply(buildPatientCard(db.patients[patientId], patientId), { parse_mode: "Markdown" });
});

bot.action("btn_new_patient", (ctx) => {
  ctx.answerCbQuery();
  setState(uid(ctx), "reg_name");
  ctx.reply("*Qual o nome completo do novo paciente?*", { parse_mode: "Markdown" });
});

// ═══════════════════════════════════════════════════════
//  TROCAR PACIENTE (/plantao)
// ═══════════════════════════════════════════════════════

bot.action("btn_switch_patient", (ctx) => {
  ctx.answerCbQuery();
  handleSwitchPatient(ctx, uid(ctx));
});

function handleSwitchPatient(ctx, userId) {
  const patientIds = getAllPatientIds(userId);
  if (patientIds.length <= 1) {
    return ctx.reply("Você tem apenas 1 paciente. Cadastre mais com o botão ➕");
  }

  const activeId = getPatientId(userId);
  const buttons = patientIds.map((pid) => {
    const p = db.patients[pid];
    if (!p) return null;
    const pri = PRIORITY_LEVELS[p.priority] || PRIORITY_LEVELS.medium;
    const isActive = pid === activeId;
    const label = `${pri.emoji} ${p.name}${p.room ? ` — Q.${p.room}` : ""}${isActive ? " ✓" : ""}`;
    return [Markup.button.callback(label, `switch_${pid}`)];
  }).filter(Boolean);

  ctx.reply(
    `🔄 *Selecionar paciente ativo:*\n\nToque no paciente que deseja acompanhar:`,
    { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) }
  );
}

bot.action(/^switch_(.+)$/, (ctx) => {
  const userId = uid(ctx);
  const patientId = ctx.match[1];
  const patient = db.patients[patientId];

  if (!patient) {
    return ctx.answerCbQuery("Paciente não encontrado.");
  }

  ctx.answerCbQuery(`Paciente: ${patient.name}`);

  if (db.caregivers[userId]) {
    db.caregivers[userId].activePatientId = patientId;
    saveDB();
  }

  const pri = PRIORITY_LEVELS[patient.priority] || PRIORITY_LEVELS.medium;
  ctx.reply(
    `✅ Paciente ativo: *${patient.name}*\n` +
    `${pri.emoji} ${pri.label}` +
    (patient.room ? ` — Quarto ${patient.room}` : "") + `\n\n` +
    buildPatientCard(patient, patientId),
    {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard([
        [Markup.button.callback("▶️ Iniciar turno", "btn_start_shift")],
        [Markup.button.callback("📋 Checklist", "btn_checklist"), Markup.button.callback("📊 Sinais", "btn_vitals")],
      ]),
    }
  );
});

// ═══════════════════════════════════════════════════════
//  HUMOR DO PACIENTE
// ═══════════════════════════════════════════════════════

bot.action("btn_humor", (ctx) => {
  ctx.answerCbQuery();
  ctx.reply("Como está o humor do paciente agora?", {
    ...Markup.inlineKeyboard([
      [
        Markup.button.callback("😊 Tranquilo", "humor_tranquilo"),
        Markup.button.callback("😄 Alegre", "humor_alegre"),
      ],
      [
        Markup.button.callback("😢 Triste", "humor_triste"),
        Markup.button.callback("😤 Irritado", "humor_irritado"),
      ],
      [
        Markup.button.callback("😵 Confuso", "humor_confuso"),
        Markup.button.callback("😴 Sonolento", "humor_sonolento"),
      ],
    ]),
  });
});

bot.action(/^humor_(.+)$/, (ctx) => {
  const userId = uid(ctx);
  const humor = ctx.match[1];
  const shift = getActiveShift(userId);

  const humorMap = {
    tranquilo: "😊 Tranquilo",
    irritado: "😤 Irritado",
    triste: "😢 Triste",
    confuso: "😵 Confuso",
    sonolento: "😴 Sonolento",
    alegre: "😄 Alegre",
  };

  const label = humorMap[humor] || humor;
  ctx.answerCbQuery(`Humor: ${label}`);

  if (shift) {
    shift.humor = label;
    shift.humorTime = timeNow();
    saveDB();
  }

  ctx.reply(`🧠 Humor registrado: *${label}* às ${timeNow()}`, { parse_mode: "Markdown" });
});

// ═══════════════════════════════════════════════════════
//  ESCALAS CLÍNICAS
// ═══════════════════════════════════════════════════════

bot.action("btn_scales", (ctx) => {
  ctx.answerCbQuery();
  ctx.reply(
    `📏 *Escalas Clínicas*\n\nSelecione a escala para registrar:`,
    {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard([
        [Markup.button.callback("😣 Escala de Dor (0-10)", "scale_pain")],
        [Markup.button.callback("🧠 Confusão Mental", "scale_confusion")],
        [Markup.button.callback("⚠️ Risco de Queda", "scale_fall_risk")],
        [Markup.button.callback("🍽️ Alimentação", "scale_feeding")],
      ]),
    }
  );
});

bot.action(/^scale_(.+)$/, (ctx) => {
  const scaleType = ctx.match[1];
  const scale = CLINICAL_SCALES[scaleType];
  if (!scale) return ctx.answerCbQuery("Escala não encontrada.");

  ctx.answerCbQuery();

  const buttons = scale.options.map((opt) => [
    Markup.button.callback(opt.label, `scaleval_${scaleType}_${opt.id}`),
  ]);

  ctx.reply(
    `${scale.emoji} *${scale.label}*\n\nSelecione o nível atual:`,
    { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) }
  );
});

bot.action(/^scaleval_(.+)_(.+)$/, (ctx) => {
  const userId = uid(ctx);
  const scaleType = ctx.match[1];
  const scaleValue = ctx.match[2];
  const scale = CLINICAL_SCALES[scaleType];
  const option = scale?.options.find((o) => o.id === scaleValue);

  ctx.answerCbQuery(`${scale?.label}: ${option?.label || scaleValue}`);

  const record = {
    type: scaleType,
    value: option?.label || scaleValue,
    time: timeNow(),
    date: todayKey(),
    registeredBy: userId,
  };

  // Salvar no turno ativo
  const shift = getActiveShift(userId);
  if (shift) {
    if (!shift.scales) shift.scales = [];
    shift.scales.push(record);
  }

  // Salvar no banco geral
  const patientId = getPatientId(userId);
  if (patientId) {
    if (!db.scales[patientId]) db.scales[patientId] = [];
    db.scales[patientId].push(record);

    // Atualizar ficha do paciente com dados relevantes
    if (scaleType === "fall_risk") {
      const riskMap = { baixo: "Baixo", moderado: "Moderado", alto: "Alto", muito_alto: "Muito alto" };
      db.patients[patientId].fallRisk = riskMap[scaleValue] || scaleValue;
    }
    if (scaleType === "feeding") {
      const dietMap = { normal: "Normal", assistida: "Assistida", pastosa: "Pastosa", liquida: "Líquida", sonda: "Sonda/Enteral", recusa: "Recusando" };
      db.patients[patientId].diet = dietMap[scaleValue] || scaleValue;
    }
  }

  saveDB();

  // Motor de Risco Clínico — verificação automática após escala
  let riskResult = null;
  if (patientId) {
    riskResult = checkAndAlertRisk(patientId, ctx);
    logAuditTrail(patientId, "ESCALA_CLINICA", userId, `${scale.label}: ${option?.label || scaleValue}`);
  }

  let msg = `${scale.emoji} *${scale.label}* registrada:\n\n`;
  msg += `*${option?.label || scaleValue}*\n`;
  msg += `🕐 ${timeNow()}\n`;

  if (riskResult && riskResult.level !== "stable") {
    msg += `\n${riskResult.emoji} *Risco: ${riskResult.label}* (score ${riskResult.score})`;
    msg += `\n${riskResult.trend.emoji} Tendência: ${riskResult.trend.label}`;
    msg += `\n🚨 Cadeia clínica notificada.`;
  }

  ctx.reply(msg, { parse_mode: "Markdown" });
});

// ═══════════════════════════════════════════════════════
//  INTERCORRÊNCIAS
// ═══════════════════════════════════════════════════════

bot.action("btn_incident", (ctx) => {
  ctx.answerCbQuery();

  const buttons = [];
  for (let i = 0; i < INCIDENT_TYPES.length; i += 2) {
    const row = [Markup.button.callback(`${INCIDENT_TYPES[i].emoji} ${INCIDENT_TYPES[i].label}`, `incident_${INCIDENT_TYPES[i].id}`)];
    if (INCIDENT_TYPES[i + 1]) {
      row.push(Markup.button.callback(`${INCIDENT_TYPES[i + 1].emoji} ${INCIDENT_TYPES[i + 1].label}`, `incident_${INCIDENT_TYPES[i + 1].id}`));
    }
    buttons.push(row);
  }

  ctx.reply(
    `⚠️ *Registrar Intercorrência*\n\nSelecione o tipo:`,
    { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) }
  );
});

bot.action(/^incident_(.+)$/, (ctx) => {
  const userId = uid(ctx);
  const incidentType = ctx.match[1];
  const type = INCIDENT_TYPES.find((t) => t.id === incidentType);

  ctx.answerCbQuery(`${type?.label || incidentType}`);

  if (incidentType === "outro") {
    setState(userId, "incident_details", { type: incidentType });
    return ctx.reply("Descreva a intercorrência:", { parse_mode: "Markdown" });
  }

  // Registrar intercorrência
  const record = {
    type: incidentType,
    time: timeNow(),
    date: todayKey(),
    registeredBy: userId,
    details: null,
  };

  const shift = getActiveShift(userId);
  if (shift) {
    if (!shift.incidents) shift.incidents = [];
    shift.incidents.push(record);
  }

  const patientId = getPatientId(userId);
  if (patientId) {
    if (!db.incidents[patientId]) db.incidents[patientId] = [];
    db.incidents[patientId].push(record);
  }

  saveDB();

  // Motor de Risco Clínico — verificação automática após intercorrência
  if (patientId) {
    const riskResult = checkAndAlertRisk(patientId, ctx);
    logAuditTrail(patientId, "INTERCORRENCIA", userId, type?.label || incidentType);
  }

  ctx.reply(
    `🚨 *Intercorrência registrada:*\n\n` +
    `${type?.emoji || "⚠️"} *${type?.label || incidentType}*\n` +
    `🕐 ${timeNow()}\n\n` +
    `Cadeia clínica notificada automaticamente.\n\n` +
    `Deseja adicionar detalhes?`,
    {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard([
        [Markup.button.callback("📝 Adicionar detalhes", `incident_detail_${incidentType}`)],
        [Markup.button.callback("✅ Pronto", "btn_checklist")],
      ]),
    }
  );
});

bot.action(/^incident_detail_(.+)$/, (ctx) => {
  ctx.answerCbQuery();
  setState(uid(ctx), "incident_details", { type: ctx.match[1] });
  ctx.reply("Descreva os detalhes da intercorrência:");
});

// ═══════════════════════════════════════════════════════
//  CADASTRO DE PACIENTE — CAMPOS CLÍNICOS
// ═══════════════════════════════════════════════════════

bot.action(/^mob_(.+)$/, (ctx) => {
  const userId = uid(ctx);
  const { data } = getState(userId);
  ctx.answerCbQuery();

  const mobilityMap = {
    independent: "Caminha sozinho",
    assisted: "Caminha com apoio",
    wheelchair: "Cadeira de rodas",
    bedridden: "Acamado",
  };

  data.mobility = mobilityMap[ctx.match[1]] || ctx.match[1];

  // Próximo passo: prioridade
  setState(userId, "reg_priority", data);
  ctx.reply(
    `Qual o *nível de dependência* do paciente?`,
    {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard([
        [Markup.button.callback("🔴 Alta dependência", "priority_high")],
        [Markup.button.callback("🟠 Dependência média", "priority_medium")],
        [Markup.button.callback("🟢 Independente", "priority_low")],
      ]),
    }
  );
});

bot.action(/^priority_(.+)$/, (ctx) => {
  const userId = uid(ctx);
  const { data } = getState(userId);
  ctx.answerCbQuery();

  data.priority = ctx.match[1];

  // Próximo: quarto/leito (opcional)
  setState(userId, "reg_room", data);
  ctx.reply(
    `🏥 Qual o *quarto/leito* do paciente?\n\n_(Se for cuidado domiciliar, digite "casa")_`,
    { parse_mode: "Markdown" }
  );
});

// ═══════════════════════════════════════════════════════
//  TURNO — CONFIRMAR ENCERRAMENTO
// ═══════════════════════════════════════════════════════

bot.action("confirm_end_shift", (ctx) => {
  ctx.answerCbQuery("Turno encerrado!");
  handleEndShift(ctx, uid(ctx));
});

bot.action("cancel_end_shift", (ctx) => {
  ctx.answerCbQuery("Turno continua ativo!");
  ctx.reply("Ok! Turno continua ativo. 💪\n\nUse /checklist para ver tarefas pendentes.");
});

// ═══════════════════════════════════════════════════════
//  SINAIS VITAIS — CALLBACKS
// ═══════════════════════════════════════════════════════

bot.action("vitals_force_start", (ctx) => {
  const userId = uid(ctx);
  const patientId = getPatientId(userId);
  ctx.answerCbQuery();
  setState(userId, "vitals_temp", { patientId });
  ctx.reply(
    `Ok! Digite a *temperatura corporal* em °C\n(Ex: 36.5 ou 36,5)`,
    { parse_mode: "Markdown" }
  );
});

bot.action("vitals_skip", (ctx) => {
  ctx.answerCbQuery();
  ctx.reply("Ok! Você pode registrar depois com /sinais 📊");
});

// ═══════════════════════════════════════════════════════
//  CHECKLIST — MARCAR TAREFA (EDITA A MENSAGEM!)
// ═══════════════════════════════════════════════════════

bot.action(/^task_(.+)$/, async (ctx) => {
  const userId = uid(ctx);
  const taskId = ctx.match[1];
  const shift = getActiveShift(userId);

  if (!shift) {
    return ctx.answerCbQuery("Nenhum turno ativo! Use /turno para iniciar.");
  }

  shift.completedTasks = shift.completedTasks || [];
  if (!shift.completedTasks.includes(taskId)) {
    shift.completedTasks.push(taskId);
    shift.completedTasks_times = shift.completedTasks_times || {};
    shift.completedTasks_times[taskId] = timeNow();
    saveDB();
  }

  const tasks = getChecklistTasks(shift.patientId);
  const taskObj = tasks.find((t) => t.id === taskId);
  const taskLabel = taskObj ? taskObj.label : taskId;

  await ctx.answerCbQuery(`✅ ${taskLabel} — feito!`);

  const { text, keyboard } = buildChecklistMessage(shift);

  try {
    if (keyboard) {
      await ctx.editMessageText(text, { parse_mode: "Markdown", ...keyboard });
    } else {
      await ctx.editMessageText(text, { parse_mode: "Markdown" });
    }
  } catch (err) {
    if (keyboard) {
      ctx.reply(text, { parse_mode: "Markdown", ...keyboard });
    } else {
      ctx.reply(text, { parse_mode: "Markdown" });
    }
  }
});

// ═══════════════════════════════════════════════════════
//  CALLBACKS DE ALTA HOSPITALAR
// ═══════════════════════════════════════════════════════

bot.action(/^discharge_start_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const patient = db.patients[patientId];
  if (!patient) return ctx.answerCbQuery("Paciente não encontrado.");

  // Criar registro de alta
  db.discharges[patientId] = {
    active: true,
    dischargeTimestamp: Date.now(),
    dischargeDate: todayKey(),
    dischargeTime: timeNow(),
    completedChecklist: [],
    followupsCompleted: [],
    postAlerts: [],
    registeredBy: uid(ctx),
  };
  saveDB();

  logAuditTrail(patientId, "ALTA_INICIADA", uid(ctx), `Protocolo pós-alta 72h iniciado`);

  // Notificar cadeia clínica
  notifyClinicalChain(patientId,
    `🏥 *ALTA HOSPITALAR — ${patient.name}*\n\n` +
    `Protocolo pós-alta 72h iniciado.\n` +
    `O sistema enviará lembretes de acompanhamento em:\n` +
    `  • 6h, 12h, 24h, 48h e 72h\n\n` +
    `⏰ ${now()}`,
    "all"
  );

  ctx.answerCbQuery("✅ Protocolo de alta iniciado!");
  return showDischargeStatus(ctx, patientId);
});

bot.action("discharge_cancel", (ctx) => {
  ctx.answerCbQuery("Cancelado.");
  return ctx.reply("❌ Protocolo de alta cancelado.");
});

bot.action(/^discharge_checklist_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const d = db.discharges[patientId];
  if (!d) return ctx.answerCbQuery("Sem protocolo de alta ativo.");

  const completed = d.completedChecklist || [];
  const pending = DISCHARGE_CHECKLIST.filter(item => !completed.includes(item.id));

  if (pending.length === 0) {
    return ctx.answerCbQuery("✅ Checklist completo!");
  }

  const buttons = pending.map(item =>
    [Markup.button.callback(`${item.emoji} ${item.label}`, `dcheck_${patientId}_${item.id}`)]
  );
  buttons.push([Markup.button.callback("⬅️ Voltar", `discharge_status_${patientId}`)]);

  ctx.answerCbQuery();
  return ctx.reply(
    `📝 *Checklist de Alta*\n\nMarque os itens concluídos:`,
    { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) }
  );
});

bot.action(/^dcheck_(.+)_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const checkId = ctx.match[2];
  const d = db.discharges[patientId];
  if (!d) return ctx.answerCbQuery("Sem protocolo de alta ativo.");

  if (!d.completedChecklist) d.completedChecklist = [];
  if (!d.completedChecklist.includes(checkId)) {
    d.completedChecklist.push(checkId);
    saveDB();
  }

  const item = DISCHARGE_CHECKLIST.find(i => i.id === checkId);
  ctx.answerCbQuery(`✅ ${item?.label || checkId}`);

  // Mostrar checklist atualizado
  const completed = d.completedChecklist;
  const pending = DISCHARGE_CHECKLIST.filter(i => !completed.includes(i.id));

  if (pending.length === 0) {
    return ctx.editMessageText(
      `✅ *Checklist de alta completo!*\n\nTodos os ${DISCHARGE_CHECKLIST.length} itens foram verificados.`,
      { parse_mode: "Markdown" }
    ).catch(() => {});
  }

  const buttons = pending.map(i =>
    [Markup.button.callback(`${i.emoji} ${i.label}`, `dcheck_${patientId}_${i.id}`)]
  );
  buttons.push([Markup.button.callback("⬅️ Voltar", `discharge_status_${patientId}`)]);

  return ctx.editMessageText(
    `📝 *Checklist de Alta* (${completed.length}/${DISCHARGE_CHECKLIST.length})\n\nMarque os itens concluídos:`,
    { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) }
  ).catch(() => {});
});

bot.action(/^discharge_followup_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const d = db.discharges[patientId];
  if (!d) return ctx.answerCbQuery("Sem protocolo de alta ativo.");

  const hoursElapsed = Math.floor((Date.now() - d.dischargeTimestamp) / 3600000);
  const completed = d.followupsCompleted || [];
  const pending = DISCHARGE_FOLLOWUP_SCHEDULE.filter(fu => hoursElapsed >= fu.hours && !completed.includes(fu.label));

  if (pending.length === 0) {
    return ctx.answerCbQuery("Nenhum acompanhamento pendente agora.");
  }

  const fu = pending[0]; // Próximo follow-up pendente
  const checkButtons = fu.checkItems.map(item =>
    [Markup.button.callback(`✅ ${item.replace(/_/g, " ")}`, `dfollowup_${patientId}_${encodeURIComponent(fu.label)}_${item}`)]
  );
  checkButtons.push([Markup.button.callback("✅ Tudo OK — Concluir acompanhamento", `dfollowup_done_${patientId}_${encodeURIComponent(fu.label)}`)]);

  ctx.answerCbQuery();
  return ctx.reply(
    `🩺 *Acompanhamento: ${fu.label}*\n\nVerifique os itens:`,
    { parse_mode: "Markdown", ...Markup.inlineKeyboard(checkButtons) }
  );
});

bot.action(/^dfollowup_done_(.+)_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const fuLabel = decodeURIComponent(ctx.match[2]);
  const d = db.discharges[patientId];
  if (!d) return ctx.answerCbQuery("Sem protocolo de alta ativo.");

  if (!d.followupsCompleted) d.followupsCompleted = [];
  if (!d.followupsCompleted.includes(fuLabel)) {
    d.followupsCompleted.push(fuLabel);
    saveDB();
  }

  logAuditTrail(patientId, "FOLLOWUP_CONCLUIDO", uid(ctx), fuLabel);

  ctx.answerCbQuery(`✅ ${fuLabel} concluído!`);
  return ctx.editMessageText(
    `✅ *${fuLabel}* — Acompanhamento concluído!\n\nUse /alta para ver o status completo.`,
    { parse_mode: "Markdown" }
  ).catch(() => {});
});

bot.action(/^dfollowup_(.+)_(.+)_(.+)$/, (ctx) => {
  // Item individual do follow-up (informativo)
  ctx.answerCbQuery("✅ Verificado!");
});

bot.action(/^discharge_status_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  ctx.answerCbQuery();
  return showDischargeStatus(ctx, patientId);
});

bot.action(/^discharge_close_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const d = db.discharges[patientId];
  const patient = db.patients[patientId];
  if (!d || !patient) return ctx.answerCbQuery("Erro.");

  d.active = false;
  d.closedAt = now();
  d.closedBy = uid(ctx);
  saveDB();

  logAuditTrail(patientId, "ALTA_ENCERRADA", uid(ctx), "Protocolo pós-alta 72h concluído");

  notifyClinicalChain(patientId,
    `✅ *PROTOCOLO CONCLUÍDO — ${patient.name}*\n\n` +
    `Acompanhamento pós-alta de 72h finalizado com sucesso.\n` +
    `⏰ ${now()}`,
    "all"
  );

  ctx.answerCbQuery("✅ Protocolo encerrado!");
  return ctx.reply(
    `✅ *Protocolo de alta encerrado — ${patient.name}*\n\n` +
    `O acompanhamento pós-alta de 72h foi concluído.\n` +
    `Paciente liberado do monitoramento intensivo.`,
    { parse_mode: "Markdown" }
  );
});

// ═══════════════════════════════════════════════════════
//  FUNÇÕES PRINCIPAIS
// ═══════════════════════════════════════════════════════

function handleStartShift(ctx, userId) {
  const existing = getActiveShift(userId);

  if (existing) {
    const dur = formatDuration(Date.now() - existing.startTimestamp);
    return ctx.reply(
      `Você já tem um turno ativo há *${dur}*.\n\nDeseja encerrar?`,
      {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard([
          [Markup.button.callback("🔴 Encerrar turno", "confirm_end_shift")],
          [Markup.button.callback("↩️ Continuar", "cancel_end_shift")],
        ]),
      }
    );
  }

  const patientId = getPatientId(userId);
  if (!patientId) {
    return ctx.reply("Cadastre um paciente primeiro. Use /start");
  }

  const patient = db.patients[patientId];
  if (!patient) {
    return ctx.reply("Paciente não encontrado. Use /start para recadastrar.");
  }

  // Encerrar turnos antigos
  Object.values(db.shifts).forEach((s) => {
    if (s.caregiverId === userId && s.active) {
      s.active = false;
      s.endedAt = now();
      s.endTimestamp = Date.now();
    }
  });

  const shiftId = `shift_${Date.now()}`;
  db.shifts[shiftId] = {
    caregiverId: userId,
    patientId: patientId,
    patientName: patient.name,
    startedAt: now(),
    startTimestamp: Date.now(),
    active: true,
    completedTasks: [],
    completedTasks_times: {},
    observations: [],
    vitals: [],
    scales: [],
    incidents: [],
    humor: null,
  };
  saveDB();

  // Mostrar ficha clínica ao iniciar turno
  const card = buildPatientCard(patient, patientId);

  ctx.reply(
    `🟢 *Turno iniciado!*\n\n` +
    card + `\n\n` +
    `🕐 Início: ${timeNow()}\n\n` +
    `Vou enviar o checklist agora.`,
    { parse_mode: "Markdown" }
  );

  setTimeout(() => handleChecklist(ctx, userId), 1000);
}

function handleEndShift(ctx, userId) {
  const shift = getActiveShift(userId);
  if (!shift) return ctx.reply("Nenhum turno ativo.");

  shift.active = false;
  shift.endedAt = now();
  shift.endTimestamp = Date.now();
  saveDB();

  const report = generateReport(shift);
  const handoff = generateShiftHandoff(shift);

  // Enviar relatório completo para o cuidador
  ctx.reply(
    `🔴 *Turno encerrado!*\n\n` + report,
    { parse_mode: "Markdown" }
  );

  // Enviar passagem de plantão para toda a cadeia clínica
  notifyFamily(shift.patientId,
    `📋 *Relatório do Turno — ${shift.patientName}*\n\n` + report
  );

  // Enviar passagem de plantão estruturada separadamente
  notifyClinicalChain(shift.patientId,
    handoff,
    "all"
  );

  db.checklists[`report_${Date.now()}`] = {
    shiftId: Object.keys(db.shifts).find((k) => db.shifts[k] === shift),
    patientId: shift.patientId,
    report,
    handoff,
    createdAt: now(),
  };
  saveDB();
}

// ═══════════════════════════════════════════════════════
//  PASSAGEM DE PLANTÃO ESTRUTURADA
// ═══════════════════════════════════════════════════════

function generateShiftHandoff(shift) {
  const patient = db.patients[shift.patientId];
  const caregiver = db.caregivers[shift.caregiverId];
  const tasks = getChecklistTasks(shift.patientId);
  const done = shift.completedTasks || [];
  const pending = tasks.filter((t) => !done.includes(t.id));
  const risk = calculateClinicalRisk(shift.patientId);
  const duration = shift.endTimestamp
    ? formatDuration(shift.endTimestamp - shift.startTimestamp)
    : formatDuration(Date.now() - shift.startTimestamp);

  let h = `━━━━━━━━━━━━━━━━━━━━━\n`;
  h += `📝 *PASSAGEM DE PLANTÃO*\n`;
  h += `━━━━━━━━━━━━━━━━━━━━━\n\n`;

  // Identificação
  h += `👤 *Paciente:* ${patient?.name || "N/A"}`;
  if (patient?.room) h += ` — Q.${patient.room}`;
  h += `\n`;
  h += `${risk.emoji} *Status:* ${risk.label}`;
  if (risk.reasons.length > 0) h += ` (${risk.reasons.slice(0, 3).join(", ")})`;
  h += `\n`;
  h += `👩‍⚕️ *Cuidador(a):* ${caregiver?.name || "N/A"}\n`;
  h += `🕒 *Período:* ${shift.startedAt} — ${shift.endedAt}\n`;
  h += `⏱️ *Duração:* ${duration}\n\n`;

  // Resumo de cuidados realizados
  h += `✅ *Cuidados realizados:* ${done.length}/${tasks.length}\n`;
  done.forEach((taskId) => {
    const task = tasks.find((t) => t.id === taskId);
    if (task) h += `   ✅ ${task.label}\n`;
  });
  h += `\n`;

  // Pendências
  if (pending.length > 0) {
    h += `❌ *Pendências para próximo turno:* ${pending.length}\n`;
    pending.forEach((t) => {
      h += `   ❌ ${t.label}\n`;
    });
    h += `\n`;
  } else {
    h += `✅ *Todas as tarefas concluídas!*\n\n`;
  }

  // Sinais vitais do turno
  if (shift.vitals && shift.vitals.length > 0) {
    h += `📊 *Sinais Vitais:*\n`;
    const lastVital = shift.vitals[shift.vitals.length - 1];
    h += `   🌡️ Temp: ${lastVital.temperatura}°C ${vitalStatus("temperatura", lastVital.temperatura)}\n`;
    h += `   💨 SpO2: ${lastVital.saturacao}% ${vitalStatus("saturacao", lastVital.saturacao)}\n`;
    h += `   🩺 PA: ${lastVital.pressao_sis}/${lastVital.pressao_dia} ${isOutOfRange("pressao_sis", lastVital.pressao_sis) || isOutOfRange("pressao_dia", lastVital.pressao_dia) ? "⚠️" : "✅"}\n`;
    h += `   ❤️ FC: ${lastVital.freq_cardiaca}bpm ${vitalStatus("freq_cardiaca", lastVital.freq_cardiaca)}\n\n`;
  }

  // Escalas clínicas
  if (shift.scales && shift.scales.length > 0) {
    h += `📏 *Escalas Clínicas:*\n`;
    shift.scales.forEach((s) => {
      const scale = CLINICAL_SCALES[s.type];
      h += `   ${scale?.emoji || "📏"} ${scale?.label || s.type}: *${s.value}*\n`;
    });
    h += `\n`;
  }

  // Intercorrências
  if (shift.incidents && shift.incidents.length > 0) {
    h += `🚨 *Intercorrências:* ${shift.incidents.length}\n`;
    shift.incidents.forEach((inc) => {
      const type = INCIDENT_TYPES.find((t) => t.id === inc.type);
      h += `   ${type?.emoji || "⚠️"} ${type?.label || inc.type}`;
      if (inc.details) h += ` — ${inc.details}`;
      h += `\n`;
    });
    h += `\n`;
  }

  // Alertas gerados
  const shiftAlerts = db.alerts.filter((a) => a.patientId === shift.patientId && a.date === todayKey());
  if (shiftAlerts.length > 0) {
    h += `🚨 *Alertas gerados:* ${shiftAlerts.length}\n`;
    shiftAlerts.slice(-5).forEach((a) => {
      h += `   ⚠️ ${a.message.substring(0, 60)}\n`;
    });
    h += `\n`;
  }

  // Observações
  if (shift.observations && shift.observations.length > 0) {
    h += `📝 *Observações clínicas:*\n`;
    shift.observations.forEach((o) => {
      h += `   • ${o.text}\n`;
    });
    h += `\n`;
  }

  // Humor
  if (shift.humor) {
    h += `🧠 *Humor/Estado emocional:* ${shift.humor}\n\n`;
  }

  h += `━━━━━━━━━━━━━━━━━━━━━\n`;
  h += `_Passagem de plantão — BazeX Care_`;
  return h;
}

function handleChecklist(ctx, userId) {
  const shift = getActiveShift(userId);
  if (!shift) {
    return ctx.reply(
      "Nenhum turno ativo. Inicie um turno primeiro:",
      Markup.inlineKeyboard([[Markup.button.callback("▶️ Iniciar turno", "btn_start_shift")]])
    );
  }

  const { text, keyboard } = buildChecklistMessage(shift);
  if (keyboard) {
    ctx.reply(text, { parse_mode: "Markdown", ...keyboard });
  } else {
    ctx.reply(text, { parse_mode: "Markdown" });
  }
}

function handleVitalsStart(ctx, userId) {
  const patientId = getPatientId(userId);
  if (!patientId) {
    return ctx.reply("Vincule-se a um paciente primeiro. Use /start");
  }

  const patient = db.patients[patientId];
  const period = getVitalPeriod();

  const todayVitals = (db.vitals[patientId] || []).filter(
    (v) => v.date === todayKey() && v.period === period
  );

  if (todayVitals.length > 0) {
    const last = todayVitals[todayVitals.length - 1];
    return ctx.reply(
      `Sinais vitais já registrados (${period}):\n\n` +
      `🌡️ ${last.temperatura}°C | 💨 ${last.saturacao}% | 🩺 ${last.pressao_sis}/${last.pressao_dia} | ❤️ ${last.freq_cardiaca} bpm\n\n` +
      `Deseja registrar novamente?`,
      Markup.inlineKeyboard([
        [Markup.button.callback("✅ Sim, registrar novamente", "vitals_force_start")],
        [Markup.button.callback("❌ Manter registro atual", "vitals_skip")],
      ])
    );
  }

  setState(userId, "vitals_temp", { patientId });
  ctx.reply(
    `📊 *Sinais Vitais — ${patient.name}*\n` +
    `Período: *${period}*\n\n` +
    `Digite a *temperatura corporal* em °C\n(Ex: 36.5 ou 36,5)`,
    { parse_mode: "Markdown" }
  );
}

function handleHistory(ctx, userId) {
  const patientId = getPatientId(userId);
  if (!patientId) {
    return ctx.reply("Nenhum paciente vinculado. Use /start ou /vincular CODIGO");
  }

  const patient = db.patients[patientId];
  const vitals = db.vitals[patientId] || [];

  if (vitals.length === 0) {
    return ctx.reply("Nenhum registro de sinais vitais ainda. Use /sinais para registrar.");
  }

  const last21 = vitals.slice(-21);
  let msg = `📊 *Histórico — ${patient.name}*\n\n`;

  const byDate = {};
  last21.forEach((v) => {
    if (!byDate[v.date]) byDate[v.date] = [];
    byDate[v.date].push(v);
  });

  const dates = Object.keys(byDate).sort().reverse();

  dates.forEach((date) => {
    msg += `📅 *${date.replace(/-/g, "/")}*\n`;
    byDate[date].forEach((v) => {
      msg += `  _${v.period}_: `;
      msg += `🌡️${v.temperatura}°C${vitalStatus("temperatura", v.temperatura)} `;
      msg += `💨${v.saturacao}%${vitalStatus("saturacao", v.saturacao)} `;
      msg += `🩺${v.pressao_sis}/${v.pressao_dia}${isOutOfRange("pressao_sis", v.pressao_sis) || isOutOfRange("pressao_dia", v.pressao_dia) ? "⚠️" : "✅"} `;
      msg += `❤️${v.freq_cardiaca}bpm${vitalStatus("freq_cardiaca", v.freq_cardiaca)}\n`;
    });
    msg += `\n`;
  });

  // Escalas clínicas recentes
  const scales = db.scales[patientId] || [];
  if (scales.length > 0) {
    const recentScales = scales.slice(-8);
    msg += `📏 *Escalas Clínicas Recentes:*\n`;
    recentScales.forEach((s) => {
      const scale = CLINICAL_SCALES[s.type];
      msg += `  ${scale?.emoji || "📏"} ${scale?.label || s.type}: ${s.value} _(${s.date} ${s.time})_\n`;
    });
    msg += `\n`;
  }

  // Intercorrências recentes
  const incidents = db.incidents[patientId] || [];
  if (incidents.length > 0) {
    const recentInc = incidents.slice(-5);
    msg += `🚨 *Intercorrências Recentes:*\n`;
    recentInc.forEach((inc) => {
      const type = INCIDENT_TYPES.find((t) => t.id === inc.type);
      msg += `  ${type?.emoji || "⚠️"} ${type?.label || inc.type} _(${inc.date} ${inc.time})_\n`;
      if (inc.details) msg += `     ↳ ${inc.details}\n`;
    });
    msg += `\n`;
  }

  msg += `━━━━━━━━━━━━━━━━━━━━━\n`;
  msg += `*Faixas normais:*\n`;
  msg += `🌡️ 35,5-37,5°C | 💨 ≥92% | 🩺 90-140/60-90 | ❤️ 50-100 bpm\n`;
  msg += `⚠️ = fora da faixa normal`;

  ctx.reply(msg, { parse_mode: "Markdown" });
}

function handleReport(ctx, userId) {
  const patientId = getPatientId(userId);
  if (!patientId) {
    return ctx.reply("Nenhum paciente vinculado. Use /start ou /vincular CODIGO");
  }

  const reports = Object.values(db.checklists)
    .filter((r) => r.patientId === patientId)
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  if (reports.length === 0) {
    const active = getActiveShiftForPatient(patientId);
    if (active) {
      return ctx.reply("Turno em andamento. O relatório será gerado quando encerrar.");
    }
    return ctx.reply("Nenhum relatório disponível. O primeiro será gerado ao encerrar um turno.");
  }

  ctx.reply(`📋 *Último Relatório*\n\n${reports[0].report}`, { parse_mode: "Markdown" });
}

// ═══════════════════════════════════════════════════════
//  PROCESSAMENTO DE TEXTO (MÁQUINA DE ESTADOS)
// ═══════════════════════════════════════════════════════

bot.on("text", (ctx) => {
  const userId = uid(ctx);
  const text = ctx.message.text.trim();
  const { step, data } = getState(userId);

  // ─── Comandos ───
  if (text.startsWith("/vincular")) {
    const code = text.split(" ")[1];
    if (!code) return ctx.reply("Use: `/vincular CODIGO`\n\nPeça o código ao cuidador.", { parse_mode: "Markdown" });
    const patient = Object.values(db.patients).find((p) => p.code === code.toUpperCase());
    if (!patient) return ctx.reply("Código não encontrado. Verifique com o cuidador.");
    patient.familyIds = patient.familyIds || [];
    if (!patient.familyIds.includes(userId)) patient.familyIds.push(userId);
    if (db.families[userId]) db.families[userId].patientCode = code.toUpperCase();
    saveDB();
    return ctx.reply(
      `✅ Vinculado ao paciente *${patient.name}*!\n\n` +
      `Você receberá:\n` +
      `• Relatórios automáticos do turno\n` +
      `• Alertas de sinais vitais fora do normal\n` +
      `• Alertas de intercorrências\n` +
      `• Alertas de escalas clínicas críticas\n\n` +
      `/relatorio — Ver último relatório\n` +
      `/historico — Ver sinais vitais`,
      { parse_mode: "Markdown" }
    );
  }

  if (text === "/turno") return handleStartShift(ctx, userId);
  if (text === "/checklist") return handleChecklist(ctx, userId);
  if (text === "/sinais") return handleVitalsStart(ctx, userId);
  if (text === "/historico") return handleHistory(ctx, userId);
  if (text === "/relatorio") return handleReport(ctx, userId);
  if (text === "/plantao") return handleSwitchPatient(ctx, userId);
  if (text === "/menu") return showCaregiverMenu(ctx, userId);
  if (text === "/painel") return handlePanel(ctx, userId);

  if (text === "/timeline") {
    const patientId = getPatientId(userId);
    if (!patientId) return ctx.reply("Nenhum paciente ativo. Use /start");
    const patient = db.patients[patientId];
    const events = buildClinicalTimeline(patientId, 48);
    const timeline = formatTimeline(events, 20);
    logAuditTrail(patientId, "CONSULTA_TIMELINE", userId);
    return ctx.reply(
      `📊 *Linha do Tempo Clínica*\n` +
      `👤 ${patient?.name || "Paciente"} (últimas 48h)\n` +
      `━━━━━━━━━━━━━━━━━━━━━\n\n` +
      timeline + `\n\n━━━━━━━━━━━━━━━━━━━━━\n` +
      `_${events.length} eventos registrados_`,
      { parse_mode: "Markdown" }
    );
  }

  if (text === "/risco") {
    const patientId = getPatientId(userId);
    if (!patientId) return ctx.reply("Nenhum paciente ativo. Use /start");
    const patient = db.patients[patientId];
    const risk = calculateClinicalRisk(patientId);
    logAuditTrail(patientId, "CONSULTA_RISCO", userId);
    let msg = `━━━━━━━━━━━━━━━━━━━━━\n`;
    msg += `🏥 *Análise de Risco Clínico*\n`;
    msg += `👤 ${patient?.name || "Paciente"}\n`;
    msg += `━━━━━━━━━━━━━━━━━━━━━\n\n`;
    msg += `${risk.emoji} *Nível: ${risk.label}* (score ${risk.score})\n`;
    msg += `${risk.trend.emoji} *Tendência: ${risk.trend.label}*\n\n`;
    if (risk.reasons.length > 0) {
      msg += `*Fatores de risco:*\n`;
      risk.reasons.forEach(r => { msg += `  • ${r}\n`; });
      msg += `\n`;
    }
    if (risk.trend.details && risk.trend.details.length > 0) {
      msg += `*Detalhes da tendência:*\n`;
      risk.trend.details.forEach(d => { msg += `  • ${d}\n`; });
      msg += `\n`;
    }
    if (risk.protocol) {
      msg += `*${risk.protocol.label}:*\n`;
      risk.protocol.actions.forEach(a => { msg += `  ▸ ${a}\n`; });
      msg += `\n`;
    }
    msg += `━━━━━━━━━━━━━━━━━━━━━\n`;
    msg += `_Motor BazeX Care — ${now()}_`;
    return ctx.reply(msg, { parse_mode: "Markdown" });
  }

  if (text === "/ficha") {
    const patientId = getPatientId(userId);
    if (!patientId || !db.patients[patientId]) return ctx.reply("Nenhum paciente ativo. Use /start");
    return ctx.reply(buildPatientCard(db.patients[patientId], patientId), { parse_mode: "Markdown" });
  }

  if (text === "/escalas") {
    return ctx.reply(
      `📏 *Escalas Clínicas*\n\nSelecione a escala:`,
      {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard([
          [Markup.button.callback("😣 Dor (0-10)", "scale_pain")],
          [Markup.button.callback("🧠 Confusão Mental", "scale_confusion")],
          [Markup.button.callback("⚠️ Risco de Queda", "scale_fall_risk")],
          [Markup.button.callback("🍽️ Alimentação", "scale_feeding")],
        ]),
      }
    );
  }

  if (text === "/intercorrencia") {
    const buttons = [];
    for (let i = 0; i < INCIDENT_TYPES.length; i += 2) {
      const row = [Markup.button.callback(`${INCIDENT_TYPES[i].emoji} ${INCIDENT_TYPES[i].label}`, `incident_${INCIDENT_TYPES[i].id}`)];
      if (INCIDENT_TYPES[i + 1]) {
        row.push(Markup.button.callback(`${INCIDENT_TYPES[i + 1].emoji} ${INCIDENT_TYPES[i + 1].label}`, `incident_${INCIDENT_TYPES[i + 1].id}`));
      }
      buttons.push(row);
    }
    return ctx.reply(
      `⚠️ *Registrar Intercorrência*\n\nSelecione:`,
      { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) }
    );
  }

  if (text === "/alta") {
    return handleDischarge(ctx, userId);
  }

  if (text === "/editar") {
    return handleEditPatient(ctx, userId);
  }

  if (text === "/ajuda" || text === "/help") {
    return ctx.reply(
      `*Comandos disponíveis:*\n\n` +
      `👩‍⚕️ *Cuidador(a):*\n` +
      `/turno — Iniciar ou encerrar turno\n` +
      `/checklist — Checklist do turno\n` +
      `/sinais — Registrar sinais vitais\n` +
      `/escalas — Escalas clínicas\n` +
      `/intercorrencia — Registrar intercorrência\n` +
      `/risco — Análise de risco clínico\n` +
      `/timeline — Linha do tempo clínica\n` +
      `/alta — Protocolo de alta hospitalar\n` +
      `/editar — Editar ficha do paciente\n` +
      `/ficha — Ficha clínica do paciente\n` +
      `/plantao — Trocar paciente ativo\n` +
      `/historico — Histórico completo\n` +
      `/relatorio — Último relatório\n` +
      `/menu — Menu principal\n\n` +
      `🩺 *Enfermeiro(a) / 🏥 Supervisor(a):*\n` +
      `/painel — Painel de supervisão (todos os pacientes)\n` +
      `/risco — Análise de risco do paciente\n` +
      `/timeline — Linha do tempo clínica\n` +
      `/alta — Protocolo de alta hospitalar\n` +
      `/vincular CODIGO — Vincular a paciente\n` +
      `/historico — Sinais vitais\n` +
      `/relatorio — Último relatório\n\n` +
      `👨‍👩‍👧 *Família:*\n` +
      `/vincular CODIGO — Vincular ao paciente\n` +
      `/relatorio — Último relatório\n` +
      `/historico — Sinais vitais\n\n` +
      `⚙️ *Geral:*\n` +
      `/start — Recomeçar\n` +
      `/ajuda — Ver comandos`,
      { parse_mode: "Markdown" }
    );
  }

  // ─── Máquina de estados ───
  switch (step) {

    // ── Cadastro do paciente ──
    case "reg_name":
      data.name = text;
      setState(userId, "reg_age", data);
      return ctx.reply(`*${text}* — anotado!\n\nQual a *idade* do paciente?`, { parse_mode: "Markdown" });

    case "reg_age":
      data.age = text;
      setState(userId, "reg_conditions", data);
      return ctx.reply(
        `${text} anos. Ok!\n\n` +
        `Quais as *condições de saúde / diagnóstico*?\n(Ex: Alzheimer, pós-AVC, diabetes, hipertensão...)`,
        { parse_mode: "Markdown" }
      );

    case "reg_conditions":
      data.conditions = text;
      setState(userId, "reg_meds", data);
      return ctx.reply(
        `Entendi. Agora as *medicações e horários*:\n\n` +
        `Exemplo:\n` +
        `Losartana 50mg — 8h e 20h\n` +
        `Metformina 500mg — 12h\n\n` +
        `_(Se não souber agora, digite "depois")_`,
        { parse_mode: "Markdown" }
      );

    case "reg_meds":
      data.meds = text;
      setState(userId, "reg_critical_med", data);
      return ctx.reply(
        `Tem alguma *medicação crítica*?\n(Ex: anticoagulante, insulina, quimioterápico)\n\n_(Se não, digite "não")_`,
        { parse_mode: "Markdown" }
      );

    case "reg_critical_med":
      data.criticalMed = text.toLowerCase() === "não" || text.toLowerCase() === "nao" ? null : text;
      setState(userId, "reg_mobility", data);
      return ctx.reply(
        `Qual o *nível de mobilidade*?`,
        {
          parse_mode: "Markdown",
          ...Markup.inlineKeyboard([
            [Markup.button.callback("🚶 Caminha sozinho", "mob_independent")],
            [Markup.button.callback("🦯 Caminha com apoio", "mob_assisted")],
            [Markup.button.callback("🧑‍🦽 Cadeira de rodas", "mob_wheelchair")],
            [Markup.button.callback("🛏️ Acamado", "mob_bedridden")],
          ]),
        }
      );

    // ── Quarto/leito ──
    case "reg_room":
      data.room = text.toLowerCase() === "casa" ? null : text;
      // Criar paciente
      finishPatientRegistration(ctx, userId, data);
      return;

    // ── Detalhes de intercorrência ──
    case "incident_details": {
      const patientId = getPatientId(userId);
      const shift = getActiveShift(userId);

      const record = {
        type: data.type,
        time: timeNow(),
        date: todayKey(),
        registeredBy: userId,
        details: text,
      };

      if (shift) {
        if (!shift.incidents) shift.incidents = [];
        // Se a última intercorrência é do mesmo tipo e sem detalhes, atualizar
        const lastInc = shift.incidents[shift.incidents.length - 1];
        if (lastInc && lastInc.type === data.type && !lastInc.details) {
          lastInc.details = text;
        } else {
          shift.incidents.push(record);
        }
      }

      if (patientId) {
        if (!db.incidents[patientId]) db.incidents[patientId] = [];
        const lastInc = db.incidents[patientId][db.incidents[patientId].length - 1];
        if (lastInc && lastInc.type === data.type && !lastInc.details) {
          lastInc.details = text;
        } else {
          db.incidents[patientId].push(record);
        }

        const patient = db.patients[patientId];
        const type = INCIDENT_TYPES.find((t) => t.id === data.type);
        notifyFamily(patientId,
          `🚨 *INTERCORRÊNCIA — ${patient?.name || "Paciente"}*\n\n` +
          `${type?.emoji || "⚠️"} *${type?.label || data.type}*\n` +
          `📝 ${text}\n` +
          `🕐 ${timeNow()}`
        );
      }

      saveDB();
      clearState(userId);
      return ctx.reply(`📝 Detalhes registrados. Família notificada.`);
    }

    // ── Sinais vitais ──
    case "vitals_temp": {
      const temp = parseFloat(text.replace(",", "."));
      if (isNaN(temp) || temp < 30 || temp > 45) {
        return ctx.reply("Valor inválido. Digite a temperatura em °C (ex: 36.5)");
      }
      data.temperatura = temp;
      if (isOutOfRange("temperatura", temp)) {
        ctx.reply(`⚠️ *Temperatura ${temp > 37.5 ? "ALTA" : "BAIXA"}:* ${temp}°C (normal: 35,5-37,5°C)`, { parse_mode: "Markdown" });
      }
      setState(userId, "vitals_sat", data);
      return ctx.reply(
        `🌡️ Temperatura: *${temp}°C* ${vitalStatus("temperatura", temp)}\n\n` +
        `Agora a *saturação de oxigênio (SpO2)* em %\n(Ex: 97)`,
        { parse_mode: "Markdown" }
      );
    }

    case "vitals_sat": {
      const sat = parseInt(text);
      if (isNaN(sat) || sat < 50 || sat > 100) {
        return ctx.reply("Valor inválido. Digite a saturação em % (ex: 97)");
      }
      data.saturacao = sat;
      if (isOutOfRange("saturacao", sat)) {
        ctx.reply(`⚠️ *Saturação BAIXA:* ${sat}% (normal: acima de 92%)`, { parse_mode: "Markdown" });
      }
      setState(userId, "vitals_bp", data);
      return ctx.reply(
        `💨 Saturação: *${sat}%* ${vitalStatus("saturacao", sat)}\n\n` +
        `Agora a *pressão arterial*\nFormato: sistólica/diastólica (Ex: 120/80)`,
        { parse_mode: "Markdown" }
      );
    }

    case "vitals_bp": {
      const parts = text.split(/[\/x]/);
      const sis = parseInt(parts[0]);
      const dia = parseInt(parts[1]);
      if (isNaN(sis) || isNaN(dia) || sis < 50 || sis > 250 || dia < 30 || dia > 150) {
        return ctx.reply("Valor inválido. Use o formato: 120/80");
      }
      data.pressao_sis = sis;
      data.pressao_dia = dia;
      const bpAlert = isOutOfRange("pressao_sis", sis) || isOutOfRange("pressao_dia", dia);
      if (bpAlert) {
        ctx.reply(`⚠️ *Pressão fora da faixa:* ${sis}/${dia} mmHg (normal: 90-140/60-90)`, { parse_mode: "Markdown" });
      }
      setState(userId, "vitals_hr", data);
      return ctx.reply(
        `🩺 Pressão: *${sis}/${dia} mmHg* ${bpAlert ? "⚠️" : "✅"}\n\n` +
        `Agora a *frequência cardíaca* em bpm\n(Ex: 72)`,
        { parse_mode: "Markdown" }
      );
    }

    case "vitals_hr": {
      const fc = parseInt(text);
      if (isNaN(fc) || fc < 20 || fc > 250) {
        return ctx.reply("Valor inválido. Digite a frequência cardíaca em bpm (ex: 72)");
      }
      data.freq_cardiaca = fc;

      const patientId = data.patientId;
      const period = getVitalPeriod();
      const record = {
        temperatura: data.temperatura,
        saturacao: data.saturacao,
        pressao_sis: data.pressao_sis,
        pressao_dia: data.pressao_dia,
        freq_cardiaca: fc,
        period,
        registeredAt: now(),
        registeredBy: userId,
        date: todayKey(),
      };

      if (!db.vitals[patientId]) db.vitals[patientId] = [];
      db.vitals[patientId].push(record);

      const shift = getActiveShift(userId);
      if (shift) {
        if (!shift.vitals) shift.vitals = [];
        shift.vitals.push(record);
      }

      saveDB();
      clearState(userId);

      // Motor de Risco Clínico — verificação automática após registro
      const risk = checkAndAlertRisk(patientId, ctx);
      logAuditTrail(patientId, "SINAIS_VITAIS", userId, `T:${data.temperatura} SpO2:${data.saturacao} PA:${data.pressao_sis}/${data.pressao_dia} FC:${fc}`);

      const alerts = [];
      if (isOutOfRange("temperatura", data.temperatura)) alerts.push(`🌡️ Temperatura: ${data.temperatura}°C`);
      if (isOutOfRange("saturacao", data.saturacao)) alerts.push(`💨 Saturação: ${data.saturacao}%`);
      if (isOutOfRange("pressao_sis", data.pressao_sis) || isOutOfRange("pressao_dia", data.pressao_dia)) {
        alerts.push(`🩺 Pressão: ${data.pressao_sis}/${data.pressao_dia} mmHg`);
      }
      if (isOutOfRange("freq_cardiaca", fc)) alerts.push(`❤️ FC: ${fc} bpm`);

      const patient = db.patients[patientId];
      let summary = `━━━━━━━━━━━━━━━━━━━━━\n`;
      summary += `📊 *Sinais Vitais — ${patient?.name || "Paciente"}*\n`;
      summary += `🕐 ${timeNow()} (${period})\n`;
      summary += `━━━━━━━━━━━━━━━━━━━━━\n\n`;
      summary += `🌡️ Temperatura: *${data.temperatura}°C* ${vitalStatus("temperatura", data.temperatura)}\n`;
      summary += `💨 Saturação: *${data.saturacao}%* ${vitalStatus("saturacao", data.saturacao)}\n`;
      summary += `🩺 Pressão: *${data.pressao_sis}/${data.pressao_dia} mmHg* ${isOutOfRange("pressao_sis", data.pressao_sis) || isOutOfRange("pressao_dia", data.pressao_dia) ? "⚠️" : "✅"}\n`;
      summary += `❤️ Freq. Cardíaca: *${fc} bpm* ${vitalStatus("freq_cardiaca", fc)}\n\n`;

      if (risk && risk.level !== "stable") {
        summary += `${risk.emoji} *Risco: ${risk.label}* (score ${risk.score})\n`;
        summary += `${risk.trend.emoji} Tendência: ${risk.trend.label}\n`;
        if (risk.protocol) {
          summary += `\n*${risk.protocol.label}:*\n`;
          risk.protocol.actions.forEach(a => { summary += `  ▸ ${a}\n`; });
        }
        summary += `\n🚨 Cadeia clínica notificada\n\n`;
      } else if (alerts.length > 0) {
        summary += `⚠️ *${alerts.length} valor(es) fora da faixa*\n\n`;
      } else {
        summary += `✅ Todos os valores normais\n\n`;
      }

      summary += `━━━━━━━━━━━━━━━━━━━━━\n`;
      summary += `_Registrado pela BazeX Care_`;

      return ctx.reply(summary, { parse_mode: "Markdown" });
    }

    // ── Edição de campos de texto livre ──
    case "edit_name": {
      const pid = data.editPatientId;
      if (!pid || !db.patients[pid]) return ctx.reply("❌ Paciente não encontrado.");
      const oldVal = db.patients[pid].name;
      db.patients[pid].name = text;
      saveDB();
      logAuditTrail(pid, "EDITAR_FICHA", userId, `Nome: ${oldVal} → ${text}`);
      clearState(userId);
      ctx.reply(`✅ *Nome* atualizado: ${text}`, { parse_mode: "Markdown" });
      return showEditMenu(ctx, pid);
    }

    case "edit_room": {
      const pid = data.editPatientId;
      if (!pid || !db.patients[pid]) return ctx.reply("❌ Paciente não encontrado.");
      const oldVal = db.patients[pid].room;
      db.patients[pid].room = text;
      saveDB();
      logAuditTrail(pid, "EDITAR_FICHA", userId, `Quarto: ${oldVal} → ${text}`);
      clearState(userId);
      ctx.reply(`✅ *Quarto/Leito* atualizado: ${text}`, { parse_mode: "Markdown" });
      return showEditMenu(ctx, pid);
    }

    case "edit_conditions": {
      const pid = data.editPatientId;
      if (!pid || !db.patients[pid]) return ctx.reply("❌ Paciente não encontrado.");
      const oldVal = db.patients[pid].conditions;
      db.patients[pid].conditions = text;
      saveDB();
      logAuditTrail(pid, "EDITAR_FICHA", userId, `Diagnóstico: ${oldVal} → ${text}`);
      clearState(userId);
      ctx.reply(`✅ *Diagnóstico* atualizado: ${text}`, { parse_mode: "Markdown" });
      return showEditMenu(ctx, pid);
    }

    case "edit_medications": {
      const pid = data.editPatientId;
      if (!pid || !db.patients[pid]) return ctx.reply("❌ Paciente não encontrado.");
      const oldVal = db.patients[pid].medications;
      db.patients[pid].medications = text.split("\n").map(m => m.trim()).filter(Boolean);
      saveDB();
      logAuditTrail(pid, "EDITAR_FICHA", userId, `Medicações atualizadas`);
      clearState(userId);
      ctx.reply(`✅ *Medicações* atualizadas:\n${db.patients[pid].medications.map(m => `  💊 ${m}`).join("\n")}`, { parse_mode: "Markdown" });
      return showEditMenu(ctx, pid);
    }

    case "edit_criticalMed": {
      const pid = data.editPatientId;
      if (!pid || !db.patients[pid]) return ctx.reply("❌ Paciente não encontrado.");
      const oldVal = db.patients[pid].criticalMed;
      db.patients[pid].criticalMed = text;
      saveDB();
      logAuditTrail(pid, "EDITAR_FICHA", userId, `Med. Crítica: ${oldVal} → ${text}`);
      clearState(userId);
      ctx.reply(`✅ *Medicação Crítica* atualizada: ${text}`, { parse_mode: "Markdown" });
      return showEditMenu(ctx, pid);
    }

    case "edit_diet": {
      const pid = data.editPatientId;
      if (!pid || !db.patients[pid]) return ctx.reply("❌ Paciente não encontrado.");
      const oldVal = db.patients[pid].diet;
      db.patients[pid].diet = text;
      saveDB();
      logAuditTrail(pid, "EDITAR_FICHA", userId, `Dieta: ${oldVal} → ${text}`);
      clearState(userId);
      ctx.reply(`✅ *Dieta* atualizada: ${text}`, { parse_mode: "Markdown" });
      return showEditMenu(ctx, pid);
    }

    case "edit_age": {
      const pid = data.editPatientId;
      if (!pid || !db.patients[pid]) return ctx.reply("❌ Paciente não encontrado.");
      const oldVal = db.patients[pid].age;
      db.patients[pid].age = text;
      saveDB();
      logAuditTrail(pid, "EDITAR_FICHA", userId, `Idade: ${oldVal} → ${text}`);
      clearState(userId);
      ctx.reply(`✅ *Idade* atualizada: ${text}`, { parse_mode: "Markdown" });
      return showEditMenu(ctx, pid);
    }

    default: {
      const shift = getActiveShift(userId);
      if (shift) {
        shift.observations = shift.observations || [];
        shift.observations.push({ time: timeNow(), text });
        saveDB();
        return ctx.reply(
          `📝 Observação registrada às ${timeNow()}.\n\n` +
          `/checklist — Tarefas\n` +
          `/sinais — Sinais vitais\n` +
          `/escalas — Escalas clínicas\n` +
          `/intercorrencia — Intercorrência\n` +
          `/turno — Encerrar turno`
        );
      }

      if (!db.caregivers[userId] && !db.families[userId]) {
        return ctx.reply("Use /start para começar! 👋");
      }

      return ctx.reply(
        "Use /ajuda para ver os comandos disponíveis. 📋"
      );
    }
  }
});

// ═══════════════════════════════════════════════════════
//  MOTOR DE RISCO CLÍNICO — 3 CAMADAS
//  Camada 1: Regras Clínicas Objetivas (score)
//  Camada 2: Tendência Individual do Paciente
//  Camada 3: Protocolo Automático de Ação
// ═══════════════════════════════════════════════════════

// --- PESOS DOS FATORES DE RISCO ---
const RISK_WEIGHTS = {
  // Sinais vitais fora da faixa
  temp_altered: 2,
  temp_high_fever: 3,       // >= 39°C
  sat_low: 3,
  sat_critical: 4,          // < 88%
  bp_altered: 2,
  bp_critical: 4,           // sis < 80 ou > 180
  hr_altered: 2,
  hr_critical: 4,           // > 130 ou < 40
  // Intercorrências
  incident_any: 1,
  incident_critical: 3,     // queda, convulsão, sangramento, dispneia
  // Escalas clínicas
  pain_intense: 2,          // 7-9 ou 10
  confusion_severe: 3,      // grave ou inconsciente
  confusion_moderate: 1,
  fall_risk_high: 2,
  fall_risk_very_high: 3,
  feeding_refusal: 2,
  feeding_tube: 1,
  // Comportamento
  no_registration_4h: 2,
  medication_refusal: 2,
  // Prioridade do paciente
  high_dependency: 1,
  // Tendência de piora
  trend_worsening: 3,
  trend_oscillating: 1,
};

// --- CAMADA 1: REGRAS CLÍNICAS OBJETIVAS ---
function calculateRiskScore(patientId) {
  const patient = db.patients[patientId];
  if (!patient) return { score: 0, reasons: [], factors: {} };

  let score = 0;
  const reasons = [];
  const factors = {};

  // 1. Sinais vitais
  const vitals = db.vitals[patientId] || [];
  if (vitals.length > 0) {
    const last = vitals[vitals.length - 1];
    if (last.temperatura && isOutOfRange("temperatura", last.temperatura)) {
      score += RISK_WEIGHTS.temp_altered;
      reasons.push(`🌡️ Temperatura ${last.temperatura}°C`);
      factors.temp = last.temperatura;
      if (last.temperatura >= 39) { score += RISK_WEIGHTS.temp_high_fever - RISK_WEIGHTS.temp_altered; }
    }
    if (last.saturacao && isOutOfRange("saturacao", last.saturacao)) {
      score += RISK_WEIGHTS.sat_low;
      reasons.push(`💨 Saturação ${last.saturacao}%`);
      factors.sat = last.saturacao;
      if (last.saturacao < 88) { score += RISK_WEIGHTS.sat_critical - RISK_WEIGHTS.sat_low; }
    }
    if (last.pressao_sis && (isOutOfRange("pressao_sis", last.pressao_sis) || isOutOfRange("pressao_dia", last.pressao_dia))) {
      score += RISK_WEIGHTS.bp_altered;
      reasons.push(`🩺 Pressão ${last.pressao_sis}/${last.pressao_dia}`);
      factors.bp = `${last.pressao_sis}/${last.pressao_dia}`;
      if (last.pressao_sis < 80 || last.pressao_sis > 180) { score += RISK_WEIGHTS.bp_critical - RISK_WEIGHTS.bp_altered; }
    }
    if (last.freq_cardiaca && isOutOfRange("freq_cardiaca", last.freq_cardiaca)) {
      score += RISK_WEIGHTS.hr_altered;
      reasons.push(`❤️ FC ${last.freq_cardiaca}bpm`);
      factors.hr = last.freq_cardiaca;
      if (last.freq_cardiaca > 130 || last.freq_cardiaca < 40) { score += RISK_WEIGHTS.hr_critical - RISK_WEIGHTS.hr_altered; }
    }
  }

  // 2. Intercorrências do dia
  const todayIncidents = (db.incidents[patientId] || []).filter((i) => i.date === todayKey());
  const criticalTypes = ["queda", "convulsao", "sangramento", "dispneia"];
  todayIncidents.forEach((inc) => {
    if (criticalTypes.includes(inc.type)) {
      score += RISK_WEIGHTS.incident_critical;
      const label = INCIDENT_TYPES.find((t) => t.id === inc.type)?.label || inc.type;
      reasons.push(`🚨 ${label}`);
    } else {
      score += RISK_WEIGHTS.incident_any;
    }
  });

  // 3. Escalas clínicas
  const scales = db.scales[patientId] || [];
  if (scales.length > 0) {
    const last = scales[scales.length - 1];
    if (last.pain === "7-9" || last.pain === "10") {
      score += RISK_WEIGHTS.pain_intense;
      reasons.push("😣 Dor intensa");
    }
    if (last.confusion === "grave" || last.confusion === "inconsciente") {
      score += RISK_WEIGHTS.confusion_severe;
      reasons.push("🧠 Confusão grave");
    } else if (last.confusion === "moderada") {
      score += RISK_WEIGHTS.confusion_moderate;
      reasons.push("🧠 Confusão moderada");
    }
    if (last.fall_risk === "muito_alto") {
      score += RISK_WEIGHTS.fall_risk_very_high;
      reasons.push("⚠️ Risco de queda muito alto");
    } else if (last.fall_risk === "alto") {
      score += RISK_WEIGHTS.fall_risk_high;
      reasons.push("⚠️ Risco de queda alto");
    }
    if (last.feeding === "recusa") {
      score += RISK_WEIGHTS.feeding_refusal;
      reasons.push("🍽️ Recusando alimentação");
    } else if (last.feeding === "sonda") {
      score += RISK_WEIGHTS.feeding_tube;
    }
  }

  // 4. Recusa de medicação (intercorrência)
  const medRefusals = todayIncidents.filter((i) => i.type === "recusa_med");
  if (medRefusals.length > 0) {
    score += RISK_WEIGHTS.medication_refusal;
    reasons.push(`💊 Recusou medicação (${medRefusals.length}x)`);
  }

  // 5. Ausência de registro nas últimas 4h
  const lastReg = getLastRegistrationTime(patientId);
  if (lastReg > 0 && (Date.now() - lastReg) > 4 * 60 * 60 * 1000) {
    score += RISK_WEIGHTS.no_registration_4h;
    reasons.push("⏰ Sem registro há 4h+");
  }

  // 6. Prioridade do paciente
  if (patient.priority === "high") {
    score += RISK_WEIGHTS.high_dependency;
  }

  return { score, reasons, factors };
}

// --- CAMADA 2: TENDÊNCIA INDIVIDUAL DO PACIENTE ---
function calculateTrend(patientId) {
  const vitals = db.vitals[patientId] || [];
  const incidents = db.incidents[patientId] || [];
  const scales = db.scales[patientId] || [];

  if (vitals.length < 2) return { status: "sem_dados", label: "Sem dados suficientes", emoji: "⚪", details: [] };

  const details = [];
  let worseningCount = 0;
  let improvingCount = 0;

  // Analisar tendência dos sinais vitais (últimos 3 registros vs anteriores)
  const recentVitals = vitals.slice(-3);
  const olderVitals = vitals.slice(-6, -3);

  if (olderVitals.length > 0) {
    // Média dos sinais recentes vs anteriores
    const avgRecent = {
      temp: avg(recentVitals.map(v => v.temperatura).filter(Boolean)),
      sat: avg(recentVitals.map(v => v.saturacao).filter(Boolean)),
      sis: avg(recentVitals.map(v => v.pressao_sis).filter(Boolean)),
      hr: avg(recentVitals.map(v => v.freq_cardiaca).filter(Boolean)),
    };
    const avgOlder = {
      temp: avg(olderVitals.map(v => v.temperatura).filter(Boolean)),
      sat: avg(olderVitals.map(v => v.saturacao).filter(Boolean)),
      sis: avg(olderVitals.map(v => v.pressao_sis).filter(Boolean)),
      hr: avg(olderVitals.map(v => v.freq_cardiaca).filter(Boolean)),
    };

    // Temperatura subindo
    if (avgRecent.temp && avgOlder.temp) {
      const diff = avgRecent.temp - avgOlder.temp;
      if (diff > 0.3) { worseningCount++; details.push(`🌡️ Temperatura subindo (+${diff.toFixed(1)}°C)`); }
      else if (diff < -0.3) { improvingCount++; details.push(`🌡️ Temperatura descendo (${diff.toFixed(1)}°C)`); }
    }
    // Saturação caindo
    if (avgRecent.sat && avgOlder.sat) {
      const diff = avgRecent.sat - avgOlder.sat;
      if (diff < -1) { worseningCount++; details.push(`💨 Saturação caindo (${diff.toFixed(0)}%)`); }
      else if (diff > 1) { improvingCount++; details.push(`💨 Saturação subindo (+${diff.toFixed(0)}%)`); }
    }
    // Pressão sistólica
    if (avgRecent.sis && avgOlder.sis) {
      const diff = avgRecent.sis - avgOlder.sis;
      if (Math.abs(diff) > 10) {
        if ((avgOlder.sis <= 140 && avgRecent.sis > 140) || (avgOlder.sis >= 90 && avgRecent.sis < 90)) {
          worseningCount++; details.push(`🩺 Pressão saindo da faixa (${diff > 0 ? "+" : ""}${diff.toFixed(0)}mmHg)`);
        } else if ((avgOlder.sis > 140 && avgRecent.sis <= 140) || (avgOlder.sis < 90 && avgRecent.sis >= 90)) {
          improvingCount++; details.push(`🩺 Pressão normalizando`);
        }
      }
    }
    // Frequência cardíaca
    if (avgRecent.hr && avgOlder.hr) {
      const diff = avgRecent.hr - avgOlder.hr;
      if (diff > 10 && avgRecent.hr > 100) { worseningCount++; details.push(`❤️ FC subindo (+${diff.toFixed(0)}bpm)`); }
      else if (diff < -10 && avgOlder.hr > 100) { improvingCount++; details.push(`❤️ FC normalizando`); }
    }
  }

  // Analisar tendência de intercorrências (últimos 3 dias)
  const now_ts = Date.now();
  const threeDaysAgo = now_ts - 3 * 24 * 60 * 60 * 1000;
  const oneDayAgo = now_ts - 24 * 60 * 60 * 1000;
  const recentIncidents = incidents.filter(i => i.timestamp && i.timestamp > oneDayAgo).length;
  const olderIncidents = incidents.filter(i => i.timestamp && i.timestamp > threeDaysAgo && i.timestamp <= oneDayAgo).length;
  if (recentIncidents > olderIncidents && recentIncidents > 0) {
    worseningCount++;
    details.push(`🚨 Mais intercorrências que o habitual (${recentIncidents} em 24h)`);
  }

  // Analisar tendência das escalas
  if (scales.length >= 2) {
    const lastScale = scales[scales.length - 1];
    const prevScale = scales[scales.length - 2];
    const painLevels = { "0": 0, "1-3": 1, "4-6": 2, "7-9": 3, "10": 4 };
    if (lastScale.pain && prevScale.pain) {
      const diff = (painLevels[lastScale.pain] || 0) - (painLevels[prevScale.pain] || 0);
      if (diff > 0) { worseningCount++; details.push(`😣 Dor aumentando`); }
      else if (diff < 0) { improvingCount++; details.push(`😣 Dor diminuindo`); }
    }
    const confLevels = { "lucido": 0, "leve": 1, "moderada": 2, "grave": 3, "inconsciente": 4 };
    if (lastScale.confusion && prevScale.confusion) {
      const diff = (confLevels[lastScale.confusion] || 0) - (confLevels[prevScale.confusion] || 0);
      if (diff > 0) { worseningCount++; details.push(`🧠 Confusão piorando`); }
      else if (diff < 0) { improvingCount++; details.push(`🧠 Confusão melhorando`); }
    }
  }

  // Classificar tendência
  if (worseningCount >= 3) return { status: "piorando", label: "Piorando", emoji: "📉", details };
  if (worseningCount >= 1 && improvingCount >= 1) return { status: "oscilando", label: "Oscilando", emoji: "📊", details };
  if (worseningCount >= 1) return { status: "piorando", label: "Piorando", emoji: "📉", details };
  if (improvingCount >= 2) return { status: "melhorando", label: "Melhorando", emoji: "📈", details };
  return { status: "estavel", label: "Estável", emoji: "➡️", details };
}

function avg(arr) {
  if (!arr || arr.length === 0) return null;
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

// --- CAMADA 3: PROTOCOLO AUTOMÁTICO DE AÇÃO ---
const RISK_PROTOCOLS = {
  attention: {
    label: "⚠️ PROTOCOLO ATENÇÃO",
    actions: [
      "Repetir sinais vitais em 2 horas",
      "Revisar medicação do paciente",
      "Registrar nova observação clínica",
      "Supervisor: validar caso",
    ],
  },
  critical: {
    label: "🚨 PROTOCOLO CRÍTICO",
    actions: [
      "Acionar enfermeiro IMEDIATAMENTE",
      "Avisar familiar responsável",
      "Sugerir contato com médico",
      "Caso marcado como PRIORIDADE MÁXIMA",
      "Registrar hora da ação e responsável",
    ],
  },
};

function getProtocol(riskLevel) {
  if (riskLevel === "critical") return RISK_PROTOCOLS.critical;
  if (riskLevel === "attention") return RISK_PROTOCOLS.attention;
  return null;
}

// --- FUNÇÃO PRINCIPAL: RISCO CLÍNICO COMPLETO ---
function calculateClinicalRisk(patientId) {
  const patient = db.patients[patientId];
  if (!patient) return { level: "unknown", emoji: "⚪", label: "Sem dados", score: 0, reasons: [], trend: { status: "sem_dados", label: "Sem dados", emoji: "⚪", details: [] }, protocol: null };

  // Camada 1: Score por regras
  const { score: baseScore, reasons, factors } = calculateRiskScore(patientId);

  // Camada 2: Tendência
  const trend = calculateTrend(patientId);

  // Adicionar pontos de tendência ao score
  let finalScore = baseScore;
  if (trend.status === "piorando") {
    finalScore += RISK_WEIGHTS.trend_worsening;
    reasons.push(`📉 Tendência de piora`);
  } else if (trend.status === "oscilando") {
    finalScore += RISK_WEIGHTS.trend_oscillating;
  }

  // Classificar nível final
  let level, emoji, label;
  if (finalScore >= 8) { level = "critical"; emoji = "🔴"; label = "Crítico"; }
  else if (finalScore >= 4) { level = "attention"; emoji = "🟡"; label = "Atenção"; }
  else { level = "stable"; emoji = "🟢"; label = "Estável"; }

  // Camada 3: Protocolo
  const protocol = getProtocol(level);

  return { level, emoji, label, score: finalScore, reasons, trend, protocol, factors };
}

// --- TRILHA DE AUDITORIA ---
function logAuditTrail(patientId, action, userId, details = "") {
  if (!db.auditTrail) db.auditTrail = [];
  db.auditTrail.push({
    patientId,
    action,
    userId,
    details,
    timestamp: Date.now(),
    date: todayKey(),
    time: timeNow(),
  });
  // Manter últimos 1000 registros
  if (db.auditTrail.length > 1000) db.auditTrail = db.auditTrail.slice(-1000);
  saveDB();
}

// --- LINHA DO TEMPO CLÍNICA ---
function buildClinicalTimeline(patientId, hoursBack = 24) {
  const cutoff = Date.now() - hoursBack * 60 * 60 * 1000;
  const events = [];

  // Sinais vitais
  (db.vitals[patientId] || []).forEach(v => {
    if (v.timestamp && v.timestamp > cutoff) {
      let desc = "Sinais vitais registrados";
      const parts = [];
      if (v.temperatura) parts.push(`${v.temperatura}°C${isOutOfRange("temperatura", v.temperatura) ? "⚠️" : ""}`);
      if (v.saturacao) parts.push(`SpO2 ${v.saturacao}%${isOutOfRange("saturacao", v.saturacao) ? "⚠️" : ""}`);
      if (v.pressao_sis) parts.push(`PA ${v.pressao_sis}/${v.pressao_dia}${isOutOfRange("pressao_sis", v.pressao_sis) || isOutOfRange("pressao_dia", v.pressao_dia) ? "⚠️" : ""}`);
      if (v.freq_cardiaca) parts.push(`FC ${v.freq_cardiaca}${isOutOfRange("freq_cardiaca", v.freq_cardiaca) ? "⚠️" : ""}`);
      if (parts.length > 0) desc = parts.join(" | ");
      events.push({ ts: v.timestamp, emoji: "🩺", desc, type: "vitals" });
    }
  });

  // Intercorrências
  (db.incidents[patientId] || []).forEach(inc => {
    if (inc.timestamp && inc.timestamp > cutoff) {
      const t = INCIDENT_TYPES.find(t => t.id === inc.type);
      events.push({ ts: inc.timestamp, emoji: t?.emoji || "🚨", desc: t?.label || inc.type, type: "incident" });
    }
  });

  // Escalas
  (db.scales[patientId] || []).forEach(s => {
    if (s.timestamp && s.timestamp > cutoff) {
      const parts = [];
      if (s.pain) parts.push(`Dor: ${s.pain}`);
      if (s.confusion) parts.push(`Confusão: ${s.confusion}`);
      if (s.fall_risk) parts.push(`Queda: ${s.fall_risk}`);
      if (s.feeding) parts.push(`Alimentação: ${s.feeding}`);
      events.push({ ts: s.timestamp, emoji: "📋", desc: parts.join(" | ") || "Escalas registradas", type: "scale" });
    }
  });

  // Alertas
  (db.alerts || []).filter(a => a.patientId === patientId && a.timestamp && a.timestamp > cutoff).forEach(a => {
    events.push({ ts: a.timestamp, emoji: "🚨", desc: a.message || "Alerta gerado", type: "alert" });
  });

  // Checklist (tarefas completadas)
  Object.values(db.shifts).forEach(s => {
    if (s.patientId === patientId && s.completedTasks_times) {
      Object.entries(s.completedTasks_times).forEach(([taskId, time]) => {
        const ts = new Date(time).getTime();
        if (!isNaN(ts) && ts > cutoff) {
          events.push({ ts, emoji: "✅", desc: taskId.replace(/_/g, " "), type: "task" });
        }
      });
    }
  });

  // Auditoria
  (db.auditTrail || []).filter(a => a.patientId === patientId && a.timestamp && a.timestamp > cutoff).forEach(a => {
    events.push({ ts: a.timestamp, emoji: "📝", desc: `${a.action}: ${a.details}`, type: "audit" });
  });

  // Ordenar por timestamp
  events.sort((a, b) => a.ts - b.ts);
  return events;
}

function formatTimeline(events, maxEvents = 15) {
  if (events.length === 0) return "Nenhum evento registrado.";
  const recent = events.slice(-maxEvents);
  return recent.map(e => {
    const time = new Date(e.ts).toLocaleTimeString("pt-BR", { timeZone: TZ, hour: "2-digit", minute: "2-digit" });
    const date = new Date(e.ts).toLocaleDateString("pt-BR", { timeZone: TZ, day: "2-digit", month: "2-digit" });
    return `${date} ${time} ${e.emoji} ${e.desc}`;
  }).join("\n");
}

// --- VERIFICAÇÃO AUTOMÁTICA DE RISCO (chamada após registros) ---
function checkAndAlertRisk(patientId, ctx) {
  const risk = calculateClinicalRisk(patientId);
  const patient = db.patients[patientId];
  if (!patient) return;

  if (risk.level === "critical") {
    const msg = `🚨 *ALERTA CRÍTICO — ${patient.name}*\n\n` +
      `Score de risco: *${risk.score}* (${risk.emoji} ${risk.label})\n` +
      `Tendência: ${risk.trend.emoji} ${risk.trend.label}\n\n` +
      `*Motivos:*\n${risk.reasons.map(r => `  • ${r}`).join("\n")}\n\n` +
      `*${risk.protocol.label}:*\n${risk.protocol.actions.map(a => `  ▸ ${a}`).join("\n")}\n\n` +
      `⏰ ${now()}`;
    notifyClinicalChain(patientId, msg, "all");
    logAuditTrail(patientId, "ALERTA_CRITICO", "sistema", `Score ${risk.score}: ${risk.reasons.join(", ")}`);
  } else if (risk.level === "attention") {
    const msg = `⚠️ *ATENÇÃO — ${patient.name}*\n\n` +
      `Score de risco: *${risk.score}* (${risk.emoji} ${risk.label})\n` +
      `Tendência: ${risk.trend.emoji} ${risk.trend.label}\n\n` +
      `*Motivos:*\n${risk.reasons.map(r => `  • ${r}`).join("\n")}\n\n` +
      `*${risk.protocol.label}:*\n${risk.protocol.actions.map(a => `  ▸ ${a}`).join("\n")}\n\n` +
      `⏰ ${now()}`;
    // Atenção: notificar apenas enfermeira e supervisor
    notifyClinicalChain(patientId, msg, "nurse");
    logAuditTrail(patientId, "ALERTA_ATENCAO", "sistema", `Score ${risk.score}: ${risk.reasons.join(", ")}`);
  }

  return risk;
}

function getLastRegistrationTime(patientId) {
  let lastTime = 0;
  // Sinais vitais
  const vitals = db.vitals[patientId] || [];
  if (vitals.length > 0) {
    const last = vitals[vitals.length - 1];
    if (last.timestamp) lastTime = Math.max(lastTime, last.timestamp);
  }
  // Turnos ativos
  Object.values(db.shifts).forEach((s) => {
    if (s.patientId === patientId && s.active && s.startTimestamp) {
      lastTime = Math.max(lastTime, s.startTimestamp);
    }
    if (s.patientId === patientId && s.completedTasks_times) {
      Object.values(s.completedTasks_times).forEach((t) => {
        const ts = new Date(t).getTime();
        if (!isNaN(ts)) lastTime = Math.max(lastTime, ts);
      });
    }
  });
  // Intercorrências
  const incidents = db.incidents[patientId] || [];
  if (incidents.length > 0) {
    const last = incidents[incidents.length - 1];
    if (last.timestamp) lastTime = Math.max(lastTime, last.timestamp);
  }
  return lastTime;
}

// ═══════════════════════════════════════════════════════
//  PAINEL DE SUPERVISÃO (/painel)
// ═══════════════════════════════════════════════════════

function handlePanel(ctx, userId) {
  const patients = Object.entries(db.patients);
  const activeShifts = Object.values(db.shifts).filter((s) => s.active);
  const todayAlertsList = db.alerts.filter((a) => a.date === todayKey());
  const unresolvedAlerts = todayAlertsList.filter((a) => !a.resolved);
  const nurseCount = Object.keys(db.nurses).length;
  const supervisorCount = Object.keys(db.supervisors).length;
  const caregiverCount = Object.keys(db.caregivers).length;

  // Calcular risco clínico de cada paciente
  const patientRisks = patients.map(([pid, patient]) => ({
    pid, patient, risk: calculateClinicalRisk(pid),
  }));

  // Ordenar: críticos primeiro, depois atenção, depois estáveis
  const riskOrder = { critical: 0, attention: 1, stable: 2, unknown: 3 };
  patientRisks.sort((a, b) => (riskOrder[a.risk.level] || 3) - (riskOrder[b.risk.level] || 3));

  const criticalCount = patientRisks.filter((p) => p.risk.level === "critical").length;
  const attentionCount = patientRisks.filter((p) => p.risk.level === "attention").length;
  const stableCount = patientRisks.filter((p) => p.risk.level === "stable" || p.risk.level === "unknown").length;

  // Pacientes sem registro nas últimas 4h
  const FOUR_HOURS = 4 * 60 * 60 * 1000;
  const nowMs = Date.now();
  const noRecentRecord = patients.filter(([pid]) => {
    const lastReg = getLastRegistrationTime(pid);
    return lastReg === 0 || (nowMs - lastReg) > FOUR_HOURS;
  });

  // Intercorrências do dia
  const todayIncidents = [];
  Object.entries(db.incidents).forEach(([pid, incidents]) => {
    (incidents || []).forEach((inc) => {
      if (inc.date === todayKey()) {
        todayIncidents.push({ ...inc, patientId: pid, patientName: db.patients[pid]?.name || "Paciente" });
      }
    });
  });

  let msg = `━━━━━━━━━━━━━━━━━━━━━\n`;
  msg += `🏥 *PAINEL DE SUPERVISÃO*\n`;
  msg += `📅 ${todayKey().replace(/-/g, "/")} — ${timeNow()}\n`;
  msg += `━━━━━━━━━━━━━━━━━━━━━\n\n`;

  // Resumo geral com semáforo
  msg += `📊 *Resumo Geral:*\n`;
  msg += `👥 Pacientes monitorados: *${patients.length}*\n`;
  msg += `   🔴 Críticos: *${criticalCount}* | 🟡 Atenção: *${attentionCount}* | 🟢 Estáveis: *${stableCount}*\n`;
  msg += `🟢 Turnos ativos: *${activeShifts.length}*\n`;
  msg += `🚨 Alertas hoje: *${todayAlertsList.length}*`;
  if (unresolvedAlerts.length > 0) msg += ` (${unresolvedAlerts.length} não resolvidos)`;
  msg += `\n`;
  msg += `👩‍⚕️ Equipe: ${caregiverCount} cuidador(es), ${nurseCount} enfermeiro(s), ${supervisorCount} supervisor(es)\n\n`;

  // INTERCORRÊNCIAS DO DIA (novo!)
  if (todayIncidents.length > 0) {
    msg += `⚠️ *INTERCORRÊNCIAS HOJE: ${todayIncidents.length}*\n`;
    msg += `─────────────────────\n`;
    todayIncidents.slice(-8).forEach((inc) => {
      const type = INCIDENT_TYPES.find((t) => t.id === inc.type);
      msg += `${type?.emoji || "⚠️"} *${inc.patientName}* — ${type?.label || inc.type}`;
      if (inc.time) msg += ` (🕒 ${inc.time})`;
      msg += `\n`;
    });
    if (todayIncidents.length > 8) msg += `_...e mais ${todayIncidents.length - 8}_\n`;
    msg += `\n`;
  }

  // PACIENTES SEM REGISTRO RECENTE (novo!)
  if (noRecentRecord.length > 0) {
    msg += `⏰ *SEM REGISTRO NAS ÚLTIMAS 4H:*\n`;
    msg += `─────────────────────\n`;
    noRecentRecord.forEach(([pid, patient]) => {
      const lastReg = getLastRegistrationTime(pid);
      if (lastReg === 0) {
        msg += `⚠️ *${patient.name}* — _Nenhum registro_\n`;
      } else {
        const hoursAgo = Math.floor((nowMs - lastReg) / 3600000);
        msg += `⚠️ *${patient.name}* — _Último registro há ${hoursAgo}h_\n`;
      }
    });
    msg += `\n`;
  }

  // Alertas ativos
  if (unresolvedAlerts.length > 0) {
    msg += `🚨 *ALERTAS ATIVOS:*\n`;
    msg += `─────────────────────\n`;
    const lastAlerts = unresolvedAlerts.slice(-8);
    lastAlerts.forEach((a) => {
      const patient = db.patients[a.patientId];
      const risk = calculateClinicalRisk(a.patientId);
      msg += `${risk.emoji} *${a.patientName || "Paciente"}*`;
      if (patient?.room) msg += ` — Q.${patient.room}`;
      msg += `\n`;
      msg += `   ${a.message.substring(0, 80)}\n`;
      msg += `   🕒 ${a.time}\n\n`;
    });
    if (unresolvedAlerts.length > 8) {
      msg += `   _...e mais ${unresolvedAlerts.length - 8} alerta(s)_\n\n`;
    }
  } else {
    msg += `✅ *Nenhum alerta ativo* — todos os pacientes estáveis\n\n`;
  }

  // Status de cada paciente COM NÍVEL DE RISCO
  msg += `👥 *PACIENTES:*\n`;
  msg += `─────────────────────\n`;

  if (patients.length === 0) {
    msg += `Nenhum paciente cadastrado.\n`;
  } else {
    patientRisks.forEach(({ pid, patient, risk }) => {
      const activeShift = activeShifts.find((s) => s.patientId === pid);
      const patientAlerts = todayAlertsList.filter((a) => a.patientId === pid);

      msg += `\n${risk.emoji} *${patient.name}*`;
      if (patient.age) msg += `, ${patient.age} anos`;
      if (patient.room) msg += ` — Q.${patient.room}`;
      msg += `\n`;

      // Nível de risco clínico + tendência
      msg += `   ${risk.emoji} *${risk.label}* (score ${risk.score})`;
      msg += ` ${risk.trend.emoji} ${risk.trend.label}`;
      if (risk.reasons.length > 0) {
        msg += `\n   ▸ ${risk.reasons.slice(0, 2).join(", ")}`;
      }
      if (risk.protocol) {
        msg += `\n   📋 ${risk.protocol.label}`;
      }
      msg += `\n`;

      // Status do turno
      if (activeShift) {
        const cg = db.caregivers[activeShift.caregiverId];
        const dur = formatDuration(Date.now() - activeShift.startTimestamp);
        const doneTasks = (activeShift.completedTasks || []).length;
        const totalTasks = getChecklistTasks(pid).length;
        msg += `   🟢 Turno ativo (${dur}) — ${cg?.name || "Cuidador"}\n`;
        msg += `   📋 Checklist: ${doneTasks}/${totalTasks}\n`;
      } else {
        msg += `   ⚪ Sem turno ativo\n`;
      }

      // Últimos sinais vitais
      const vitals = db.vitals[pid] || [];
      if (vitals.length > 0) {
        const last = vitals[vitals.length - 1];
        msg += `   📊 🌡️${last.temperatura}°C 💨${last.saturacao}% 🩺${last.pressao_sis}/${last.pressao_dia} ❤️${last.freq_cardiaca}bpm\n`;
      } else {
        msg += `   📊 Sinais: Não registrados\n`;
      }

      // Alertas do dia
      if (patientAlerts.length > 0) {
        msg += `   🚨 ${patientAlerts.length} alerta(s) hoje\n`;
      }

      // Diagnóstico resumido
      if (patient.conditions) {
        msg += `   🩺 ${patient.conditions.substring(0, 50)}\n`;
      }
    });
  }

  msg += `\n━━━━━━━━━━━━━━━━━━━━━\n`;
  msg += `_Painel BazeX Care — Atualizado às ${timeNow()}_`;

  ctx.reply(msg, { parse_mode: "Markdown" });
}

// ═══════════════════════════════════════════════════════
//  FINALIZAR CADASTRO DO PACIENTE
// ═══════════════════════════════════════════════════════

function finishPatientRegistration(ctx, userId, data) {
  const code = generateCode();
  const patientId = `patient_${Date.now()}`;

  db.patients[patientId] = {
    name: data.name,
    age: data.age,
    conditions: data.conditions,
    medicationsRaw: data.meds,
    medications: data.meds === "depois" ? [] : data.meds.split("\n").filter((l) => l.trim()),
    criticalMed: data.criticalMed,
    mobility: data.mobility,
    priority: data.priority || "medium",
    room: data.room,
    diet: null,
    fallRisk: null,
    caregiverId: userId,
    familyIds: [],
    code,
    registeredAt: now(),
  };

  // Vincular ao cuidador (multi-paciente)
  if (db.caregivers[userId]) {
    if (!db.caregivers[userId].patientIds) db.caregivers[userId].patientIds = [];
    db.caregivers[userId].patientIds.push(patientId);
    db.caregivers[userId].activePatientId = patientId;
    db.caregivers[userId].patientId = patientId; // compatibilidade
  }

  saveDB();
  clearState(userId);

  const card = buildPatientCard(db.patients[patientId], patientId);

  ctx.reply(
    `✅ *Paciente cadastrado!*\n\n` +
    card + `\n\n` +
    `_Compartilhe o código com a família para acompanhamento._\n\n` +
    `Agora você pode:`,
    {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard([
        [Markup.button.callback("▶️ Iniciar turno", "btn_start_shift")],
        [Markup.button.callback("📊 Registrar sinais vitais", "btn_vitals")],
        [Markup.button.callback("📏 Escalas clínicas", "btn_scales")],
      ]),
    }
  );
}

// ═══════════════════════════════════════════════════════
//  EDITAR FICHA CLÍNICA DO PACIENTE
// ═══════════════════════════════════════════════════════

const EDIT_FIELDS = [
  { id: "name", label: "Nome", emoji: "👤" },
  { id: "room", label: "Quarto/Leito", emoji: "🛏️" },
  { id: "conditions", label: "Diagnóstico/Condições", emoji: "🩺" },
  { id: "medications", label: "Medicações", emoji: "💊" },
  { id: "criticalMed", label: "Medicação Crítica", emoji: "⚠️" },
  { id: "diet", label: "Dieta", emoji: "🍽️" },
  { id: "mobility", label: "Mobilidade", emoji: "🚶" },
  { id: "priority", label: "Nível de Prioridade", emoji: "🚦" },
  { id: "fallRisk", label: "Risco de Queda", emoji: "⚠️" },
  { id: "age", label: "Idade", emoji: "🎂" },
];

function handleEditPatient(ctx, userId) {
  const caregiver = db.caregivers[userId];
  const nurse = db.nurses?.[userId];
  const supervisor = db.supervisors?.[userId];

  let patientId = null;
  if (caregiver) patientId = caregiver.activePatientId || caregiver.patientId;
  else if (nurse) patientId = nurse.patientIds?.[0];
  else if (supervisor) {
    // Supervisor pode editar qualquer paciente — mostrar lista
    const patientIds = Object.keys(db.patients);
    if (patientIds.length === 0) return ctx.reply("❌ Nenhum paciente cadastrado.");
    const buttons = patientIds.map((pid) => {
      const p = db.patients[pid];
      return [Markup.button.callback(`✏️ ${p.name}`, `edit_select_${pid}`)];
    });
    return ctx.reply("*Selecione o paciente para editar:*", {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard(buttons),
    });
  }

  if (!patientId || !db.patients[patientId]) {
    return ctx.reply("❌ Nenhum paciente ativo. Use /plantao para selecionar.");
  }

  return showEditMenu(ctx, patientId);
}

function showEditMenu(ctx, patientId) {
  const p = db.patients[patientId];
  if (!p) return ctx.reply("❌ Paciente não encontrado.");

  const currentValues = [
    `👤 *Nome:* ${p.name}`,
    `🎂 *Idade:* ${p.age || "N/A"}`,
    `🛏️ *Quarto:* ${p.room || "Não definido"}`,
    `🩺 *Diagnóstico:* ${p.conditions || "Não definido"}`,
    `💊 *Medicações:* ${p.medications?.length ? p.medications.join(", ") : "Nenhuma"}`,
    `⚠️ *Med. Crítica:* ${p.criticalMed || "Não definida"}`,
    `🍽️ *Dieta:* ${p.diet || "Não definida"}`,
    `🚶 *Mobilidade:* ${p.mobility || "Não definida"}`,
    `🚦 *Prioridade:* ${p.priority === "high" ? "🔴 Alta" : p.priority === "medium" ? "🟠 Média" : "🟢 Independente"}`,
    `⚠️ *Risco Queda:* ${p.fallRisk || "Não avaliado"}`,
  ];

  const buttons = EDIT_FIELDS.map((f) => [
    Markup.button.callback(`${f.emoji} ${f.label}`, `edit_field_${patientId}_${f.id}`),
  ]);
  buttons.push([Markup.button.callback("❌ Fechar", "edit_close")]);

  return ctx.reply(
    `✏️ *Editar Ficha Clínica*\n\n` +
    `Paciente: *${p.name}*\n\n` +
    currentValues.join("\n") + "\n\n" +
    `_Selecione o campo para editar:_`,
    { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) }
  );
}

// Callback: Supervisor seleciona paciente para editar
bot.action(/^edit_select_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  ctx.answerCbQuery();
  return showEditMenu(ctx, patientId);
});

// Callback: Selecionar campo para editar
bot.action(/^edit_field_(.+)_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const fieldId = ctx.match[2];
  const userId = ctx.from.id.toString();
  ctx.answerCbQuery();

  if (fieldId === "priority") {
    // Prioridade usa botões
    return ctx.reply(
      `🚦 *Selecione o nível de prioridade:*`,
      {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard([
          [Markup.button.callback("🔴 Alta dependência", `edit_priority_${patientId}_high`)],
          [Markup.button.callback("🟠 Média", `edit_priority_${patientId}_medium`)],
          [Markup.button.callback("🟢 Independente", `edit_priority_${patientId}_low`)],
        ]),
      }
    );
  }

  if (fieldId === "mobility") {
    return ctx.reply(
      `🚶 *Selecione a mobilidade:*`,
      {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard([
          [Markup.button.callback("🚶 Deambula sozinho", `edit_mob_${patientId}_deambula_sozinho`)],
          [Markup.button.callback("🦽 Deambula com apoio", `edit_mob_${patientId}_deambula_apoio`)],
          [Markup.button.callback("🦽 Cadeirante", `edit_mob_${patientId}_cadeirante`)],
          [Markup.button.callback("🛏️ Acamado", `edit_mob_${patientId}_acamado`)],
        ]),
      }
    );
  }

  if (fieldId === "fallRisk") {
    return ctx.reply(
      `⚠️ *Selecione o risco de queda:*`,
      {
        parse_mode: "Markdown",
        ...Markup.inlineKeyboard([
          [Markup.button.callback("🟢 Baixo", `edit_fall_${patientId}_baixo`)],
          [Markup.button.callback("🟡 Moderado", `edit_fall_${patientId}_moderado`)],
          [Markup.button.callback("🔴 Alto", `edit_fall_${patientId}_alto`)],
        ]),
      }
    );
  }

  // Campos de texto livre
  const field = EDIT_FIELDS.find((f) => f.id === fieldId);
  const fieldLabel = field ? field.label : fieldId;
  setState(userId, `edit_${fieldId}`, { editPatientId: patientId });
  return ctx.reply(
    `✏️ *Editando: ${fieldLabel}*\n\n` +
    `Digite o novo valor:`,
    { parse_mode: "Markdown" }
  );
});

// Callback: Editar prioridade
bot.action(/^edit_priority_(.+)_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const value = ctx.match[2];
  ctx.answerCbQuery();
  if (!db.patients[patientId]) return ctx.reply("❌ Paciente não encontrado.");
  db.patients[patientId].priority = value;
  saveDB();
  const label = value === "high" ? "🔴 Alta" : value === "medium" ? "🟠 Média" : "🟢 Independente";
  ctx.reply(`✅ Prioridade atualizada para: ${label}`);
  return showEditMenu(ctx, patientId);
});

// Callback: Editar mobilidade
bot.action(/^edit_mob_(.+)_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const value = ctx.match[2].replace(/_/g, " ");
  ctx.answerCbQuery();
  if (!db.patients[patientId]) return ctx.reply("❌ Paciente não encontrado.");
  db.patients[patientId].mobility = value;
  saveDB();
  ctx.reply(`✅ Mobilidade atualizada para: ${value}`);
  return showEditMenu(ctx, patientId);
});

// Callback: Editar risco de queda
bot.action(/^edit_fall_(.+)_(.+)$/, (ctx) => {
  const patientId = ctx.match[1];
  const value = ctx.match[2];
  ctx.answerCbQuery();
  if (!db.patients[patientId]) return ctx.reply("❌ Paciente não encontrado.");
  db.patients[patientId].fallRisk = value;
  saveDB();
  ctx.reply(`✅ Risco de queda atualizado para: ${value}`);
  return showEditMenu(ctx, patientId);
});

// Callback: Fechar menu de edição
bot.action("edit_close", (ctx) => {
  ctx.answerCbQuery("✅ Edição finalizada");
  try { ctx.deleteMessage(); } catch (e) {}
});

// ═══════════════════════════════════════════════════════
//  PROTOCOLO PÓS-ALTA 72H
// ═══════════════════════════════════════════════════════

const DISCHARGE_CHECKLIST = [
  { id: "med_orientacao", label: "Orientação de medicações pós-alta", emoji: "💊" },
  { id: "sinais_basais", label: "Sinais vitais basais registrados", emoji: "🩺" },
  { id: "retorno_agendado", label: "Retorno médico agendado", emoji: "📅" },
  { id: "cuidador_orientado", label: "Cuidador/família orientado", emoji: "👨\u200d👩\u200d👧" },
  { id: "sinais_alerta", label: "Sinais de alerta explicados", emoji: "⚠️" },
  { id: "dieta_orientada", label: "Orientação alimentar fornecida", emoji: "🍽️" },
  { id: "mobilidade_orientada", label: "Orientação de mobilidade", emoji: "🚶" },
  { id: "contato_emergencia", label: "Contato de emergência fornecido", emoji: "📞" },
];

const DISCHARGE_FOLLOWUP_SCHEDULE = [
  { hours: 6,  label: "6 horas pós-alta",  checkItems: ["temperatura", "dor", "estado_geral"] },
  { hours: 12, label: "12 horas pós-alta", checkItems: ["medicação", "alimentação", "sono"] },
  { hours: 24, label: "24 horas pós-alta", checkItems: ["sinais_vitais", "mobilidade", "humor"] },
  { hours: 48, label: "48 horas pós-alta", checkItems: ["sinais_vitais", "feridas", "medicação"] },
  { hours: 72, label: "72 horas pós-alta", checkItems: ["avaliação_geral", "sinais_vitais", "encaminhamentos"] },
];

function handleDischarge(ctx, userId) {
  const patientId = getPatientId(userId);
  if (!patientId) {
    return ctx.reply("❌ Você não está vinculado a nenhum paciente.\nUse /vincular CODIGO para vincular.");
  }
  const patient = db.patients[patientId];
  if (!patient) return ctx.reply("❌ Paciente não encontrado.");

  // Verificar se já tem alta ativa
  const existing = db.discharges[patientId];
  if (existing && existing.active) {
    return showDischargeStatus(ctx, patientId);
  }

  // Iniciar protocolo de alta
  return ctx.reply(
    `🏥 *PROTOCOLO DE ALTA — ${patient.name}*\n\n` +
    `Você está iniciando o protocolo de alta hospitalar.\n` +
    `O sistema acompanhará o paciente por *72 horas* após a alta.\n\n` +
    `*Checklist de alta:*`,
    {
      parse_mode: "Markdown",
      ...Markup.inlineKeyboard([
        [Markup.button.callback("✅ Iniciar protocolo de alta", `discharge_start_${patientId}`)],
        [Markup.button.callback("❌ Cancelar", "discharge_cancel")],
      ]),
    }
  );
}

function showDischargeStatus(ctx, patientId) {
  const d = db.discharges[patientId];
  const patient = db.patients[patientId];
  if (!d || !patient) return;

  const hoursElapsed = Math.floor((Date.now() - d.dischargeTimestamp) / 3600000);
  const hoursRemaining = Math.max(0, 72 - hoursElapsed);
  const completedChecks = d.completedChecklist || [];
  const totalChecks = DISCHARGE_CHECKLIST.length;
  const followupsCompleted = d.followupsCompleted || [];
  const totalFollowups = DISCHARGE_FOLLOWUP_SCHEDULE.length;

  // Progress bar
  const progress = Math.min(100, Math.round((hoursElapsed / 72) * 100));
  const barFilled = Math.round(progress / 10);
  const bar = "█".repeat(barFilled) + "░".repeat(10 - barFilled);

  let msg = `🏥 *PÓS-ALTA — ${patient.name}*\n\n`;
  msg += `⏰ Tempo desde alta: *${hoursElapsed}h* de 72h\n`;
  msg += `⏳ Restante: *${hoursRemaining}h*\n`;
  msg += `📊 Progresso: [${bar}] ${progress}%\n\n`;

  // Checklist de alta
  msg += `*Checklist de alta:* ${completedChecks.length}/${totalChecks}\n`;
  DISCHARGE_CHECKLIST.forEach(item => {
    const done = completedChecks.includes(item.id);
    msg += `${done ? "✅" : "⬜"} ${item.emoji} ${item.label}\n`;
  });

  // Follow-ups
  msg += `\n*Acompanhamentos:* ${followupsCompleted.length}/${totalFollowups}\n`;
  DISCHARGE_FOLLOWUP_SCHEDULE.forEach(fu => {
    const done = followupsCompleted.includes(fu.label);
    const due = hoursElapsed >= fu.hours;
    const status = done ? "✅" : (due ? "🔴 PENDENTE" : "⏰ Agendado");
    msg += `${status} ${fu.label}\n`;
  });

  // Sinais de alerta pós-alta
  const postAlerts = (d.postAlerts || []).slice(-5);
  if (postAlerts.length > 0) {
    msg += `\n🚨 *Alertas pós-alta:*\n`;
    postAlerts.forEach(a => {
      msg += `  • ${a.time}: ${a.message}\n`;
    });
  }

  if (hoursRemaining === 0) {
    msg += `\n✅ *Protocolo de 72h concluído!*\n`;
    msg += `Paciente pode ser liberado do acompanhamento intensivo.`;
  }

  const buttons = [];
  // Botões para checklist pendente
  const pendingChecks = DISCHARGE_CHECKLIST.filter(item => !completedChecks.includes(item.id));
  if (pendingChecks.length > 0) {
    buttons.push([Markup.button.callback(`📝 Completar checklist (${pendingChecks.length} pendentes)`, `discharge_checklist_${patientId}`)]);
  }
  // Botão para follow-up pendente
  const pendingFollowups = DISCHARGE_FOLLOWUP_SCHEDULE.filter(fu => hoursElapsed >= fu.hours && !followupsCompleted.includes(fu.label));
  if (pendingFollowups.length > 0) {
    buttons.push([Markup.button.callback(`🩺 Registrar acompanhamento`, `discharge_followup_${patientId}`)]);
  }
  // Registrar sinais vitais pós-alta
  buttons.push([Markup.button.callback("📊 Registrar sinais vitais", "btn_vitals")]);

  if (hoursRemaining === 0 && d.active) {
    buttons.push([Markup.button.callback("✅ Encerrar protocolo de alta", `discharge_close_${patientId}`)]);
  }

  return ctx.reply(msg, { parse_mode: "Markdown", ...Markup.inlineKeyboard(buttons) });
}

// ═══════════════════════════════════════════════════════
//  LEMBRETES AUTOMÁTICOS (CRON)
// ═══════════════════════════════════════════════════════

// Sinais vitais 3x ao dia: 8h, 14h, 20h
cron.schedule("0 8 * * *", () => sendVitalsReminder("manhã"), { timezone: TZ });
cron.schedule("0 14 * * *", () => sendVitalsReminder("tarde"), { timezone: TZ });
cron.schedule("0 20 * * *", () => sendVitalsReminder("noite"), { timezone: TZ });

function sendVitalsReminder(period) {
  Object.entries(db.caregivers).forEach(([userId, cg]) => {
    const patientIds = cg.patientIds || (cg.patientId ? [cg.patientId] : []);
    if (patientIds.length === 0 || !cg.chatId) return;

    patientIds.forEach((pid) => {
      const patient = db.patients[pid];
      if (!patient) return;

      const already = (db.vitals[pid] || []).filter(
        (v) => v.date === todayKey() && v.period === period
      );

      if (already.length === 0) {
        bot.telegram.sendMessage(
          cg.chatId,
          `⏰ *Lembrete — Sinais Vitais (${period})*\n\n` +
          `Hora de registrar os sinais de *${patient.name}*!\n\n` +
          `Use /sinais para registrar 📊`,
          { parse_mode: "Markdown" }
        ).catch(() => {});
      }
    });
  });
}

// Checklist a cada 2h (8h-22h)
cron.schedule("0 8,10,12,14,16,18,20,22 * * *", () => {
  Object.values(db.shifts).forEach((shift) => {
    if (!shift.active) return;
    const cg = db.caregivers[shift.caregiverId];
    if (!cg || !cg.chatId) return;

    const tasks = getChecklistTasks(shift.patientId);
    const pending = tasks.length - (shift.completedTasks || []).length;

    if (pending > 0) {
      bot.telegram.sendMessage(
        cg.chatId,
        `⏰ *Lembrete:* ${pending} tarefa(s) pendente(s) no checklist de *${shift.patientName}*.\n\nUse /checklist para ver.`,
        { parse_mode: "Markdown" }
      ).catch(() => {});
    }
  });
}, { timezone: TZ });

// Alerta de medicação atrasada (a cada hora)
cron.schedule("0 * * * *", () => {
  const h = currentHour();
  Object.values(db.shifts).forEach((shift) => {
    if (!shift.active) return;
    const done = shift.completedTasks || [];
    const cg = db.caregivers[shift.caregiverId];
    if (!cg || !cg.chatId) return;

    // Verificar medicações por período
    if (h >= 10 && !done.includes("remedio_manha")) {
      bot.telegram.sendMessage(cg.chatId,
        `💊 *ALERTA:* Medicação da manhã de *${shift.patientName}* ainda não foi dada!\nUse /checklist`,
        { parse_mode: "Markdown" }
      ).catch(() => {});

      notifyFamily(shift.patientId,
        `💊 *ALERTA — ${shift.patientName}*\n\nMedicação da manhã atrasada (${timeNow()}).`
      );
    }

    if (h >= 16 && !done.includes("remedio_tarde")) {
      bot.telegram.sendMessage(cg.chatId,
        `💊 *ALERTA:* Medicação da tarde de *${shift.patientName}* ainda não foi dada!\nUse /checklist`,
        { parse_mode: "Markdown" }
      ).catch(() => {});
    }

    if (h >= 23 && !done.includes("remedio_noite")) {
      bot.telegram.sendMessage(cg.chatId,
        `💊 *ALERTA:* Medicação da noite de *${shift.patientName}* ainda não foi dada!\nUse /checklist`,
        { parse_mode: "Markdown" }
      ).catch(() => {});
    }
  });
}, { timezone: TZ });

// Alerta de ausência (30 min)
cron.schedule("*/30 * * * *", () => {
  const threeHoursAgo = Date.now() - 3 * 3600000;

  Object.values(db.shifts).forEach((shift) => {
    if (!shift.active || shift.startTimestamp > threeHoursAgo) return;

    let lastActivity = shift.startTimestamp;
    const taskTimes = Object.values(shift.completedTasks_times || {});
    if (shift.vitals && shift.vitals.length > 0) lastActivity = Date.now();
    if (taskTimes.length > 0 || (shift.observations && shift.observations.length > 0)) lastActivity = Date.now();
    if (shift.scales && shift.scales.length > 0) lastActivity = Date.now();
    if (shift.incidents && shift.incidents.length > 0) lastActivity = Date.now();

    if (lastActivity < threeHoursAgo) {
      notifyFamily(shift.patientId,
        `⚠️ *Alerta — ${shift.patientName}*\n\n` +
        `O cuidador não registrou atividade nas últimas 3 horas.\nRecomendamos verificar.`
      );
    }
  });
}, { timezone: TZ });

// Lembretes de pós-alta (a cada hora)
cron.schedule("30 * * * *", () => {
  Object.entries(db.discharges).forEach(([patientId, d]) => {
    if (!d.active) return;
    const patient = db.patients[patientId];
    if (!patient) return;

    const hoursElapsed = Math.floor((Date.now() - d.dischargeTimestamp) / 3600000);
    const completed = d.followupsCompleted || [];

    // Verificar se há follow-up pendente
    DISCHARGE_FOLLOWUP_SCHEDULE.forEach(fu => {
      if (hoursElapsed >= fu.hours && !completed.includes(fu.label)) {
        // Enviar lembrete para cuidador
        const cg = db.caregivers[patient.caregiverId];
        if (cg && cg.chatId) {
          bot.telegram.sendMessage(cg.chatId,
            `⏰ *LEMBRETE PÓS-ALTA — ${patient.name}*\n\n` +
            `🩺 *${fu.label}* está pendente!\n\n` +
            `Itens a verificar:\n` +
            fu.checkItems.map(i => `  • ${i.replace(/_/g, " ")}`).join("\n") + "\n\n" +
            `Use /alta para registrar o acompanhamento.`,
            { parse_mode: "Markdown" }
          ).catch(() => {});
        }

        // Notificar família também
        if (patient.familyIds && patient.familyIds.length > 0) {
          patient.familyIds.forEach(fId => {
            const fam = db.families[fId];
            if (fam && fam.chatId) {
              bot.telegram.sendMessage(fam.chatId,
                `⏰ *PÓS-ALTA — ${patient.name}*\n\n` +
                `Acompanhamento de *${fu.label}* está pendente.\n` +
                `Verifique com o cuidador se tudo está bem.`,
                { parse_mode: "Markdown" }
              ).catch(() => {});
            }
          });
        }
      }
    });

    // Verificar se protocolo expirou (72h)
    if (hoursElapsed >= 72 && d.active) {
      // Enviar resumo final
      const completedFollowups = completed.length;
      const totalFollowups = DISCHARGE_FOLLOWUP_SCHEDULE.length;
      const completedChecks = (d.completedChecklist || []).length;
      const totalChecks = DISCHARGE_CHECKLIST.length;

      notifyClinicalChain(patientId,
        `⏰ *72H CONCLUÍDAS — ${patient.name}*\n\n` +
        `Protocolo pós-alta completou 72 horas.\n\n` +
        `📋 Checklist: ${completedChecks}/${totalChecks}\n` +
        `🩺 Acompanhamentos: ${completedFollowups}/${totalFollowups}\n\n` +
        `Use /alta para ver o resumo e encerrar o protocolo.`,
        "all"
      );
    }
  });
}, { timezone: TZ });

// ═══════════════════════════════════════════════════════
//  INICIAR BOT
// ═══════════════════════════════════════════════════════

console.log("🚀 Iniciando BazeX Care Bot...");
console.log(`📊 Dados: ${Object.keys(db.patients).length} pacientes, ${Object.keys(db.caregivers).length} cuidadores, ${Object.keys(db.families).length} famílias`);

bot.launch({ dropPendingUpdates: true })
  .then(() => console.log("Bot parou."))
  .catch((err) => {
    console.error("❌ Erro:", err.message || err);
    process.exit(1);
  });

console.log("✅ BazeX Care Bot ativo! @BasexCareBot — aguardando mensagens...");

bot.catch((err) => {
  console.error("Bot error:", err.message || err);
});

process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
