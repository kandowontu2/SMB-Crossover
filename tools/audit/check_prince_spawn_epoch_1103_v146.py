"""Actual constructors/native entrance and first8 resync; no fixed spawn Y."""
from pathlib import Path
from collections import Counter
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_cold_1103_v131 as C
import check_prince_strike_actual_1103_v134 as A
N,O=C.N,C.O


def inject(m):
 m.ram[3][:8159]=(O/'native-runtime-v145.bin').read_bytes();m.ram[2][0x800:0x800+6095]=(O/'native-metadata-v145.bin').read_bytes();m.ram[2][0x766:0x800]=(O/'native-state-v145.bin').read_bytes()[-154:]
 return json.loads((O/'native-labels-v145.json').read_text())


def main():
 base,manifest=C.image();lab=json.loads((O/'native-labels-v122.json').read_text());actual=N.NesMPU;entries=[]
 class Trace(actual):
  def step(self):
   if self.memory.rawtags[2]==2 and self.pc==lab['PpNativeInit']:entries.append(dict(ready=self.memory.ram[2][0xab],valid=self.memory.ram[2][0xaa],Y=N.get(self.memory,'Player_Y_Position'),YHigh=N.get(self.memory,'Player_Y_HighPos')))
   return super().step()
 N.NesMPU=Trace
 try:
  seed,_=C.cold(base,38);cold_entries=entries[:];assert cold_entries and all(e['ready']==0 for e in cold_entries)
  all_fresh=[]
  for version in [122,145]:
   for row in [15,36]:
    for y,high in [(0,0),(32,1),(176,1),(208,1)]:
     m=N.fork(seed)
     if version==145:inject(m)
     N.put(m,Player_Y_Position=y,Player_Y_HighPos=high);entries.clear();C.I.invoke(m,193,0xb08c+3*row)
     assert len(entries)==1 and entries[0]['ready']==0,(version,row,y,high,entries)
     all_fresh.append(dict(version=version,row=row,Y=y,YHigh=high,entry=entries[0]))
 finally:N.NesMPU=actual
 # Genuine native entrance owns the position write. This typed header input
 # uses the unchanged native table; no player position/death outcome is set
 # after Fresh. Native PlayerEntrance performs the engine7->8 transition.
 m=N.fork(seed);N.put(m,Player_Y_Position=0,Player_Y_HighPos=0,PlayerEntranceCtrl=2,AltEntranceControl=0,ScreenLeft_PageLoc=0,AreaType=1,GameTimerSetting=1,FetchNewGameTimerFlag=1)
 C.I.invoke(m,193,0xb08c+3*36);assert m.ram[2][0x84]+256*m.ram[2][0x85]==0xff20
 N.invoke(m,'Entrance_GameTimerSetupCore',a=83,x=0,y=0,p=0x21)
 assert N.get(m,'Player_Y_Position')==176 and N.get(m,'Player_Y_HighPos')==1 and N.get(m,'GameEngineSubroutine')==7
 guards=[]
 for version in [122,145]:
  z=N.fork(m)
  if version==145:inject(z)
  before=[bytes(a)for a in z.ram];out=C.I.invoke(z,193,0xb08c,(83,0,0,0x21));assert not out['regs'][3]&1 and before==[bytes(a)for a in z.ram];guards.append(version)
 N.invoke(m,'PlayerEntrance',a=83,x=0,y=0,p=0x21);assert N.get(m,'GameEngineSubroutine')==8
 N.put(m,OperMode_Task=3,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,Mirror_PPUMASK=30);m[0x2001]=30;A.U.T.terrain(m,lambda x,y:0x54 if y>=208 else 0)
 e=A.environment();pair=[N.fork(m),N.fork(m)];newlab=inject(pair[1]);outs=[]
 for z,labels in zip(pair,[lab,newlab]):outs.append(e['run'](z,'GameLoop',labels))
 assert N.get(pair[0],'Player_Y_Position')==0,('Original native negative not reproduced',N.get(pair[0],'Player_Y_Position'))
 assert N.get(pair[1],'Player_Y_Position')==176 and pair[1].ram[2][0x84]+256*pair[1].ram[2][0x85]==208
 start=N.get(pair[1],'Player_X_Position');minimum=outs[1]['minSP']
 for epoch in range(48):
  z=pair[1];z.controller_pad=1;N.put(z,SavedJoypad1Bits=1,SavedJoypadBits=1);out=e['run'](z,'GameLoop',newlab);minimum=min(minimum,out['minSP']);assert N.get(z,'NumberofLives')==2 and N.get(z,'GameEngineSubroutine')==8
 assert N.get(pair[1],'Player_X_Position')>start and N.get(pair[1],'Player_Y_Position')==176
 # Exact cold continuation destroys pre-constructor private prefix, then
 # enters the same canonical ResetTail used by both public Fresh slots.
 runtime=(O/'native-runtime-v122.bin').read_bytes();public=(O/'native-public-v122.s').read_text();services=(O/'native-services-v122.s').read_text()
 assert runtime[0xbfc6-0xa000:0xbfce-0xa000]==bytes.fromhex('9900c0c8c0b0d0f8')and runtime[0xbfd6-0xa000:0xbfd9-0xa000]==bytes.fromhex('4ce7de')
 assert public.count('jmp PpNativeInit')==1 and services.count('jsr PpHostInit')==1 and 'FreshPrefix:\n sta $c000,x'in public
 sources=[(O/f'native-{n}-v122.s').read_text()for n in ['services','battle','proxy','public','policies','audio','small']]
 assert sum(s.count(' jsr PpNativeInit')+s.count(' jmp PpNativeInit')for s in sources)==1
 q=dict(passed=True,CPU_only=True,source_code_injected=True,changed_full_cold_qualified=False,ROM_written=False,parent_memory_SHA256=manifest['expected_memory_only_SHA256'],actual_cold_NativeInit_entries=cold_entries,all16_public_Fresh_constructor_cases=all_fresh,native_engine7_public_move_rejections_exact=guards,original_stale_first8_native_Y=0,actual_native_entrance_Y=176,resynchronized_source_foot=208,resynchronized_native_Y=176,real_native_PlayerEntrance_transition=True,following_Right_updates=48,Right_first_X=start,Right_last_X=N.get(pair[1],'Player_X_Position'),foreground_minimum_SP=minimum,constructor_closure='All pre-existing source-backed direct NativeInit calls: sole JMP in canonical public ResetTail. Both public row15/36 Fresh paths zeroC000..AF before it; actual cold BFD6 JMPs that same ResetTail after exact BFC6 prefixzero loop. All seven emitted private sources have no other direct target; typed resident/descriptor entry is publicRoute, not Init. New sole helper call occurs at EpochValid0 after engine8/auth guards and before any original live update. Full original indirect-reader closure remains frozen grants; no new vector/table target is introduced.',scope='Actual sharedcold observes Ready0 at every current constructor;16 real Fresh calls across old/new code and four coordinate/high inputs retain Ready0 ingress. Actual native Entrance_GameTimerSetupCore table suppliesY176/high1 and PlayerEntrance sets engine8. Old code reproduces real native firstTickY0 negative; proposed145 resync uses actual coordinates and preserves176/foot208 then genuine48Rightupdates. Typed world/header preconditions only; no postFresh position or native outcome seeds. Prototype only: new backing/cookie/cold/currentIRQ/nested/native still pending; backdrop/status remain separate.',bindings={p.relative_to(R).as_posix():C.M.M.sha(p.read_bytes())for p in [Path(__file__),O/'deferred-strike-measurement-v145.json',O/'native-services-v145.s',O/'native-public-v122.s',O/'native-runtime-v122.bin',O/'native-metadata-v145.bin',O/'native-labels-v145.json',O/'native-spawn-diagnostic-v144/capture/spawn-first-write.csv',R/'src/player.s']})
 (O/'spawn-epoch-CPU-v146.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','all16_public_Fresh_constructor_cases']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'spawn-epoch-negative-v146.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
