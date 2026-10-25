"""Matched staged native foreground/lag benchmark, never a campaign proof."""
from pathlib import Path
import csv,hashlib,importlib.util,json,statistics,subprocess,sys,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'matched-benchmark-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 O.mkdir(exist_ok=False)
 # The existing replay pipeline owns one worker until its final receipt.
 # Queue behind it rather than briefly starting a third emulator between cases.
 marker=P/'remaining-roster-v1/pipeline.json'
 (O/'queued.json').write_text(json.dumps(dict(waiting_for=str(marker),max_total_native_workers=2),indent=2))
 while not marker.exists():time.sleep(10)
 helper=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 profiler=R/'build/verification/root49-current-f-samus-exclusive-profile-bj/profile-actual-ram-return.lua'
 assert sha(profiler)=='69876d2888b8461512b4129537fa4f30919dc09d2a9bdab0437be9a1a24c47b5'
 (O/'profiler.lua').write_bytes(profiler.read_bytes())
 report=dict(complete=False,passed=False,goal_complete=False,runs=[],scope='Matched staged stationary scene with three real initialized Goomba actors reset at each native logical update. Music/audio remain enabled. Only ordinary completed interrupt-excluded native function timings within the admitted fixture window are used. This is neither a controller-only route nor a hardware-wide FPS claim.')
 for name,route in [('megaman',P/'routes-v1/megaman-easy'),('samus',P/'routes-v1/samus-easy'),('bill',P/'routes-v1/bill-easy'),('raphael',P/'remaining-roster-v1/raphael-easy')]:
  for version,rom in [('pz',R/'build/checkpoints/native-head-pz/candidate.nes'),('qa',P/'candidate.nes')]:
   out=O/(name+'-'+version);out.mkdir();(out/'frames').mkdir();image=im.Image(rom)
   hooks={n:image.hook(n)for n in ('GameLoop','PlayerBGCollision','CrossoverHeadProbe','CrossoverSourceSideProbe','EnemiesAndLoopsCore')}
   hooks.update(NMI=image.hook('NonMaskableInterrupt'),IRQ=image.hook('IrqScrollSplit'),NMI_END=image.hook('NonMaskableInterrupt',delta='last'),IRQ_END=image.hook('IrqScrollSplit',delta='last'))
   pc=image.ram['FarcallJmpTarget_SMC']+3;ret=image.hook('FarCallCommon',delta=pc-image.ram['FarCallCommon'])
   fields=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_PageLoc','Enemy_X_Position','Enemy_Y_HighPos','Enemy_Y_Position','Enemy_X_Speed','Enemy_Y_Speed','Enemy_Y_MoveForce','Enemy_X_MoveForce','Enemy_MovingDir','Enemy_BoundBoxCtrl','Enemy_SprAttrib','EnemyIntervalTimer','EnemyFrameTimer','MmEnemyHealthLo','MmEnemyHealthHi']
   fields=[n for n in fields if n in image.ram]
   lua=r'''
local active=false
local startFrame,physicalFrames,logicalUpdates,lag,previousLag=0,0,0,0,0
local template={}
local csv=assert(io.open(ROSTER_CONFIG.out..'fixture.csv','w'))
csv:write('frame,physical,logical,lag,x,y,state,engine,enemy0x,enemy0y,enemy1x,enemy1y,enemy2x,enemy2y\n')
local function r(n,i)return emu.read(assert(BENCH.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,i,v)emu.write(assert(BENCH.ram[n],n)+i,v,emu.memType.nesDebug)end
local function writeFixture()
 for i=0,5 do
  if i<3 then
   for _,n in ipairs(BENCH.fields)do w(n,i,template[n])end
   local x=288+i*32
   w('Enemy_Flag',i,1);w('Enemy_ID',i,6);w('Enemy_State',i,0)
   w('Enemy_X_Position',i,x%256);w('Enemy_PageLoc',i,x//256)
  else w('Enemy_Flag',i,0)end
 end
end
emu.addMemoryCallback(function()
 if not active then return end
 local h=BENCH.gameLoop;local p=emu.convertAddress(h.address)
 if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
 for j,v in ipairs(h.bytes)do assert(emu.read(h.address+j-1,emu.memType.nesDebug)==v,'Exact actual GameLoop fixture boundary')end
 assert(r('GameEngineSubroutine')==8 and r('WorldNumber')==0 and r('LevelNumber')==0,'Staged benchmark stays in live1-1')
 logicalUpdates=logicalUpdates+1;writeFixture()
end,emu.callbackType.exec,BENCH.gameLoop.address)
emu.addEventCallback(function()
 if not active then return end
 physicalFrames=physicalFrames+1
 local now=r('NmiSkipped');lag=lag+((now-previousLag)&255);previousLag=now
 csv:write(table.concat({startFrame+physicalFrames,physicalFrames,logicalUpdates,lag,r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('GameEngineSubroutine'),r('Enemy_X_Position')+256*r('Enemy_PageLoc'),r('Enemy_Y_Position'),r('Enemy_X_Position',1)+256*r('Enemy_PageLoc',1),r('Enemy_Y_Position',1),r('Enemy_X_Position',2)+256*r('Enemy_PageLoc',2),r('Enemy_Y_Position',2)},',')..'\n')
 if physicalFrames==1200 then
  csv:close()
  local f=assert(io.open(ROSTER_CONFIG.out..'fixture-result.json','w'))
  f:write(string.format('{"start_frame":%d,"end_frame":%d,"physical_frames":%d,"logical_updates":%d,"skipped_NMIs":%d,"staged":true,"original_audio_enabled":true}',startFrame,startFrame+physicalFrames,physicalFrames,logicalUpdates,lag));f:close()
  emu.stop(0)
 end
end,emu.eventType.endFrame)
return function(c)
 if active then return{}end
 if c.world==0 and c.level==0 and c.engine==8 and c.x>=208 and c.grounded then
  local slot
  for i=0,5 do if r('Enemy_Flag',i)==1 and r('Enemy_ID',i)==6 and r('Enemy_State',i)==0 then slot=i;break end end
  if slot then
   for _,n in ipairs(BENCH.fields)do template[n]=r(n,slot)end
   startFrame=c.frame;previousLag=r('NmiSkipped');active=true;writeFixture();return{}
  end
 end
 return{right=c.x<208}
end
'''
   base=out/'fixture-policy.lua';base.write_text('BENCH='+im.lua(dict(ram=image.ram,gameLoop=hooks['GameLoop'],fields=fields))+'\n'+lua.replace('\\n','\n'))
   policy=out/'policy.lua';policy.write_text('ORDINARY_PROFILE='+im.lua(dict(hooks=hooks,ram=image.ram,ram_return=ret,start_frame=350,stop_frame=5000,base_policy=base.as_posix()))+'\nreturn dofile('+im.lua((O/'profiler.lua').as_posix())+')\n')
   text=(route/'run.lua').read_text();text=text.replace('out='+json.dumps(route.as_posix()+'/'),'out='+json.dumps(out.as_posix()+'/'));text=text.replace('policy='+json.dumps((route/'policy.lua').as_posix()),'policy='+json.dumps(policy.as_posix())).replace('capture=12,','capture=60,')
   script=out/'run.lua';script.write_text(text)
   with(out/'host.log').open('w')as log:
    p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(rom),'--timeout','150','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
   assert p.returncode==0,(out/'host.log').read_text()[-2500:]
   result=json.loads((out/'fixture-result.json').read_text());rows=list(csv.DictReader((out/'fixture.csv').open()));assert len(rows)==1200
   assert all(z['engine']=='8'and z['state']=='0'and z['y']=='176'for z in rows),'Stationary live floor scene throughout'
   assert max(int(z['x'])for z in rows)-min(int(z['x'])for z in rows)<=4,'No locomotion workload drift'
   groups={}
   for line in(out/'ordinary-profile.jsonl').open():
    z=json.loads(line)
    if result['start_frame']+60<=z['frame'] and z['return_frame']<result['end_frame']-1:groups.setdefault(z['name'],[]).append(z['exclusive_cycles'])
   assert all(n in groups for n in ('GameLoop','PlayerBGCollision','CrossoverSourceSideProbe'))
   metrics={n:dict(calls=len(v),median=statistics.median(v),mean=statistics.mean(v),p95=sorted(v)[int((len(v)-1)*.95)])for n,v in groups.items()}
   row=dict(identity=name,version=version,ROM_sha256=sha(rom),passed=True,fixture=result,metrics=metrics,source_run_sha256=sha(route/'run.lua'),staged_fields=fields,folder=str(out));report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(identity=name,version=version,fixture=result,GameLoop=metrics['GameLoop'])),flush=True)
 report['complete']=True;report['passed']=True;(O/'proof.json').write_text(json.dumps(report,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
