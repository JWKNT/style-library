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
 const wall=page.slice(page.indexOf('<section id="icons"'),page.indexOf('</main>'));
 assert.equal(sha(wall),'5bfdb7caea7853de0cffc02188a9b96cdb23b9e946e242074f9dbbcdd554d4ef');
 assert.equal(sha(await readFile(new URL('data/icons.json',root))),'d87997164401dd48e3f0fb58ff8b5c1d238c57c9b264c64abba64711aca9e209');
});
