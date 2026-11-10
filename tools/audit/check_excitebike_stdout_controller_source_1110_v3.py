"""V3 effect diagnostics API proof; all acceptance conditions retained."""
from hashlib import sha256
import json
from unittest.mock import patch

import check_excitebike_stdout_controller_source_1110_v2 as V2

C=V2.C
LUA=C.P.W.R/'tools/playthroughs/excitebike_earned_powerup_stdout_1110_v3.lua'
V2_PIN='5605c4f2a73c21ecfcc7c8013ad67ce427bdd713a722fe91e08c5fca1d053056'


def main():
    assert sha256(V2.LUA.read_bytes()).hexdigest()==V2_PIN
    old=V2.LUA.read_text();new=LUA.read_text()
    expected=old.replace('-- V2 observer: physical work-RAM2 source reads at native Main return.',
        '-- V3 observer: record native effects before the unchanged acceptance checks.\n-- V2 observer: physical work-RAM2 source reads at native Main return.')
    line="   assert(r('Enemy_Flag',slot)==0 and r('FloateyNum_Control',slot)==6 and r('Square2SoundQueue')==32,'Native erase/floaty/SFX')"
    diagnostic="""   note('native_collection_effects',{slot=slot,flag=r('Enemy_Flag',slot),id=r('Enemy_ID',slot),
    floaty=r('FloateyNum_Control',slot),floaty_timer=read(0x12c+slot),
    square1=read(0xff),square2=r('Square2SoundQueue'),
    A=c['cpu.a'],X=c['cpu.x'],Y=c['cpu.y'],P=c['cpu.ps']or c['cpu.p'],player=state()})
"""
    expected=expected.replace(line,diagnostic+line);assert expected.strip()==new.strip()
    with patch.object(V2,'LUA',LUA),patch.object(C,'LUA',LUA),patch.object(C,'runtime',V2.runtime):
        C.checks()
        for address,value,key in ((0x15,1,'flag'),(0x112,0,'floaty'),(0x104,0,'square2')):
            rt=V2.runtime()
            rt.execute(f'''local oldRead=emu.read
function emu.read(at,kind)if kind==1 and at=={address} then return {value} end;return oldRead(at,kind)end''')
            C.before_collect(rt);q=C.receipt(rt)
            assert not q['passed'] and 'Native erase/floaty/SFX' in q['reason'],q
            d=next(e['value'] for e in q['events'] if e['event']=='native_collection_effects')
            assert d[key]==value and d['slot']==5,d
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,outputs_written=0,
        unchanged_controller_and_acceptance=True,three_effect_negatives_logged_before_assert=True,
        v2_preserved_SHA256=V2_PIN,v3_Lua_SHA256=sha256(LUA.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
