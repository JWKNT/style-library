import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const script=await readFile(new URL('../assets/app.js',import.meta.url),'utf8');
function setup({observer=true}={}){
 const handlers=new Map();
 const element=(props={})=>({hidden:false,tabIndex:0,attrs:{},...props,setAttribute(k,v){this.attrs[k]=v;},addEventListener(k,fn){const a=this.events??={};(a[k]??=[]).push(fn);},focus(){document.activeElement=this;}});
 const tabs=[element({hash:'#fonts'}),element({hash:'#icons'})];
 const panels=[element({id:'fonts'}),element({id:'icons'})];const bar=element();const sample=element();
 const items=Array.from({length:100},(_,i)=>element({dataset:{fontFamily:`Family ${i}`,fontUrl:`assets/Webfonts/font${i}.woff2`,fontFallback:'serif'},preview:{style:{},textContent:''},querySelector(){return this.preview;},getBoundingClientRect(){return {top:i*200,bottom:i*200+180};}}));
 const fontSet=[];const requested=[];let onIntersection;const observed=new Set();
 const document={activeElement:tabs[0],fonts:{add(f){fontSet.push(f);}},querySelector(s){return ({'.tabs':bar,'#fonts':panels[0],'#icons':panels[1],'#sample':sample})[s];},querySelectorAll(s){return ({'.tabs a':tabs,'.font-item':items,'.font-preview':items.map(i=>i.preview)})[s];}};
 const location={hash:''};const window={innerHeight:800,addEventListener(k,fn){handlers.set(k,fn);}};
 class IO{constructor(fn){onIntersection=fn;}observe(x){observed.add(x);}unobserve(x){observed.delete(x);}}
 class FontFace{constructor(family,url){this.family=family;this.url=url;}async load(){requested.push(this.url);return this;}}
 if(observer)window.IntersectionObserver=IO;
 const context={document,window,location,FontFace,IntersectionObserver:IO,requestAnimationFrame(fn){queueMicrotask(fn);},history:{replaceState(a,b,hash){location.hash=hash;},pushState(a,b,hash){location.hash=hash;}}};
 vm.runInNewContext(script,context);
 return {items,tabs,panels,bar,sample,document,location,requested,fontSet,observed,intersect:(index)=>onIntersection([{target:items[index],isIntersecting:true}])};
}
const settle=()=>new Promise(resolve=>setImmediate(resolve));
test('font requests wait for an intersecting preview and load once',async()=>{
 const s=setup();assert.equal(s.requested.length,0);assert.equal(s.observed.size,100);
 s.intersect(3);await settle();assert.equal(s.requested.length,1);assert.equal(s.fontSet.length,1);
 assert.equal(s.items[3].dataset.fontStatus,'loaded');assert.match(s.items[3].preview.style.fontFamily,/Family 3/);
 s.intersect(3);await settle();assert.equal(s.requested.length,1);assert.equal(s.observed.size,99);
});
test('shared sample updates every preview, including fonts not loaded yet',()=>{
 const s=setup();s.sample.events.input[0]({target:{value:'Sphinx 0O1lI AV fi'}});
 assert.ok(s.items.every(i=>i.preview.textContent==='Sphinx 0O1lI AV fi'));assert.equal(s.requested.length,0);
});
test('tab clicks and keyboard keep panels and focus synchronized',()=>{
 const s=setup();s.tabs[1].events.click[0]({preventDefault(){}});assert.equal(s.location.hash,'#icons');assert.ok(s.panels[0].hidden);assert.ok(!s.panels[1].hidden);
 s.document.activeElement=s.tabs[1];s.bar.events.keydown[0]({key:'Home',preventDefault(){}});assert.equal(s.location.hash,'#fonts');assert.ok(!s.panels[0].hidden);assert.equal(s.document.activeElement,s.tabs[0]);
 s.bar.events.keydown[0]({key:'End',preventDefault(){}});assert.equal(s.location.hash,'#icons');assert.ok(s.panels[0].hidden);
});
test('browsers without IntersectionObserver load only nearby previews',async()=>{
 const s=setup({observer:false});await settle();assert.ok(s.requested.length>0);assert.ok(s.requested.length<10);
});
test('font loading is script-controlled with a no-script CSS fallback',async()=>{
 const page=await readFile(new URL('../index.html',import.meta.url),'utf8');
 assert.match(page,/<noscript><link rel="stylesheet" href="assets\/Webfonts\/fonts.css[^\"]*"><\/noscript>/);
 assert.doesNotMatch(page.replace(/<noscript>.*?<\/noscript>/gs,''),/rel="stylesheet" href="assets\/Webfonts\/fonts.css/);
 assert.match(script,/IntersectionObserver/);assert.match(script,/new FontFace/);
 assert.match(page,/data-font-family=/);assert.match(page,/data-font-url=/);
});
