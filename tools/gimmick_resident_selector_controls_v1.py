"""Independent same-span resident selector source/CPU controls; no native run."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,collections
R=Path(__file__).resolve().parents[1];P=R/'build/pit-retold-host-v3'
O=R/'build/gimmick-resident-selector-v1'
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_roster_compact_11_v1 import BASE
from smb2_roster_main_callers_v2 import make,same_live

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):p=Path(p).resolve();return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def key(b,n):return address(b,n),(location(b,n)-16)//8192
def cold(b,raw,field,variant,mode):
 q=make(b,raw,field,variant,mode)
 # Match actual reset ownership before any translated native audio call.
 # In particular, Metroid's private bank field is not a zero-valid state.
 c,t=q.invoke('CrossoverInit');q._prior=t;q.put(SelectedCharacter=raw,CrossoverBehaviorVersion=mode)
 if field:q.set(field,variant)
 c,t=q.invoke('NrFreshGameInit');q._prior+=t;return q
def build():
 O.mkdir(exist_ok=True);sd=O/'src';sd.mkdir(exist_ok=True)
 proof=json.loads((P/'build-proof.json').read_text())
 assert sha(P/'candidate.nes')=='ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2'
 for p,h in proof['actual_dependencies'].items():assert sha(p)==h,p
 source=R/'build/gimmick-admission-v3/overlay/src/mmc5.s'
 (sd/'mmc5.s').write_bytes(source.read_bytes())
 cmd=list(proof['commands'][0]);at=cmd.index('-I');cmd[at:at]=['-I',str(sd)]
 cmd=[x.replace(str(P/'main.o'),str(O/'main.o')).replace(str(P/'main.d'),str(O/'main.d'))for x in cmd]
 cmds=[cmd];p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
 (O/'assemble.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr[-4000:]
 cmd=[x.replace(str(P/'candidate.'),str(O/'candidate.')).replace(str(P/'main.o'),str(O/'main.o'))for x in proof['commands'][-1]]
 cmd+=['-m',str(O/'candidate.map')];cmds.append(cmd)
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'link.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr[-4000:]
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'candidate.nes')
 deps=dict(proof['actual_dependencies']);old=[p for p in deps if Path(p).name=='mmc5.s'];assert len(old)==1
 del deps[old[0]];deps[str((sd/'mmc5.s').resolve())]=sha(sd/'mmc5.s')
 inputs=[bind(p)for p in deps]+[bind(x)for x in proof['commands'][-1]if x.endswith('.o')and x!=str(P/'main.o')]+[bind(P/'smb1base-mmc5-expanded.cfg')]
 (O/'build-proof.json').write_text(json.dumps(dict(parent=bind(P/'candidate.nes'),source=bind(sd/'mmc5.s'),source_preimage=bind(old[0]),commands=cmds,inputs=inputs,candidate=bind(O/'candidate.nes'),native=False),indent=2)+'\n')
 print('Independent selector source link complete',sha(O/'candidate.nes'),flush=True)

def direct(bs):
 rows=[]
 for raw in range(6,24):
  for status in [0,1,2]:
   qs=[make(b,raw,mode=0)for b in bs];cs=[]
   for q in qs:q.set('PlayerStatus',status);c,t=q.invoke('DwResidentGraphicsSelector',x=85,y=170);cs.append(c)
   assert (cs[0].a,cs[0].y,cs[0].p,cs[0].sp)==(cs[1].a,cs[1].y,cs[1].p,cs[1].sp),(raw,status,'selector live registers')
   assert qs[0].m.banks==qs[1].m.banks
   assert bytes(qs[0].m[:0x100])==bytes(qs[1].m[:0x100])
   assert bytes(qs[0].m[0x200:0x8000])==bytes(qs[1].m[0x200:0x8000])
   assert cs[0].x==(raw-6)and cs[1].x==raw
   rows.append(dict(raw=raw,status=status,cycles_parent=cs[0].processorCycles,cycles_new=cs[1].processorCycles))
 for raw,bank in [(26,73),(28,12)]:
  q=make(bs[1],raw);q.invoke('DwResidentGraphicsSelector');assert q.m.banks[2]==bank and q.get('CurrentBankC')==bank|128
 return rows

def run_nmi(q,lag):
 # Genuine NMI vector and RTI. CPU-only memory model, no PPU/DMA timing claim.
 m=q.m;m.page(0,126);m.page(3,127);q.put(NmiDisable=255 if lag else 0,DisableScreenFlag=1,GamePauseStatus=0,VRAM_Buffer_AddrCtrl=0)
 m[0x2002]=128;c=NesMPU(memory=m,pc=0x5b00);c.a,c.x,c.y,c.p,c.sp=85,170,51,0x30,0xfd
 m.writes=[];c.nmi();trace=[]
 for _ in range(150000):
  if(c.pc,c.sp)==(0x5b00,0xfd):return c,trace
  pc=c.pc;bank=m.banks[(pc-0x8000)//8192]if pc>=0x8000 else -1;before=len(m.writes)
  assert m[c.pc]!=0,('NMI BRK',hex(c.pc),bank)
  c.step();trace += [dict(pc=pc,bank=bank,address=p,value=v)for p,v in m.writes[before:]]
 raise AssertionError(('NMI bound',hex(c.pc),m.banks))

def closure(bs):
 a,b=bs;old=a['raw'];new=b['raw'];moved=[]
 for n,d in a['syms'].items():
  if n in b['syms']and d['val']!=b['syms'][n]['val']:
   moved.append(dict(name=n,old=int(d['val'],0),new=address(b,n)))
 allowed={'CheatsInjuryMask','Cv3AdderOther','Cv3AdderLegacy','Cv3ResidentAdder','Cv3BankReturn','Cv3BankLegacy','Cv3ResidentRosterBank','DwResidentGraphicsBanks','StoreGraphics','NativeGraphics'}
 assert all(q['name'].split('::')[-1]in allowed for q in moved),moved
 assert address(a,'DwResidentGraphicsSelector')==address(b,'DwResidentGraphicsSelector')
 lo=16+126*8192+0x9a;hi=16+126*8192+0x122
 # The unchanged publication prefix begins at actual StartPublication.
 assert old[lo:location(a,'DwResidentGraphicsSelector')]==new[lo:location(a,'DwResidentGraphicsSelector')]
 diffs=[i for i,(x,y)in enumerate(zip(old,new))if x!=y]
 outside=[i for i in diffs if not lo<=i<hi]
 refs=[]
 for pos in outside:
  assert old[pos-1]in [0x20,0x4c]
  oldptr=old[pos]+256*old[pos+1];newptr=new[pos]+256*new[pos+1]
  assert (oldptr,newptr)in [(0x80df,0x80e0),(0x8118,0x8119),(0x80f9,0x80fa)]
  refs.append(dict(physical_bank=(pos-16)//8192,offset=(pos-16)%8192-1,old_target=oldptr,new_target=newptr,opcode=old[pos-1]))
 assert len(refs)==4 and len(diffs)==116
 # Real instructions at every reached resident selector site interrupted by
 # the existing actual IRQ handler. No foreign stack/register mask.
 irq=[];original=NesMPU.step
 for raw,variant in [(6,0),(12,0),(12,1),(26,0),(28,0)]:
  q=make(b,raw);q.set('DarkwingVariant',variant);sites=[]
  def observe(c):
   bank=c.memory.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
   if bank==126 and address(b,'DwResidentGraphicsSelector')<=c.pc<address(b,'DwResidentGraphicsBanks'):sites.append(c.pc)
   return original(c)
  NesMPU.step=observe
  try:q.invoke('DwResidentGraphicsSelector')
  finally:NesMPU.step=original
  for site in sorted(set(sites)):
   q=make(b,raw);q.set('DarkwingVariant',variant);fired=False;low=255
   def step(c):
    nonlocal fired,low
    if not fired and c.pc==site:
     m=c.memory;before=(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,m.banks.copy())
     live=(bytes(m[:256]),bytes(m[0x15a:0x17b]),bytes(m[0x5c00:0x5c80]))
     m[0x5204]=128;c.irq()
     for _ in range(1000):
      low=min(low,c.sp);original(c)
      if(c.pc,c.sp)==(before[0],before[5]):break
     else:raise AssertionError('actual selector IRQ bound')
     assert(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,m.banks)==before
     assert live==(bytes(m[:256]),bytes(m[0x15a:0x17b]),bytes(m[0x5c00:0x5c80]))
     fired=True
    return original(c)
   NesMPU.step=step
   try:q.invoke('DwResidentGraphicsSelector')
   finally:NesMPU.step=original
   assert fired;irq.append(dict(raw=raw,darkwing_variant=variant,pc=site,minimum_SP=low))
 result=dict(passed=True,changed_bytes=len(diffs),changed_banks=sorted(set((i-16)//8192 for i in diffs)),outer_capsule=[0x809a,0x8122],old_symbols_checked=len(a['syms']),real_relocations=moved,all_external_relocated_operands=refs,actual_IRQ=irq,source=bind(O/'src/mmc5.s'),candidate=bind(O/'candidate.nes'),native=False)
 (O/'closure.json').write_text(json.dumps(result,indent=2)+'\n');return result

def controls():
 bs=[scoped_load(p/'candidate.nes')for p in [P,O]];rows=[];nr=[];portraits=[]
 direct_rows=direct(bs)
 identities=[(n,x[1],x[2],x[3])for n,x in BASE.items()]
 identities += [('popo',20,'IcVariant',0),('nana',20,'IcVariant',1),('alex',21,'RcVariant',0),('ryan',21,'RcVariant',1),('sunny',23,None,0),('celeste',0,'MarioVariant',4),('kamikaze',0,'MarioVariant',3)]
 for name,raw,field,variant in identities:
  for mode in [0,1]:
   qs=[cold(b,raw,field,variant,mode)for b in bs];history=[q._prior.copy()for q in qs]
   for mask in [0,1,129,0]:
    cs=[]
    for j,q in enumerate(qs):
     q.put(SavedJoypadBits=mask,SavedJoypad1Bits=mask);c,t=q.invoke('GameLoop');cs.append(c);history[j]+=t
    dead=same_live(qs,cs,(name,mode,mask),history)
    rows.append(dict(identity=name,mode=mode,mask=mask,cycles_parent=cs[0].processorCycles,cycles_new=cs[1].processorCycles,dead_stack=dead))
   # All genuine audio/CHR restoration passes, not a naked selector return.
   for lag in [True,False]:
    cs=[];tr=[]
    for q in qs:
     try:c,t=run_nmi(q,lag)
     except BaseException as e:raise AssertionError(('NMI fixture',name,mode,lag,str(e)))from e
     cs.append(c);tr.append(t)
    same_live(qs,cs,('NMI',name,mode,lag),[history[i]+tr[i]for i in range(2)])
    for i in range(2):history[i]+=tr[i]
    nr.append(dict(identity=name,mode=mode,lag=lag,cycles_parent=cs[0].processorCycles,cycles_new=cs[1].processorCycles))
   for state in [0,1]:
    qs=[cold(b,raw,field,variant,mode)for b in bs];cs=[];tr=[]
    for q in qs:
     q.put(OperMode=state,Player_X_Position=128,Player_PageLoc=0,Player_Y_Position=96)
     c,t=q.invoke('DrawPlayer_Intermediate');cs.append(c);tr.append(t)
     c,t=q.invoke('X5PortraitRender',a=0,x=q.get('ObjectMetasprite'),y=0);cs[-1]=c;tr[-1]+=t
    same_live(qs,cs,('portrait/lives',name,mode,state),[qs[i]._prior+tr[i]for i in range(2)])
    portraits.append(dict(identity=name,mode=mode,oper_mode=state,cycles_parent=cs[0].processorCycles,cycles_new=cs[1].processorCycles))
  if len(rows)%32==0:print('selector complete Main controls',len(rows),flush=True)
 cl=closure(bs)
 result=dict(passed=True,native=False,source_CPU_only=True,candidate=bind(O/'candidate.nes'),parent=bind(P/'candidate.nes'),direct=direct_rows,full_Main=rows,full_NMI=nr,menu_lives=portraits,closure=bind(O/'closure.json'),limits='CPU-only typed arenas; no native PPU/deadline/gameplay. Leaf changes terminal X from raw-6 to raw. Complete caller endpoints retain all live AXYP/SP/banks/RAM/33SMC; dead call-stack differences have actual push-writer attribution. raw26/28 entry bank selection only here; their real owner modules are independently qualified by their owners. Unsupported24/25/27 remain unadmitted.',tool=bind(__file__))
 (O/'controls.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,Main=len(rows),NMI=len(nr),menu_lives=len(portraits),proof=bind(O/'controls.json'))),flush=True)

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--build',action='store_true');x=a.parse_args()
 try:
  if x.build:build()
  controls()
 except BaseException as e:
  p=O/'first-control-negative.json'
  if not p.exists():p.write_text(json.dumps(dict(error=repr(e),candidate=bind(O/'candidate.nes')if(O/'candidate.nes').exists()else None),indent=2)+'\n')
  raise
