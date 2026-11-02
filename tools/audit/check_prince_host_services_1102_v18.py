"""All-callbacks-bound private lifecycle/ingress and actual interrupt cuts."""
from collections import Counter
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_host_events_1102_v17 as E
P,O,W,N=E.P,E.O,E.W,E.N


def host(b,phase=0):
 h=E.quiet(b);blob=(O/'host-services-v18.bin').read_bytes();h.s[0x1b9a:0x1b9a+len(blob)]=blob;h.lab.update(P.T.labels(O/'host-services-v18.lbl'))
 # Rebind the prior event leaves because v18's admission prefix is longer.
 old=P.T.labels(O/'host-services-v17.lbl');targets={old[n]:h.lab[n]for n in ['PpNativeQuietSfx','PpNativeQuietMusic','PpNativeUnpublishedMaterial']}
 for tag,v in h.recovery['instructions'].items():
  if v['mn']not in ['JSR','JMP']:continue
  bank,pc=tag.split(':');at=h.lab[f'PpN_{bank}_{pc}'];dest=h.m[at+1]|h.m[at+2]<<8
  if dest in targets:
   dest=targets[dest];h.m[at+1]=dest&255;h.m[at+2]=dest>>8
 assert not h.callbacks,h.callbacks
 h.terrain(lambda x,y:0x54 if y>=208 else 0)
 N.put(h.m,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,NumberofLives=2,NmiDisable=1,ReloadCHRBank=0)
 h.source('PpNativeInit');h.s[0xa6]=phase
 return h


