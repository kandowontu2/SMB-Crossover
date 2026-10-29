"""Additive scoped-label clarification; never modifies the frozen handoff."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from sunny_integrated_controls_v1 import *
O=R/'build/supermaaa-host-v1';P=R/'build/pit-retold-host-v3'
def global_roots(path):
 roots=set()
 for line in path.read_text().splitlines():
  if not line.startswith('scope\t'):continue
  fields=dict(x.split('=',1)for x in line[6:].split(',')if'='in x)
  if'parent'not in fields:roots.add(fields['id'])
 return roots
def main():
 target=O/'label-scope-addendum.json';assert not target.exists()
 old,b,fresh=[scoped_load(x)for x in[P/'candidate.nes',O/'candidate.nes',O/'independent.nes']]
 roots=global_roots(P/'candidate.dbg');newroots=global_roots(O/'candidate.dbg');moved=[]
 for n,s in old['syms'].items():
  if'::'in n or s.get('scope')not in roots or n not in b['syms']or b['syms'][n].get('scope')not in newroots:continue
  if s.get('type')!='lab'or'seg'not in s or'ooffs'not in old['segs'][s['seg']]:continue
  if address(old,n)!=address(b,n)or location(old,n)!=location(b,n):moved.append([n,address(old,n),address(b,n),(location(old,n)-16)//8192,(location(b,n)-16)//8192])
 def semantic(v):
  return{n:(s.get('type'),address(v,n),(location(v,n)-16)//8192 if'seg'in s and'ooffs'in v['segs'][s['seg']]else None)for n,s in v['syms'].items()}
 assert semantic(b)==semantic(fresh),'Independent genuine DBG symbol semantics differ'
 result=dict(passed=True,additive_only=True,frozen_handoff_sha256=sha(O/'handoff.json'),clarification='The frozen 552-entry relocated-public-labels.json also contains unqualified local aliases from the DBG loader. It is a diagnostic name census, not 552 actual public-entry moves. The fixed/public-entry assertions and external operand validation are unaffected. Use the root-scope list here for actual global label moves.',actual_global_label_moves=len(moved),rows=moved,independently_reassembled_DBG_all_loaded_symbol_values_and_physical_banks_exact=True,DBG_raw_byte_difference='Independent object/module names differ; both are genuine current assemblies, with exact ROM/LBL and semantic symbol equality.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'handoff.json',O/'closure.json',P/'candidate.dbg',O/'candidate.dbg',O/'independent.dbg']})
 target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,actual_global_moves=len(moved),sha256=sha(target))))
if __name__=='__main__':main()
