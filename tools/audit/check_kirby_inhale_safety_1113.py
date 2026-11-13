"""Current Kirby inhale boundary/state/copy audit, explicit CPU fixtures only."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json

import check_kirby_inhale_native_1112 as Old
import check_kirby_red_catch_1112 as Catch

A,N,Main,Bind=Old.A,Old.N,Old.Main,Old.Bind
PIN='a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
KIRBY_BANK_SHA='119a6fe415a914c415a51bc46f0cc22569cd4c7e1282d83f512c3b2031573e9d'


def bundle(raw):
    assert len(raw)==2097168
    if KIRBY_BANK_SHA is None:
        assert sha256(raw).hexdigest()==PIN
    else:
        start=Old.Wide.offset(0xa000)
        assert sha256(raw[start:start+8192]).hexdigest()==KIRBY_BANK_SHA
    b=Old.bundle(raw)
    # Authenticate the delivered capture and shell changes by exact inverse
    # preimages and forward source recomposition; do not rerun passed suites.
    parent=bytearray(raw)
    for pc,body in (Old.CLOCK,Old.TAIL):
        at=Old.Wide.offset(pc);parent[at:at+len(body)]=body
    assert Old.proposal(bytes(parent))[0]==raw
    parent=raw[:Catch.offset(Catch.START)]+Catch.PREIMAGE+raw[Catch.offset(Catch.END):]
    assert Catch.proposal(parent)[0]==raw
    return b


def actor(m,name,slot,face,gap,dy=8):
    kind=A.address(m.bundle,name)
    Main.actor(m,kind,112+(gap if face==1 else -gap),y=176+dy,slot=slot)
    N.put(m,ObjectOffset=slot)
    Bind.call(m,'CheckpointEnemyID',x=slot)
    Bind.put_slot(m,slot,Enemy_Y_Position=176+dy,Enemy_Y_HighPos=1,EnemyOffscrBitsMasked=0,
                  Enemy_MovingDir=3-face)
    if name=='BulletBill_CannonVar':
        Bind.put_slot(m,slot,Enemy_State=1,Enemy_BoundBoxCtrl=9)
    if name in ('GreenKoopa','BuzzyBeetle','RedKoopa','HammerBro','Goomba','Spiny'):
        speed=N.get(m,'Enemy_X_Speed',slot)
        signed=speed-256 if speed&128 else speed
        Bind.put_slot(m,slot,Enemy_X_Speed=((-abs(signed)) if face==1 else abs(signed))&255)


def step(m,pad):
    Main.keys(m,pad)
    o=Old.Observe(m.bundle)
    Main.call(m,'GameLoop',o)
    assert not m.blocked and not o.errors,(m.blocked,o.errors)
    return o.events


def boundaries(seed):
    counts,witnesses=Counter(),[]
    for name,face,mode,gap in product(Old.ENEMIES,(1,2),(0,1),range(6)):
        m=N.fork(seed);Main.scene(m,face)
        N.put(m,CrossoverBehaviorVersion=mode)
        actor(m,name,0,face,gap)
        before=Old.eligible(m,0)
        events=step(m,64)
        after=Old.eligible(m,0)
        health=N.get(m,'KbHealth')
        counts['cases']+=1
        counts['injured' if health<6 else 'uninjured']+=1
        if N.get(m,'KbMouth'):counts['captured']+=1
        if before['in_range'] and health<6:
            witnesses.append(dict(name=name,face=face,mode=mode,gap=gap,before=before,after=after,
                health=health,mouth=N.get(m,'KbMouth'),events=events))
    return dict(counts=dict(counts),front_start_injuries=witnesses)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part',choices=('bindings','boundaries'),default='boundaries')
    args=parser.parse_args()
    raw=Bind.NIGHTLY.read_bytes();b=bundle(raw)
    start=Old.Wide.offset(0xa000)
    print(json.dumps(dict(event='bindings',ROM_SHA256=sha256(raw).hexdigest(),
        Kirby_PRG74_SHA256=sha256(raw[start:start+8192]).hexdigest(),output_files=0)),flush=True)
    if args.part=='bindings':return
    seed,origin=Old.Wide.spawn_seed(b)
    print(json.dumps(dict(event='actual_menu_parser',parser_updates=origin,settle_updates=40)),flush=True)
    result=boundaries(seed)
    print(json.dumps(dict(part=args.part,result=result,source_CPU=True,native_emulator=False,
                         actor_data_fixtures=True,output_files=0)),flush=True)


if __name__=='__main__':main()
