"""Full independent H Samus replay, actual accepted-jump/support and hardware audit."""
from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-fixed-gj'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
LUA=r'''local H=HOOKS
local frame,depth=0,0
local f=assert(io.open(ROSTER_CONFIG.out..'samus-accepted-native.jsonl','w'))
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function tile(x,y)
 if y<32 or y>=240 then return -1 end
 return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)
end
local function capture(name,h)
 local s=emu.getState();local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position');local a={}
 for i=0,5 do a[#a+1]=string.format('[%d,%d,%d,%d,%d,%d,%d,%d,%d]',i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i),r('PlatformCollisionFlag',i),r('Enemy_BoundBoxCtrl',i))end
 f:write(string.format('{"event":"%s","frame":%d,"pc":%d,"bank":%d,"cycle":%d,"world":%d,"level":%d,"areaType":%d,"x":%d,"y":%d,"yHigh":%d,"xf":%d,"yf":%d,"state":%d,"raw":%d,"previousAB":%d,"clearance":%d,"ball":%d,"crouch":%d,"sourceJumped":%d,"power":%d,"spring":%d,"springForce":%d,"footL":%d,"footR":%d,"actors":[%s]}\n',name,frame+1,h.address,h.physical_bank,s['cpu.cycleCount'],r('WorldNumber'),r('LevelNumber'),r('AreaType'),x,y,r('Player_Y_HighPos'),r('MmXFraction')+256*r('MmXFraction',1),r('MmYFraction')+256*r('MmYFraction',1),r('Player_State'),r('SavedJoypadBits'),r('PreviousA_B_Buttons'),r('SmClearance'),r('SmBall'),r('SmCrouch'),r('SmSourceJumped'),r('PlayerStatus'),r('JumpspringAnimCtrl'),r('JumpspringForce'),tile(x+2,y+32),tile(x+13,y+32),table.concat(a,',')));f:flush()
end
for name,h in pairs(H)do
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual H Samus physical8 '..name)end
  if name=='NMI'or name=='IRQ'then depth=depth+1;return end
  if name=='NMIEnd'or name=='IRQEnd'then depth=depth-1;assert(depth>=0,'Balanced native interrupts');return end
  if depth~=0 or r('GameEngineSubroutine')~=8 or r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
  assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1,'Actual H Samus Easy identity')
  capture(name,h)
 end,emu.callbackType.exec,h.address)
end
local saved=false
emu.addEventCallback(function()
 if not saved and r('WorldNumber')==1 and r('LevelNumber')==2 and r('GameEngineSubroutine')==8 then
  saved=true;local raw={};for i=0,2047 do raw[#raw+1]=string.char(emu.read(i,emu.memType.nesDebug))end;for i=0x6000,0x7fff do raw[#raw+1]=string.char(emu.read(i,emu.memType.nesDebug))end
  local z=assert(io.open(ROSTER_CONFIG.out..'actual-2-3-ram.bin','wb'));z:write(table.concat(raw));z:close()
 end
 frame=frame+1
end,emu.eventType.endFrame)
return function()return{}end
'''
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 source=R/'build/roster-through-2-2/root49-h-samus-ball-wait-gh-2-v0-mmc3';m=json.loads((source/'manifest.json').read_text());assert m['result']['cleared']and m['result']['frames']==32224 and m['controller_only']and not m['memory_or_register_writes']and not m['full_frame_audit']
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('samus_gj_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 hooks={'AcceptedJump':image.hook('CrouchReady',scope='SamusMovement',delta=9),'NativeSpring':image.hook('IndexedSpring',scope='MegaManSpringVelocityModes'),'MorphEnter':image.hook('SamusMorphEnter'),'MorphExit':image.hook('SamusMorphExit'),'NMI':image.hook('NonMaskableInterrupt'),'IRQ':image.hook('IrqScrollSplit'),'NMIEnd':image.hook('NonMaskableInterrupt',delta='last'),'IRQEnd':image.hook('IrqScrollSplit',delta='last')}
 assert hooks['AcceptedJump']['bytes'][:4]==[169,1,133,image.ram['Player_State']]
 policy=J/'fixed-policy.lua';policy.write_text(LUA.replace('HOOKS',im.lua(hooks)),encoding='utf-8')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+150000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),source_manifest_sha256=sha(source/'manifest.json'),source_inputs_sha256=sha(source/'inputs.csv'),image_helper_sha256=sha(helper),hooks=hooks,policy_sha256=sha(policy),workspace_before=used,phase_cap=150000000,reserve=50000000,global_cap=80000000000,scope='Full independent actual H power-on replay of all32223 ordinary inputs, no adaptive tail or state writes. Fresh exact native accepted source jump, intrinsicMorph and indexedSpring hooks; actual live terrain/platform actors. Full hardware/audio event audit; source effect/waveform/complete arsenal not promoted. Earlier GH observer was explicitly tail-only after retained prefix; this independent pass observes the whole route.'),indent=2)+'\n',encoding='utf-8')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag','root49-h-samus-fixed-gj','--policy',str(policy),'--replay',str(source/'inputs.csv'),'--frames','35000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 d=R/'build/roster-through-2-2/root49-h-samus-fixed-gj-2-v0-mmc3';fixed=json.loads((d/'manifest.json').read_text());streams={n:sha(d/n)==sha(source/n)for n in ['inputs.csv','trace.csv','events.csv']}
 assert q.returncode==0 and fixed['verified_through_2_2']and fixed['result']==m['result']and all(streams.values())
 rows=[json.loads(s)for s in(d/'samus-accepted-native.jsonl').read_text().splitlines()]
 counts={k:sum(z['event']==k for z in rows)for k in hooks};assert counts['AcceptedJump']>50 and counts['MorphEnter']>=1 and counts['MorphExit']>=1
 result=dict(status='PASS_ACTUAL_H_SAMUS_FULL_FIXED_HARDWARE_SUPPORT_REVIEW_PENDING',manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json'),result=fixed['result'],streams_literal=streams,native_events=counts,all10240_endpoint=sha(d/'actual-2-3-ram.bin'),hardware_source_support_review_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
