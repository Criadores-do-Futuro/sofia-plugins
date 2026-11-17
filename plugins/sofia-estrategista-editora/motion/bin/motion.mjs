#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { chromium } from 'playwright-core';

const here=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2), command=args.shift();
function opt(name, required=true) { const i=args.indexOf('--'+name); if(i<0){if(required) throw Error(`Informe --${name}`);return null;} if(!args[i+1]||args[i+1].startsWith('--')) throw Error(`Valor ausente para --${name}`); return args[i+1]; }
async function exists(p) {return fs.access(p).then(()=>true,()=>false);}
async function validateProject(p){
  const base=await fs.realpath(p); const config=JSON.parse(await fs.readFile(path.join(base,'motion.json'),'utf8'));
  const {width,height,fps,duration}=config;
  if(!Number.isInteger(width)||!Number.isInteger(height)||width<2||height<2||width%2||height%2||width>4096||height>4096||!Number.isInteger(fps)||fps<1||fps>60||!Number.isFinite(duration)||duration<=0||duration>600) throw Error('motion.json inválido: dimensões pares até 4096, fps inteiro 1–60 e duração até 600 s.');
  await fs.access(path.join(base,'index.html')); await fs.access(path.join(base,'animation.js')); return {base,config};
}
async function fingerprint(base){
  const hash=createHash('sha256');
  async function walk(dir){ for(const item of (await fs.readdir(dir,{withFileTypes:true})).sort((a,b)=>a.name.localeCompare(b.name))){const file=path.join(dir,item.name), relative=path.relative(base,file); if(item.isSymbolicLink()) throw Error(`Links simbólicos não são permitidos no projeto: ${relative}`); if(item.isDirectory()) await walk(file); else if(item.isFile()){hash.update(JSON.stringify(relative)+'\n');hash.update(await fs.readFile(file));hash.update('\n');}}}
  await walk(base);return hash.digest('hex');
}
async function external(base,p){const absolute=path.resolve(p);const realParent=await fs.realpath(path.dirname(absolute));const result=path.join(realParent,path.basename(absolute));if(result===base||result.startsWith(base+path.sep))throw Error('Aprovação e saída devem ficar fora do projeto.');return result;}
async function serve(base){const server=createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost'); const pathname=decodeURIComponent(url.pathname); const requested=path.resolve(base,'.'+pathname); if(requested!==base&&!requested.startsWith(base+path.sep))throw Error('fora do projeto');const real=await fs.realpath(requested);if(real!==base&&!real.startsWith(base+path.sep))throw Error('fora do projeto');const ext=path.extname(real).toLowerCase();const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml','.webp':'image/webp'};res.writeHead(200,{'Content-Type':types[ext]||'application/octet-stream','Cache-Control':'no-store'});res.end(await fs.readFile(real));}catch{res.writeHead(404);res.end();}});await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));return {server,url:`http://127.0.0.1:${server.address().port}/index.html`};}
async function main(){
 if(command==='init'){const target=path.resolve(opt('projeto'));if(await exists(target))throw Error('O destino já existe.');await fs.cp(path.join(here,'../template'),target,{recursive:true,errorOnExist:true});console.log(`Projeto criado: ${target}`);return;}
 const {base,config}=await validateProject(opt('projeto'));
 if(command==='preview'){const {server,url}=await serve(base);console.log(`Abra ${url} para revisar; Ctrl+C encerra a prévia.`);await new Promise(resolve=>server.on('close',resolve));return;}
 if(command==='approve'){const output=await external(base,opt('registro'));const digest=await fingerprint(base);await fs.writeFile(output,JSON.stringify({version:1,project:base,sha256:digest,reviewed_at:new Date().toISOString()},null,2)+'\n',{flag:'wx'});console.log(`Revisão registrada: ${output}`);return;}
 if(command==='render'){
  const approval=JSON.parse(await fs.readFile(await external(base,opt('registro')),'utf8'));const digest=await fingerprint(base);
  if(approval.version!==1||approval.project!==base||approval.sha256!==digest)throw Error('Projeto alterado após revisão ou registro inválido; revise e registre novamente.');
  const output=await external(base,opt('saida')); if(path.extname(output).toLowerCase()!=='.mp4')throw Error('Saída deve terminar em .mp4'); if(await exists(output))throw Error('A saída já existe.');
  const {server,url}=await serve(base);let browser,encoder,ownedOutput=false;
  try{
   const chrome=opt('chrome',false)||process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
   browser=await chromium.launch({headless:true,executablePath:chrome});const page=await browser.newPage({viewport:{width:config.width,height:config.height},deviceScaleFactor:1});
   await page.goto(url+'?render=1');await page.waitForFunction(()=>window.motionReady||window.motionError,{timeout:15000});const err=await page.evaluate(()=>window.motionError);if(err)throw Error(err);
   const canvas=page.locator('canvas'); const total=Math.ceil(config.duration*config.fps);
   const fd=await fs.open(output,'wx'); ownedOutput=true; await fd.close();
   encoder=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(config.fps),'-vcodec','png','-i','pipe:0','-an','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',output],{stdio:['pipe','ignore','pipe']});
   let errors='';encoder.stderr.on('data',d=>errors+=d.toString());const finished=new Promise((resolve,reject)=>{encoder.on('error',reject);encoder.on('close',code=>code===0?resolve():reject(Error(`ffmpeg falhou (${code}): ${errors}`)));});
   encoder.stdin.on('error',()=>{});
   for(let i=0;i<total;i++){await page.evaluate(t=>window.setMotionTime(t),i/config.fps);const png=await canvas.screenshot({animations:'disabled'});if(!encoder.stdin.write(png)) await new Promise((resolve,reject)=>{encoder.stdin.once('drain',resolve);encoder.once('error',reject);encoder.once('close',code=>reject(Error(`ffmpeg encerrou antes do fim (${code})`)));});}
   encoder.stdin.end();await finished;
   if(await fingerprint(base)!==digest) throw Error('Projeto mudou durante o render; resultado descartado.');
   const hash=createHash('sha256').update(await fs.readFile(output)).digest('hex');
   console.log(JSON.stringify({arquivo:output,sha256:hash,quadros:total,duracao_segundos:total/config.fps,projeto:base,revisao:approval.reviewed_at,proximo_passo:'Importar o arquivo na timeline escolhida; elementos internos não são editáveis como camadas.'},null,2));
  }catch(error){if(encoder&&!encoder.killed)encoder.kill();if(ownedOutput)await fs.rm(output,{force:true});throw error;} finally{if(browser)await browser.close();server.close();}
  return;
 }
 throw Error('Comandos: init, preview, approve, render.');
}
main().catch(e=>{console.error(`Erro: ${e.message}`);process.exitCode=1;});
