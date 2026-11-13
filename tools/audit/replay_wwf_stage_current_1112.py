"""Rebind retained successful WWF routes to the current menu; stdout only."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import compose_metal_kirby_1112 as Current
from run_stdout_mesen_1110 import run, R
from nightly_patch_guard_v1 import check

SOURCES = (
 ('native-hogan3','4a3aecd1943e61febc170d98043401f165a69d6050b9261e9a5e2d522b3e4acf'),
 ('native-wwf-1','c051fa4f46b03f514461b79894fd9b59d35ee3fa330701ed1227f7c63b285413'),
 ('native-wwf-2','472543926c58271e7b4c473e0ed71eac25dc037a0915aa292aa409820e07c269'),
 ('native-wwf-3','6d0a1394cd539fc4497ebe02ce421e6bdbdcbb4ed0ceb5ec0f59db1ba6647395'),
 ('native-wwf-4','e869415b8769fc63ea9cde10a19798f510a557a5e92ee7387a374f28ffcde4c9'),
 ('native-andre-timing','27f4e7cd4337857fae5e5f756473cc9ae1145b7221d7a3ee6b0a607168eaeae4'),
)


def controller(role):
    directory,pin=SOURCES[role]
    source=R/'build/wwf-helper-stable-1102-v2'/directory/'controller.lua'
    assert sha256(source.read_bytes()).hexdigest()==pin
    text=source.read_text()
    begin=text.index('local actions=')
    end=text.index('\n',begin)
    actions=['down']*3+['right']*4+['select']*role
    text=text[:begin]+'local actions={'+','.join("'"+x+"'" for x in actions)+'}'+text[end:]
    if role != 5:
        # Retain the source walking-action retirement already proven necessary
        # for Andre. Check approaching enemies even during the landing cooldown.
        text=text.replace('local pipe=1','local pipe=1\nlocal combatStart=nil',1)
        text=text.replace('  local danger=nearest()', '''  local danger=nearest()
  if ground and danger and danger<=44 then combatStart=combatStart or updates else combatStart=nil end
  if ground and danger and danger<=44 then pad.right=false;local attackAge=(updates-(combatStart or updates))%18;pad.b=attackAge>=2 and attackAge<5 end''',1)
        text=text.replace('pad.b=updates%18<3 end','local attackAge=(updates-(combatStart or updates))%18;pad.b=attackAge>=2 and attackAge<5 end')
        text=text.replace('if jumping then pad.a=jumpAge<36 end',
            'if jumping then pad.a=jumpAge<36;pad.b=updates%18<3 end')
    if role == 3:
        text=text.replace(' emu.setInput(pad,0)',
            " if phase=='play' and active() and r('Player_State')==0 and pad.b then pad.down=true end\n emu.setInput(pad,0)",1)
    begin=text.index(" local hf=assert(io.open(")
    end=text.index('\nend\nemu.addMemoryCallback',begin)
    receipt=text[text.index(' out:write(string.format(',begin):text.index('\n out:close()',begin)]
    receipt=receipt.replace(' out:write('," print('SMB_NATIVE_RECEIPT '..",1)
    receipt=receipt.replace('{"passed":%s,','{"ROM_SHA256":"'+Current.PIN+'","output_files":0,"helper_carries":'+"%d"+',"passed":%s,',1)
    receipt=receipt.replace('tostring(passed),reason,','helperCarries,tostring(passed),reason,',1)
    receipt=receipt.replace('"trace":[%s]', '"contact_trace":[%s],"trace":[%s]')
    receipt=receipt.replace("table.concat(trace,',')))", "table.concat(contactTrace,','),table.concat(trace,',')))")
    text=text[:begin]+receipt+'\n emu.stop(passed and 0 or 1)'+text[end:]
    text=text.replace("local passed=reason=='active-1-2' and initialLives==r('NumberofLives')",
        "local passed=reason=='active-1-2' and initialLives==r('NumberofLives') and helperCarries>0")
    # Ordinary menu navigation, native physics, enemy combat and platform
    # carries are retained. No emulated state or file-writing API survives.
    assert 'io.' not in text and 'takeScreenshot' not in text
    text='local L={}\nlocal contactTrace={}\nlocal traceEpoch=-1\n'+text
    text=text.replace(' frame=frame+1;age=age+1', ''' frame=frame+1;age=age+1
 if phase=='play' and active() and ((wx()>=760 and wx()<840) or (wx()>=1100 and wx()<1250)) and traceEpoch~=r('FrameCounter') then
  traceEpoch=r('FrameCounter')
  local actors={}
  for i=0,5 do if r('Enemy_Flag',i)~=0 then
   actors[#actors+1]=string.format('[%d,%d,%d,%d,%d]',i,r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i))
  end end
  if #contactTrace==20 then table.remove(contactTrace,1) end
  contactTrace[#contactTrace+1]=string.format('{"frame":%d,"x":%d,"y":%d,"state":%d,"engine":%d,"jumpAge":%d,"jumping":%s,"input":%d,"action":%d,"pose":%d,"actors":[%s]}',frame,wx(),r('Player_Y_Position'),r('Player_State'),r('GameEngineSubroutine'),jumpAge,tostring(jumping),emu.read(0xdc,emu.memType.nesDebug),emu.read(2*8192+0x3c,emu.memType.nesWorkRam),emu.read(2*8192+0x32,emu.memType.nesWorkRam),table.concat(actors,','))
 end''',1)
    text=text.replace("if done then return end\n frame=frame+1;age=age+1",
        "if done then return end\n assert(emu.read(0x7ffb,emu.memType.nesDebug)==0 and emu.read(0x7ffc,emu.memType.nesDebug)==0,'No cheats')\n frame=frame+1;age=age+1")
    return text


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--role',type=int,choices=range(6),required=True)
    args=parser.parse_args()
    rom=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert check(rom)['ROM_sha256']==Current.PIN
    script=Current.OUTPUT/'controller.lua'
    script.write_text(controller(args.role),encoding='utf-8',newline='\n')
    result=run(script,rom,Current.OUTPUT/'capture',Current.PIN,150)
    receipt=result['receipt']
    print(json.dumps(dict(role=args.role,passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
        script_SHA256=result['script_SHA256'],receipt={k:v for k,v in receipt.items()
            if k!='trace' and (k!='contact_trace' or not result['passed'])})),flush=True)
    assert result['passed']


if __name__=='__main__':
    main()
