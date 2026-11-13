"""Run retained Metal controllers with stdout-only receipts on a specified ROM."""
import argparse
import json
import re
from pathlib import Path
from hashlib import sha256
import check_prince_brick_support_1111 as Native
from run_stdout_mesen_1110 import run, R


def controller(raw, mode, head_trace=False):
    relative = ('metal-storm-natural-armor-1101-v26/native' if mode == 'armor'
                else 'metal-reservation-1102-v42/route')
    original = R/'build'/relative/'controller.lua'
    text = original.read_text(encoding='utf-8')
    if mode == 'upgrades':
        text = text.replace('local route,ticks,initialLives=0,0,nil',
            'local route,ticks,initialLives=0,0,nil\nlocal upgradePhase=0\nlocal upgradeBirths={}\nlocal upgradedShot=false\nlocal pickupTrace={}')
        start = text.index(" if phase=='play' then\n")
        end = text.index(' emu.setInput(pad,0)',start)
        ordinary = text[start+len(" if phase=='play' then\n"):end]
        assert ordinary.endswith(' end\n')
        ordinary = ordinary[:-len(' end\n')]
        replacement = ''' if phase=='play' then
  local x=worldx()
  local function source(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
  if upgradePhase==0 and source(0x5d0)==128 then
   upgradePhase=1;route=2;ticks=0
  end
  if upgradePhase==0 then
   pad.b=true
   if route==0 then pad.right=true;if x>=105 then route=1;ticks=0 end
   elseif route==1 then pad.right=true;pad.a=ticks<35;if ticks>=50 then route=2 end
   elseif route==2 then if x<336 then pad.right=true else route=3;ticks=0 end
   elseif route==3 then pad.a=ticks<35;if ticks>=65 then route=4 end
   elseif route==4 then pad.right=true end
   ticks=ticks+1
  elseif upgradePhase==1 then
ORDINARY
   if pipe>4 and x>=1210 and r('Player_State')==0 then upgradePhase=2;ticks=0 end
  elseif upgradePhase==2 then
   pad.b=true
   if x<1250 then pad.right=true
   elseif r('Player_State')==0 then upgradePhase=3;ticks=0 end
  elseif upgradePhase==3 then
   pad.b=true;pad.a=ticks<35;ticks=ticks+1
   if ticks>=70 then upgradePhase=4;ticks=0 end
  elseif upgradePhase==4 then
   pad.b=true;pad.a=(ticks%100)<40;ticks=ticks+1
   if source(0x718)==128 then upgradePhase=5;ticks=0 end
  elseif upgradePhase==5 then
   pad.b=true;ticks=ticks+1
  end
 end
'''.replace('ORDINARY',ordinary)
        text = text[:start]+replacement+text[end:]
        # Inspect actual native item birth/maturity, and source upgraded shots.
        marker=" elseif phase=='play' then\n"
        assert text.count(marker)==1
        text=text.replace(marker,marker+'''  for slot=0,5 do
   if r('Enemy_Flag',slot)>0 and r('Enemy_ID',slot)==46 then
    local kind=r('PowerUpType',slot)
    upgradeBirths[kind+1]=upgradeBirths[kind+1] or {kind=kind,x=r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),frame=frame,mature=false}
    if r('Enemy_State',slot)>=128 then upgradeBirths[kind+1].mature=true end
    if frame%20==0 and #pickupTrace<60 then pickupTrace[#pickupTrace+1]={frame=frame,phase=upgradePhase,playerX=worldx(),playerY=r('Player_Y_Position'),itemX=r('Enemy_X_Position',slot)+256*r('Enemy_PageLoc',slot),itemY=r('Enemy_Y_Position',slot),state=r('Enemy_State',slot),kind=kind} end
   end
  end
  for slot=2,3 do
   if emu.read(2*8192+0x528+slot,emu.memType.nesWorkRam)==129 and emu.read(2*8192+0x510+slot,emu.memType.nesWorkRam)~=0 then upgradedShot=true end
  end
''')
        old="if killed and r('WorldNumber')==0 and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 and r('OperMode_Task')==3 then finish('entered-1-2')"
        assert text.count(old)==1
        text=text.replace(old,"if upgradePhase==5 and ticks>=40 then finish('earned-flower-shot')")
        text=text.replace("elseif age>=6000 then finish('route-bound')",
            "elseif (upgradePhase==0 and age>=1100) or age>=6000 then finish('route-bound')")
    if mode == 'armor':
        assert text.count(" if phase=='play' then\n") == 1
        text = text.replace(" if phase=='play' then\n", " if phase=='play' then\n  pad.b=true\n")
        text = text.replace('if x<240 then', 'if x<336 then')
    labels = set(re.findall(r"r\('([^']+)'", text)) | set(re.findall(r'L\.(\w+)', text))
    labels.update(('PowerUpType','Enemy_State','Enemy_Flag','Enemy_ID','PlayerStatus'))
    bundle = Native.C.Start.W.bundle(raw)
    prefix = 'local L={' + ','.join(f'{name}={Native.N.address(bundle,name)}' for name in sorted(labels)) + '}\n'
    pickup_pc = Native.N.address(bundle,'HandlePowerUpCollision')
    pickup_offset = Native.N.location(bundle,'HandlePowerUpCollision')-16
    prefix += '''local collections,pickupHooks,pendingPickup={},{},nil
local function pickupRead(a)return emu.read(a,emu.memType.nesDebug)end
local function pickupSource(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
emu.addMemoryCallback(function()
 local map=emu.convertAddress(PICKUP_PC)
 if pickupRead(0x6002)~=35 or not map or map.memType~=emu.memType.nesPrgRom or map.address~=PICKUP_OFFSET then return end
 local cpu=emu.getState()
 local slot=cpu['cpu.x']
 if slot>5 or pickupRead(L.Enemy_ID+slot)~=46 then return end
 local sp=cpu['cpu.sp']
 local ret=pickupRead(0x100+((sp+1)&255))+256*pickupRead(0x100+((sp+2)&255))+1
 pendingPickup={slot=slot,kind=pickupRead(L.PowerUpType+slot),mature=pickupRead(L.Enemy_State+slot)>=128,
  beforeStatus=pickupRead(L.PlayerStatus),beforeArmor=pickupSource(0x5d0),beforeWeapon=pickupSource(0x718)}
 if not pickupHooks[ret] then
  pickupHooks[ret]=true
  emu.addMemoryCallback(function()
   if pendingPickup then
    local row=pendingPickup;pendingPickup=nil
    row.afterFlag=pickupRead(L.Enemy_Flag+row.slot)
    row.afterStatus=pickupRead(L.PlayerStatus);row.afterArmor=pickupSource(0x5d0);row.afterWeapon=pickupSource(0x718)
    if row.afterFlag==0 and #collections<8 then collections[#collections+1]=row end
   end
  end,emu.callbackType.exec,ret)
 end
end,emu.callbackType.exec,PICKUP_PC)
'''.replace('PICKUP_PC',str(pickup_pc)).replace('PICKUP_OFFSET',str(pickup_offset))
    prefix += '''local headHits,headPending,headReturnHooks={},nil,{}
local headCalls,headReturned,bumps=0,0,0
local sourceContacts={}
local function debugRead(a)return emu.read(a,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if debugRead(0x6002)~=35 then return end
 local x=debugRead(0x75)+256*debugRead(0x5c)
 if x<320 or x>380 then return end
 headCalls=headCalls+1
 local cpu=emu.getState()
 local sp=cpu['cpu.sp']
 local ret=debugRead(0x100+((sp+1)&255))+256*debugRead(0x100+((sp+2)&255))+1
 headPending={x=x,y=debugRead(0xbd),dy=debugRead(0x8e)}
 if not headReturnHooks[ret] then
  headReturnHooks[ret]=true
  emu.addMemoryCallback(function()
   if headPending then
    headReturned=headReturned+1
    headPending.tile=emu.getState()['cpu.a']
    headPending.lowY=debugRead(7)
    if headPending.tile~=0 and #headHits<20 then headHits[#headHits+1]=headPending end
    headPending=nil
   end
  end,emu.callbackType.exec,ret)
 end
end,emu.callbackType.exec,0xf113)
emu.addMemoryCallback(function()
 if debugRead(0x6002)==35 then bumps=bumps+1 end
end,emu.callbackType.exec,0x9ef5)
emu.addMemoryCallback(function(_,value)
 local map=emu.convertAddress(0xc810)
 if value~=0xe0 or debugRead(0x6002)~=35 or not map or map.memType~=emu.memType.nesWorkRam or map.address~=2*8192+0x810 then return end
 local function source(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
 local x=debugRead(0x75)+256*debugRead(0x5c)
 if x>=330 and x<=350 and source(0x5b)<176 and #sourceContacts<30 then
  sourceContacts[#sourceContacts+1]={x=x,y=debugRead(0xbd),dy=debugRead(0x8e),
   queryX=source(0x59)+256*source(0x5a),queryY=source(0x5b),tile=source(0x811),
   velocity=source(0x570),sourceY=source(0x4b0),pc=emu.getState()['cpu.pc']}
 end
end,emu.callbackType.write,0xc810)
'''
    text, count = re.subn(r'local function shot\(n\).*?end\n', 'local function shot(n) end\n', text)
    assert count == 1
    old = text[text.index('local function finish(reason)'):text.index('emu.addEventCallback(function()',text.index('local function finish(reason)'))]
    condition = ('got and spawned and matured and r(\'NumberofLives\')==initialLives'
                 if mode == 'armor' else "killed and r('WorldNumber')==0 and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 and r('NumberofLives')==initialLives")
    if mode == 'upgrades':
        condition = "upgradePhase==5 and upgradedShot and upgradeBirths[1] and upgradeBirths[1].mature and upgradeBirths[2] and upgradeBirths[2].mature and #collections==2 and collections[1].kind==0 and collections[1].mature and collections[1].afterArmor==128 and collections[1].afterStatus==1 and collections[2].kind==1 and collections[2].mature and collections[2].afterWeapon==128 and collections[2].afterStatus==2 and r('NumberofLives')==initialLives"
    encoder = (R/'tools/playthroughs/prince_original_first_pipe_stdout_1110.lua').read_text()
    encoder = encoder[encoder.index('local function encode(value)'):encoder.index('local function finish(passed,reason)')]
    new = encoder + '''local function finish(reason)
 local passed=CONDITION
 local receipt={passed=passed,reason=reason,controller_only=true,frames=frame,
  ROM_SHA256=os.getenv('SMB_STDOUT_ROM_SHA'),physical_frames=frame,
  world_x=worldx(),world=r('WorldNumber'),level=r('LevelNumber'),engine=r('GameEngineSubroutine'),
  spawned=spawned,matured=matured,collected=got,lives=r('NumberofLives'),initial_lives=initialLives,
  status=r('PlayerStatus'),armor=emu.read(2*8192+0x5d0,emu.memType.nesWorkRam),
  weapon=emu.read(2*8192+0x718,emu.memType.nesWorkRam),output_files=0,
  headHits=headHits,headCalls=headCalls,headReturned=headReturned,bumps=bumps,sourceContacts=sourceContacts,collections=collections}
 print('SMB_NATIVE_RECEIPT '..encode(receipt))
 done=true;emu.stop(passed and 0 or 1)
end
'''.replace('CONDITION', condition)
    for name in ('WorldNumber','LevelNumber','GameEngineSubroutine','PlayerStatus'):
        if name not in labels:
            prefix += f'L.{name}={Native.N.address(bundle,name)}\n'
    text = text.replace(old,new)
    if mode == 'upgrades':
        text=text.replace(" print('SMB_NATIVE_RECEIPT '..encode(receipt))",
            " receipt.upgradePhase=upgradePhase;receipt.upgradeBirths=upgradeBirths;receipt.upgradedShot=upgradedShot;receipt.pickupTrace=pickupTrace\n print('SMB_NATIVE_RECEIPT '..encode(receipt))")
    if head_trace:
        entries=[]
        for name in ('NrPickupCollision','PlayerEnemyCollision','PlayerCollisionCore'):
            entries.append('{"'+name+'",'+str(Native.N.address(bundle,name))+','+str(Native.N.location(bundle,name)-16)+'}')
        prefix += '''local pickupCalls={}
local function pickupCall(label)
 local ix=5
 local px=debugRead(0x75)+256*debugRead(0x5c)
 local ex=debugRead(L.Enemy_X_Position+ix)+256*debugRead(L.Enemy_PageLoc+ix)
 if debugRead(0x6002)~=35 or debugRead(L.Enemy_ID+ix)~=46 or debugRead(L.Enemy_State+ix)<128 or math.abs(px-ex)>12 or debugRead(L.Enemy_Y_Position+ix)<180 or #pickupCalls>=24 then return end
 local cpu=emu.getState()
 local boxes={}
 for i=0,3 do boxes[i+1]=debugRead(0x658+i);boxes[i+5]=debugRead(0x658+24+i) end
 pickupCalls[#pickupCalls+1]={label=label,x=px,itemX=ex,y=debugRead(0xbd),a=cpu['cpu.a'],ix=cpu['cpu.x'],iy=cpu['cpu.y'],p=cpu['cpu.ps'],offscreen=debugRead(0x5a8+ix),playerBox=debugRead(0x645),boxes=boxes}
end
for _,entry in ipairs({ENTRIES}) do
 local name,pc,offset=entry[1],entry[2],entry[3]
 emu.addMemoryCallback(function()
  local map=emu.convertAddress(pc)
  if map and map.memType==emu.memType.nesPrgRom and map.address==offset then pickupCall(name) end
 end,emu.callbackType.exec,pc)
end
'''.replace('ENTRIES',','.join(entries))
        prefix += '''local headBridge={}
local function bridgeEvent(label,value)
 local x=debugRead(0x75)+256*debugRead(0x5c)
 if debugRead(0x6002)~=35 or x<330 or x>350 or debugRead(0xbd)>170 or #headBridge>=100 then return end
 local cpu=emu.getState()
 local packet={}
 for i=0,6 do packet[i+1]=emu.read(2*8192+0x880+i,emu.memType.nesWorkRam) end
 if label=='packet-write' and value~=0xa7 and packet[1]~=0xa7 then return end
 headBridge[#headBridge+1]={label=label,value=value,pc=cpu['cpu.pc'],a=cpu['cpu.a'],ix=cpu['cpu.x'],iy=cpu['cpu.y'],p=cpu['cpu.ps'],x=x,y=debugRead(0xbd),epoch=debugRead(L.FrameCounter),packet=packet}
end
for _,entry in ipairs({{0xad54,3},{0xbfc0,3},{0xdcd9,2},{0xd8af,2},{0xb5b2,3}}) do
 local pc,bank=entry[1],entry[2]
 emu.addMemoryCallback(function()
  local map=emu.convertAddress(pc)
  if map and map.memType==emu.memType.nesWorkRam and map.address==bank*8192+(pc&8191) then bridgeEvent(string.format('%04X',pc)) end
 end,emu.callbackType.exec,pc)
end
emu.addMemoryCallback(function(_,value)
 local map=emu.convertAddress(0xc880)
 if map and map.memType==emu.memType.nesWorkRam and map.address==2*8192+0x880 then bridgeEvent('packet-write',value) end
end,emu.callbackType.write,0xc880)
'''
        prefix += f'L.FrameCounter={Native.N.address(bundle,"FrameCounter")}\n'
        text = text.replace(" print('SMB_NATIVE_RECEIPT '..encode(receipt))",
                            " receipt.headBridge=headBridge;receipt.pickupCalls=pickupCalls\n print('SMB_NATIVE_RECEIPT '..encode(receipt))")
    assert 'io.' not in text
    return prefix+text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rom', type=Path, default=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'))
    parser.add_argument('--mode', choices=('armor','route','upgrades'), default='armor')
    parser.add_argument('--flower-candidate', action='store_true')
    parser.add_argument('--head-trace', action='store_true')
    args = parser.parse_args()
    output = R/'build/metal-flower-native-1112'
    output.mkdir(exist_ok=True)
    raw = args.rom.read_bytes()
    if args.flower_candidate:
        from compose_metal_flower_1112 import transform
        raw, _ = transform(raw)
        args.rom = output/'candidate.nes'
        args.rom.write_bytes(raw)
    script = output/'controller.lua'
    script.write_text(controller(raw,args.mode,args.head_trace),encoding='utf-8',newline='\n')
    result = run(script,args.rom,output/'capture',sha256(raw).hexdigest(),120)
    print(json.dumps({k:result[k] for k in ('passed','receipt','receipt_SHA256','script_SHA256')}),flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
