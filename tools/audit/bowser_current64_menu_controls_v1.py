"""Actual full Select cycles and conditional Start flags on final Bowser source."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_current64_host_checks_v1 as A
from check_tmnt_render_oa import load,address
T=A.T;H=A.H;C=A.N.C;J=A.J;O=R/'build/bowser-current64-menu-controls-v1'
P=R/'build/peach-palette-fix-1030-v1/joint';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COUNTS=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,2,4,4,2,2,4,1,1,4,1,2,1,6,2,4,2]
def queue(m):
 a=address(m.bundle,'VRAM_Buffer1');return bytes(m[a:a+H.get(m,'VRAM_Buffer1_Offset')+1])
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,source_CPU=True,checks={});ck=q['checks']
 try:
  old,new=load(P/'candidate.nes'),load(J/'candidate.nes');rows=[]
  for slot,count in enumerate(COUNTS):
   pair=[]
   for b in [old,new]:
    m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=slot,FfVariant=0,FmAlts=0);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection');pair.append(m)
   for v in range(count):
    if v:
     for m in pair:
      H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
      C.invoke(m,'CrossoverMenuInput')
    got=[]
    for m in pair:
     r=C.invoke(m,'FmPending');got.append([H.get(m,'SelectedCharacter'),r['AXYP_SP'][0],r['AXYP_SP'][3]&1,queue(m)])
    if slot==26:assert got[0][2]==1 and got[1][2]==0 and got[1][0]==27
    else:assert got[0]==got[1],('actual foreign Select/identity/name/readiness',slot,v,got[0][:3],got[1][:3])
    rows.append(dict(slot=slot,variant=v,selected=got[1][0],nameindex=got[1][1],pending=got[1][2],foreign_exact=slot!=26))
  ck['actual_all83_menu_entries_including_pending_BTplaceholder']=rows
  seed=T.make(new);tests=[]
  cases=list(itertools.product(range(32),range(256)))
  for slot,bits in cases:
   m=T.fork(seed);H.put(m,FmAlts=bits,FmGroups=bits)
   c,lo=T.call(m,'FmStartFlags',x=slot,a=0x55,y=0x63,p=0xf9)
   assert H.get(m,'FmAlts')==bits*0+(bits&{9:32,26:8,31:128}.get(slot,0))
   assert H.get(m,'FmGroups')==(bits&{23:32,30:24}.get(slot,0))
   assert(c.a,c.x,c.y,c.p,c.sp)==(0,slot,0x63,(0xf9&0x7d)|2,224)
  for slot,f,alts,groups in itertools.product(range(32),range(64),[0,8,32,128,255],[0,24,32,255]):
   m=T.fork(seed);H.put(m,FmAlts=alts,FmGroups=groups);p=T.flags(f)
   c,lo=T.call(m,'FmStartFlags',x=slot,a=0x55,y=0x63,p=p)
   assert(c.a,c.x,c.y,c.p,c.sp)==(0,slot,0x63,(p&0x7d)|2,224)
   assert H.get(m,'FmAlts')==(alts&{9:32,26:8,31:128}.get(slot,0))and H.get(m,'FmGroups')==(groups&{23:32,30:24}.get(slot,0))
  ck['genuine_Start_helper']=dict(all32slots_all256bits=len(cases),all64flags_criticalmask_cases=32*64*5*4,original_AXYP_SP_flags_exact=True,maskAlts={'9':'20','26':'08','31':'80'},maskGroups={'23':'20','30':'18'},BT_CF_still_pending=True)
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),traceback=q.get('traceback'))));assert q['passed']
if __name__=='__main__':main()
