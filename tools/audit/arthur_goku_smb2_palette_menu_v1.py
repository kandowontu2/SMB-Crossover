"""Actual combined81-menu profiles including one generic pending BT cell."""
from pathlib import Path
import collections,json,traceback
import arthur_quick_functional_admission_v1 as A
import prepare_functional_roster_visuals58_v1 as B
R=B.R;P=R/'build/arthur-goku-select-remap-v3/joint';J=R/'build/arthur-goku-smb2-palette-v1/joint';O=J.parent;T=A.T

def main():
 out=O/'menu-controls.json';assert not out.exists();d=dict(passed=False,source=True,native=False,candidate=B.sha(J/'candidate.nes'));rows=[]
 try:
  counts=A.COUNTS[:];counts[31]=2
  for slot,count in enumerate(counts):
   mm=[A.fresh(p,slot)for p in[P,J]]
   for m in mm:A.call(m,'MenuResolveCharacter');A.call(m,'QueueSelection')
   for v in range(count):
    if v:
     for m in mm:A.button(m,32)
    rr=[A.call(m,'FmPending')[0]for m in mm]
    assert rr[0]==rr[1],('actual pending AXYP',slot,v,rr)
    assert mm[0].get('SelectedCharacter')==mm[1].get('SelectedCharacter')
    q=[[q for q in A.commands(m)if q['address']==0x2328]for m in mm];assert q[0]==q[1],('completeactualname',slot,v,q)
    for key in[16,128]:
     zz=[A.start_boundary(T.fork(m),key,0xf9)for m in mm]
     assert zz[0]==zz[1],('actualStart/AABI',slot,v,key,zz)
    rows.append(dict(slot=slot,variant=v,raw=mm[1].get('SelectedCharacter'),pending=bool(rr[1]['P']&1),name=q[1]))
  assert len(rows)==81 and sum(not r['pending']for r in rows)==62
  assert next(r for r in rows if(r['slot'],r['variant'])==(23,0))['pending']
  assert[(r['raw'],r['pending'])for r in rows if r['slot']==31]==[(32,False),(24,False)]
  own=[]
  for v in[0,1]:
   m=A.fresh(J,31);A.call(m,'MenuResolveCharacter');A.call(m,'QueueSelection')
   if v:A.button(m,32)
   r=A.call(m,'DrawSelectionPreview');assert m.get('CurrentOAMOffset')==(16 if v==0 else 24)
   if v:assert m.get('DpRenderIndex')==1
   names=['IcGlobalInit','QwBoot','SunnyGlobalInit','ArGenConstruct','DpAdmissionFresh'];points={(m.bank(n)|128,m.lab[n]):n for n in names};seen=collections.Counter()
   def hook(c):
    if c.pc>=0x8000:
     key=(m.tags[(c.pc-0x8000)//8192],c.pc)
     if key in points:seen[points[key]]+=1
   A.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverContinue=0)
   z=A.S.execute(m,'CrossoverMenuInput',hook=hook)
   assert m.get('SelectedCharacter')==(32 if v==0 else 24)
   assert seen['IcGlobalInit']==seen['QwBoot']==seen['SunnyGlobalInit']==1
   assert seen['ArGenConstruct']==(v==0)and seen['DpAdmissionFresh']==(v==1)
   own.append(dict(variant=v,raw=m.get('SelectedCharacter'),constructors=dict(seen),Start_return=z[0],minimumSP=z[2]))
  d.update(passed=True,actual_menu_profiles=81,existing_individuals_preserved=80,generic_pending_BT_placeholder=1,ready=62,pending=19,actual_Start_A_pairs=162,rows=rows,Arthur_Goku_source_cold_Start=own,scope='Exact combinedcart menu/name/ready/Start includingAr-Goku actualpostIc constructors. Broader remapflag/ISR and sourceBG/eye proof bound from immutableparents plus actualcombined S2 receipt. No native/publish claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):B.sha(p)for p in[Path(__file__),P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',O/'source-stage.json']}
 B.write(out,json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in['rows','bindings','traceback']}));assert d['passed'],d.get('error')

if __name__=='__main__':main()
