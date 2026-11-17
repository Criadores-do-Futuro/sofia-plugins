#!/usr/bin/env node
// Confere se toda ferramenta do conector citada no plugin existe no servidor.
//
// Uso: node scripts/conferir-ferramentas.mjs <pasta-do-webapp>
//
// Lê os nomes registrados com server.registerTool("nome", ...) em <pasta-do-webapp>/src e compara com os
// nomes entre crases citados nos .md do plugin. Sai com código 1 se o plugin citar uma ferramenta que o
// servidor não tem, e lista também as ferramentas do servidor que o plugin nunca cita (só aviso).
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const webapp = process.argv[2];
if (!webapp) {
  console.error("Uso: node scripts/conferir-ferramentas.mjs <pasta-do-webapp>");
  process.exit(2);
}

const raiz = join(fileURLToPath(new URL(".", import.meta.url)), "..");
// O plugin é a raiz do repositório.
const plugin = raiz;
const fora = new Set(["node_modules", "tests", "dist", "__pycache__"]);

function arquivos(pasta, fim) {
  return readdirSync(pasta).flatMap((nome) => {
    if (fora.has(nome) || nome.startsWith(".git")) return [];
    const caminho = join(pasta, nome);
    if (statSync(caminho).isDirectory()) return arquivos(caminho, fim);
    return fim.some((f) => nome.endsWith(f)) ? [caminho] : [];
  });
}

const doServidor = new Set();
for (const arquivo of arquivos(join(webapp, "src"), [".ts", ".tsx"])) {
  const texto = readFileSync(arquivo, "utf8");
  for (const m of texto.matchAll(/registerTool\(\s*["'`]([a-z][a-z0-9_]*)["'`]/g)) doServidor.add(m[1]);
}
if (doServidor.size === 0) {
  console.error(`Nenhuma ferramenta achada em ${webapp}/src. A pasta está certa?`);
  process.exit(2);
}

// Famílias de nome que o conector usa. Um nome citado nessas famílias tem de existir no servidor.
const familia = /^(sofia|planejamento|cerebro|referencia|perfil)_[a-z0-9_]+$/;
// As ferramentas de nome avulso que o plugin pode citar. A lista é fixa, e não tirada do servidor, para
// que um nome avulso citado no plugin e sumido do servidor acuse em vez de passar despercebido.
const avulsas = new Set([
  "buscar_no_curso",
  "destravar",
  "escrever_abordagem",
  "glossario",
  "kit",
  "marcar_etapa",
  "onde_estou",
  "preco_e_contrato",
  "preparar_reuniao",
  "ver_etapa",
  "ver_situacao",
]);
const avulsasNovas = [...doServidor].filter((n) => !familia.test(n) && !avulsas.has(n)).sort();

const citadas = new Map();
for (const arquivo of arquivos(plugin, [".md"])) {
  const texto = readFileSync(arquivo, "utf8");
  for (const m of texto.matchAll(/`([a-z][a-z0-9_]*)`/g)) {
    const nome = m[1];
    if (!familia.test(nome) && !avulsas.has(nome)) continue;
    if (!citadas.has(nome)) citadas.set(nome, new Set());
    citadas.get(nome).add(relative(raiz, arquivo));
  }
}

const faltando = [...citadas.keys()].filter((n) => !doServidor.has(n)).sort();
const naoCitadas = [...doServidor].filter((n) => !citadas.has(n)).sort();

console.log(`Servidor: ${doServidor.size} ferramentas. Plugin cita: ${citadas.size}.`);
if (naoCitadas.length) console.log(`Aviso, o plugin não cita: ${naoCitadas.join(", ")}`);
if (avulsasNovas.length)
  console.log(`Aviso, ferramentas avulsas novas no servidor (inclua na lista de avulsas deste script): ${avulsasNovas.join(", ")}`);
if (faltando.length) {
  console.error("O plugin cita ferramentas que o servidor não tem:");
  for (const n of faltando) console.error(`  ${n}  (em ${[...citadas.get(n)].join(", ")})`);
  process.exit(1);
}
console.log("Tudo certo: toda ferramenta citada existe no servidor.");
