"""Replay the exact original ordinary tape against private G6; observe only."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-g6-coral-replay-by'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local C=CORAL_DIAGNOSTIC
dofile(IDENTITY)
local frame=0
local f=assert(io.open(ROSTER_CONFIG.out..'coral-writers.csv','w'))
f:write('frame,event,pc,physicalBank,A,X,Y,P,SP,playerX,playerY,writeAddress,writeValue,SmTempY,SmCeilingHit,SmSourceJumped,SmTempX,SmTempPage,R0,R1,R2,R3,R4,R5,R6,R7,code8\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function phys(pc)local p=emu.convertAddress(pc);return p and p.memType==emu.memType.nesPrgRom and p.address//8192 or-1 end
local function emit(event,addr,value)
 if r('WorldNumber')~=1 or r('LevelNumber')~=1 or frame<28000 then return end
 local s=emu.getState();local pc=s['cpu.pc'];local bytes={}
 for i=0,7 do bytes[#bytes+1]=string.format('%02x',emu.read((pc+i)%65536,emu.memType.nesDebug))end
 local a={frame+1,event,pc,phys(pc),s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps'],s['cpu.sp'],r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),addr or-1,value or-1,r('SmTempY'),r('SmCeilingHit'),r('SmSourceJumped'),r('SmTempX'),r('SmTempPage')}
 for i=0,7 do a[#a+1]=emu.read(i,emu.memType.nesDebug)end
 a[#a+1]=table.concat(bytes);f:write(table.concat(a,',')..'\n');f:flush()
end
for _,n in ipairs({'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos'})do
 emu.addMemoryCallback(function(a,v)emit('write-'..n,a,v)end,emu.callbackType.write,L[n])
end
for n,h in pairs(C.hooks)do
 emu.addMemoryCallback(function()
  if phys(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual coral hook8 '..n)end
  emit(n)
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return function()return{}end
'''
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    build=V/'root49-samus-head-axis-g6/build-review.json';assert sha(build)=='be822330c0121132506583325f3489f5380870a59a58a79b65584756abb36ae6'
    helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('coral_g6_metadata',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(V/'root49-samus-head-axis-g6/source/build/smb-crossover-mmc3.nes')
    hooks={n:image.hook(n)for n in ['SamusMovement','SamusHeadProbe','SamusAfterBGCollision','SamusStopAtWallBanked','PlayerBGCollision']}
    hooks.update(HeadProbeDone=image.hook('Done',scope='SamusHeadProbe'),WallLeftClamp=image.hook('LeftClamp',scope='SamusStopAtWallBanked'),WallRightClamp=image.hook('RightClamp',scope='SamusStopAtWallBanked'))
    parent=R/'build/roster-through-2-2/root49-f-samus-route-v-2-v0-mmc3';source=json.loads((parent/'manifest.json').read_text());assert source['result']['frames']==30466
    ident=V/'root49-current-c-transfers-a/identity.lua';policy=H/'policy.lua';policy.write_text('CORAL_DIAGNOSTIC='+im.lua(dict(hooks=hooks))+'\n'+BODY.replace('dofile(IDENTITY)','dofile('+im.lua(ident.as_posix())+')'))
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size+100000000<80000000000
    pre=dict(script_sha256=sha(__file__),checkpoint_F_sha256=sha(cp),candidate_build_sha256=sha(build),dependencies={str(p.relative_to(R)):sha(p)for p in [helper,ident,parent/'inputs.csv',parent/'manifest.json',build]},hooks=hooks,policy_sha256=sha(policy),workspace_before=size,global_cap=80000000000,phase_cap=120000000,reserve=20000000,
      authority='root49-global-allocation-bm.json',scope='Pure passive coordinate-write/hook observation, exact original F V tape replayed on private G6 from power-on. No emulated writes/state loads. Timing changes may invalidate controller decisions before coral; no full clear or fix acceptance inferred just from a completed launch.')
    (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag','root49-g6-samus-coral-by','--policy',str(policy),'--replay',str(parent/'inputs.csv'),'--frames','29945','--timeout','900','--workspace-cap-gb','80']
    (H/'command.json').write_text(json.dumps(args,indent=2)+'\n')
    with (H/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
    p=R/'build/roster-through-2-2/root49-g6-samus-coral-by-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text())
    report=dict(exit=q.returncode,result=m.get('result'),manifest_sha256=sha(p/'manifest.json'),native_log_sha256=sha(H/'native.log'),preparation_sha256=sha(H/'preparation.json'),analysis_pending=True,goal_complete=False)
    (H/'native-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
