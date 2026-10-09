import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const root=new URL('../',import.meta.url);
const read=p=>readFile(new URL(p,root),'utf8');

test('one hundred font families retain both formats',async()=>{
  const fonts=JSON.parse(await read('data/fonts.json'));
  assert.equal(fonts.length,100);assert.equal(new Set(fonts.map(f=>f.family)).size,100);
  for(const f of fonts)for(const key of ['ttf','woff2']){
    const bytes=await readFile(new URL(f[key],root));assert.ok(bytes.length>1000);
    assert.equal(bytes.subarray(0,4).toString('hex'),key==='woff2'?'774f4632':'00010000');
  }
});

test('1148 stable unique IDs point to 1148 safe SVG downloads',async()=>{
  const icons=JSON.parse(await read('data/icons.json'));
  assert.equal(icons.length,1148);assert.equal(new Set(icons.map(x=>x.id)).size,1148);
  assert.equal(new Set(icons.map(x=>x.svg)).size,1148);
  assert.equal(icons.filter(x=>x.legacyId).length,148);
  const addedHashes=new Set();
  for(const [i,icon] of icons.entries()){
    assert.equal(icon.id,`i${String(i+1).padStart(4,'0')}`);
    assert.ok(icon.name);const svg=await read(icon.svg);
    assert.match(svg,/<svg[^>]*viewBox="0 0 24 24"/);
    assert.doesNotMatch(svg,/<script|<image|<foreignObject|\bon\w+=|https?:\/\/(?!www.w3.org)/i);
    if(i>=148){
      assert.ok(icon.svg.endsWith(`/${icon.id}.svg`));
      const geometry=svg.replace(/<title>.*?<\/title>/gs,'').replace(/\s+/g,' ').trim();
      const hash=createHash('sha256').update(geometry).digest('hex');
      assert.ok(!addedHashes.has(hash),`Duplicate geometry: ${icon.id}`);addedHashes.add(hash);
    }
  }
});

test('one continuous icon wall contains only preview and ID labels',async()=>{
  const page=await read('index.html');const icons=JSON.parse(await read('data/icons.json'));
  assert.equal((page.match(/class="font-item"/g)||[]).length,100);
  assert.equal((page.match(/class="icon-item"/g)||[]).length,1148);
  assert.equal((page.match(/class="icon-grid"/g)||[]).length,1);
  assert.doesNotMatch(page,/icon-collection/);
  const wall=page.slice(page.indexOf('<section id="icons"'),page.indexOf('</main>'));
  assert.doesNotMatch(wall,/<h[1-6]|<select|<button|<input/);
  assert.deepEqual([...wall.matchAll(/<span class="icon-label">([^<]+)<\/span>/g)].map(m=>m[1]),icons.map(x=>x.id));
  for(const icon of icons){
    assert.ok(wall.includes(`id="${icon.id}"`));
    assert.ok(wall.includes(`href="${icon.svg}" download="${icon.id}.svg"`));
    assert.ok(wall.includes(`aria-label="Download ${icon.id}: `));
  }
  assert.match(page,/href="https:\/\/jehlp.net\/"/);
  assert.match(page,/<button disabled type="button">Dropcaps<\/button>/);
  assert.match(page,/href="licenses.html"/);
  for(const match of page.matchAll(/(?:href|src)="((?:assets|data)\/[^"?#]+)"/g))await access(new URL(match[1],root));
});

test('font license links and design records point to bundled files',async()=>{
 const page=await read('licenses.html');
 for(const match of page.matchAll(/href="((?:licenses|sources|data)\/[^"?#]+)"/g))await access(new URL(match[1],root));
 const fonts=JSON.parse(await read('data/fonts.json'));
 for(const font of fonts.slice(10)){
  assert.ok(font.basis_and_license);assert.ok(font.design_changes.length);
  await access(new URL(font.design_metadata,root));
  assert.equal(font.ascii_complete,true);assert.ok(font.glyph_count>=95);
 }
});
