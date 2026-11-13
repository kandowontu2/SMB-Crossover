"""Pure exact-current natural Bowser mushroom/flower controller factory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import replay_bowsers_current_1113 as Base

PIN=Base.PIN
SOURCE=Path(__file__).resolve().parents[1]/'reference/bowser_natural_powerups_1113.lua'
BASE=(
    '0be5c10a092f5214821a033b4bbf8e7028847febacc92abb8853ed77d3af0c46',
    '0c09bb637a4fda2eac517adcf6f5bd0602f610e39e9d130714f6859d63e69856',
)
SCRIPTS=(
    '58d777bc44d5b7ff370ace86b20a76e57f69f6f70e11e0cc57940a263f4e4de1',
    'd23ba56d64b6efacc3ba21463717df4764623bba3b10100073758f3cb5d2fb63',
)


def controller(raw,identity=0):
    assert identity in (0,1) and sha256(raw).hexdigest()==PIN
    text=Base.controller(raw,identity)
    assert sha256(text.encode()).hexdigest()==BASE[identity],'Frozen original full-stage controller'
    b=dict(Base.W.Symbols.bundle(),raw=raw)
    names=('Enemy_Y_Position','PowerUpType','GuestPowerupActive','GuestPowerupAge','PlayerStatus',
        'Square2SoundQueue','FloateyNum_Control','BwPickup','BwPowerupTick','NativeRarePlayerHeadCollisionCore')
    extra=','.join(f'{name}={Base.W.address(b,name)}'for name in names)
    text=text.replace('local F={','local F={'+extra+',',1)
    text='local BOWSER_HEAD_OFFSET='+str(Base.W.location(b,'NativeRarePlayerHeadCollisionCore')-16)+'\n'+text
    replacements={
        'local frames,updates,pad=0,0,0':"local natural={phase='mushroom-approach',since=0,pickups={},heads={},events={}}\nlocal frames,updates,pad=0,0,0",
        'return_counts=returns,pipes=pipes,recent=records':'return_counts=returns,pipes=pipes,recent=records,natural=natural',
        'local function drive()':'local function traversalDrive()',
        "string.format('%q',k)":"string.format('%q',tostring(k))",
        '-- Observe every actual GameLoop return, including the native catch-up caller.':SOURCE.read_text()+'\n-- Observe every actual GameLoop return, including the native catch-up caller.',
        'local task=coroutine.create(function()':"local task=coroutine.create(function()\n if CPU_CONTROLLER_OPENING then assert(r('SelectedCharacter')==27 and r('FmAlts')&8==identity*8,'Actual CPU Bowser menu');game=true;phase='game';pad=0;return end",
        "assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,":"assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,",
    }
    for old,new in replacements.items():
        assert text.count(old)==1,old
        text=text.replace(old,new)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    Base.LuaRuntime().compile(text)
    assert sha256(text.encode()).hexdigest()==SCRIPTS[identity],'Frozen natural item controller'
    return text


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',type=int,choices=(0,1),default=0)
    args=p.parse_args();raw=Base.ROM.read_bytes();text=controller(raw,args.identity)
    print(json.dumps(dict(ROM_SHA256=PIN,identity=args.identity,controller_SHA256=sha256(text.encode()).hexdigest(),
        bytes=len(text),Lua_compile=True,output_files=0,Mesen_run=False)),flush=True)
