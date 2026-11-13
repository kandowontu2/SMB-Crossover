"""Run retained Metal controllers with stdout-only receipts on a specified ROM."""
import argparse
import json
import re
from pathlib import Path
from hashlib import sha256
import check_prince_brick_support_1111 as Native
from run_stdout_mesen_1110 import run, R


def controller(raw, mode):
    relative = ('metal-storm-natural-armor-1101-v26/native' if mode == 'armor'
                else 'metal-reservation-1102-v42/route')
    original = R/'build'/relative/'controller.lua'
    text = original.read_text(encoding='utf-8')
    if mode == 'armor':
        assert text.count(" if phase=='play' then\n") == 1
        text = text.replace(" if phase=='play' then\n", " if phase=='play' then\n  pad.b=true\n")
        text = text.replace('if x<240 then', 'if x<336 then')
    labels = set(re.findall(r"r\('([^']+)'", text)) | set(re.findall(r'L\.(\w+)', text))
    bundle = Native.C.Start.W.bundle(raw)
    prefix = 'local L={' + ','.join(f'{name}={Native.N.address(bundle,name)}' for name in sorted(labels)) + '}\n'
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
  headHits=headHits,headCalls=headCalls,headReturned=headReturned,bumps=bumps,sourceContacts=sourceContacts}
 print('SMB_NATIVE_RECEIPT '..encode(receipt))
 done=true;emu.stop(passed and 0 or 1)
end
'''.replace('CONDITION', condition)
    for name in ('WorldNumber','LevelNumber','GameEngineSubroutine','PlayerStatus'):
        if name not in labels:
            prefix += f'L.{name}={Native.N.address(bundle,name)}\n'
    text = text.replace(old,new)
    assert 'io.' not in text
    return prefix+text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rom', type=Path, default=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'))
    parser.add_argument('--mode', choices=('armor','route'), default='armor')
    parser.add_argument('--flower-candidate', action='store_true')
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
    script.write_text(controller(raw,args.mode),encoding='utf-8',newline='\n')
    result = run(script,args.rom,output/'capture',sha256(raw).hexdigest(),120)
    print(json.dumps({k:result[k] for k in ('passed','receipt','receipt_SHA256','script_SHA256')}),flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
