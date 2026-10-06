#!/usr/bin/env python3
"""Check offline HTML starters and run their actual JS with a small DOM test double.

Python's standard library checks markup/contracts. Node (if available on PATH or
specified with DESIGN_NODE) checks JS syntax and behavior; no npm package needed.
These checks complement a browser pass and do not verify pixel layout or a11y.
"""
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ASSETS = Path(__file__).resolve().parent.parent / "assets"
NAMES = ("interactive-interface.html", "interactive-explainer.html")
NODE = os.environ.get("DESIGN_NODE") or shutil.which("node")


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.nodes, self.scripts, self.styles, self.csp = [], [], [], [], None
        self.external = []
        self.current = None
        self.buffer = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.nodes.append({"tag":tag,"attrs":attrs})
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "content-security-policy":
            self.csp=attrs.get("content", "")
        if tag in ("script","style"):
            self.current=tag
            self.buffer=[]
        if tag in ("script","img","iframe","source","audio","video") and attrs.get("src"):
            self.external.append(attrs["src"])
        if tag=="link" and attrs.get("href"):
            self.external.append(attrs["href"])

    def handle_data(self, data):
        if self.current:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == self.current:
            (self.scripts if tag=="script" else self.styles).append("".join(self.buffer))
            self.current=None


DOM_HARNESS = r'''
const vm=require('node:vm'),assert=require('node:assert/strict');
const data=JSON.parse(require('node:fs').readFileSync(process.argv[2],'utf8'));
class Node {
  constructor(attrs={}) { this.id=attrs.id||'';this.value=attrs.value||'';this.textContent='';this.innerHTML='';this.checked=false;this.attrs={...attrs};this.events={};this.dataset={}; for(const [key,value] of Object.entries(attrs))if(key.startsWith('data-'))this.dataset[key.slice(5)]=value; }
  addEventListener(name,fn) { this.events[name]=fn; }
  setAttribute(name,value) { this.attrs[name]=String(value); }
  getAttribute(name) { return this.attrs[name]??null; }
  focus() { this.focused=true; }
  querySelector() { return new Node(); }
  matches(selector) { return selector==='[data-task]' && this.dataset.task!==undefined; }
}
const nodes=new Map(),filters=[];
for(const entry of data.nodes) { const node=new Node(entry.attrs);if(node.id)nodes.set(node.id,node);if(node.dataset.filter)filters.push(node); }
nodes.get('pattern')&&(nodes.get('pattern').value='steady');
const document={getElementById:id=>{if(!nodes.has(id))nodes.set(id,new Node({id}));return nodes.get(id);},querySelectorAll:selector=>selector==='[data-filter]'?filters:[]};
const context=vm.createContext({document,console});
vm.runInContext(data.script,context,{timeout:2000});
const run=code=>vm.runInContext(code,context,{timeout:2000});
const event=(id,type,target=nodes.get(id))=>nodes.get(id).events[type]({target});
if(data.kind==='interface') {
  assert.equal(String(nodes.get('total-projects').textContent),'6');
  assert.equal(nodes.get('completed-tasks').textContent,'7 / 18');
  nodes.get('search').value='prototype';event('search','input');
  assert.equal(nodes.get('visible-count').textContent,'1 of 6');
  assert.match(nodes.get('project-detail').innerHTML,/Prototype review/);
  const task=new Node();task.dataset.task='0';task.checked=true;event('project-detail','change',task);
  assert.equal(nodes.get('completed-tasks').textContent,'8 / 18');
  assert.match(nodes.get('project-detail').innerHTML,/1 of 3 tasks complete/);
  const status=new Node({id:'project-status'});status.value='active';event('project-detail','change',status);
  assert.equal(String(nodes.get('active-projects').textContent),'4');
  nodes.get('search').value='not-a-project';event('search','input');
  assert.equal(nodes.get('visible-count').textContent,'0 of 6');
  assert.match(nodes.get('project-detail').innerHTML,/Nothing selected/);
  event('add-project','click');
  assert.equal(String(nodes.get('total-projects').textContent),'7');
  assert.equal(nodes.get('completed-tasks').textContent,'8 / 21');
  assert.match(nodes.get('project-detail').innerHTML,/Untitled project 7/);
  assert.equal(nodes.get('search').value,'');
  filters.find(node=>node.dataset.filter==='done').events.click();
  assert.equal(nodes.get('visible-count').textContent,'1 of 7');
  assert.match(nodes.get('project-list').innerHTML,/Analytics notes/);
} else {
  assert.equal(String(nodes.get('finished-result').textContent),'72');
  assert.equal(String(nodes.get('queue-result').textContent),'24');
  event('preset-recovery','click');
  assert.equal(String(nodes.get('queue-result').textContent),'0');
  assert.equal(nodes.get('utilization-result').textContent,'75%');
  event('preset-balanced','click');
  assert.equal(String(nodes.get('finished-result').textContent),'80');
  assert.equal(String(nodes.get('queue-result').textContent),'0');
  // Burst totals equal nominal capacity, but early idle capacity is lost.
  nodes.get('arrival').value='8';nodes.get('capacity').value='10';nodes.get('pattern').value='burst';event('pattern','change');
  assert.equal(String(nodes.get('finished-result').textContent),'74');
  assert.equal(String(nodes.get('queue-result').textContent),'6');
  assert.match(nodes.get('insight').textContent,/More items arrived than finished/);
  assert.match(nodes.get('insight').textContent,/cannot carry over/);
  assert.equal((nodes.get('hourly-table').innerHTML.match(/<tr>/g)||[]).length,8);
  assert.equal((nodes.get('chart-content').innerHTML.match(/<rect /g)||[]).length,16);
  // Test conservation and execution bounds over many deterministic scenarios.
  run(`for(let arrival=2;arrival<=24;arrival+=3)for(let capacity=2;capacity<=24;capacity+=4)for(const pattern of ['steady','burst']) {
    const inputs={arrival,capacity,initial:17,duration:8,pattern};const result=simulate(inputs);
    if(result.waiting+result.totalFinished!==inputs.initial+result.totalArrived)throw Error('Conservation failed');
    if(result.hours.some(hour=>hour.finished>capacity||hour.waiting<0))throw Error('Physical bounds failed');
  }`);
}
console.log(data.kind+' actual-script behavior OK');
'''


