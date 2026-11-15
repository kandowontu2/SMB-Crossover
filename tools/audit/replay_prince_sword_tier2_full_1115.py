"""Strict tier2 candidate facade over frozen53c1 ordinary full controls."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import compose_prince_sword_tier2_1115 as C
import replay_prince_full_fresh_current_1115 as Frozen
import replay_prince_body_transition_1115 as Readback

PIN=C.CANDIDATE
FROZEN_SOURCE='77729f1c83d5bbf52b23319ecb3a51ce9b4ac48ea6f68c9baa86c6ec05edb1ba'
FROZEN_LUA='53c107fec29692356caa88d727fb64aea096c39f0220be2a5749da81e01b8235'

@lru_cache(maxsize=1)
def controller(raw):
    assert isinstance(raw,bytes)and C.digest(raw)==PIN
    parent=C.inverse(raw);assert C.digest(Path(Frozen.__file__).read_bytes())==FROZEN_SOURCE
    old=Frozen.controller(parent);assert C.digest(old.encode())==FROZEN_LUA;text=old
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    change(C.PIN,PIN)
    change(parent[C.Packet.COOKIE:C.Packet.COOKIE+16].hex(),raw[C.Packet.COOKIE:C.Packet.COOKIE+16].hex())
    oldparts=C.Packet.extract(parent)[1];parts=C.Packet.extract(raw)[1];oldrows=[];newrows=[]
    for row in Readback.C.allocation()['decoded_spans']:
        stream=row['stream'];lo,hi=row['decoded_half_open'];origin=0xa000 if stream==0 else 0xc800 if stream==1 else 0xc0b0
        oldrows.append(dict(bank=3 if stream==0 else 2,offset=(origin+lo)&8191,bytes=list(oldparts[stream][lo:hi])))
    for row in Readback.C.Plan.Current.Graphics.allocation()['decoded_envelopes']:
        stream=row['stream'];lo=row['offset'];size=row['bytes'];origin=0xa000 if stream==0 else 0xc800
        oldrows.append(dict(bank=3 if stream==0 else 2,offset=(origin+lo)&8191,bytes=list(oldparts[stream][lo:lo+size])))
    newrows=list(oldrows)
    for row in C.Plan.arrays(parent)[3]:
        stream=row['stream'];lo,hi=row['decoded_half_open'];pc=row['live_CPU_half_open'][0]
        newrows.append(dict(bank=2,offset=pc&8191,bytes=list(parts[stream][lo:hi])))
    assert sum(len(row['bytes'])for row in oldrows)==4027 and sum(len(row['bytes'])for row in newrows)==4185
    change('local candidateStaticExtents='+Readback.lua(oldrows),'local candidateStaticExtents='+Readback.lua(newrows))
    change("if passed then assert(newPacketVerified,'Actual16a packet consumer readback required')end",
        "if passed then assert(newPacketVerified,'Actual tier2 packet consumer readback required');assert(read(0x75b)==2 and source(0x6ee)==1,'Earned sword persists into actual1-2')end")
    change('source_draws=sourceDraws,new_candidate_readback=newPacketVerified,',
        'source_draws=sourceDraws,new_candidate_readback=newPacketVerified,persistent_sword={native_PlayerStatus=read(0x75b),Sword=source(0x6ee)},')
    # All navigation, combat and completed-Main endpoint conditions are frozen.
    Readback.Full.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(text.encode()),required_native_variant=3,
        frozen_parent_factory_SHA256=FROZEN_SOURCE,frozen_parent_Lua_SHA256=FROZEN_LUA,
        navigation_and_combat_unchanged=True,first_BBC1_both_cookies_and_4185_static_bytes=True,
        full_endpoint='Actual1-2,25 living grounded completed Main returns, native075B2/privateSword1',
        no_gameplay_seeds=True,portable_inverse_parent=C.PIN,source_qualified=False,native_qualified=False,outputs=0,Mesen=False)

if __name__=='__main__':
    from unittest.mock import patch
    import json
    def deny(*a,**k):raise AssertionError('Tier2 full metadata attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,_=C.proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes());q=metadata(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
