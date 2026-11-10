"""V4 real-write sound witness API mocks; native sound remains unqualified."""
from hashlib import sha256
import json
from unittest.mock import patch

import check_excitebike_stdout_controller_source_1110_v2 as V2

C=V2.C
LUA=C.P.W.R/'tools/playthroughs/excitebike_earned_powerup_stdout_1110_v4.lua'
V3_PIN='5406c2ca1b1d4ed13bb2b2042820a5692b2e8f913ac0af588db0da8562073a59'


def runtime():
    rt=V2.runtime()
    rt.execute('''local baseExec=host.exec
function host.exec(pc,sp)
 if pc==0xe100 and not host.noPowerupWrite then
  host.write(0x104,32);host.mem[0x104]=0;host.write(0x104,0)
 end
 baseExec(pc,sp)
end''')
    return rt


def main():
    v3=LUA.with_name('excitebike_earned_powerup_stdout_1110_v3.lua')
    assert sha256(v3.read_bytes()).hexdigest()==V3_PIN
    source=LUA.read_text()
    assert "emu.callbackType.write,L.Square2SoundQueue" in source
    assert "assert(sound.writes20>0,'Native pickup SFX20 write witness')" in source
    assert "r('Square2SoundQueue')==32" not in source
    with patch.object(V2,'LUA',LUA),patch.object(C,'LUA',LUA),patch.object(C,'runtime',runtime):
        C.checks()
        rt=runtime();C.before_collect(rt)
        assert rt.globals().host.status is None
        # The queue is actually consumed before the return callback. The
        # event proves one source write and its clear, not held-queue state.
        assert rt.globals().host.mem[0x104]==0
        rt.execute('host.noPowerupWrite=true')
        for _ in range(96):
            C.main(rt)
            if rt.globals().host.status is not None:break
        q=C.receipt(rt)
        d=next(e['value'] for e in q['events'] if e['event']=='native_collection_effects')
        assert d['square2']==0 and d['sound_witness']['writes20']==1 and d['sound_witness']['clears']==1,d
        rt=runtime();rt.execute('host.noPowerupWrite=true');C.before_collect(rt);q=C.receipt(rt)
        assert not q['passed'] and 'SFX20 write witness' in q['reason'],q
    print(json.dumps(dict(passed=True,API_mock_only=True,Mesen_run=False,outputs_written=0,
        source_sound_write_then_NMI_consume_before_return=True,absent_write_fails=True,
        v3_preserved_SHA256=V3_PIN,v4_Lua_SHA256=sha256(LUA.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':main()
