"""Strict40a facade retaining frozen53c1 navigation and tier2 observers."""
from functools import lru_cache
from pathlib import Path
import compose_prince_sword_tier2_fresh_1115 as C
import replay_prince_sword_tier2_full_1115 as Previous

PIN=C.CANDIDATE
PREVIOUS_SOURCE='982fbb9103c12abd939f72348d75cf2434ba45792cf067ab73b40e0a30ed9c02'
PREVIOUS_LUA='df467cb383f0c180d304350377a0f7d3201221d479820c730de525db289c7f18'

@lru_cache(maxsize=1)
def controller(raw):
    assert C.digest(raw)==PIN and C.digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SOURCE
    parent=C.inverse(raw);reference=Previous.C.proposal(parent)[0]
    old=Previous.controller(reference);assert C.digest(old.encode())==PREVIOUS_LUA;text=old
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change(Previous.PIN,PIN)
    change(reference[C.Packet.COOKIE:C.Packet.COOKIE+16].hex(),raw[C.Packet.COOKIE:C.Packet.COOKIE+16].hex())
    row=C.Plan.arrays(parent)[3][-1];part=C.Packet.extract(raw)[1][0];lo,hi=row['decoded_half_open']
    additional=dict(bank=3,offset=0xb3f1&8191,bytes=list(part[lo:hi]))
    # Keep all prior4185 exact checks, append only the8-byte Fresh extent.
    lines=text.splitlines(keepends=True);matches=[i for i,line in enumerate(lines)if line.startswith('local candidateStaticExtents=')]
    assert len(matches)==1;i=matches[0];line=lines[i];assert line.endswith('}\n')
    lines[i]=line[:-2]+','+Previous.Readback.lua(additional)+'}\n';text=''.join(lines)
    Previous.Readback.Full.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw).encode()),required_native_variant=3,
        frozen_parent_factory_SHA256=PREVIOUS_SOURCE,frozen_parent_Lua_SHA256=PREVIOUS_LUA,
        navigation_and_combat_exact53c1=True,first_BBC1_both_cookies_and_4193_static_bytes=True,
        terminal_requires_native075B2_privateSword1_and25completed_grounded_Main=True,
        portable_inverse_parent7a80=C.PIN,gameplay_seeds=0,outputs=0,Mesen=False)

if __name__=='__main__':
    from unittest.mock import patch
    import json
    def deny(*a,**k):raise AssertionError('Fresh controller metadata attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,_=C.proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes());q=metadata(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
