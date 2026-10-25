"""One sequential worker: cold options, actual ability owners and native guards."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def section(text,start,end,replacement):
 assert text.count(start)==text.count(end)==1,(start,end);i=text.index(start);j=text.index(end,i);return text[:i]+replacement+text[j:]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',type=int,choices=[0,1],required=True);p.add_argument('--event',type=lambda s:int(s,0),choices=[0,0x13,0x15,0x24,0x21,0x1e,0x2f,0x1f],default=0x24);p.add_argument('--profile',choices=['basic','priority','pause','scene','death','pressure'],default='basic');p.add_argument('--run',action='store_true');a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);b=load(a.rom);event=a.event
 variant,sub={0:(3,0),0x13:(1,1),0x15:(1,2),0x24:(2,1),0x21:(2,2),0x1e:(2,3),0x2f:(3,0),0x1f:(3,0)}[event]
 if a.profile=='priority':assert event==0x21
 if a.profile=='death':assert event==0x2f
 if a.profile=='pressure':assert event in[0,0x1f]
 kind='idle'if event==0 else'bat'if event==0x2f else'fireball'if event==0x1f else'sub'
 q=dict(name=f'{a.profile}-source{event:02x}-coldmode{a.mode}',kind=kind,profile=a.profile,mode=a.mode,sub=sub,event=event,updates=240 if a.profile=='pressure'else 140)
 names=['PauseSkip','Cv3WeaponsGate','Cv3InjuryStartGate','Cv3SpawnAudioType','Cv3BatUpdate','Cv3NoiseSceneReset','KillPlayer','RemainingDmcStart','Cv3MusicAndNoiseTick','AudioUpdate','NonMaskableInterrupt','IrqScrollSplit','DrawAllMetasprites','RosterOamReady'];hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names};n='NonMaskableInterrupt';delta=int(b['syms'][n]['size'],0)-1;hooks['NmiReturn']=dict(address=address(b,n)+delta,physical_bank=hooks[n]['physical_bank'],bytes=[b['raw'][location(b,n)+delta]])
 perf_names=[n for n in ['AudioUpdate','Cv3MusicAndNoiseTick','Cv3FxTick','Cv3FxService','CvAudioPlay','Cv3FxSpawn']if n in b['syms']]
 for n in perf_names:hooks[n]=dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))
 text=(ROOT/'tools/audit/cv3_dmc_complete_native_v1.lua').read_text().replace('CV3_DMC_COMPLETE_NATIVE_CONFIG','CV3_REMAINING_NATIVE_CONFIG')
 text=text.replace('(v==21 or v==22 or v==26)','(v==21 or v==22 or(v>=26 and v<=32))')
 # Preserve all mapper, physical DMC payload, IRQ, stack, CHR and full OAM guards.
 text=section(text,"if C.hooks.Cv3MusicAndNoiseTick then\n","local function seed(q)",'''local fx=assert(io.open(OUTPUT..'source-voices.csv','w'))
fx:write('wall,age,audioEpoch,pulseID,noiseID,owned,index,pulseFrame,sharedHigh,request,noiseActive,paused,death\\n')
local function voice(n)return C.new_fx==1 and r(n)or 0 end
emu.addMemoryCallback(function()
 if not entered or done or not valid('Cv3NoiseSceneReset')or current.q.profile~='scene'or not current.controlApplied then return end
 local beforePulse,beforeNoise=voice('Cv3FxPulseID'),voice('Cv3FxNoiseID')
 onReturn('actualSceneCancel',function()
  current.sceneResets=current.sceneResets+1;current.sceneReturnWall=wall
  if C.new_fx==1 then
   assert(beforePulse==0x2f and beforeNoise==0x2f,'Real scene cancellation starts with active bat voices')
   assert(voice('Cv3FxPulseID')==0 and voice('Cv3FxNoiseID')==0 and r('AvAudioRequest')==0,'Real scene owner immediately clears source IDs and requests')
   current.sceneImmediate=current.sceneImmediate+1
  end
 end)
end,emu.callbackType.exec,C.hooks.Cv3NoiseSceneReset.address)

emu.addMemoryCallback(function()
 if not entered or done or not valid('Cv3SpawnAudioType')then return end
 local st=emu.getState();current.spawnCalls=current.spawnCalls+1;current.firstActionWall=current.firstActionWall or wall
 current.spawnTypes[#current.spawnTypes+1]={age=age,type=st['cpu.a'],pc=st['cpu.pc'],bank=bank(st['cpu.pc'])}
end,emu.callbackType.exec,C.hooks.Cv3SpawnAudioType.address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('Cv3BatUpdate')then return end
 local before=r('Cv3Bat')
 onReturn('Cv3BatUpdate',function()if before==0 and r('Cv3Bat')==1 then current.batEntries=current.batEntries+1;current.firstActionWall=current.firstActionWall or wall end end)
end,emu.callbackType.exec,C.hooks.Cv3BatUpdate.address)
emu.addMemoryCallback(function()
 if not entered or done or not valid('AudioUpdate')then return end
 onReturn('Cv3FxAudio',function()
  fx:write(table.concat({wall,age,audioEpoch,voice('Cv3FxPulseID'),voice('Cv3FxNoiseID'),voice('Cv3FxOwned'),r('Cv3NoiseIndex'),voice('Cv3FxPulseFrame'),voice('Cv3FxSourceHigh'),r('AvAudioRequest'),r('Cv3NoiseActive'),r('GamePauseStatus')&1,r('MmDeathFlag')},',')..'\\n');fx:flush()
  if C.new_fx==1 and current.spawnCalls>=4 and voice('Cv3FxNoiseID')==0x21 then current.mixedPriority=current.mixedPriority+1 end
  if current.controlApplied and voice('Cv3FxOwned')==0 and r('Cv3NoiseActive')==0 then current.controlReleased=true end
 end)
end,emu.callbackType.exec,C.hooks.AudioUpdate.address)
''')
 text=text.replace("audioUpdate,register,value,cycle,pc,bank", "audioUpdate,register,value,cycle,pc,bank,audioEpoch")
 text=text.replace("st['cpu.pc'],bank(st['cpu.pc'])},',')..'\\n')", "st['cpu.pc'],bank(st['cpu.pc']),audioEpoch},',')..'\\n')")
 text=text.replace("current.requests=current.requests+1\n", "current.requests=current.requests+1;local requestState=emu.getState();requests:write(table.concat({wall,age,audioEpoch,v,requestState['cpu.pc'],bank(requestState['cpu.pc'])},',')..'\\n');requests:flush()\n",1)
 text=text.replace("local audioEpoch=0", "local audioEpoch=0\nlocal requests=assert(io.open(OUTPUT..'requests.csv','w'));requests:write('wall,age,audioEpoch,request,pc,bank\\n')\nlocal audioInFlight=false\nemu.addMemoryCallback(function()if entered and not done and audioInFlight then local pc=emu.getState()['cpu.pc'];local owner=bank(pc);assert(owner~=27 and owner~=28 and owner~=29 and owner~=82 and owner~=84,'Audio bank must not write viewport VRAM')end end,emu.callbackType.write,0x2007)")
 text=text.replace("audioEpoch=audioEpoch+1", "audioEpoch=audioEpoch+1;audioInFlight=true")
 text=text.replace("onReturn('Cv3FxAudio',function()", "onReturn('Cv3FxAudio',function()\n  audioInFlight=false")
 text=text.replace("w('CrossoverBehaviorVersion',q.mode);assert(r('CrossoverBehaviorVersion')==q.mode,'Mode readback matches requested mode')","assert(q.mode==C.mode and r('CrossoverBehaviorVersion')==C.mode,'Cold options mode readback matches requested mode')")
 text=text.replace("w('Cv3Subweapon',0,C.variant-1);w('Cv3Health',64,C.variant-1)","w('Cv3Subweapon',q.sub,C.variant-1);w('Cv3Hearts',64,C.variant-1);w('Cv3Health',64,C.variant-1)")
 text=text.replace("liveDmc=nil;lastDmcEnable=0;lastApu={}","current.spawnCalls=0;current.spawnTypes={};current.batEntries=0;current.mixedPriority=0;current.controlReleased=false;current.sceneResets=0;current.sceneImmediate=0;liveDmc=nil;lastDmcEnable=0;lastApu={}")
 text=text.replace("if q.kind=='idle'then w('Cv3Invul',255);w('InjuryTimer',255);w('GuestInvulTicks',255)end","if q.profile=='pressure'then w('Cv3Invul',255);w('InjuryTimer',255);w('GuestInvulTicks',255)end")
 text=text.replace("if q.kind=='contact'or q.kind=='pressure'or q.kind=='pause'or q.kind=='idle'then","if q.profile=='pressure'then")
 text=text.replace("((q.kind=='pressure'or q.kind=='idle')and 5 or 0)","5 ")
 text=section(text,'local function finishCase()','emu.addMemoryCallback(function()\n if done or not valid(\'PauseSkip\')', '''local function finishCase()
 local q=current.q
 local f=assert(io.open(OUTPUT..'last-case.json','w'));f:write(json(current));f:close();capture('case-end')
 assert(current.modeReadback==C.mode,'Actual cold mode remains bound')
 if q.kind=='idle'then assert(current.requests==0 and current.spawnCalls==0 and current.realInjuries==0,'Equal-work no-source pressure is cue-free')
 elseif q.kind=='bat'then assert(current.batEntries>0,'Actual Down+A reaches bat entry')
 else assert(current.spawnCalls>0,'Actual B/Up+B creates real native projectile')end
 local expected=q.event==0x1f or C.new_fx==1
 if q.kind~='idle'then
  assert((current.requests>0)==expected,'Actual weapon release has expected source cue or bound missing-cue negative')
 end
 if q.profile=='priority'and C.new_fx==1 then assert(current.mixedPriority>0,'Actual ice then lower-priority lightning retains source noise33')end
 if q.profile=='pause'then assert(current.pauseFrames>=30,'Actual Start pause/resume exercised')end
 if q.profile=='scene'and C.new_fx==1 then assert(current.controlApplied and current.controlReleased and current.sceneImmediate>0 and current.requests==1,'Actual scene reset immediately cancels IDs and releases before any retrigger')end
 if q.profile=='death'then assert(current.deathCalls and current.realInjuries>0,'Actual fatal enemy contact reaches KillPlayer');if C.new_fx==1 then assert(voice('Cv3FxOwned')==0 or voice('Cv3FxNoiseID')==0 and voice('Cv3FxPulseID')==0,'Death cancels source priorities')end end
 current.durationUpdates=age;results[#results+1]=current
end
''')
 text=text.replace("if current.q.kind=='idle'and age%24==0 then", "if current.q.profile=='pressure'and age%24==0 then")
 text=section(text," if(age==28 and current.q.kind=='attack')",' if age>=C.cases[index].updates then', ''' if current.q.profile=='priority'and age==32 then w('Cv3Subweapon',3,C.variant-1)end
 if current.q.profile=='death'and age==40 then
  w('Cv3Health',1,C.variant-1);w('Cv3Invul',0);w('InjuryTimer',0);w('GuestInvulTicks',0)
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_X_Position',(r('Player_X_Position')-8)&255);w('Enemy_PageLoc',0)
  w('Enemy_Y_Position',184);w('Enemy_Y_HighPos',1);w('Enemy_MovingDir',1);w('Enemy_X_Speed',8);w('Enemy_Y_Speed',0)
 end
''')
 text=section(text,'emu.addEventCallback(function()\n local b={}', 'emu.addEventCallback(function()\n wall=wall+1', '''local phase=C.mode==1 and'options-focus'or'start'
local function menu()
 if wall<120 or wall%12~=0 then return{}end
 if phase=='options-focus'then phase='options-open';return{down=true}end
 if phase=='options-open'then phase='mode-focus';return{a=true}end
 if phase=='mode-focus'then
  if r('CrossoverMenuState')~=4 then return{}end
  if r('CrossoverOptionsFocus')~=1 then return{down=true}end
  phase='mode-set'
 end
 if phase=='mode-set'then if r('CrossoverBehaviorVersion')==0 then return{a=true}end;phase='back';return{}end
 if phase=='back'then phase='start';return{b=true}end
 if r('CrossoverMenuState')==2 then
  local ix=r('CrossoverMenuIndex');if ix~=C.menu_index then return{[assert(C.menu_next[tostring(ix)])]=true}end
  if r('Cv3Variant')~=C.variant then return{select=true}end
  return{a=true}
 end
 return{start=true}
end
emu.addEventCallback(function()
 if not entered then emu.setInput(menu(),0);return end
 local b={}
 if not done then
  local q=current.q;local pressed=age>=4 and age<=6
  if q.profile=='priority'then pressed=pressed or age>=32 and age<=34 end
  if q.profile=='pressure'and q.kind=='fireball'then pressed=age%32>=4 and age%32<=6 end
  if q.kind=='sub'then b.b=pressed;b.up=pressed
  elseif q.kind=='fireball'then b.b=pressed
  elseif q.kind=='bat'then b.a=pressed;b.down=pressed end
  if q.profile=='pause'and current.firstActionWall then b.start=wall==current.firstActionWall+1 or wall==current.firstActionWall+50 end
 end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
''')
 text=section(text,'  if current.firstDmcWall and wall>=', '  current.frames=current.frames+1', '''  if current.firstActionWall and wall>=current.firstActionWall+6 and current.q.profile=='scene'and not current.controlApplied then w('Cv3LastArea',r('Cv3LastArea')~1);current.controlApplied=true end
''')
 text=text.replace("if(current.q.kind=='pause'or current.q.kind=='primary-pause')and r('GamePauseStatus')&1~=0", "if current.q.profile=='pause'and r('GamePauseStatus')&1~=0")
 text=text.replace("if current.q.kind=='death'and current.deathWall", "if current.q.profile=='death'and current.deathWall").replace('wall-current.deathWall>=45','wall-current.deathWall>=65')
 text=text.replace("current.cueEpoch=audioEpoch+1;current.cueSerial", "current.firstCueWall=current.firstCueWall or wall;current.cueEpoch=audioEpoch+1;current.cueSerial")
 text=text.replace("audio:close();cadence:close();actors:close();fetch:close()", "audio:close();cadence:close();actors:close();fetch:close();fx:close();requests:close()")
 text=text.replace("local function seed(q)","""local perf=assert(io.open(OUTPUT..'native-cycles.csv','w'));perf:write('wall,age,audioEpoch,name,cycles,entryCycle,exitCycle\\n')
