"""Current66 menus/Start preserve all pending identities during inert CF join."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_current64_menu_controls_v1 as M
from check_tmnt_render_oa import load,address,location
T=M.T;H=M.H;C=M.C;sha=M.sha
P=R/'build/cf-cold-warm-palette-source-v1/joint';J=R/'build/cf-preload-name-source-v1/joint';O=R/'build/cf-preload-name-menu-controls-v2'
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,menus=[])
 try:
  old,new=load(P/'candidate.nes'),load(J/'candidate.nes')
  for slot,count in enumerate(M.COUNTS):
   pair=[]
   for b in[old,new]:
    m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=slot,FfVariant=0,FmAlts=0)
    C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection');pair.append(m)
   for variant in range(count):
    if variant:
     for m in pair:
      H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0);C.invoke(m,'CrossoverMenuInput')
    got=[]
    for m in pair:
     z=C.invoke(m,'FmPending');got.append([H.get(m,'SelectedCharacter'),z['AXYP_SP'][0],z['AXYP_SP'][3]&1,M.queue(m)])
    assert got[0]==got[1],('actual menu identity/name/readiness',slot,variant,got[0][:3],got[1][:3])
    q['menus'].append(dict(slot=slot,variant=variant,selected=got[1][0],name_index=got[1][1],pending=got[1][2]))
  # Real Start masking instructions/PCs are unchanged, not just the source text.
  at=location(old,'FmStartIdentityFlags');an=location(new,'FmStartIdentityFlags');assert old['raw'][at:at+51]==new['raw'][an:an+51]
  seed=T.make(new)
  for slot,p,bits in itertools.product(range(32),range(64),[0,24,32,128,255]):
   m=T.fork(seed);H.put(m,FmAlts=bits,FmGroups=bits);flags=T.flags(p)
   c,_=T.call(m,'FmStartFlags',x=slot,a=0x55,y=0x63,p=flags)
   assert(c.a,c.x,c.y,c.p,c.sp)==(0,slot,0x63,(flags&0x7d)|2,224)
   assert H.get(m,'FmAlts')==(bits&{9:32,26:8,31:128}.get(slot,0))
   assert H.get(m,'FmGroups')==(bits&{23:32,30:24}.get(slot,0))
  assert all(row['pending']for row in q['menus']if row['slot']in[23,30])
  q.update(passed=True,actual_menu_identities=len(q['menus']),Start_flag_cases=32*64*5,current66_readiness_exact=True,CF_BT_still_pending=True,Benj_Mario_cycle_7_preserved=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/cf_preload_name_menu_controls_v1.py',R/'build/cf-preload-name-menu-controls-v1/controls.json',Path(M.__file__),J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['menus','bindings']}));assert q['passed']
if __name__=='__main__':main()
