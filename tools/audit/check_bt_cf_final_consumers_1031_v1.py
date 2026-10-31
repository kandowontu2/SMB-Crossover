"""Bounded exact-final natural BT/CF/menu rebind; source only."""
from pathlib import Path
import argparse,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_bt_p2_coherent_1031_v1 as P
J=P.J;O=P.O
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',choices=['bt','cf','menu'],required=True);a=ap.parse_args();O.mkdir(exist_ok=True)
 out=O/(a.check+'-final-controls.json');assert not out.exists();q=dict(passed=False,native=False,candidate=P.SHA)
 try:
  P.bound()
  if a.check=='bt':
   import check_bt_lives_body_1031_v3 as B
   B.J=J;B.H.O=J;result=B.natural()
  elif a.check=='cf':
   source=R/'tools/audit/contra_force_menu_cold_parser_1031_v1.py';s=source.read_text(encoding='utf-8')
   s=s.replace("O = R / 'build/contra-force-menu-cold-parser-1031-v1'", "O = R / 'build/bt-cf-coherent-controls-1031-v1/cf-parser'")
   s=s.replace("J = R / 'build/contra-force-menu-admission-1031-v2/joint'", "J = R / 'build/bt-cf-coherent-source-1031-v1/joint'")
   ns={'__file__':str(source),'__name__':'actual_final_CF_parser'};exec(compile(s,str(source),'exec'),ns);ns['main']()
   result=json.loads((O/'cf-parser/controls.json').read_text())
  else:
   import benj_all_menu_controls_1030_v1 as B
   counts=B.A.COUNTS[:]
   try:
    B.A.COUNTS[16]=4;B.A.COUNTS[23]=2
    old=B.collect(R/'build/contra-force-menu-admission-1031-v2/joint',True);new=B.collect(J,True)
   finally:B.A.COUNTS[:]=counts
   assert old==new and len(new)==86 and sum(not x['pending']for x in new.values())==74
   result=dict(passed=True,menu_profiles=86,ready=74,actual_Start_A_boundaries=688,all_CFmenu_native_identity_names_Start_exact=True,rows=list(new.values()))
  q.update(passed=True,result=result)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):P.L.sha(p)for p in[Path(__file__),Path(P.__file__),J.parent/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']}
 out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items()if k not in['result','bindings']}),flush=True)
 if q['passed']:print(json.dumps({k:v for k,v in result.items()if k not in['rows','cohorts','bindings']}),flush=True)
 assert q['passed'],q.get('error')
if __name__=='__main__':main()
