"""Explicit native tier constructor/death/newgame components, not earned play."""
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_sword_tier2_fresh_cold_1115 as Cold
import check_prince_sword_tier2_fresh_dispatch_1115 as Dispatch

C,N,W,Frames=Cold.C,Cold.N,Cold.W,Cold.Frames

def run(parent):
    raw,_=C.proposal(parent);m,opening=Cold.cold(raw)
    part=C.Packet.extract(raw)[1][1]
    assert part[0xd963-0xc800:0xd963-0xc800+6]==bytes.fromhex('20b0c0ad84c0')
    for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    cases=[]
    for tier in(0,1,2):
        b=N.fork(m);N.put(b,PlayerStatus=tier)
        # Actual current private constructor, with its real RAM2/RAM3 map
        # precondition. Only native075B is a declared diagnostic state input.
        call=Dispatch.invoke(b,0xd963)
        assert b.ram[2][0x6ee]==(tier==2)and N.get(b,'PlayerStatus')==tier
        cases.append(dict(tier=tier,Sword=b.ram[2][0x6ee],call=call))
    newgame=N.fork(m);N.put(newgame,PlayerStatus=2)
    N.invoke(newgame,'InitializeMemory',a=0,x=0,y=0x6f,p=0x21)
    assert N.get(newgame,'PlayerStatus')==0
    death=N.fork(m);N.put(death,PlayerStatus=2)
    N.invoke(death,'KillPlayer',a=0,x=0,y=0,p=0x21);assert N.get(death,'PlayerStatus')==0
    q=dict(passed=True,ROM_SHA256=C.CANDIDATE,opening=opening,constructor_tier_cases=cases,
        public_InitializeMemory_newgame_limit=0x6f,newgame_native_PlayerStatus=N.get(newgame,'PlayerStatus'),
        explicit_KillPlayer_native_PlayerStatus=N.get(death,'PlayerStatus'),
        scope='Explicit native-tier public/private component units on real cold code. Tier2 is diagnostic, not earned acquisition or natural death.',
        native_tier_seeds_declared=True,private_HP_Sword_actor_seeds=0,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Lifecycle components attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
