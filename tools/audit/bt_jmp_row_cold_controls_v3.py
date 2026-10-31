"""Actual223B JMP-row ingress/callback/interrupt proof, no admission."""
from pathlib import Path
import collections,copy,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import cf_preload_name_transport_controls_v1 as A
H=L.H;address=L.address;J=R/'build/bt-jmp-row-cold-source-v1/joint';P=R/'build/bt-current-cf-component-v2/joint';O=R/'build/bt-jmp-row-cold-controls-v3'

def start(m,service,p=0x30):return A.startrow(m,service,p)
def finish(m,c,watch=None):
 c,lo,r=A.finish(m,c,watch)
 return c,lo,(*r,m.rawtags[:],bytes(m[0x1e1:0x200]))
def direct(m,name,p):return H.start(m,name,p=p)

def fork(m):
 z=type(m).__new__(type(m));list.__init__(z,list(m))
 for n,v in vars(m).items():setattr(z,n,v if n=='bundle'else copy.deepcopy(v))
 z.writes.clear();z.ram_writes.clear();return z

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,checks={},vectors=[])
 try:
  assert L.sha(J/'candidate.nes')=='7247fa87d1b03100af449bd3bb05868915205f187b3c25947565a32c6253770b'
  bundles=[H.C.qualified(x/'candidate.nes')for x in[P,J]];seeds=[]
  for b in bundles:
   m=L.make(b);c,_=L.call(m,'BtLoad');assert c.p&1;H.put(m,OperMode=0,FamilyMainCommit=1,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0)
   seeds.append(m)
  for n in['BtServiceVeneers','BtServiceUnavailable','BtRouter']:
   assert address(bundles[0],n)==address(bundles[1],n)
  counts=collections.Counter();deltas=[];minimum=255;witness=[]
  # All three owner values reach every public row with all architectural
  # flag combinations. BT additionally covers every valid actual callback.
  for raw,valid in[(27,0),(31,0),(33,0),(33,1)]:
   for slot,flag in itertools.product(range(37),range(64)):
    cold=raw==33 and slot in[17,26];pair=[];cycles=[]
    for side in[0,1]:
     m=fork(seeds[side]);H.put(m,SelectedCharacter=raw)
     if not valid:m.ram[3][0x1fe0]=0;m.ram[2][0x1fe0]=0
     m.writes.clear();m.ram_writes.clear();entries=[]
     # New cold overrides are compared to the genuine owned ROM callback,
     # not to the obsolete cache draw/colors path they intentionally replace.
     if cold and side==0:
      m.bundle=bundles[1];c=direct(m,{17:'BtColdPortrait',26:'BtColdColors'}[slot],L.flags(flag))
     else:c=start(m,slot,L.flags(flag))
     def watch(mem,c,i):
      if side==1 and c.pc==address(mem.bundle,'BtRouter')and mem.rawtags[1]==0xd7:
       ptr=mem[address(mem.bundle,'FarcallJmpTarget_SMC')+1]+256*mem[address(mem.bundle,'FarcallJmpTarget_SMC')+2]
       assert 0xb020<=ptr<0xb08c and (ptr-0xb020)%3==0,('all real nested targets',ptr)
       entries.append((ptr,c.sp))
       if len(entries)>1:return
       assert ptr==0xb020+slot*3 and(c.a,c.x,c.y)==(85,7,91)
       assert c.p==(L.flags(flag)&0x7d),('genuine SFC entry flags',raw,slot,flag,c.p)
       assert c.sp==219,('no own row JSR frame',c.sp)
       if flag==0 and not valid:witness.append(dict(owner=raw,service=slot,step=i,SP=c.sp,SMCtarget=ptr,live_stack=bytes(mem[0x101+c.sp:0x200]).hex()))
     c,lo,result=finish(m,c,watch);pair.append(result);cycles.append(c.processorCycles);minimum=min(minimum,lo)
    assert pair[0]==pair[1],('native callback AXYP/RAM/ordered writes/maps/page1',raw,valid,slot,flag,[i for i in range(len(pair[0]))if pair[0][i]!=pair[1][i]],pair[0][0],pair[1][0])
    counts['all_owner_rows_flags']+=1;counts['new_ROM_callback_pairs'if cold else'unchanged_callback_pairs']+=1
    if not cold:deltas.append(cycles[1]-cycles[0])
   print('owner/valid all37x64 PASS',raw,valid,flush=True)
  assert len(witness)==108
  q['checks']['actual_public_rows']=dict(counts,all108_owner_row_target_witnesses=witness,minimum_SP=minimum,unchanged_CPU_delta=[min(deltas),max(deltas)],scope='Genuine SFC entry target/AXYP/stack; valid BT all36 callbacks, invalid all27/31/33 callbacks; cold17/26 compared directly to actual ROM callback.')
  # Foreign values must reject before the pure resolver or either ROM cold
  # override. These calls may never map C or write guest/application state.
  foreign=0;b=bundles[1];resolver=address(b,'BwBtResolve')
  for raw in range(256):
   if raw in[27,31,33]:continue
   m=fork(seeds[1]);H.put(m,SelectedCharacter=raw);before=[bytes(x)for x in m.ram]
   for slot,flag in itertools.product([0,15,17,18,19,26,35],range(64)):
    m.writes.clear();m.ram_writes.clear();seen=[]
    def guard(mem,c,i):
     if c.pc==resolver and mem.rawtags[1]==0xc3:seen.append(i)
    c,lo,result=finish(m,start(m,slot,L.flags(flag)),guard)
    assert not seen and not c.p&1 and(c.a,c.x,c.y,c.sp)==(85,7,91,224)
    assert c.p==L.flags(flag)&0x7c and not m.ram_writes and not result[3] and [bytes(x)for x in m.ram]==before
    assert not any(a==0x5116 for a,v in m.writes);foreign+=1
  q['checks']['foreign']=dict(pairs=foreign,all253raw_all64flags=True,no_resolver_Cmap_or_application_writes=True)
  print('foreign allflags PASS',foreign,flush=True)
  poison=0
  for byte,flag in itertools.product(range(16),range(64)):
   m=fork(seeds[1]);m.ram[3][0x1fe0+byte]^=1;before=[bytes(x)for x in m.ram]
   c,lo,result=finish(m,start(m,0,L.flags(flag)))
   assert not c.p&1 and [bytes(x)for x in m.ram]==before and not m.ram_writes;poison+=1
  q['checks']['poison']=dict(pairs=poison,all16cookie_bytes_all64flags=True,reject_before_cache_opcode=True)
  # Every reached router/SMC/mapper/return instruction on RAM, cold ROM,
  # native fallback and reject paths is cut by actual normal/lag/paused NMI
  # and legal IRQ. Normal contexts are stable zero-input genuine title;
  # no input is restored or manually changed after interrupt return.
  paths=[]
  for raw,valid,slot in[(33,1,0),(33,0,15),(33,0,18),(33,0,19),(33,0,17),(33,0,26),(31,0,18),(0,0,17)]:
   seed=fork(seeds[1]);H.put(seed,SelectedCharacter=raw,OperMode=0)
   if not valid:seed.ram[3][0x1fe0]=0;seed.ram[2][0x1fe0]=0
   cuts=[];seen=set()
   def trace(mem,c,i):
    tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
    owned=(tag==0xd7 and 0xb08e<=c.pc<0xb0ff)or 0x15a<=c.pc<0x17b
    if owned and(tag,c.pc)not in seen:seen.add((tag,c.pc));cuts.append((i,c.pc,bool(c.p&4)))
   m=fork(seed);finish(m,start(m,slot),trace)
   for step,pc,masked in cuts:
    for kind,lag,pause in[('NMI',0,0),('NMI',255,0),('NMI',0,1)]+([]if masked else[('IRQ',255,0)]):
     m=fork(seed);H.put(m,NmiDisable=lag,GamePauseStatus=pause);proof=[]
     def inject(mm,c,i):
      if i==step:assert c.pc==pc;proof.append(L.V.interrupt(mm,c,kind))
     finish(m,start(m,slot),inject);assert len(proof)==1
     q['vectors'].append(dict(owner=raw,valid=valid,service=slot,PC=pc,lag=lag,pause=pause,**proof[0]))
   paths.append(dict(owner=raw,valid=valid,service=slot,instruction_cuts=len(cuts)))
  q['checks']['vectors']=dict(cases=len(q['vectors']),paths=paths,all33SMC_livepage1_AXYP_SP_rawmaps=True,minimum_ISR_SP=min(r['minimum_SP']for r in q['vectors']))
  q.update(passed=True,scope='Linked223B experiment only. Actual all108 owner entries/37rows/all64flags, direct ROM17/26 callback contract, fullcookie/foreign rejects and actual normal/lag/paused NMI+legalIRQ. Native world32 and natural retirement/load/cold Main remain separate obligations; no admission.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['retained_v1_negative']='BtInjury legitimately reenters row7 with native callback A1/X0; V1 falsely required every nested entry to equal outer row5 A55/X7. V2 pins outer input exactly and independently requires every nested target to be a valid B020+3Y row. No source change.'
 files=[R/'tools/audit/bt_jmp_row_cold_controls_v2.py',R/'build/bt-jmp-row-cold-controls-v2/interruption.json',R/'tools/audit/bt_jmp_row_cold_controls_v1.py',R/'build/bt-jmp-row-cold-controls-v1/controls.json',Path(__file__),Path(L.__file__),Path(H.__file__),Path(L.V.__file__),Path(A.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/router.s',P/'source-stage.json',P/'candidate.nes',P/'candidate.dbg',J/'bt/cache.bin',J/'bt/cookie.bin',R/'build/bt-jmp-row-cold-proposal-v1/proposal.json']
 q['bindings']={str(p.resolve()):L.sha(p)for p in files};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['vectors','bindings']}),flush=True);assert q['passed'],q.get('error')
if __name__=='__main__':main()
