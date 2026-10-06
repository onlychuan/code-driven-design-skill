#!/usr/bin/env python3
"""Offline SVG asset-board contracts and actual inline-JS export behavior.

No npm modules are needed. Put Node on PATH or set DESIGN_NODE to run JS tests.
The DOM test double checks state/output behavior; a browser still checks layout.
"""
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

ASSET=Path(__file__).resolve().parent.parent/"assets"/"logo-icon-study.html"
NODE=os.environ.get("DESIGN_NODE") or shutil.which("node")


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.nodes,self.ids,self.scripts,self.external=[],[],[],[]
        self.script=None
        self.csp=""
        self.feed(source)

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        self.nodes.append({"tag":tag,"attrs":attrs})
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag=="meta" and attrs.get("http-equiv","").lower()=="content-security-policy":
            self.csp=attrs.get("content","")
        if tag=="script":
            self.script=[]
        if tag in ("script","img","iframe","source","audio","video") and attrs.get("src"):
            self.external.append(attrs["src"])
        if tag=="link" and attrs.get("href"):
            self.external.append(attrs["href"])

    def handle_data(self,data):
        if self.script is not None:
            self.script.append(data)

    def handle_endtag(self,tag):
        if tag=="script" and self.script is not None:
            self.scripts.append("".join(self.script))
            self.script=None


HARNESS=r'''
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
class Node {
  constructor(attrs={}) { this.id=attrs.id||'';this.value=attrs.value||'';this.attrs={...attrs};this.dataset={};this.events={};this.innerHTML='';this.textContent='';for(const [name,value] of Object.entries(attrs))if(name.startsWith('data-'))this.dataset[name.slice(5)]=value; }
  addEventListener(name,fn) { this.events[name]=fn; }
  focus() { this.focused=true; }
  select() { this.selected=true; }
  querySelector() { return new Node(); }
  closest() { return this; }
  remove() { this.removed=true; }
  click() { if(this.href)downloads.push({filename:this.download,source:urls.get(this.href).parts.join(''),type:urls.get(this.href).options.type}); }
}
const nodes=new Map(),styles={},downloads=[],urls=new Map(),revoked=[];
for(const item of data.nodes)if(item.attrs.id)nodes.set(item.attrs.id,new Node(item.attrs));
const document={getElementById:id=>nodes.get(id),documentElement:{style:{setProperty:(key,value)=>styles[key]=value}},body:{appendChild:()=>{}},createElement:()=>new Node()};
class BlobDouble { constructor(parts,options) { this.parts=parts;this.options=options; } }
const URLDouble={createObjectURL:blob=>{const id='blob:demo-'+urls.size;urls.set(id,blob);return id;},revokeObjectURL:id=>revoked.push(id)};
const context=vm.createContext({document,Blob:BlobDouble,URL:URLDouble,setTimeout:fn=>fn(),console});
vm.runInContext(data.script,context,{timeout:2000});
const run=code=>vm.runInContext(code,context,{timeout:2000});
const event=(id,type)=>nodes.get(id).events[type]({target:nodes.get(id)});
const exportedAssets=[];
for(const kind of ['mark','search','add','check','tune'])exportedAssets.push({kind,phase:'initial',source:run(`exportSVG('${kind}')`)});
assert.match(nodes.get('size-grid').innerHTML,/width="16"/);
assert.match(nodes.get('size-grid').innerHTML,/width="20"/);
assert.match(nodes.get('size-grid').innerHTML,/width="24"/);
assert.match(nodes.get('size-grid').innerHTML,/width="32"/);
function checkTitleIds() { const board=['lockups','size-grid','icon-grid'].map(id=>nodes.get(id).innerHTML).join('');const ids=[...board.matchAll(/<title id="([^"]+)"/g)].map(match=>match[1]);assert.equal(ids.length,7);assert.equal(new Set(ids).size,ids.length);assert.equal((nodes.get('icon-grid').innerHTML.match(/aria-hidden="true" focusable="false"/g)||[]).length,4);return ids; }
checkTitleIds();
nodes.get('palette').value='teal';event('palette','change');
assert.equal(styles['--accent'],'#14786D');
nodes.get('background').value='dark';event('background','change');
assert.equal(styles['--preview'],'#252935');
nodes.get('mark-mode').value='reverse';event('mark-mode','change');
assert.match(nodes.get('svg-source').value,/fill="#FFFFFF"/);
nodes.get('stroke').value='2.5';event('stroke','input');
assert.equal(nodes.get('stroke-output').textContent,'2.5 units');
const button=new Node({'data-icon':'search'});
nodes.get('icon-grid').events.click({target:button});
assert.match(nodes.get('svg-source').value,/viewBox="0 0 24 24"/);
assert.match(nodes.get('svg-source').value,/stroke-width="2.5"/);
assert.match(nodes.get('size-caption').textContent,/Search/);
event('select-source','click');assert.equal(nodes.get('svg-source').selected,true);
event('download-svg','click');
assert.equal(downloads.length,1);assert.equal(downloads[0].filename,'demo-search.svg');assert.equal(downloads[0].type,'image/svg+xml;charset=utf-8');assert.equal(revoked.length,1);
assert.equal(downloads[0].source,nodes.get('svg-source').value);
for(const kind of ['mark','search','add','check','tune'])exportedAssets.push({kind,phase:'dark-teal',source:run(`exportSVG('${kind}')`)});
event('choose-mark','click');assert.match(nodes.get('export-caption').textContent,/reversed/);
event('download-svg','click');assert.equal(downloads[1].filename,'demo-mark-reverse.svg');
nodes.get('mark-mode').value='mono';event('mark-mode','change');
exportedAssets.push({kind:'mark',phase:'mono',source:run("exportSVG('mark')")});
assert.match(nodes.get('export-caption').textContent,/monochrome/);
event('download-svg','click');assert.equal(downloads[2].filename,'demo-mark-mono.svg');
nodes.get('mark-mode').value='color';event('mark-mode','change');
event('download-svg','click');assert.equal(downloads[3].filename,'demo-mark-color.svg');
assert.equal(new Set(downloads.map(download=>download.filename)).size,4);
const titleIds=checkTitleIds();
console.log(JSON.stringify({exports:exportedAssets,downloads,titleIds}));
'''


