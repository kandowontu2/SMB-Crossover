"""Pure current SMB2/Doki natural item controller; no ROM/state/capture writes."""
from hashlib import sha256
import argparse
import json
from pathlib import Path

import replay_smb2_stage_current_1113 as Root

PIN=Root.PIN
SOURCE=Path(__file__).resolve().parents[1]/'reference/smb2_natural_powerups_1113.lua'
BASE='6371ab8df461a9a347ad6baf5f7f3d84de78fa1472af4a49d73b98574958231e'
MODES=('injured-mushroom','healthy-flower-birth')


def controller(raw,variant=4,mode='injured-mushroom'):
    assert sha256(raw).hexdigest()==PIN and 0<=variant<8 and mode in MODES
    flags=dict(jump_hold=24,enemy_gap=48,source_edges=True,injury_trace=True,last_pit_settle=True,runup=True)
    base=Root.controller(raw,4,**flags);assert sha256(base.encode()).hexdigest()==BASE
    text=base.replace('local identity,expectedRom,gameOffset,attrs=4,',f'local identity,expectedRom,gameOffset,attrs={variant},')
    assert text==Root.controller(raw,variant,**flags)
    b=dict(Root.Base.W.Symbols.bundle(),raw=raw)
    names=('Enemy_Y_Position','PowerUpType','S2Variant','S2Health','S2MaxHealth','S2Vegetables',
        'S2Size','S2Air','S2VX','S2VY','S2Held','S2Fresh','S2Holding','S2State','S2Timer',
        'S2Hurt','PlayerStatus','Square2SoundQueue','FloateyNum_Control',
        'NativeRarePlayerHeadCollisionCore','S2MainPrepare','S2MainPickup')
    extra=','.join(f'{name}={Root.Base.W.address(b,name)}'for name in names)
    text=Root.once(text,'local F={','local F={'+extra+',')
    hooks={n:dict(offset=Root.Base.W.location(b,n)-16,hex=raw[Root.Base.W.location(b,n):Root.Base.W.location(b,n)+12].hex())
        for n in('NativeRarePlayerHeadCollisionCore','S2MainPrepare','S2MainPickup')}
    literal='local itemHooks={'+','.join(n+'={offset='+str(q['offset'])+',hex="'+q['hex']+'"}'for n,q in hooks.items())+'}\n'
    text=literal+f'local itemMode={json.dumps(mode)}\n'+text
    replacements={
        'local frames,updates,pad=0,0,0':"local natural={phase='approach',since=0,hold=0,previousHealth=31,heads={},prepares={},pickups={},injuries={},events={}}\nlocal frames,updates,pad=0,0,0",
        'return_counts=returns,pipes=pipes,recent=records':'return_counts=returns,pipes=pipes,recent=records,natural=natural,item_mode=itemMode',
        'local function drive()':'local function traversalDrive()',
        "string.format('%q',k)":"string.format('%q',tostring(k))",
        '-- Observe every actual GameLoop return, including the native catch-up caller.':SOURCE.read_text()+'\n-- Observe every actual GameLoop return, including the native catch-up caller.',
        'local task=coroutine.create(function()':"local task=coroutine.create(function()\n if CPU_CONTROLLER_OPENING then assert(r('SelectedCharacter')==25 and r('S2Variant')==identity,'Actual CPU SMB2/Doki menu');game=true;phase='game';pad=0;return end",
        "assert(os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,":"assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==expectedRom,",
    }
    for before,after in replacements.items():text=Root.once(text,before,after)
    needle='-- Ordinary current-stage item evidence.'
    check="for _,h in pairs(itemHooks)do for i=1,#h.hex,2 do assert(emu.read(h.offset+(i-1)//2,emu.memType.nesPrgRom)==tonumber(h.hex:sub(i,i+1),16),'Exact current SMB2 item hook')end end\n"
    text=Root.once(text,needle,check+needle)
    Root.Base.LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',type=int,choices=range(8),default=4)
    p.add_argument('--mode',choices=MODES,default=MODES[0]);args=p.parse_args()
    text=controller(Root.Base.ROM.read_bytes(),args.variant,args.mode)
    print(json.dumps(dict(ROM_SHA256=PIN,variant=args.variant,mode=args.mode,
        controller_SHA256=sha256(text.encode()).hexdigest(),Lua_compile=True,outputs=0,Mesen_run=False)),flush=True)
