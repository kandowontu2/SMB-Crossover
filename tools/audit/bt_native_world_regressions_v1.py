"""Existing meaningful current66 Main/menu/Bowser parser checks, exact9b10."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
J=R/'build/bt-native-world-source-v2/joint';P=R/'build/bt-current-cf-component-v2/joint'

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',choices=['foreign','bowser','menu'],required=True);a=p.parse_args();O=R/'build'/('bt-native-world-'+a.check+'-v1')
 if a.check=='foreign':
  import cf_preload_name_foreign_main_v1 as A
  A.J=J;A.P=P;A.O=O;A.main()
 elif a.check=='bowser':
  import cf_preload_name_bowser_cold_v1 as A
  A.J=J;A.O=O;A.H.O=J;A.ROM=[n if n!='FmStartIdentityFlags'else'FmStartRetireFlags'for n in A.ROM];A.main()
 else:
  import bowser_current64_menu_controls_v1 as A
  from check_tmnt_render_oa import load
  O.mkdir(exist_ok=False);rows=[]
  old,new=load(P/'candidate.nes'),load(J/'candidate.nes')
  for slot,count in enumerate(A.COUNTS):
   pair=[]
   for b in[old,new]:
    m=A.C.fresh(b,0);A.H.put(m,CrossoverMenuIndex=slot,FfVariant=0,FmAlts=0);A.C.invoke(m,'MenuResolveCharacter');A.C.invoke(m,'QueueSelection');pair.append(m)
   for variant in range(count):
    if variant:
     for m in pair:A.H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);A.C.invoke(m,'CrossoverMenuInput')
    got=[]
    for m in pair:
     z=A.C.invoke(m,'FmPending');got.append([A.H.get(m,'SelectedCharacter'),z['AXYP_SP'][0],z['AXYP_SP'][3]&1,A.queue(m)])
    assert got[0]==got[1],(slot,variant);rows.append(dict(slot=slot,variant=variant,selected=got[1][0],name_index=got[1][1],pending=got[1][2]))
  assert all(row['pending']for row in rows if row['slot']in[23,30])
  q=dict(passed=True,native=False,actual_menu_identities=len(rows),current66_readiness_exact=True,BT_CF_pending=True,rows=rows,bindings={str(Path(A.__file__).resolve()):A.sha(A.__file__)})
  (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n')
 out=O/'controls.json';q=json.loads(out.read_text());q['bindings'].update({str(n.resolve()):A.sha(n)for n in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'source-stage.json',P/'candidate.nes',P/'candidate.dbg']});out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(check=a.check,passed=q['passed'],receipt=str(out),sha256=A.sha(out))))
if __name__=='__main__':main()
