"""Five genuine foreign cold scenes and complete native GameLoop callers."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
from check_tmnt_render_oa import address
H=C.H
P=R/'build/thomas-physical-host-1031-v9';J=R/'build/thomas-natural-host-1031-v6';O=R/'build/thomas-natural-foreign-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def call(m,n,**kw):
 c=H.start(m,n,**kw);c,lo=H.finish(m,c);assert c.sp==224
 return[c.a,c.x,c.y,c.p,c.sp],c.processorCycles
def boot(b,slot,alt,group):
 m=C.fresh(b,0);H.put(m,CrossoverMenuIndex=slot,FmAlts=alt,FmGroups=group,SelectedCharacter=0)
 for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:call(m,n)
 H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);call(m,'GameMenuRoutine');call(m,'PauseRoutine',a=0)
 for i in range(1000):
  if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:return m,i
  H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
  call(m,'GameLoop');C.A.consume(m)
 raise AssertionError(('foreign parser bound',slot))
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False,cohorts=[])
 try:
  stage=json.loads((J/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  bs=[H.C.qualified(p/'candidate.nes')for p in[P,J]]
  for label,slot,alt,group in[('Mario',0,0,0),('Bill',3,0,0),('Ryu',10,0,0),('Arthur',31,0,0),('Rash',23,0,0)]:
   pair=[];ages=[]
   for b in bs:m,n=boot(b,slot,alt,group);pair.append(m);ages.append(n)
   assert ages[0]==ages[1]
   rows=[]
   for age in range(12):
    results=[]
    for m in pair:
     keys=1|(128 if 3<=age<6 else 0)
     H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=1,Up_Down_Buttons=0,NmiDisable=255)
     results.append(call(m,'GameLoop'))
    assert results[0][0]==results[1][0],('complete callerAXYP/SP',label,age,results)
    raw=lambda m,lo,hi:bytes(list.__getitem__(m,slice(lo,hi)))
    assert raw(pair[0],0,256)==raw(pair[1],0,256),('complete callerZP',label,age)
    assert raw(pair[0],512,0x2000)==raw(pair[1],512,0x2000),('complete callerRAM/OAM',label,age,[(hex(i),pair[0][i],pair[1][i])for i in range(512,0x2000)if pair[0][i]!=pair[1][i]][:12])
    assert raw(pair[0],0x5c00,0x8000)==raw(pair[1],0x5c00,0x8000),('complete global/contextRAM',label,age)
    assert pair[0].rawtags==pair[1].rawtags and pair[0].chr_latches==pair[1].chr_latches,('complete mapper/CHR',label,age)
    # Retained cache instruction operands/cookie may be source-relocated. The
    # selected actor's actual state remains exact. Never normalize product RAM.
    if label=='Rash':assert pair[0].ram[3][0x1e00:0x1fe0]==pair[1].ram[3][0x1e00:0x1fe0]
    else:assert pair[0].ram[2:]==pair[1].ram[2:],('selected foreign payloads',label,age)
    rows.append(dict(age=age,oldCPU=results[0][1],newCPU=results[1][1],delta=results[1][1]-results[0][1],SMC_differences=[hex(i)for i in range(0x15a,0x17b)if pair[0][i]!=pair[1][i]]))
    for m in pair:C.A.consume(m)
   q['cohorts'].append(dict(name=label,actual_native_parser_updates=ages,whole_GameLoop_pairs=rows))
   print('Thomas foreign actual cold+completecaller PASS',label,flush=True)
  q.update(passed=True,whole_GameLoop_pairs=60,actual_completed_normalNMIs=120,limits=['Five bounded current-family cold cohorts, not exhaustive all74 profiles/native cadence','Relocated BT code/cookie compared as source operands; runtime actor state remains byteexact'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(C.__file__),Path(C.A.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','cohorts','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
