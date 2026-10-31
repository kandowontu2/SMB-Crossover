"""Complete genuine foreign callers, including their authentic owner NMI state.

The v1 FF-only ISR assertion rejected Arthur's real RAM2 clock. This successor
keeps actual vectors, full context checks and pairwise owner-state equality;
it neither removes nor rewrites any actor/NMI state in the cartridge fixture.
"""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
from check_tmnt_render_oa import address
H=C.H;V=C.A.V
P=R/'build/thomas-physical-host-1031-v9';J=R/'build/thomas-natural-host-1031-v6';O=R/'build/thomas-natural-foreign-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def call(m,n,**kw):
 c=H.start(m,n,**kw);c,lo=H.finish(m,c);assert c.sp==224
 return[c.a,c.x,c.y,c.p,c.sp],c.processorCycles
def consume(m):
 H.put(m,NmiDisable=0);m.writes.clear();m.ppu_log.clear()
 c=H.start(m,'FwCheck');before=(V.cpu_state(c),m.rawtags[:],H.get(m,'CurrentBank'),H.get(m,'CurrentBankC'),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]),[bytes(x)for x in m.ram])
 cycles=c.processorCycles;low=c.sp;c.nmi()
 for steps in range(100000):
  if V.cpu_state(c)==before[0]:break
  low=min(low,c.sp);assert m[c.pc]!=0,('actual normalNMI BRK',hex(c.pc));c.step()
 else:raise AssertionError(('normalNMI did not RTI',V.cpu_state(c),before[0]))
 assert m.rawtags==before[1] and [H.get(m,'CurrentBank'),H.get(m,'CurrentBankC')]==list(before[2:4])
 assert bytes(m[0x15a:0x17b])==before[4] and bytes(m[0x101+c.sp:0x200])==before[5],('normalNMI SMC33/page1')
 assert bytes(m[3:5])==before[6][3:5] and bytes(m[9:11])==before[6][9:11],('normalNMI borrowed pairs')
 changed=[[bank,off,a,z]for bank,(old,new)in enumerate(zip(before[7],m.ram))for off,(a,z)in enumerate(zip(old,new))if a!=z]
 data=[i for i,(a,v)in enumerate(m.writes)if a==0x2007];dma=[i for i,(a,v)in enumerate(m.writes)if a==0x4014]
 assert dma and(not data or max(data)<min(dma))
 H.finish(m,c)
 return dict(CPU=c.processorCycles-cycles,minimumSP=low,owner_RAM_changes=changed,data_writes=len(data),all33SMC_maps_AXYP_SP_page1_borrowed_pairs_exact=True)
def boot(b,slot,alt,group):
 m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=slot,FmAlts=alt,FmGroups=group,SelectedCharacter=0)
 for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:call(m,n)
 H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);call(m,'GameMenuRoutine');call(m,'PauseRoutine',a=0)
 nm=[]
 for i in range(1000):
  if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:return m,i,nm
  H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
  call(m,'GameLoop');nm.append(consume(m))
 raise AssertionError(('foreign parser bound',slot))
def same(pair,label,age):
 raw=lambda m,lo,hi:bytes(list.__getitem__(m,slice(lo,hi)))
 for lo,hi in[(0,256),(512,0x2000),(0x5c00,0x8000)]:
  assert raw(pair[0],lo,hi)==raw(pair[1],lo,hi),('complete application bytes',label,age,hex(lo),[(hex(i),pair[0][i],pair[1][i])for i in range(lo,hi)if pair[0][i]!=pair[1][i]][:12])
 assert pair[0].rawtags==pair[1].rawtags and pair[0].chr_latches==pair[1].chr_latches,('complete mapper/CHR',label,age)
 if label=='Rash':
  assert pair[0].ram[2]==pair[1].ram[2] and pair[0].ram[3][0x1e00:0x1fe0]==pair[1].ram[3][0x1e00:0x1fe0],('BT runtime state',label,age)
 else:assert pair[0].ram[2:]==pair[1].ram[2:],('selected foreign payloads',label,age)
 assert pair[0].vram==pair[1].vram,('actual completed PPU',label,age)
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False,cohorts=[])
 try:
  stage=json.loads((J/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  bs=[H.C.qualified(p/'candidate.nes')for p in[P,J]]
  for label,slot,alt,group in[('Mario',0,0,0),('Bill',3,0,0),('Ryu',10,0,0),('Arthur',31,0,0),('Rash',23,0,0)]:
   pair=[];ages=[];setup=[]
   for b in bs:m,n,nm=boot(b,slot,alt,group);pair.append(m);ages.append(n);setup.append(nm)
   assert ages[0]==ages[1];same(pair,label,'parser')
   assert [r['owner_RAM_changes']for r in setup[0]]==[r['owner_RAM_changes']for r in setup[1]],('actual setup NMI owner writes',label)
   rows=[]
   for age in range(12):
    results=[]
    for m in pair:
     keys=1|(128 if 3<=age<6 else 0)
     H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=1,Up_Down_Buttons=0,NmiDisable=255)
     results.append(call(m,'GameLoop'))
    assert results[0][0]==results[1][0],('complete callerAXYP/SP',label,age,results)
    same(pair,label,age)
    row=dict(age=age,oldCPU=results[0][1],newCPU=results[1][1],delta=results[1][1]-results[0][1],SMC_differences=[hex(i)for i in range(0x15a,0x17b)if pair[0][i]!=pair[1][i]])
    nmi=[consume(m)for m in pair];same(pair,label,('NMI',age))
    assert nmi[0]['owner_RAM_changes']==nmi[1]['owner_RAM_changes'],('actual active NMI writes',label,age,nmi)
    row['NMI']=nmi;rows.append(row)
   q['cohorts'].append(dict(name=label,actual_native_parser_updates=ages,whole_GameLoop_pairs=rows,setup_owner_NMI_changes=[r for r in setup[1]if r['owner_RAM_changes']]))
   print('Thomas foreign actual cold+completecaller+ownerNMI PASS',label,flush=True)
  q.update(passed=True,whole_GameLoop_pairs=60,actual_completed_normalNMIs=sum(2*(c['actual_native_parser_updates'][0]+len(c['whole_GameLoop_pairs']))for c in q['cohorts']),limits=['Five bounded current-family cold cohorts, not exhaustive all74 profiles/native cadence','BT relocated instruction/cookie bytes excluded only from old/new runtime-state equality; actual cache source import/cookie has independent closure','Authentic owner NMI RAM writes are preserved and compared pairwise; v1 FF-only immutable-RAM assertion retained as fixture negative'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(C.__file__),Path(C.A.__file__),Path(V.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','cohorts','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
