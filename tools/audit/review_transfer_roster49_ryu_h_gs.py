"""Rehash frozen G Ryu and execute actual H with fresh launch/wall receipts."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';A=V/'agent-lsr-current-g-roster-a';J=V/'root49-ryu-g-review-h-transfer-gs'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
LUA=r'''local original=dofile(__ORIGINAL__)
local H=__HOOKS__
local frame,depth=0,0
local f=assert(io.open(ROSTER_CONFIG.out..'ryu-accepted-native.jsonl','w'))
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function capture(name,h)
 local s=emu.getState();local q={event=string.format('%q',name),frame=frame+1,pc=h.address,bank=h.physical_bank,cycle=s['cpu.cycleCount'],a=s['cpu.a'],p=s['cpu.ps'],x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),xf=r('MmXFraction')+256*r('MmXFraction',1),yf=r('MmYFraction')+256*r('MmYFraction',1),world=r('WorldNumber'),level=r('LevelNumber'),areaType=r('AreaType')}
 local fields={yHigh='Player_Y_HighPos',state='Player_State',raw='SavedJoypadBits',previous='RgPreviousButtons',fresh='XgFresh',AB='A_B_Buttons',previousAB='PreviousA_B_Buttons',power='PlayerStatus',spring='JumpspringAnimCtrl',springForce='JumpspringForce',wall='XgWall',wallLock='XgWallLock',wallContact='XgWallContact',jumpUsed='XgJumpUsed',facing='PlayerFacingDir',crouch='RgCrouch',attack='RgAttack',attackKind='RgAttackKind',side='RyWallSide',edge='RyWallEdge',edgePage='RyWallPage',supported='RyWallSupported',resolved='RyWallResolved',blocked='RyWallBlocked',oldHeight='RyWallOldHeight',wasGround='RyWallWasGround',oldX='RyWallOldX',oldPage='RyWallOldPage',oldXFine='RyWallOldXFine',oldXFrac='RyWallOldXFrac',oldY='RyWallOldY',oldYFine='RyWallOldYFine',oldYFrac='RyWallOldYFrac',platform='RyPlatformSlot',platformCancel='RyPlatformCancel',underwater='MmUnderwater',hurt='GuestHurtTicks'}
 for k,n in pairs(fields)do q[k]=r(n)end
 q.vy=r('MmVY')+256*r('MmVY',1)+65536*r('MmVY',2)
 q.vx=r('MmVX')+256*r('MmVX',1)+65536*r('MmVX',2)
 local actors={}
 for i=0,5 do actors[#actors+1]=string.format('[%d,%d,%d,%d,%d,%d,%d,%d,%d,%d]',i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i),r('PlatformCollisionFlag',i),r('Enemy_BoundBoxCtrl',i),r('Enemy_X_MoveForce',i))end
 q.actors='['..table.concat(actors,',')..']'
 local grid={};for i=0,415 do grid[#grid+1]=string.format('%02x',r('Block_Buffer_1',i))end
 q.grid=string.format('%q',table.concat(grid))
 local a={};for k,v in pairs(q)do a[#a+1]=string.format('%q',k)..':'..tostring(v)end
 table.sort(a);f:write('{'..table.concat(a,',')..'}\n');f:flush()
end
for name,h in pairs(H)do
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual H Ryu physical8 '..name)end
  if name=='NMI'or name=='IRQ'then depth=depth+1;return end
  if name=='NMIEnd'or name=='IRQEnd'then depth=depth-1;assert(depth>=0,'Balanced Ryu interrupts');return end
  if depth~=0 or r('GameEngineSubroutine')~=8 or r('OperMode')~=1 or r('OperMode_Task')~=3 then return end
  assert(r('SelectedCharacter')==10 and r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1,'Actual H Ryu Easy identity')
  if name=='FreshInput'and r('XgFresh')&128==0 then return end
  capture(name,h)
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return original
'''

def main():
 assert not J.exists();J.mkdir()
 freeze=A/'ryu-al-proof/freeze.json';assert sha(freeze)=='d1de815ddf9ece22c7ba5086e20d3368de71760b208880ec0b9d4f2d489343cc';f=read(freeze)
 cat=A/'ryu-al-proof/catalog.json';report=A/'ryu-al-proof/report.json'
 assert sha(cat)==f['catalog_sha256']and sha(report)==f['report_sha256']
 catalogue=read(cat);assert len(catalogue)==789
 for n,z in catalogue.items():assert sha(n)==z['sha256']and Path(n).stat().st_size==z['bytes'],n
 source=Path(f['fixed']);sm=read(source/'manifest.json');assert sm['verified_through_2_2']and sm['result']['frames']==23098
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('ryu_gs_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 specs={'FreshInput':('Input','ExpandedMovement'),'GroundLaunch':('Launch','ExpandedMovement'),'AcceptedLaunch':('AfterJumpVelocity','ExpandedMovement'),'WallAttempt':('RyuPlatformJump',None),'WallJump':('RyuWallJump',None),'WallAcceptedVelocity':('Launch','RyuWallJump'),'WallDrop':('Drop','RyuWallJump'),'WallReturnNoJump':('NoJump','RyuWallJump'),'PlatformDrop':('Drop','RyuPlatformJump'),'SpringEntry':('MegaManSpringVelocity',None),'NMI':('NonMaskableInterrupt',None),'IRQ':('IrqScrollSplit',None),'NMIEnd':('NonMaskableInterrupt',None),'IRQEnd':('IrqScrollSplit',None)}
 hooks={n:image.hook(label,scope=scope,**({'delta':'last'}if n.endswith('End')else{}))for n,(label,scope)in specs.items()}
 assert hooks['AcceptedLaunch']['bytes'][:2]==[169,1]
 policy=J/'policy.lua';policy.write_text(LUA.replace('__HOOKS__',im.lua(hooks)).replace('__ORIGINAL__',im.lua((source/'policy.lua').as_posix())),encoding='utf-8')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+150000000<80000000000
 (J/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),G_freeze_sha256=sha(freeze),G_catalogue_files=len(catalogue),G_catalogue_sha256=sha(cat),G_report_sha256=sha(report),checkpoint_H_sha256=sha(cp),source_manifest_sha256=sha(source/'manifest.json'),source_inputs_sha256=sha(source/'inputs.csv'),image_helper_sha256=sha(helper),hooks=hooks,policy_sha256=sha(policy),workspace_before=used,phase_cap=150000000,reserve=50000000,global_cap=80000000000,scope='Independent actual H whole fixed Ryu replay after rehashing frozen789-file G packet. Passive new accepted/input/wall/drop/spring hooks capture exact current source state, all416 terrain bytes and all six live actors. No writes/grants/load or G-to-H retag. Support/physical review remains separate.'),indent=2)+'\n',encoding='utf-8')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','10','--mapper','mmc3','--rom',str(image.path),'--tag','root49-h-ryu-gs','--policy',str(policy),'--replay',str(source/'inputs.csv'),'--frames','28000','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n',encoding='utf-8')
 with(J/'native.log').open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 d=R/'build/roster-through-2-2/root49-h-ryu-gs-10-v0-mmc3';m=read(d/'manifest.json')
 names=['inputs.csv','trace.csv','events.csv','ryu-native.csv','support-grid.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']
 streams={n:sha(d/n)==sha(source/n)for n in names};good=q.returncode==0 and m['verified_through_2_2']and m['result']==sm['result']and all(streams.values())
 z=dict(status='PASS_ACTUAL_H_RYU_FULL_FIXED_NATIVE_SUPPORT_REVIEW_PENDING'if good else'RETAINED_H_RYU_TRANSFER_NEGATIVE',exit=q.returncode,manifest=str((d/'manifest.json').relative_to(R)),manifest_sha256=sha(d/'manifest.json'),result=m.get('result'),streams_literal=streams,endpoint_raw_literal=sha(d/'final-ram.csv')==sha(source/'final-ram.csv'),support_and_physical_review_pending=True,goal_complete=False)
 (J/'result.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
