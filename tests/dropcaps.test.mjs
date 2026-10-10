import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {crc32,makeZip,downloadAlphabet,zipEntryName} from '../assets/dropcaps.js';
const root=new URL('../',import.meta.url);
const read=p=>readFile(new URL(p,root),'utf8');
const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
test('ten complete alphabets contain distinct self-contained artwork',async()=>{
 const sets=JSON.parse(await read('data/dropcaps.json'));assert.equal(sets.length,10);
 const hashes=new Set();
 for(const set of sets){
  assert.ok(set.name);assert.ok(set.license_files.length);assert.ok(set.design_changes);
  for(const path of set.license_files)assert.ok((await read(path)).length>20);
  for(const letter of alphabet){
   const svg=await read(`assets/Dropcaps/${set.id}/${letter}.svg`);
   assert.match(svg,/<svg\b[^>]*\bviewBox=/);assert.match(svg,/<title\b/);assert.match(svg,/<path\b/);
   assert.doesNotMatch(svg,/<(?:script|text|image|foreignObject)\b|\bon\w+=|(?:href|src)=["']https?:/i);
   const geometry=svg.replace(/<title\b[^>]*>.*?<\/title>/gs,'').replace(/<desc>.*?<\/desc>/gs,'').replace(/<metadata>.*?<\/metadata>/gs,'');
   const hash=createHash('sha256').update(geometry).digest('hex');
   assert.ok(!hashes.has(hash),`${set.id} ${letter} duplicates artwork`);hashes.add(hash);
  }
 }
 assert.equal(hashes.size,260);
});
test('dropcap panel contains 260 accessible SVG downloads and ten ZIP controls',async()=>{
 const html=await read('index.html');const section=html.match(/<section id="dropcaps"[\s\S]*?<\/section>/)[0];
 assert.equal((section.match(/class="dropcap-set"/g)||[]).length,10);
 assert.equal((section.match(/class="dropcap-zip"/g)||[]).length,10);
 assert.equal((section.match(/download="[a-z]+-[A-Z]\.svg"/g)||[]).length,260);
 assert.match(html,/<a href="#dropcaps" id="tab-dropcaps">Dropcaps<\/a>/);
 assert.doesNotMatch(section,/<text\b/);
 const sets=JSON.parse(await read('data/dropcaps.json'));
 for(const set of sets)for(const letter of alphabet)assert.ok(section.includes(`aria-label="Download ${set.name} ${letter} SVG"`));
});
test('ZIP stores exact SVG bytes with valid headers, directory offsets, CRCs and UTF-8 names',async()=>{
 assert.equal(crc32(new TextEncoder().encode('123456789')),0xcbf43926);
 const sets=JSON.parse(await read('data/dropcaps.json'));
 for(const set of sets){
  const files=[];for(const letter of alphabet)files.push({name:`${set.id}/${letter}.svg`,bytes:new Uint8Array(await readFile(new URL(`assets/Dropcaps/${set.id}/${letter}.svg`,root)))});
  for(const path of set.download_files)files.push({name:zipEntryName(set.id,path),bytes:new Uint8Array(await readFile(new URL(path,root)))});
  const bytes=new Uint8Array(await makeZip(files).arrayBuffer()),view=new DataView(bytes.buffer);let offset=0;
  for(const file of files){
   assert.equal(view.getUint32(offset,true),0x04034b50);assert.equal(view.getUint16(offset+6,true),0x0800);
   const length=view.getUint16(offset+26,true);assert.equal(view.getUint32(offset+14,true),crc32(file.bytes));
   assert.equal(new TextDecoder().decode(bytes.slice(offset+30,offset+30+length)),file.name);
   assert.deepEqual(bytes.slice(offset+30+length,offset+30+length+file.bytes.length),file.bytes);
   offset+=30+length+file.bytes.length;
  }
  const centralOffset=offset;
  for(const file of files){assert.equal(view.getUint32(offset,true),0x02014b50);offset+=46+new TextEncoder().encode(file.name).length;}
  assert.equal(view.getUint32(offset,true),0x06054b50);assert.equal(view.getUint16(offset+8,true),files.length);
  assert.equal(view.getUint32(offset+16,true),centralOffset);assert.equal(offset+22,bytes.length);
 }
});
test('ZIP failure resets the control for a retry; repeated clicks do not duplicate requests',async()=>{
 const savedFetch=globalThis.fetch;const status={textContent:''};let calls=0,release;
 const button={disabled:false,dataset:{set:'test',files:''},setAttribute(){},removeAttribute(){},closest(){return {querySelector(){return status;},querySelectorAll(){return [{getAttribute(){return 'assets/Dropcaps/test/A.svg';}}];}};}};
 globalThis.fetch=()=>{calls++;return new Promise(resolve=>{release=()=>resolve({ok:false});});};
 try{const pending=downloadAlphabet(button);assert.equal(button.disabled,true);await downloadAlphabet(button);assert.equal(calls,1);release();await pending;assert.equal(button.disabled,false);assert.match(status.textContent,/Try again/);}finally{globalThis.fetch=savedFetch;}
});
