"""Real menu resolution/Select/queue execution across all80 identities."""
from pathlib import Path
import json,traceback,sys
import build_celeste_exact_menu_name_v3 as B
import arthur_expanded_context_v2 as V
from sunny_integrated_controls_v1 import registers
A=V.A
COUNTS=[5,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,2,4,4,2,2,4,1,1,4,1,2,1,6,2,4,1]
def fresh(b,slot=0):
 q=A.C.setup(b,0);q.put(OperMode=0,CrossoverMenuState=2,CrossoverMenuIndex=slot,CrossoverMenuButtons=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0,MarioVariant=0,FamilyMainCommit=1,Mirror_PPUMASK=24)
 return q
def name(q):
 at=A.address(q.b,'VRAM_Buffer1');v=list(q.m[at:at+q.get('VRAM_Buffer1_Offset')+1]);pos=0;found=[]
 while pos<len(v)-1 and v[pos]:
  n=v[pos+2]&63
  if v[pos:pos+3]==[35,40,16]:found.append(bytes(v[pos+3:pos+19]))
  pos+=3+n
 assert found,('no actual name command',v);return found[-1]
def main():
 mode=sys.argv[1]if len(sys.argv)>1 else'current';spec=B.CASES[0 if mode=='current'else 1];O=B.R/'build'/spec[0];P=B.R/'build'/spec[1]/'joint';N=O/'joint';out=O/'menu-controls-v2.json';assert not out.exists();d=dict(passed=False,native=False,rows=[])
 try:
  old,b=[A.scoped_load(p/'candidate.nes')for p in [P,N]];expect=b['raw'][A.location(b,'NrQueueSelectName::Names')+44*16:A.location(b,'NrQueueSelectName::Names')+45*16]
  assert len(expect)==16
  for slot,count in enumerate(COUNTS):
   pair=[fresh(v,slot)for v in [old,b]]
   for q in pair:A.call(q,'MenuResolveCharacter');A.call(q,'QueueSelection')
   for variant in range(count):
    result=[]
    for q in pair:
     if variant:
      q.put(VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);r=A.call(q,'CrossoverMenuInput')
     else:r=A.call(q,'QueueSelection')if False else None
     result.append((name(q),q.get('SelectedCharacter'),q.get('CrossoverMenuIndex')))
    aa,bb=result
    assert aa[1:]==bb[1:] and bb[2]==slot
    if(slot,variant)==(0,4):assert aa[0]!=expect and bb[0]==expect
    else:assert aa==bb,(slot,variant,aa,bb)
    assert A.C.M.fastapp(pair[0])==A.C.M.fastapp(pair[1])if(slot,variant)!=(0,4)else True,(slot,variant,'foreign application')
    d['rows'].append([slot,variant,bb[1],list(bb[0])])
  # Real cold publisher all64flags on all5 Mario variants; source/name output,
  # full returned ABI, own map restoration and all foreign application bytes.
  flags=[]
  for variant in range(5):
   for f in range(64):
    p=0x30|(f&3)|(f&12)|((f&16)<<2)|((f&32)<<2);pair=[]
    for v in [old,b]:
     q=fresh(v);q.put(MarioVariant=variant);A.call(q,'MenuResolveCharacter');q.put(VRAM_Buffer1_Offset=0)
     c,tr,mn=A.call(q,'KmQueueName',a=91,x=3,y=27,p=p);pair.append((q,c,name(q)))
    (qa,ca,na),(qb,cb,nb)=pair
    if variant==4:
     ref=fresh(b);ref.put(MarioVariant=4);A.call(ref,'MenuResolveCharacter');ref.put(VRAM_Buffer1_Offset=0);rc,_,_=A.call(ref,'NrQueueSelectName::NameIndex',a=44,x=3,y=27,p=p);assert registers(rc)==registers(cb),('authentic index44 worker ABI',p,registers(rc),registers(cb))
    else:assert registers(ca)==registers(cb),(variant,p,'foreign AXYP')
    assert qa.m.rawtags==qb.m.rawtags
    if variant==4:assert na!=expect and nb==expect
    else:assert na==nb and A.C.M.fastapp(qa)==A.C.M.fastapp(qb),(variant,p,'foreign')
    flags.append([variant,p,cb.processorCycles-ca.processorCycles])
  d.update(passed=True,cases=len(d['rows']),actual_Mario_allflags=len(flags),cold_name_CPU_delta=[min(x[2]for x in flags),max(x[2]for x in flags)],old_Celeste_name=list(d['rows'][0][3]),new_Celeste_name=list(expect),limits=['Linked CPU/controller-input fixture, not native PPU/video.','Only profile0 variant4 text changes; all other79 actual menu outputs/application states and all5×64 cold publisher ABI pass.'])
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):B.sha(p)for p in [Path(__file__),Path(B.__file__),N/'candidate.nes',N/'candidate.dbg',O/'source-proof.json',P/'candidate.nes',P/'candidate.dbg']};out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in ['rows','bindings','traceback']}));assert d['passed'],d.get('error')
if __name__=='__main__':main()
