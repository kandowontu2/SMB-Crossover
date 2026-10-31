"""Exact current70 menu/Start rebind after BT body-only source repairs."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import benj_all_menu_controls_1030_v1 as B
import battletoads_current_loader_controls_v1 as L
P=R/'build/bt-ready-menu-1031-v2/joint';J=R/'build/bt-lives-body-source-v5/joint';O=R/'build/bt-lives-body-controls-v2'
def main():
 out=O/'menu-controls.json';assert not out.exists();counts=B.A.COUNTS[:]
 try:
  B.A.COUNTS[16]=4;B.A.COUNTS[23]=2
  old,new=B.collect(P,True),B.collect(J,True)
 finally:B.A.COUNTS[:]=counts
 assert old==new and len(new)==86 and sum(not x['pending']for x in new.values())==70
 q=dict(passed=True,native=False,candidate=L.sha(J/'candidate.nes'),all86_menu_identity_name_flags_and_Start_A_boundaries_exact=True,
   ready=70,CF_pending=True,input_boundaries=688,rows=list(new.values()),bindings={str(p.resolve()):L.sha(p)for p in[Path(__file__),Path(B.__file__),Path(B.A.__file__),P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',J.parent/'source-stage.json']})
 out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings']}))
if __name__=='__main__':main()
