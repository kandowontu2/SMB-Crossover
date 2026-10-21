"""Authored side-wall jump regression; retain the unmodified F failures."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-coral-regression-br'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BODY=r'''local frame,index,age=0,0,0
local current=nil
local cases={}
for _,water in ipairs({true,false})do for mode=0,1 do for power=0,2 do for _,dir in ipairs({1,2})do for _,tile in ipairs({105,84})do
 cases[#cases+1]={water=water,mode=mode,power=power,dir=dir,tile=tile}
end end end end end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function px()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function cell(x,y)return x//256%2*208+(y-32)//16*16+x%256//16 end
local f=assert(io.open(OUTPUT..'coral-side-jump.csv','w'));f:write('case,frame,age,water,mode,power,dir,tile,x,y,sourceJumped,ceiling,headIndex\n')
local function actual(h,fn)
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Exact coral fixture hook8')end
  fn()
 end,emu.callbackType.exec,h.address)
end
actual(CORAL_HOOKS.BG,function()if current then w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)end end)
actual(CORAL_HOOKS.HeadDone,function()
 if not current then return end
 current.heads=current.heads+1
 local x,y=px(),r('Player_Y_Position')
 f:write(table.concat({index,frame,age,current.water and 1 or 0,current.mode,current.power,current.dir,current.tile,x,y,r('SmSourceJumped'),r('SmCeilingHit'),emu.getState()['cpu.y']},',')..'\n');f:flush()
 assert(y<=176,'Coral side jump must not be separated downward into floor: actualY='..y..' case='..index)
 assert(math.abs(x-current.lastX)<=3,'Coral side jump cannot snap across16px cells: '..current.lastX..' to '..x)
 current.lastX=x
end)
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or(current and current.dir==1),left=current and current.dir==2,start=frame==200,a=current~=nil},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;if frame<550 then return end
 if current then age=age+1 end
 if not current or age>=24 then
  if current then assert(current.heads>0,'Every coral arena attained the actual head routine')end
  index=index+1;current=cases[index];age=0
  if not current then f:close();print('PASS48 real freshA side-jump arenas: Easy/Hard, water/dry,3tiers, left/right and coral/solid; no downward or cell-sized displacement');emu.stop(0);return end
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for col=0,15 do w('Block_Buffer_1',current.tile,p*208+176+col)end end
  for yy=160,192,16 do for xx=1248,1264,16 do w('Block_Buffer_1',current.tile,cell(xx,yy))end end
  for i=0,5 do w('Enemy_Flag',0,i);w('Enemy_State',0,i);w('AvFrozen',0,i);w('AvFrozenHi',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i);w('SmShotType',0,i);w('SmBombAge',0,i)end
  for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
  local x=current.dir==1 and 1233 or 1279
  w('Player_X_Position',x);w('Player_PageLoc',x//256);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('MmXFraction',current.dir==1 and192 or64,1)
  w('SelectedCharacter',2);w('CrossoverBehaviorVersion',current.mode);w('PlayerStatus',current.power);w('PlayerSize',0)
  w('AreaType',current.water and0 or2);w('SwimmingFlag',current.water and1 or0);w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0)
  w('InvOwnedLo',1,2);w('InvSelected',0,2);w('PlayerFacingDir',current.dir)
  for _,n in ipairs({'SmBall','SmCrouch','CrouchingFlag','SmPreviousDirections','SmFlip','SmCeilingHit','SmSourceJumped','PreviousA_B_Buttons','A_B_Buttons','TimerControl','GuestPowerupActive','GuestHurtTicks','InjuryTimer','StarInvincibleTimer','MmDeathFlag','DisableCollisionDet'})do w(n,0)end
  w('GameEngineSubroutine',8);w('ScreenLeft_X_Pos',1122);w('ScreenLeft_PageLoc',4);w('ScreenRight_X_Pos',1377);w('ScreenRight_PageLoc',5)
  w('ScrollLock',1);w('AreaParserTaskNum',0);w('ScrollThirtyTwo',0)
  current.heads=0;current.lastX=x
 end
end,emu.eventType.endFrame)
'''
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text());assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('coral_regression_F',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
    fixture=H/'coral-side-jump.lua';fixture.write_text(BODY.replace('and192','and 192').replace('or64','or 64').replace('and0','and 0').replace('or2','or 2').replace('and1','and 1').replace('or0','or 0'))
    (H/'preparation.json').write_text(json.dumps(dict(script_sha256=sha(__file__),fixture_sha256=sha(fixture),checkpoint_sha256=sha(cp),scope='Explicit authored geometry/state; actual freshA controller invokes native movement/head/side resolution. Not an ordinary route or original HitTester pixel proof.',phase_cap=120000000,reserve=20000000,global_cap=80000000000),indent=2)+'\n')
    results=[]
    for mapper in ['mmc3','mmc5']:
        image=im.Image(cp.parent/f'smb-crossover-{mapper}.nes');out=H/mapper;out.mkdir()
        hooks=dict(BG=image.hook('PlayerBGCollision'),HeadDone=image.hook('Done',scope='SamusHeadProbe'))
        wrapper=H/f'{mapper}.lua';wrapper.write_text('CORAL_HOOKS='+im.lua(hooks)+'\nTEST_DIR='+im.lua((R/'tests').as_posix()+'/')+'\ndofile(TEST_DIR.."menu-bootstrap.lua")\ndofile('+im.lua(fixture.as_posix())+')\n')
        q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(wrapper),str(image.path),'--timeout','60'],cwd=R,capture_output=True,text=True)
        log=H/f'{mapper}-host.log';log.write_text(q.stdout+q.stderr)
        results.append(dict(mapper=mapper,exit=q.returncode,hooks=hooks,wrapper_sha256=sha(wrapper),host_log_sha256=sha(log),files={str(p.relative_to(H)):sha(p)for p in out.iterdir()if p.is_file()}))
        print(mapper,'exit',q.returncode,flush=True)
    report=dict(status='RETAINED_UNMODIFIED_F_CORAL_SIDE_JUMP_BASELINE_FAILURES',script_sha256=sha(__file__),preparation_sha256=sha(H/'preparation.json'),results=results,all48_cases_executed=False,fix_implemented=False,goal_complete=False)
    dst=H/'baseline-results.json';dst.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(dst),flush=True)
if __name__=='__main__':main()
