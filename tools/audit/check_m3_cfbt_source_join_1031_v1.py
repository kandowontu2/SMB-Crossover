"""Rebind qualified M3 and installed68 foreign controls to genuine final shared join."""
from pathlib import Path
import argparse,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_smb3plus_low_table_factor_1031_v1 as F
from link_pit_rygar_sophia_audit_cpu import scoped_load
O=R/'build/m3-cfbt-source-join-v1';J=O/'joint'
E=R/'build/smb3plus-low-table-factor-host-1031-v4/joint'
C=R/'build/bt-native-world-source-v2/joint'
B=F.B
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',choices=['regressions','pixels','menu','whole','foreign','vectors'],required=True);a=ap.parse_args()
 stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage);assert stage['candidate']==B.sha(J/'candidate.nes')=='79634f4581f223293a86d2bae28a0cc8ad05949a24f29695433b806eccf6a4b3'
 out=O/(a.check+'-controls-v1.json');assert not out.exists()
 F.O=O;F.J=J;F.P=E;F.BS=[scoped_load(p/'candidate.nes')for p in[E,J]]
 q=dict(passed=False,native=False,source_CPU=True,candidate=stage['candidate'],check=a.check)
 try:
  if a.check in['regressions','pixels','vectors']:result=getattr(F,a.check)()
  elif a.check=='menu':
   p=R/'tools/audit/smb3plus_menu_controls_1031_v1.py';s=p.read_text()
   s=s.replace("O=R/'build/smb3plus-menu-host-1031-v4';J=O/'joint'",f"O=R/{O.relative_to(R).as_posix()!r};J=O/'joint'")
   s=s.replace("P=R/'build/smb3plus-peach-float-host-1031-v4/joint'",f"P=R/{C.relative_to(R).as_posix()!r}")
   s=s.replace("stage['status_names'][variant]","['MARIO3 ','LUIGI3 ',' TOAD3 ',' PEACH3'][variant]").replace("stage['limits']","stage['limitations']")
   ns={'__file__':str(p),'__name__':'joined_current_menu'};exec(compile(s,str(p),'exec'),ns);ns['main']();result=json.loads((O/'menu-controls-v1.json').read_text())
  elif a.check=='whole':
   p=R/'tools/audit/smb3plus_whole_controller_edges_1031_v1.py';s=p.read_text().replace('smb3plus-whole-controller-edges-1031-v1','m3-cfbt-whole-controller-v1').replace('smb3plus-peach-complete-controller-1031-v3',O.name)
   s=s.replace('text=prior.read_text()',"text=prior.read_text().replace('for i in range(8):bus.ram','for i in range(4):bus.ram')")
   ns={'__file__':str(p),'__name__':'joined_original_controller'};exec(compile(s,str(p),'exec'),ns);ns['main']();result=json.loads((R/'build/m3-cfbt-whole-controller-v1/probe.json').read_text())
  else:
   import cf_bt_shared_foreign_main_v1 as T
   T.J=J;T.P=E;T.O=O/'foreign';T.main();result=json.loads((T.O/'controls.json').read_text())
  q.update(passed=True,result=result)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 paths=[Path(__file__),Path(F.__file__),O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',E/'candidate.nes',E/'candidate.dbg',C.parent/'handoff.json']
 q['bindings']={str(p.resolve()):B.sha(p)for p in paths};B.write(out,json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['result','bindings']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
