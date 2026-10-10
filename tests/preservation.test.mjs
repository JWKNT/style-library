import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const root=new URL('../',import.meta.url);
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
test('the original ten TTF and WOFF2 files remain byte-identical',async()=>{
 const hashes=JSON.parse(await readFile(new URL('tests/original-font-hashes.json',root),'utf8'));
 for(const [path,expected] of Object.entries(hashes))assert.equal(sha(await readFile(new URL(path,root))),expected,path);
});
test('the complete icon wall and icon manifest remain byte-identical',async()=>{
 const page=await readFile(new URL('index.html',root),'utf8');
 const wall=page.slice(page.indexOf('<section id="icons"'),page.indexOf('</section>',page.indexOf('<section id="icons"'))+'</section>'.length);
 assert.equal(sha(wall),'5bfdb7caea7853de0cffc02188a9b96cdb23b9e946e242074f9dbbcdd554d4ef');
 assert.equal(sha(await readFile(new URL('data/icons.json',root))),'d87997164401dd48e3f0fb58ff8b5c1d238c57c9b264c64abba64711aca9e209');
});

test('all 100 font pairs and 1148 icon SVGs retain their pre-dropcap bytes',async()=>{
 const fonts=JSON.parse(await readFile(new URL('data/fonts.json',root),'utf8'));
 const icons=JSON.parse(await readFile(new URL('data/icons.json',root),'utf8'));
 const paths=[...fonts.flatMap(f=>[f.ttf,f.woff2]),...icons.map(i=>i.svg)].sort();
 assert.equal(paths.length,1348);
 const lines=[];for(const path of paths)lines.push(path+'\0'+sha(await readFile(new URL(path,root))));
 assert.equal(sha(lines.join('\n')),'0fd653bee9db826284314aacedbc69c30e67ce18da847d630a2f226afb98768e');
});
