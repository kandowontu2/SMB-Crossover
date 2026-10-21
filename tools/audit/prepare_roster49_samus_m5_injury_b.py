"""Observe the actual first MMC5 negative before any controller/source change."""
from pathlib import Path
import hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-current-d-transfers-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=D/'injury-binding-b.json';assert not out.exists()
    checkpoint=R/'build/checkpoints/roster-audit-v49-sophia-head-axis-d/manifest.json'
    assert sha(checkpoint)=='1fcbdec758e0a4c09e769f66b110d4d8d60b05cb11dffa55061bfc32bda55c88'
    c=json.loads(checkpoint.read_text())
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    dep=V/'agent49k-samus-water-up-direction-component-a/image.py'
    sp=importlib.util.spec_from_file_location('samus_d_m5_image',dep)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    im=m.Image(V/'root49-sophia-head-axis-d/source/build/smb-crossover-mmc5.nes')
    hooks={n:im.hook(n)for n in ['InjurePlayer','ForceInjury','NonMaskableInterrupt','IrqScrollSplit']}
    for n in ['NonMaskableInterrupt','IrqScrollSplit']:hooks[n+'End']=im.hook(n,delta='last')
    policy=r'''dofile(IDENTITY)
local H=HOOKS
local frame,depth,serial=0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local f=assert(io.open(ROSTER_CONFIG.out..'actual-injury-b.csv','w'))
f:write('frame,event,slot,owner,flag,id,estate,ex,ey,playerX,playerY,xf,yf,state,vx,vy,power,ball,flip,sourceJumped,playerBox,enemyBox,hp,AXYP,SP\n')
local function capture(event,h)
 local s=emu.getState();local pb={};for j=0,3 do pb[#pb+1]=r('BoundingBox_UL_Corner',j)end
 for i=0,5 do
  local eb={};for j=0,3 do eb[#eb+1]=r('EnemyBoundingBoxCoord',i*4+j)end
  local a={frame+1,event,i,r('ObjectOffset'),r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('MmXFraction')+256*r('MmXFraction',1),r('MmYFraction')+256*r('MmYFraction',1),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed'),r('PlayerStatus'),r('SmBall'),r('SmFlip'),r('SmSourceJumped'),table.concat(pb,':'),table.concat(eb,':'),r('MmEnemyHealthLo',i)+256*r('MmEnemyHealthHi',i),table.concat({s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']},':'),s['cpu.sp']}
  f:write(table.concat(a,',')..'\n')
 end
 f:flush()
 if h then
  serial=serial+1;assert(serial<12,'Bounded actual injury snapshots')
  local raw={};for a=0,2047 do raw[#raw+1]=string.char(emu.read(a,emu.memType.nesDebug))end
  for a=0x6000,0x7fff do raw[#raw+1]=string.char(emu.read(a,emu.memType.nesDebug))end
  local z=assert(io.open(ROSTER_CONFIG.out..string.format('injury-%02d-%s.ram',serial,event),'wb'));z:write(table.concat(raw));z:close()
 end
end
local function hook(name,fn)
 local h=H[name]
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual D MMC5 injury eight bytes '..name)end
  fn(h)
 end,emu.callbackType.exec,h.address)
end
for _,n in ipairs({'NonMaskableInterrupt','IrqScrollSplit'})do hook(n,function()depth=depth+1 end)end
for _,n in ipairs({'NonMaskableInterruptEnd','IrqScrollSplitEnd'})do hook(n,function()depth=depth-1;assert(depth>=0,'Balanced observed native interrupts')end)end
for _,n in ipairs({'InjurePlayer','ForceInjury'})do hook(n,function(h)if depth==0 and frame>=2100 and frame<=2500 then capture(n,h)end end)end
emu.addEventCallback(function()if frame>=2100 and frame<=2500 then capture('EndFrame')end;frame=frame+1 end,emu.eventType.endFrame)
return function()return{}end
'''
    policy=policy.replace('IDENTITY',json.dumps((V/'root49-current-c-transfers-a/identity.lua').as_posix())).replace('HOOKS',m.lua(hooks))
    p=D/'injury-policy-b.lua';p.write_text(policy)
    record=dict(status='PREPARED_READ_ONLY_REAL_MMC5_INJURY_OWNER',script_sha256=sha(__file__),ROM=im.metadata(),hooks=hooks,
                checkpoint_sha256=sha(checkpoint),policy_sha256=sha(p),emulated_writes=False,state_loads=False,
                input_sha256=sha(R/'build/roster-through-2-2/lsr-samus-c-u-2-v0-mmc3/inputs.csv'),
                phase_cap_bytes=1000000000,final_reserve_bytes=100000000,global_cap_bytes=70000000000)
    out.write_text(json.dumps(record,indent=2)+'\n');print(record['status'])


if __name__=='__main__':main()