def invoke(h,name,args=(85,91,197,0x21),interrupt=None):
 h.map();m=h.m;c=N.NesMPU(memory=m,pc=h.lab[name]);c.a,c.x,c.y,c.p=args;c.sp=224;c.stPushWord(0x5aff);cuts=set();low=c.sp;injected=False;kill=0
 start,end=json.loads((O/'host-services-layout-v18.json').read_text())['code_half_open']
 for _ in range(150000):
  if c.pc==0x5b00:break
  low=min(low,c.sp);cut=(c.pc,c.sp,m.rawtags[1])
  if start<=c.pc<end or 0x150<=c.pc<0x180:cuts.add(cut)
  if interrupt is not None and not injected and cut==interrupt[1]:
   injected=True;regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);mapping=m.rawtags[:];state=[bytes(m.ram[k])for k in [2,3]];r0=W.address(h.b,'R0');scratch=bytes(m[r0:r0+8]);smc=bytes(m[0x15a:0x17b]);write_start=len(m.ram_writes);assert not c.p&4
   c.irq()if interrupt[0]=='IRQ'else c.nmi()
   for _ in range(200000):
    low=min(low,c.sp)
    if c.pc==regs[5]and c.sp==regs[4]:break
    assert m[c.pc]!=0,('Real service ISR BRK',interrupt,hex(c.pc));c.step()
   else:raise AssertionError(('Service ISR bound',interrupt))
   assert not any(bank in [2,3]for bank,at,value in m.ram_writes[write_start:])
   if mapping!=m.rawtags:
    assert bytes(m[c.pc:c.pc+3])==bytes([0x8d,0x15,0x51])and m.rawtags[1]==N.get(m,'CurrentBank')and all(mapping[i]==m.rawtags[i]for i in [0,2,3])
   # py65 RTI synthesizes its nonphysical B bit; all real status bits match.
   status=(regs[3]&0xef)==(c.p&0xef)
   assert regs[:3]==(c.a,c.x,c.y)and status and regs[4:]==(c.sp,c.pc)and state==[bytes(m.ram[k])for k in [2,3]]and scratch==bytes(m[r0:r0+8])and smc==bytes(m[0x15a:0x17b]),(interrupt,'registers',regs,(c.a,c.x,c.y,c.p,c.sp,c.pc),'private',state==[bytes(m.ram[k])for k in [2,3]],'scratch',scratch,list(m[r0:r0+8]),'SMC',smc==bytes(m[0x15a:0x17b]))
  if c.pc==W.address(h.b,'KillPlayer')and m.rawtags[1]==((W.location(h.b,'KillPlayer')-16)//8192)|128:kill+=1
  assert m[c.pc]!=0,('Bound private native BRK',name,hex(c.pc));c.step()
 else:raise AssertionError(('Bound private source/services',name,hex(c.pc)))
 assert c.sp==224 and(interrupt is None or injected)
 return dict(C=bool(c.p&1),CPU=c.processorCycles,minSP=low,cuts=cuts,kill=kill,state=[bytes(x)for x in m.ram],native=bytes(m[:0x100]),smc=bytes(m[0x15a:0x17b]),maps=m.rawtags[:])


def main():
 b=W.scoped_load(E.C.BASE);cases=0
 for phase in range(4):
  expected=None
  for x in [0,14,91,255]:
   for y in [0,73,255]:
    for p in [0x20,0x21,0x61,0xa1]:
     h=host(b,phase);out=invoke(h,'PpNativeTick',(85,x,y,p));assert out['C'];view=(out['state'],out['native'])
     if expected is None:expected=view
     else:assert view==expected,('Ingress live state depends on caller X/Y/P',phase,x,y,p)
     cases+=1
 # Replay v16 admission/death suite against the final all-bound successor.
 src=R/'tools/audit/check_prince_host_services_1102_v16.py';text=src.read_text();text=text.replace("h=C.World(b);labels=C.P.T.labels(O/'host-services-v16.lbl');h.lab.update(labels)","h=host18(b);labels=C.P.T.labels(O/'host-services-v18.lbl');h.lab.update(labels)").replace('host-services-v16','host-services-v18').replace('host-services-CPU-v16','host-services-CPU-v18')
 env=dict(__file__=str(src),__name__='prince_final_service_suite',host18=host);exec(compile(text,str(src),'exec'),env)
 with contextlib.redirect_stdout(io.StringIO()):env['main']()
 fixture=O/'host-services-CPU-v18.json';fq=json.loads(fixture.read_text());fq.update(source_audio_remains_explicit_fixture=False,all_original_environment_targets_bound=True,wrapper_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),actual_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),scope='Final all-bound v18 image executes original source/world/native export, quiet original-event bookkeeping and genuine native KillPlayer. Native R0..R7/SMC/maps preserved. Shared auth/cold/retirement, native combat, Main respawn and emulator/full1-1 remain unqualified.');fixture.write_text(json.dumps(fq,indent=2)+'\n')
 total=0;minimum=224;bykind=Counter();scenarios=[]
 for name,death in [('PpNativeTick',False),('PpNativePitDeath',True)]:
  h=host(b)
  if death:N.put(h.m,Player_Y_HighPos=1,Player_Y_Position=240)
  expected=invoke(h,name);cuts=sorted(expected['cuts']);scenarios.append(dict(name=name,unique_service_transport_cuts=len(cuts),real_KillPlayer_calls=expected['kill']))
  for kind in ['IRQ','lagNMI']:
   for cut in cuts:
    z=host(b)
    if death:N.put(z.m,Player_Y_HighPos=1,Player_Y_Position=240)
    got=invoke(z,name,interrupt=(kind,cut))
    assert got['state']==expected['state']and got['maps']==expected['maps']and got['smc']==expected['smc']
    minimum=min(minimum,got['minSP']);total+=1;bykind[kind]+=1
 old=P.T.labels(O/'host-services-v17.lbl');new=P.T.labels(O/'host-services-v18.lbl');a=(O/'host-services-v17.bin').read_bytes()[old['PpNativeQuietSfx']-0xdb9a:];z=(O/'host-services-v18.bin').read_bytes()[new['PpNativeQuietSfx']-0xdb9a:]
 # The translated branches inside the relocated suffix have identical relative
 # operands and native/source absolute operands, hence complete byte equality.
 assert a==z
 q=dict(passed=True,base_ROM_SHA256=E.C.PIN,source_CPU_only=True,native_emulator=False,host_ROM_created=False,all_original_environment_targets_bound=True,remaining_environment_fixture_callbacks=0,all_ingress_X_Y_flags_cases=cases,actual_ISR_service_transport_cuts=total,ISR_by_kind=dict(bykind),minimum_SP=minimum,scenarios=scenarios,zero_ISR_writes_to_RAM2_RAM3_including_same_value=True,source_Physics_and_world_original_bytes_unchanged=True,v17_qualified_quiet_event_motion_suffix_byte_identical=True,audio_quiet_WIP=True,scope='Final private service image; actual original source/world/native query/project and native death execute without callback stubs. Header/cold/foreign retirement/menu integration, native damage/combat, Main respawn and emulator/full1-1 remain unqualified.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'host-services-v18.bin',O/'host-services-layout-v18.json',O/'host-events-CPU-v17.json',O/'host-services-CPU-v18.json',E.C.BASE]})
 (O/'host-ingress-CPU-v18.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
