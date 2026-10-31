"""Actual menu/scene SFC inputs, complete callback outputs, new live vector seams."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_owner_retirement_coverage_v1 as V
import contra_force_loader_isr_controls_v2 as U
T,C=V.T,V.C
O=R/'build/cf-owner-retirement-hook-abi-v1'
FLAGS=[v for v in range(256)if v&0x30==0x30]
def seed(root,raw=0,family=9):
 V.select_bundle(root);U.B=T.B;m=T.Bus()
 T.put(m,SelectedCharacter=raw,FmGroups=0,FmAlts=0,CrossoverMenuIndex=0,MarioVariant=0,OperMode=0,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=0,NmiDisable=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,GamePauseStatus=0,Sprite0HitDetectFlag=0,ReloadCHRBank=0,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0)
 m[T.address(T.B,'VRAM_Buffer1')]=0;m.ram[2][0x1fe0:0x1ff0]=bytes([167,family,0,1])+bytes(range(12))
 # This is a declined-load callback ABI fixture. Actual accepted cold
 # writes/parser are checked separately, not substituted by this state.
 m.writes.clear();m.ram_writes.clear();return m
def invoke(m,n,p=0x30,a=0x57):
 c=C.start(m,T.address(T.B,n),(T.location(T.B,n)-16)//8192|128,a=a,x=0xa9,y=0x63,p=p);z=T.finish(m,c)
 return c,z
def application(m):
 return bytes(m[i]for i in range(0x8000)if not(0x100<=i<0x1e1 or 0x2000<=i<0x5c00))
def writes(m):
 # The retired family check introduces only C-shadow/mapper writes and
 # the intentional C2 validity clear; all original application writes retain order.
 skip={T.address(T.B,'CurrentBank'),T.address(T.B,'CurrentBankC')}
 return[(a,v)for a,v in m.writes if a<0x8000 and a not in skip and not(0x100<=a<0x1e1 or 0x2000<=a<0x5c00)]
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,source_CPU=True,ABI=[],vectors=[])
 try:
  for entry,raw,slot,family,p in itertools.product(['MenuResolveCharacter','BwScene'],[0,27],[0,9,26,31],[9,31],FLAGS):
   if entry=='BwScene'and slot:continue
   pair=[]
   for root in[V.P/'joint',V.J]:
    m=seed(root,raw,family);T.put(m,CrossoverMenuIndex=slot)
    _,z=invoke(m,entry,p=p)
    # Retirement is the declared intentional family31 validity output.
    if root==V.P/'joint'and family==31:m.ram[2][0x1fe0]=0
    pair.append((z['AXYP'],application(m),[bytes(x)for x in m.ram],T.smc(m),m.rawtags[:],bytes(m[0x1e1:0x200]),writes(m),z['CPU']))
   assert pair[0][:7]==pair[1][:7],('actual hook ABI/application/write order',entry,raw,slot,family,p,[(i,pair[0][i],pair[1][i])for i in range(7)if pair[0][i]!=pair[1][i]][:1])
   q['ABI'].append([entry,raw,slot,family,p,pair[0][7],pair[1][7]])
  # Actual public SFC frame and every new hook instruction/stack/map seam.
  # Normal/paused uses stable zero input and a rejected-load raw0 context;
  # accepted forcedblank transfer lag/IRQ seams are in the loader receipt.
  for entry,(lag,pause)in itertools.product(['MenuResolveCharacter','BwScene'],[(0,0),(0,1),(255,0)]):
   base=seed(V.J,0,31);T.put(base,NmiDisable=lag,GamePauseStatus=pause)
   e=C.clone(base);expected,z=invoke(e,entry,p=0x31)
   m=C.clone(base);c=C.start(m,T.address(T.B,entry),(T.location(T.B,entry)-16)//8192|128,a=0x57,x=0xa9,y=0x63,p=0x31)
   start=T.address(T.B,'MenuResolveCharacter');scene=T.address(T.B,'BwScene');helper=T.address(T.B,'BwSceneNativePrepared');seen=set();steps=0
   while c.pc!=0x7fff:
    pc=c.pc;raw=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    owned=(raw>=128 and ((raw&127)==69 and 0xbfbd<=pc<0xbfe1 or (raw&127)==88 and (scene<=pc<scene+18 or helper<=pc<0xb400) or (raw&127)==66 and start<=pc<start+34))
    seam=pc<0x8000 and m[pc]in[0x48,0x68,0x60]
    key=(raw,pc)
    if (owned or seam)and key not in seen:
     seen.add(key)
     for kind in['NMI','IRQ']:
      if kind=='IRQ'and c.p&4:continue
      mem,cpu=U.clone(m,c);mem[0x5204]=128;proof=U.interrupt(mem,cpu,kind,keep_ppu=False);actual=T.finish(mem,cpu)
      assert actual['AXYP']==z['AXYP']and mem.rawtags==e.rawtags and [bytes(x)for x in mem.ram]==[bytes(x)for x in e.ram],('resumed hook callback',entry,lag,pause,hex(pc),kind)
      q['vectors'].append(dict(entry=entry,lag=lag,pause=pause,PC=pc,raw=raw,sourceSP=c.sp,**proof))
    c.step();steps+=1;assert steps<50000
  q.update(passed=True,actual_allflag_hook_pairs=len(q['ABI']),real_vector_cases=len(q['vectors']),minimum_ISR_SP=min(r['minimum_SP']for r in q['vectors']),fullAXYP_SP_all33SMC_livepage1_rawmaps_orderedapplication_exact=True,CF_validity_is_only_intentional_guest_output=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):V.sha(p)for p in[Path(__file__),Path(V.__file__),Path(U.__file__),Path(T.__file__),V.J/'source-stage.json',V.J/'candidate.nes',V.J/'candidate.dbg',V.P/'joint/candidate.nes',V.P/'joint/candidate.dbg']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['ABI','vectors','bindings']}));assert q['passed']
if __name__=='__main__':main()
