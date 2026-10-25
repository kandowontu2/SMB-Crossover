"""Record exact real-menu diagnostic inputs and native cooldown writes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--mapper',choices=('mmc3','mmc5'),default='mmc3');p.add_argument('--record',action='store_true');p.add_argument('--frames',type=int,default=2200);a=p.parse_args()
O=R/'build/verification'/('cannon-replay-config-'+a.tag);assert not O.exists();O.mkdir()
P=R/'build/roster-through-2-2/cannon-bv-bill-3-v0-mmc3'
src=R/'build/verification/diagnostic-config-cannon-bv-bill/policy.lua'
s=src.read_text(encoding='utf-8')
hook=r'''
local timerFrame=0
local timers=assert(io.open(ROSTER_CONFIG.out..'cannon-timer-writes.csv','w'))
timers:write('frame,world,level,area,slot,old,new,pc,bank,logicFrame\n')
local function read(n,i)return emu.read(assert(L[n])+(i or 0),emu.memType.nesDebug)end
emu.addMemoryCallback(function(addr,value)
 if timerFrame<800 then return end
 local i=addr-L.Cannon_Timer;local st=emu.getState()
 timers:write(table.concat({timerFrame+1,read('WorldNumber'),read('LevelNumber'),read('AreaType'),i,read('Cannon_Timer',i),value,st['cpu.pc'],read('CurrentBank'),read('FrameCounter')},',')..'\n');timers:flush()
end,emu.callbackType.write,L.Cannon_Timer,L.Cannon_Timer+5)
emu.addEventCallback(function()timerFrame=timerFrame+1;if timerFrame>=ROSTER_CONFIG.limit then timers:close()end end,emu.eventType.endFrame)
return choose
'''
assert s.count('return choose\n')==1;s=s.replace('return choose\n',hook)
policy=O/'policy.lua';policy.write_text(s,encoding='utf-8')
rom=a.rom.resolve();inputs=P/'inputs.csv'
cmd=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','3','--mapper',a.mapper,'--rom',str(rom),'--tag',a.tag,'--replay',str(inputs),'--policy',str(policy),'--frames',str(a.frames),'--timeout','150','--workspace-cap-gb','100']
if a.record:cmd+=['--record-segments']
(O/'config.json').write_text(json.dumps(dict(ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),input_sha256=hashlib.sha256(inputs.read_bytes()).hexdigest(),policy_sha256=hashlib.sha256(policy.read_bytes()).hexdigest(),emulated_writes=False,explicit_cheats='Invincibility ON and real level select5-2. Not an ordinary final route.',command=cmd),indent=2)+'\n',encoding='utf-8')
raise SystemExit(subprocess.run(cmd,cwd=R).returncode)