class DigitalAssetTests(unittest.TestCase):
    def test_offline_markup_unique_ids_and_semantic_controls(self):
        for name in NAMES:
            with self.subTest(asset=name):
                doc=Document((ASSETS/name).read_text(encoding="utf-8"))
                self.assertEqual(len(doc.ids),len(set(doc.ids)),"Duplicate IDs")
                self.assertEqual(doc.external,[],"Starter must be self-contained")
                self.assertEqual(len(doc.scripts),1)
                self.assertTrue(doc.styles)
                for directive in ("default-src 'none'","connect-src 'none'","font-src 'none'","base-uri 'none'","form-action 'none'"):
                    self.assertIn(directive,doc.csp)
                labels={node["attrs"].get("for") for node in doc.nodes if node["tag"]=="label"}
                for node in doc.nodes:
                    if node["tag"] in ("input","select"):
                        self.assertIn(node["attrs"].get("id"),labels)
                self.assertTrue(any(node["tag"]=="main" for node in doc.nodes))
                self.assertIn(":focus-visible",doc.styles[0])
                self.assertIn("@media",doc.styles[0])

    @unittest.skipUnless(NODE,"Node is optional; set DESIGN_NODE or put node on PATH for script checks")
    def test_actual_javascript_syntax_and_interactions(self):
        for name in NAMES:
            with self.subTest(asset=name),tempfile.TemporaryDirectory(prefix="digital-starter-test-") as folder:
                doc=Document((ASSETS/name).read_text(encoding="utf-8"))
                temporary=Path(folder)
                script=temporary/"starter.js";script.write_text(doc.scripts[0],encoding="utf-8")
                syntax=subprocess.run([NODE,"--check",str(script)],capture_output=True,text=True,timeout=15)
                self.assertEqual(syntax.returncode,0,syntax.stderr)
                data=temporary/"data.json"
                data.write_text(json.dumps({"script":doc.scripts[0],"nodes":doc.nodes,"kind":"interface" if name==NAMES[0] else "explainer"}),encoding="utf-8")
                harness=temporary/"check.cjs";harness.write_text(DOM_HARNESS,encoding="utf-8")
                result=subprocess.run([NODE,str(harness),str(data)],capture_output=True,text=True,timeout=15)
                self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
