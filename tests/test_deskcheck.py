import copy,json,tempfile,unittest
from pathlib import Path
import deskcheck as d
BASE=json.loads(Path('examples/healthy.json').read_text())
class Tests(unittest.TestCase):
 def test_healthy(self): self.assertEqual(d.analyze(BASE),[])
 def test_attention(self): self.assertEqual({x['code'] for x in d.analyze(json.loads(Path('examples/attention.json').read_text()))},{'LOW_MEMORY','LOW_DISK','APIPA','NO_GATEWAY','NO_DNS'})
 def test_thresholds(self):
  x=copy.deepcopy(BASE); x['memory_free_percent']=10; x['disks'][0]['free_percent']=15
  self.assertEqual(d.analyze(x),[])
 def test_empty(self):
  x=copy.deepcopy(BASE); x['disks']=[]; x['interfaces']=[]
  self.assertEqual(len(d.analyze(x)),2)
 def test_extra(self):
  x=copy.deepcopy(BASE); x['hostname']='secret'
  with self.assertRaises(ValueError): d.analyze(x)
 def test_percent(self):
  for v in (True,-1,101,float('nan'),float('inf'),'1',None):
   x=copy.deepcopy(BASE); x['memory_free_percent']=v
   with self.subTest(v=v),self.assertRaises(ValueError): d.analyze(x)
 def test_flags(self):
  x=copy.deepcopy(BASE); x['interfaces'][0]['has_dns']='false'
  with self.assertRaises(ValueError): d.analyze(x)
 def test_version(self):
  x=copy.deepcopy(BASE); x['schema_version']=True
  with self.assertRaises(ValueError): d.analyze(x)
 def test_duplicate(self):
  with self.assertRaises(ValueError): json.loads('{"x":1,"x":2}',object_pairs_hook=d.no_duplicates)
 def test_escaping(self): self.assertNotIn('<script>',d.render([dict(code='<script>',evidence='&',next_step='x')]))
 def test_cli(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'in.json'; out=Path(t)/'out'; p.write_text('\ufeff'+json.dumps(BASE),encoding='utf-8')
   self.assertEqual(d.main([str(p),'--out',str(out)]),0)
   self.assertEqual(json.loads((out/'report.json').read_text()),{'findings':[]})
   p.write_text('{bad'); self.assertEqual(d.main([str(p)]),2)
 def test_size(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'big'; p.write_bytes(b' '*1048577); self.assertEqual(d.main([str(p)]),2)
 def test_no_ipv4(self):
  x=copy.deepcopy(BASE); x['interfaces'][0]['has_ipv4']=False
  self.assertEqual(d.analyze(x)[0]['code'],'NO_IPV4')
 def test_limit(self):
  x=copy.deepcopy(BASE); x['disks']=[{'free_percent':30}]*129
  with self.assertRaises(ValueError): d.analyze(x)
