"""Interrupt actual new Mini head and side routes at native GameLoop depth."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import check_mini_floor_pair_fast_1108_v1 as F
import check_mini_lift_admission_async_1108_v1 as A
from check_mini_native_side_single_map_1109_v1 import BASE, PIN, N, sha


def apply(image,receipt,parent=PIN):
    assert receipt['passed'] and receipt['parent_SHA256']==parent
    for row in receipt['patches']:
        site=row['file_offset']
        before,after=(bytes.fromhex(row[k]) for k in ('old_hex','new_hex'))
        assert image[site:site+len(before)]==before
        image=image[:site]+after+image[site+len(after):]
    return image


def check(image,head,adder):
    b=F.F.bundle(image)
    cpu_class=A.CPU
    counts=Counter()
    nested={}
    minimum=255
    seed=F.F.fixture(b,0,False,False)
    idle,game_loop,game_core=(F.F.address(b,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine'))
    lag,regular=A.lag_pcs(seed)
    stop=idle+12
    assert bytes(seed[0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(seed[idle+9:idle+12])==bytes((0x20,game_loop&255,game_loop>>8))

    def handler(c,kind,role):
        nonlocal minimum
        m=c.memory
        at=(c.pc,c.sp)
        before=A.live(c)
        n=len(m.writes)
        skipped=N.get(m,'NmiSkipped')
        if kind=='lag_FF':
            assert N.get(m,'NmiDisable')==255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
            assert (A.tags(c),c.pc)==(254,0x8000)
        visits=0
        for _ in range(16000):
            if (c.pc,c.sp)==at:
                break
            minimum=min(minimum,c.sp)
            if kind=='lag_FF':
                assert c.pc!=regular
                visits+=c.pc==lag
                if not c.p&4:
                    key=A.tags(c),c.pc
                    if key not in nested or c.sp<nested[key].sp:
                        nested[key]=A.clone(c)
            assert m[c.pc],(kind,role,at,hex(c.pc))
            cpu_class.step(c)
        else:
            raise AssertionError(('bounded ISR',kind,role,at,hex(c.pc)))
        assert A.live(c)==before,(kind,role,at)
        assert visits==(kind=='lag_FF')
        assert N.get(m,'NmiSkipped')==(skipped+(kind=='lag_FF'))&255
        assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in m.writes[n:])
        counts[kind,role]+=1

    def finish(c):
        for _ in range(42000):
            if c.pc==stop:
                m=c.memory
                return A.final(c),bytes(m[0x300:0x4a0]),bytes(m[0x600:0x73f])
            assert c.memory[c.pc],hex(c.pc)
            cpu_class.step(c)
        raise AssertionError(('native continuation',hex(c.pc)))

    summaries={}
    for label,owner,x,y,tile in (('Mini4sides',41,1513,135,0),('MiniSideCoin',41,758,112,0xc2),
                                ('ForeignMario',0,1513,135,0),('ForeignSamus',6,1513,135,0)):
        bus=N.fork(seed)
        F.setup(bus,x,y,0,0,side=tile,actor=owner)
        N.put(bus,GuestLandingLimit=1,NmiDisable=255)
        reached=set()
        entries={}
        resumes=[]
        visits=Counter()

        class Trace(cpu_class):
            def step(self):
                tag,pc=A.tags(self),self.pc
                if tag==254 and pc in (game_loop,game_core):
                    entries[pc]=self.sp
                if tag==148 and pc==0xbdf4 and owner==41:
                    # Hold the source CPU fixture at the reached fallback
                    # ingress. The real Mini control update can replace the
                    # earlier seeded host coordinates and landing limit.
                    N.put(bus,Player_X_Position=x&255,Player_PageLoc=x>>8,
                          Player_Y_Position=y,Player_Y_HighPos=1,Player_State=1,
                          GuestLandingLimit=1)
                    F.tiles(bus,x,y,0,0,side=tile)
                if tag==254 and pc in (0x9c85,0x9cac):
                    visits['native_side_call']+=1
                role=None
                if tag==254 and (0x90e4<=pc<0x9109 or 0x913d<=pc<0x9144):
                    role='fixed_side'
                elif tag==161 and 0xbea2<=pc<0xbf00:
                    role='foreign_side'
                elif tag==217 and 0xbfb0<=pc<0xc000 and head:
                    role='head_route'
                elif adder and tag in (247,248,253,255) and (0xed41<=pc<0xed53 or 0xe4a7<=pc<0xe4b3):
                    role='adder_route'
                if role:
                    visits[role]+=1
                    if (tag,pc) not in reached:
                        reached.add((tag,pc))
                        for kind in ('IRQ','lag_FF'):
                            fork=A.clone(self)
                            handler(fork,kind,role)
                            resumes.append(fork)
                return cpu_class.step(self)

        c=Trace(memory=bus,pc=idle)
        c.sp,c.p=255,0x31
        c.stPushWord(0xe33b)
        for _ in range(42000):
            if c.pc==stop:
                break
            assert bus[c.pc],hex(c.pc)
            c.step()
        else:
            raise AssertionError(('native GameLoop',label,hex(c.pc)))
        assert entries=={game_loop:250,game_core:248} and c.sp==252
        assert resumes and visits['fixed_side'],(label,visits)
        if owner==41:
            assert not visits['foreign_side'] and (not head or visits['head_route']), (label,visits)
            assert not adder or visits['adder_route'],(label,visits)
            if label=='Mini4sides':
                assert visits['native_side_call']==4,(label,visits)
        else:
            assert visits['foreign_side'],(label,visits)
        expect=finish(c)
        assert all(finish(q)==expect for q in resumes),(label,'full continuation')
        summaries[label]=dict(distinct_reached=len(reached),resumed=len(resumes),visits=dict(visits))
    for cut in nested.values():
        handler(cut,'nested_IRQ','lag_handler')
    assert minimum>0x7a and nested
    return dict(scenarios=summaries,min_ISR_SP=minimum,exact_entries=dict(GameLoop=250,GameCoreRoutine=248),
                cuts={kind:{role:n for (k,role),n in counts.items() if k==kind}
                      for kind in ('IRQ','lag_FF','nested_IRQ')})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--include-head',action='store_true')
    parser.add_argument('--include-adder',action='store_true')
    args=parser.parse_args()
    out=args.output.resolve()
    raw=BASE.read_bytes()
    assert sha(BASE)==PIN
    side=json.loads((out/'proof.json').read_text())
    image=apply(raw,side)
    assert hashlib.sha256(image).hexdigest()==side['expected_memory_only_SHA256']
    if args.include_adder:
        adder=json.loads((out/'adder-proof.json').read_text())
        image=apply(image,adder,side['expected_memory_only_SHA256'])
        assert hashlib.sha256(image).hexdigest()==adder['expected_memory_only_SHA256']
    if args.include_head:
        head=json.loads((out/'head-proof.json').read_text())
        assert hashlib.sha256(apply(raw,head)).hexdigest()==head['expected_memory_only_SHA256']
        image=apply(image,head)
    results=check(image,args.include_head,args.include_adder)
    receipt=dict(passed=True,parent_SHA256=PIN,memory_only_SHA256=hashlib.sha256(image).hexdigest(),
                 source_CPU_only=True,ROM_written=False,include_head=args.include_head,
                 include_adder=args.include_adder,**results)
    path=out/('adder-async-proof.json' if args.include_adder else 'async-proof.json')
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':
    main()
