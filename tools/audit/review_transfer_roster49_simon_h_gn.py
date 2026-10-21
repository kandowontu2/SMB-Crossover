"""Frozen G Simon review and actual H replay with accepted ground/air jump hooks."""
from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'agent-lsr-current-g-roster-a';J=V/'root49-simon-g-review-h-transfer-gn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
LUA=r'''local original=dofile(ORIGINAL)
local H=HOOKS
local frame,depth=0,0
local f=assert(io.open(ROSTER_CONFIG.out..'simon-accepted-native.jsonl','w'))
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function tile(x,y)
 if y<32 or y>=240 then return -1 end
 return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)
end
local function capture(name,h)
 local s=emu.getState();local x=r('Player_X_Position')+256*r('Player_PageLoc');local y=r('Player_Y_Position');local a={}
 for i=0,5 do a[#a+1]=string.format('[%d,%d,%d,%d,%d,%d,%d,%d,%d]',i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i),r('PlatformCollisionFlag',i),r('Enemy_BoundBoxCtrl',i))end
 f:write(string.format('{"event":"%s","frame":%d,"pc":%d,"bank":%d,"cycle":%d,"world":%d,"level":%d,"areaType":%d,"x":%d,"y":%d,"yHigh":%d,"xf":%d,"yf":%d,"state":%d,"raw":%d,"AB":%d,"previousAB":%d,"airAvailable":%d,"power":%d,"spring":%d,"springForce":%d,"footL":%d,"footR":%d,"actors":[%s]}\n',name,frame+1,h.address,h.physical_bank,s['cpu.cycleCount'],r('WorldNumber'),r('LevelNumber'),r('AreaType'),x,y,r('Player_Y_HighPos'),r('MmXFraction')+256*r('MmXFraction',1),r('MmYFraction')+256*r('MmYFraction',1),r('Player_State'),r('SavedJoypadBits'),r('A_B_Buttons'),r('PreviousA_B_Buttons'),r('RgDoubleJump'),r('PlayerStatus'),r('JumpspringAnimCtrl'),r('JumpspringForce'),tile(x+2,y+32),tile(x+13,y+32),table.concat(a,',')));f:flush()
end
for name,h in pairs(H)do
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual H Simon physical8 '..name)end
  if name=='NMI'or name=='IRQ'then depth=depth+1;return end
  if name=='NMIEnd'or name=='IRQEnd'then depth=depth-1;assert(depth>=0,'Balanced native interrupts');return end
  if depth~=0 or r('GameEngineSubroutine')~=8 or r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
  assert(r('SelectedCharacter')==5 and r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1,'Actual H Simon Easy identity')
  if name=='FreshInput'and not(r('A_B_Buttons')&128~=0 and r('PreviousA_B_Buttons')&128==0)then return end
  capture(name,h)
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return original
'''
def main():
 assert not J.exists();J.mkdir()
 freeze=A/'simon-az-proof/freeze.json';assert sha(freeze)=='1cdde2d88edd63643da8f8b3926a826fb0dc5d733239a779721d021fbc6b65b1';f=read(freeze)
 cat=A/'simon-az-proof/catalog.json';report=A/'simon-az-proof/report.json';assert sha(cat)==f['catalog_sha256']and sha(report)==f['report_sha256']
 catalogue=read(cat);assert len(catalogue)==777
 for n,z in catalogue.items():assert sha(n)==z['sha256']and Path(n).stat().st_size==z['bytes'],n
 source=Path(f['fixed']);sm=read(source/'manifest.json');assert sm['verified_through_2_2']and sm['result']['frames']==28793
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('simon_gn_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 hooks={'FreshInput':image.hook('Input',scope='RosterMovement'),'AcceptedLaunch':image.hook('Launch',scope='RosterMovement'),'SpringEntry':image.hook('MegaManSpringVelocity'),'NMI':image.hook('NonMaskableInterrupt'),'IRQ':image.hook('IrqScrollSplit'),'NMIEnd':image.hook('NonMaskableInterrupt',delta='last'),'IRQEnd':image.hook('IrqScrollSplit',delta='last')}
 assert hooks['AcceptedLaunch']['bytes'][:3]==[173,image.ram['SelectedCharacter']&255,image.ram['SelectedCharacter']>>8]
 policy=J/'policy.lua';policy.write_text(LUA.replace('HOOKS',im.lua(hooks)).replace('ORIGINAL',im.lua((source/'policy.lua').as_posix())),encoding='utf-8')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+150000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),G_freeze_sha256=sha(freeze),G_catalogue_files=777,G_catalogue_sha256=sha(cat),G_report_sha256=sha(report),checkpoint_H_sha256=sha(cp),source_manifest_sha256=sha(source/'manifest.json'),source_inputs_sha256=sha(source/'inputs.csv'),image_helper_sha256=sha(helper),hooks=hooks,policy_sha256=sha(policy),workspace_before=used,phase_cap=150000000,reserve=50000000,global_cap=80000000000,scope='Separate actual H whole fixed replay after rehashing frozen777-file G packet. Original G passive observer/endpoint retained; new actual source consumed-launch/input/spring hooks add current terrain/platform/air-availability receipts. No state/controller writes or old-G retag. Full support/physical review remains separate.'),indent=2)+'\n',encoding='utf-8')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','5','--mapper','mmc3','--rom',str(image.path),'--tag','root49-h-simon-gn','--policy',str(policy),'--replay',str(source/'inputs.csv'),'--frames','33000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
 with(J/'native.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 d=R/'build/roster-through-2-2/root49-h-simon-gn-5-v0-mmc3';m=read(d/'manifest.json')
 names=['inputs.csv','trace.csv','events.csv','simon-native.csv','support-grid.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']
 streams={n:sha(d/n)==sha(source/n)for n in names};good=q.returncode==0 and m['verified_through_2_2']and m['result']==sm['result']and all(streams.values())
 result=dict(status='PASS_ACTUAL_H_SIMON_FULL_FIXED_NATIVE_SUPPORT_REVIEW_PENDING'if good else'RETAINED_H_SIMON_TRANSFER_NEGATIVE',exit=q.returncode,manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json'),result=m.get('result'),streams_literal=streams,endpoint_raw_literal=sha(d/'final-ram.csv')==sha(source/'final-ram.csv'),support_and_physical_review_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
