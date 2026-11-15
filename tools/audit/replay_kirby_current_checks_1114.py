"""Strict current571 replays of delivered inhale and copied-shell repairs."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_native_floatey_score_1114 as Score
import check_ff_white_mushroom_current_1110 as W
from check_ff_stdout_controller_source_1110 import LuaRuntime
import replay_kirby_left_inhale_1112 as Left
import replay_kirby_red_current_1112 as Red

R,ROM,PIN=Score.R,Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'),Score.CANDIDATE
BANK_SHA='119a6fe415a914c415a51bc46f0cc22569cd4c7e1282d83f512c3b2031573e9d'
INHALE=R/'tools/playthroughs/kirby_current_inhale_stdout_1110_v3.lua'
GREEN=R/'tools/playthroughs/kirby_current_green_stdout_1110_v5.lua'
PINS={INHALE:'943e6886e3d76e427c54e7df107fdbeb768e26ac16bd3f6e8ad79c9f0a8b674a',
      GREEN:'730a40160788c5fa41b3bf8b931bfd14834bb463ae75a04b18f07f12e0d2ff20',
      Path(Left.__file__):'6936ff6ef6db415e98184c1751f5123e23c3e7a860d1c5734bce740b26f4a5b6'}
CASES=('right_easy','right_hard','left_easy','left_hard','green_full','red_catch')


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def hard(text):
    identity="r('KbVariant')==0 and r('CrossoverBehaviorVersion')==0 and noCheats()"
    text=once(text,identity,identity.replace("Version')==0","Version')==1"))
    old=" press('start')\n ready(function()return r('CrossoverMenuState')==2"
    new=""" press('down');press('a')
 assert(r('CrossoverMenuState')==4,'Actual Options opens')
 press('down');press('a')
 assert(r('CrossoverBehaviorVersion')==1,'Actual Hard selected')
 press('b')
 ready(function()return r('CrossoverMenuState')==0 and r('DisableScreenFlag')==0 end,180,'title return')
 press('start')
 ready(function()return r('CrossoverMenuState')==2"""
    return once(text,old,new).replace('Actual Easy Kirby selection','Actual Hard Kirby selection')


@lru_cache(maxsize=6)
def controller(raw,case):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN and case in CASES
    assert all(sha256(p.read_bytes()).hexdigest()==pin for p,pin in PINS.items())
    lo=16+74*8192;assert sha256(raw[lo:lo+8192]).hexdigest()==BANK_SHA
    if case.startswith('left_'):text=Left.controller(2,case.endswith('_hard'))
    elif case.startswith('right_'):
        text=INHALE.read_text();text=hard(text)if case.endswith('_hard')else text
    elif case=='green_full':text=GREEN.read_text()
    else:text=Red.controller(return_flight=True,expect_catch=True)
    first,body=text.split('\n',1)
    runtime=LuaRuntime(unpack_returned_tuples=True);q=runtime.execute(first+'\nreturn C')
    b=dict(W.Symbols.bundle(),raw=raw)
    for name,at in q.ram.items():assert W.address(b,name)==at,(case,name,'retained RAM binding')
    for name,h in q.hooks.items():
        values=bytes(v for _,v in sorted(h.bytes.items()))
        if name=='erased':values=bytes.fromhex('a9018d0c5c')
        assert raw[16+h.offset:16+h.offset+len(values)]==values,(case,name,'current hook preimage')
    # Same five-byte authentication update used in the delivered1112 replay.
    text=first+'\nC.hooks.erased.bytes={169,1,141,12,92}\n'+body
    runtime.compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def variant(case):return 2 if case.startswith(('left_','right_'))else 1 if case=='green_full'else 0


def metadata(raw):
    return dict(ROM_SHA256=PIN,Kirby_PRG74_SHA256=BANK_SHA,
        cases={case:dict(script_SHA256=sha256(controller(raw,case).encode()).hexdigest(),
            variant=variant(case))for case in CASES},normal_inputs_only=True,
        actor_health_ability_position_and_outcome_seeds=0,ROM_changes=0,outputs=0,Mesen_run=False,
        scope='Current actual input/hook/preservation qualification; native outcomes require separate runs')


if __name__=='__main__':print(json.dumps(metadata(ROM.read_bytes()),separators=(',',':')),flush=True)
