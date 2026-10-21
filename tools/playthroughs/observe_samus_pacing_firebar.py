"""Rebind a read-only contact observer to the current candidate's actual hooks."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/root49-samus-reference-pacing-a'
S = R / 'build/verification/root49-sophia-land-fix-a/source-e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(R / 'build/verification/agent49k-samus-water-up-direction-component-a'))
    from image import Image
    image = Image(S / 'build/smb-crossover-mmc3.nes')
    hooks = {name: image.hook(label) for name, label in [('FirebarHit', 'ChgSDir'), ('Injury', 'InjurePlayer')]}
    target = D / 'firebar-observer-c.lua'
    assert not target.exists()
    lua_hooks = '{' + ','.join(name+'={pc='+str(h['address'])+',bank='+str(h['physical_bank'])+',bytes={'+','.join(map(str, h['bytes']))+'}}' for name, h in hooks.items()) + '}'
    text = r'''dofile(IDENTITY)
local hooks=HOOKS
local frame=0
local f=assert(io.open(ROSTER_CONFIG.out..'samus-firebar-contact.csv','w'))
local parts=assert(io.open(ROSTER_CONFIG.out..'samus-firebar-parts.csv','w'))
f:write('frame,event,pc,bank,cpuX,world,level,x,y,yHigh,xf,yf,state,engine,power,pose,crouch,ball,flip,sourceJumped,relativeX,bodyL,bodyT,bodyR,bodyB,R0,R1,R2,R3,R4,R5,R6,R7,objectOffset\n')
parts:write('frame,event,slot,enemyFlag,enemyID,enemyX,enemyY,spinHigh,spinLow,count,part,screenX,screenY\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function capture(name,h)
 local s=emu.getState()
 local z={frame+1,name,h and h.pc or -1,h and h.bank or -1,s['cpu.x']or-1,r('WorldNumber'),r('LevelNumber'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('MmXFraction')+256*r('MmXFraction',1),r('MmYFraction')+256*r('MmYFraction',1),r('Player_State'),r('GameEngineSubroutine'),r('PlayerStatus'),r('SmPose'),r('SmCrouch'),r('SmBall'),r('SmFlip'),r('SmSourceJumped'),r('Player_Rel_XPos')}
 for k=0,3 do z[#z+1]=r('BoundingBox_UL_Corner',k)end
 for k=0,7 do z[#z+1]=r('R'..k)end;z[#z+1]=r('ObjectOffset')
 f:write(table.concat(z,',')..'\n');f:flush()
 for slot=0,5 do
  local id=r('Enemy_ID',slot)
  if r('Enemy_Flag',slot)~=0 and id>=0x1b and id<=0x23 then
   local count=r('FirebarPartCount',slot)
   for k=0,count-1 do
    local row={frame+1,name,slot,r('Enemy_Flag',slot),id,r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),r('Enemy_Y_Position',slot),r('FirebarSpinState_High',slot),r('FirebarSpinState_Low',slot),count,k,r('FirebarPartX',slot*12+k),r('FirebarPartY',slot*12+k)}
    parts:write(table.concat(row,',')..'\n')
   end
  end
 end
 parts:flush()
end
for name,h in pairs(hooks)do
 emu.addMemoryCallback(function()
  if frame<14700 or frame>14745 then return end
  local p=emu.convertAddress(h.pc)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Actual current Samus contact bank+eight')end
  assert(r('SelectedCharacter')==2 and r('CrossoverBehaviorVersion')==0,'Actual Easy Samus contact')
  capture(name,h)
 end,emu.callbackType.exec,h.pc)
end
emu.addEventCallback(function()
 if frame>=14700 and frame<=14745 then capture('EndFrame',nil)end
 frame=frame+1
end,emu.eventType.endFrame)
return function()return{}end
'''
    text = text.replace('dofile(IDENTITY)', 'dofile('+json.dumps((D / 'identity.lua').as_posix())+')')
    text = text.replace('local hooks=HOOKS', 'local hooks='+lua_hooks)
    target.write_text(text)
    (D / 'firebar-binding-c.json').write_text(json.dumps(dict(image=image.metadata(), hooks=hooks,
        observer_sha256=sha(target), controller_only=True, emulated_writes=False,
        fixed_input_source='build/roster-through-2-2/root49-samus-pacing-b-2-v0-mmc3/inputs.csv',
        purpose='Classify the actual first castle contact; source-disjointness is unproven.'), indent=2)+'\n')
    print('Prepared current-hook contact observer.')


if __name__ == '__main__':
    main()
