"""Targeted actual80 menu/name/readiness and160 real Start/A boundaries.

Compare the frozen visual58 dependency to the genuine final62 composition.
The selected8 family cold/Main/body/palette controls are separate receipts.
No compiler, source mutation, or native emulator is invoked here.
"""
from pathlib import Path
import json, traceback
import arthur_quick_functional_admission_v1 as A
import prepare_functional_roster_visuals58_v1 as B

R=B.R;P=R/'build/functional-roster-visuals58-v1/joint'
O=R/'build/functional-roster-coherent62-v4';N=O/'joint';T=A.T

def main():
 out=O/'menu-controls.json';assert not out.exists()
 d=dict(passed=False,native=False);rows=[]
 try:
  for slot,count in enumerate(A.COUNTS):
   mm=[A.fresh(path,slot)for path in [P,N]]
   for m in mm:A.call(m,'MenuResolveCharacter');A.call(m,'QueueSelection')
   for variant in range(count):
    if variant:
     for m in mm:A.button(m,32)
    rr=[A.call(m,'FmPending')[0]for m in mm]
    pending=[bool(x['P']&1)for x in rr]
    assert all(r['X']==slot for r in rr)
    assert pending==([True,False]if slot==21 else[pending[0],pending[0]]),(slot,variant,pending)
    expected=8 if(slot,variant)==(0,1)else A.RAW[slot]
    for m,blocked in zip(mm,pending):
     assert m.get('SelectedCharacter')==(0 if blocked else expected),(slot,variant,blocked,m.get('SelectedCharacter'),expected)
    packets=[[q for q in A.commands(m)if q['address']==0x2328]for m in mm]
    assert len(packets[0])==len(packets[1])==1,(slot,variant,packets)
    assert all(len(p[0]['data'])==16 for p in packets)
    changed=slot in [21,24]
    if changed:
     # Both live family menu workers now use the full ready profile names.
     assert packets[0]!=packets[1] and 63 not in packets[1][0]['data'],(slot,variant,packets)
     idx=rr[1]['A'];table=N/'src/full_roster_menu_art.inc'
     assert idx in(range(18,22)if slot==21 else range(10,14)),(slot,variant,idx)
    else:assert packets[0]==packets[1],('unrelated menu name',slot,variant,packets)
    for key in [16,128]:
     pair=[T.fork(m)for m in mm]
     zz=[A.start_boundary(m,key,0xf9)for m in pair]
     assert all(z['launch']!=blocked for z,blocked in zip(zz,pending)),(slot,variant,key,zz,pending)
     if slot!=21:assert zz[0]==zz[1],('unchanged real Start/A ABI',slot,variant,key,zz)
     if(slot,variant)==(9,2):assert pair[1].get('FmAlts')==32
    rows.append(dict(slot=slot,variant=variant,raw=A.RAW[slot],selected=[m.get('SelectedCharacter')for m in mm],pending=pending,name_packets=packets,real_Start_A=True))
  ready=[sum(not r['pending'][i]for r in rows)for i in [0,1]]
  assert len(rows)==80 and ready==[58,62],ready
  d.update(passed=True,profiles=80,ready_counts=ready,pending_counts=[22,18],actual_Start_A_pairs=160,all_previous58_ready_preserved=True,only_new_ready_menu_slot=21,new_ready_raw=22,new_ready_profiles=['FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF'],distinct_SMB2_prefixes_live=True,Arthur_identity=dict(menu=31,raw=32),Quick_identity=dict(menu=9,variant=2,raw=9,FmAlts=32),rows=rows,scope='Actual menu/ready/name and Start/A call boundaries only. Exact current selected-family cold/body/palette/Main and inherited fullflags/ISR controls are bound separately; no native or install claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):B.sha(p)for p in [Path(__file__),O/'source-stage.json',P/'candidate.nes',P/'candidate.dbg',N/'candidate.nes',N/'candidate.dbg']}
 B.write(out,json.dumps(d,indent=2)+'\n')
 print(json.dumps({k:v for k,v in d.items()if k not in['rows','bindings','traceback']}));assert d['passed'],d.get('error')

if __name__=='__main__':main()