for _,name in ipairs(C.perf_names)do
 local n=name
 emu.addMemoryCallback(function()
  if not entered or done or not valid(n)then return end
  local begin=emu.getState()['cpu.cycleCount']
  onReturn('perf:'..n,function()local finish=emu.getState()['cpu.cycleCount'];perf:write(table.concat({wall,age,audioEpoch,n,finish-begin,begin,finish},',')..'\\n');perf:flush()end)
 end,emu.callbackType.exec,C.hooks[n].address)
end
local function seed(q)""")
 text=text.replace('fetch:close();fx:close();requests:close()', 'fetch:close();fx:close();requests:close();perf:close()')
 guard=(ROOT/'tools/audit/z2_platform_native_qa.lua').read_text();text=text.replace('-- NMI_GUARD_INSERT',guard[guard.index('local savedNmi=nil'):guard.index('local function seed(q)')])
 tables={n:list(b['raw'][location(b,'X5Menu'+n):location(b,'X5Menu'+n)+19])for n in['Up','Down','Left','Right']};nav={}
 for start in range(19):
  queue=[(start,[])];seen={start}
  for node,path in queue:
   if node==5:nav[str(start)]=path[0]if path else'a';break
   for n,t in tables.items():
    nxt=t[node]
    if nxt not in seen:seen.add(nxt);queue.append((nxt,path+[n.lower()]))
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text));mirror=int('Cv3DmcPriority'in b['syms']);samples=[];orig=json.loads((D/'cv3-dmc-followup-v1/capacity-source-v1/proof.json').read_text())
 for snd,name in[(0x74,'Grant'),(0x75,'Sypha'),(0x76,'Alucard'),(0x73,'Simon')]:
  rec=next(r for r in orig['source_injury']if r['character']==name);payload=(D/'cv3-dmc-followup-v1/capacity-source-v1'/(name.lower()+'-injury.dmc')).read_bytes();samples.append(dict(sound=snd,bank=125 if snd!=0x73 else 127,address=0xf5c0 if snd==0x75 else 0xff00,rate=rec['rate'],payload=list(payload)))
 payload=(D/'cv3-primary-sfx-v1/source-cpu-v2/cv3-event72.dmc').read_bytes();samples.append(dict(sound=0x72,bank=125,address=0xf140,rate=15,payload=list(payload)))
 lo,hi=location(b,'AvDmcLinkTakeDamage'),location(b,'AvDmcLinkTakeDamageEnd');samples.append(dict(sound=21,bank=127,address=address(b,'AvDmcLinkTakeDamage'),rate=15,payload=list(b['raw'][lo:hi])))
 cfg=dict(perf_names=perf_names,character=5,variant=variant,mode=a.mode,menu_index=5,menu_next=nav,cases=[q],new_fx=int('Cv3FxOwned'in b['syms']),observe=0,mirror=mirror,samples=samples,overlays=[[0x1140,0x1581],[0x15c0,0x1681],[0x1af7,0x1b8a]],hooks=hooks,ram={n:address(b,n)for n in used if n in b['syms']},smc_fields=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 irq=location(b,'IrqScrollSplit');cfg['irq_scroll_stores']=[address(b,'IrqScrollSplit')+i for i in range(66)if b['raw'][irq+i:irq+i+3]in[bytes.fromhex('8d0520'),bytes.fromhex('8e0520')]]
 script=out/'run.lua';script.write_bytes(('CV3_REMAINING_NATIVE_CONFIG='+lua(cfg)+'\n'+text).encode());assert not re.search(r'\b(?:True|False)\b',script.read_text().splitlines()[0]);(out/'configuration.json').write_text(json.dumps(cfg,indent=2)+'\n')
 deps=[Path(__file__),ROOT/'tools/audit/cv3_dmc_complete_native_v1.lua',ROOT/'tools/audit/z2_platform_native_qa.lua',ROOT/'tools/audit/observe_chip_committed_write.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/check_tmnt_render_oa.py'];frozen=out/'frozen';frozen.mkdir();bindings={}
 for f in deps:shutil.copyfile(f,frozen/f.name);bindings[str(f)]=sha(f)
 (out/'bindings.json').write_text(json.dumps(dict(ROM_sha256=sha(a.rom),script_sha256=sha(script),dependencies=bindings,emulator_sha256=sha('C:/mesen2/Mesen.exe'),numeric_cold_mode=a.mode),indent=2)+'\n')
 if not a.run:print(json.dumps(dict(prepared=True,output=str(out),ROM_sha256=sha(a.rom))));return
 cmd=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator','C:/mesen2/Mesen.exe',str(script),str(a.rom.resolve()),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(out/'host.log').open('w')as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 proof=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False);proof.update(ROM_sha256=sha(a.rom),bindings_sha256=sha(out/'bindings.json'),profile=a.profile,event=event,mode=a.mode,emulator_exit=r.returncode,passed=not r.returncode and proof.get('passed',False),accepted=False,scope='Cold real options/character/alternate selection, staged legal ability/terrain/enemy arenas with actual physical controls. Native IRQ/NMI/fiveSMC/bank/stack/OAM/CHR guards. No waveform, complete campaign or universal cadence certification.');(out/'native-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],exit=r.returncode,output=str(out))));raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