class LogoIconAssetTests(unittest.TestCase):
    def test_offline_markup_and_control_contracts(self):
        doc=Document(ASSET.read_text(encoding="utf-8"))
        self.assertEqual(doc.external,[])
        self.assertEqual(len(doc.ids),len(set(doc.ids)))
        self.assertEqual(len(doc.scripts),1)
        for directive in ("default-src 'none'","connect-src 'none'","font-src 'none'","base-uri 'none'","form-action 'none'"):
            self.assertIn(directive,doc.csp)
        labels={node["attrs"].get("for") for node in doc.nodes if node["tag"]=="label"}
        for node in doc.nodes:
            if node["tag"] in ("input","select","textarea"):
                self.assertIn(node["attrs"].get("id"),labels)
        self.assertIn("System-font name stays separate",ASSET.read_text(encoding="utf-8"))

    @unittest.skipUnless(NODE,"Node is optional; set DESIGN_NODE or put node on PATH")
    def test_actual_script_state_downloads_and_standalone_svgs(self):
        doc=Document(ASSET.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="logo-icon-study-") as folder:
            temporary=Path(folder)
            script=temporary/"study.js";script.write_text(doc.scripts[0],encoding="utf-8")
            syntax=subprocess.run([NODE,"--check",str(script)],capture_output=True,text=True,timeout=15)
            self.assertEqual(syntax.returncode,0,syntax.stderr)
            payload=temporary/"data.json";payload.write_text(json.dumps({"script":doc.scripts[0],"nodes":doc.nodes}),encoding="utf-8")
            harness=temporary/"harness.cjs";harness.write_text(HARNESS,encoding="utf-8")
            result=subprocess.run([NODE,str(harness),str(payload)],capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            artifacts=json.loads(result.stdout)
        for item in artifacts["exports"]:
            with self.subTest(asset=item["kind"],phase=item["phase"]):
                root=ET.fromstring(item["source"])
                self.assertEqual(root.tag,"{http://www.w3.org/2000/svg}svg")
                self.assertEqual(root.get("viewBox"),"0 0 32 32" if item["kind"]=="mark" else "0 0 24 24")
                self.assertEqual(root.get("aria-labelledby"),"asset-title")
                self.assertTrue(root.find("{http://www.w3.org/2000/svg}path") is not None or root.find("{http://www.w3.org/2000/svg}g") is not None)
                ids=[node.get("id") for node in root.iter() if node.get("id")]
                self.assertEqual(ids,["asset-title"])
                for node in root.iter():
                    self.assertIn(node.tag.split("}")[-1],{"svg","title","g","path","circle"})
                    for key,value in node.attrib.items():
                        self.assertFalse(key.lower().startswith("on"))
                        self.assertNotIn(key.split("}")[-1],{"href","src"})
                        self.assertNotIn("url(",value.lower())
                if item["kind"]!="mark":
                    group=root.find("{http://www.w3.org/2000/svg}g")
                    self.assertEqual(group.get("stroke"),"currentColor")
                    self.assertEqual(group.get("fill"),"none")
                    self.assertEqual(group.get("stroke-linecap"),"round")
                    self.assertEqual(group.get("stroke-linejoin"),"round")
                    self.assertEqual(group.get("stroke-width"),"2" if item["phase"]=="initial" else "2.5")
                    self.assertEqual(root.get("color"),"#5C49C4" if item["phase"]=="initial" else "#7DC8BA")
                elif item["phase"]=="dark-teal":
                    self.assertTrue(all(path.get("fill")=="#FFFFFF" for path in root.findall("{http://www.w3.org/2000/svg}path")))
                elif item["phase"]=="mono":
                    self.assertTrue(all(path.get("fill")=="#242A34" for path in root.findall("{http://www.w3.org/2000/svg}path")))


if __name__=="__main__":
    unittest.main()
