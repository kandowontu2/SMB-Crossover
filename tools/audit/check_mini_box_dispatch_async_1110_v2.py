"""Compare native Mini box interrupts and pair inherited Proto lag effects."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from check_mini_box_dispatch_1110_v1 import A, BASE, BOX_CALL, BOX_RETURN, F, N, PIN, SOURCE
from check_mini_box_dispatch_1110_v1 import address, bundle, compare_memory, sha


def check(before,after):
    seeds=[F.F.fixture(bundle(image),0,False,False) for image in (before,after)]
    b=seeds[1].bundle
    idle,game_loop,game_core=(address(b,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine'))
    lag,regular=A.lag_pcs(seeds[1])
    stop=idle+12
    assert bytes(seeds[1][0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(seeds[1][idle+9:stop])==bytes((0x20,game_loop&255,game_loop>>8))
    cpu=A.CPU
    counts=Counter()
    nested={}
    min_sp=255

    def interrupt(c,kind,role,index):
        nonlocal min_sp
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
            min_sp=min(min_sp,c.sp)
            if kind=='lag_FF':
                assert c.pc!=regular
                visits+=c.pc==lag
                if index and not c.p&4:
                    key=A.tags(c),c.pc
                    if key not in nested or c.sp<nested[key].sp:
                        nested[key]=A.clone(c)
            assert m[c.pc],(kind,role,at,hex(c.pc))
            cpu.step(c)
        else:
            raise AssertionError(('Native interrupt did not return',kind,role,at))
        assert A.live(c)==before,(kind,role,at)
        assert visits==(kind=='lag_FF')
        assert N.get(m,'NmiSkipped')==(skipped+(kind=='lag_FF'))&255
        assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in m.writes[n:])
        counts[index,kind,role]+=1

    def complete(c):
        for _ in range(42000):
            if c.pc==stop:
                m=c.memory
                return A.final(c),bytes(m[0x300:0x4a0]),bytes(m[0x600:0x73f])
            assert c.memory[c.pc],hex(c.pc)
            cpu.step(c)
        raise AssertionError(('Native continuation did not return',hex(c.pc)))

    scenarios={}
    proto_lag=[]
    for label,owner,x,y,status,keys in (('MiniPeak',41,750,107,0,0xc1),
            ('MiniPowered',41,1513,135,2,0x41),('ForeignProto',2,750,107,0,0),
            ('ForeignMario',0,750,107,0,0),('ForeignSamus',6,750,107,0,0)):
        pair=[N.fork(seed) for seed in seeds]
        returns=[]
        paths=[]
        interrupted=[{},{}]
        for index,bus in enumerate(pair):
            F.setup(bus,x,y,0,0,actor=owner)
            N.put(bus,NmiDisable=255,PlayerStatus=status,SavedJoypadBits=keys,SavedJoypad1Bits=keys)
            entries={}
            visits=Counter()
            active=False

            class Trace(cpu):
                def step(self):
                    nonlocal active
                    tag,pc=A.tags(self),self.pc
                    if tag==254 and pc in (game_loop,game_core):
                        entries[pc]=self.sp
                    if tag==129 and pc==BOX_CALL:
                        active=True
                    if tag==129 and pc==BOX_RETURN:
                        assert active
                        active=False
                        visits['return']+=1
                    role=None
                    if active and tag in (247,248,253,255):
                        if 0xed7a<=pc<0xed8c or 0xedaa<=pc<0xedb1:
                            role='box_gate'
                        elif 0xed5b<=pc<0xed65:
                            role='shared_tail'
                    elif active and tag==129 and 0xb981<=pc<0xb990:
                        role='proto'
                    if role:
                        visits[role]+=1
                        if index or role=='proto':
                            for kind in ('IRQ','lag_FF'):
                                key=kind,role,tag,pc
                                if key in interrupted[index]:
                                    continue
                                fork=A.clone(self)
                                interrupt(fork,kind,role,index)
                                interrupted[index][key]=complete(fork)
                    return cpu.step(self)

            c=Trace(memory=bus,pc=idle)
            c.sp,c.p=255,0x31
            c.stPushWord(0xe33b)
            for _ in range(42000):
                if c.pc==stop:
                    break
                assert bus[c.pc],(label,hex(c.pc),bus.rawtags)
                c.step()
            else:
                raise AssertionError(('Native GameLoop did not return',label,hex(c.pc)))
            assert entries=={game_loop:250,game_core:248} and c.sp==252 and not active
            assert visits['return']==1,(label,visits)
            paths.append(dict(visits))
            returns.append(c)
        compare_memory(*pair)
        assert A.registers(returns[0])==A.registers(returns[1]),label
        old_paths,new_paths=paths
        expected=complete(returns[1])
        if owner==2:
            assert new_paths.get('proto',0)>0 and old_paths==new_paths
            assert interrupted[0] and interrupted[0]==interrupted[1],label
            assert complete(returns[0])==expected
            for (kind,_,_,pc),actual in interrupted[1].items():
                if actual!=expected:
                    assert kind=='lag_FF' and actual[0][:5]==expected[0][:5]
                    assert actual[0][6:]==expected[0][6:] and actual[1]==expected[1]
                    changes={}
                    for base,old,new in ((0x200,expected[0][5],actual[0][5]),(0x600,expected[2],actual[2])):
                        changes.update({hex(base+i):[u,v] for i,(u,v) in enumerate(zip(old,new,strict=True)) if u!=v})
                    proto_lag.append(dict(cut_PC=pc,observed_changes_from_uninterrupted=changes))
        else:
            assert all(result==expected for result in interrupted[1].values()),label
            if owner==41:
                assert new_paths.get('box_gate',0)>0 and not new_paths.get('shared_tail',0)
            elif owner==6:
                assert new_paths.get('shared_tail',0)>0
        scenarios[label]=dict(cycles_saved=returns[0].processorCycles-returns[1].processorCycles,
                old_visits=old_paths,new_visits=new_paths,baseline_resumed=len(interrupted[0]),
                candidate_resumed=len(interrupted[1]))
    for cut in nested.values():
        interrupt(cut,'nested_IRQ','lag_handler',1)
    assert min_sp>0x7a and nested and proto_lag
    return dict(scenarios=scenarios,min_ISR_SP=min_sp,exact_entries=dict(GameLoop=250,GameCoreRoutine=248),
                cuts={label:{kind:{role:n for (i,k,role),n in counts.items() if i==index and k==kind}
                             for kind in ('IRQ','lag_FF','nested_IRQ')}
                      for index,label in enumerate(('parent','candidate'))},
                inherited_Proto_FF_lag=proto_lag)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    path=out/'proof.json'
    proof=json.loads(path.read_text())
    assert proof['passed'] and proof['parent_SHA256']==PIN==sha(BASE)
    assert all(sha(Path(file))==digest for file,digest in proof['bindings'].items())
    raw=BASE.read_bytes()
    new=bytearray(raw)
    for row in proof['patches']:
        site=row['file_offset']
        old,patch=(bytes.fromhex(row[k]) for k in ('old_hex','new_hex'))
        assert len(old)==len(patch) and raw[site:site+len(old)]==old
        new[site:site+len(patch)]=patch
    digest=hashlib.sha256(new).hexdigest()
    assert digest==proof['expected_memory_only_SHA256'] and args.candidate.read_bytes()==new
    q=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
           memory_only_SHA256=digest,exact_disk_candidate=True,**check(raw,bytes(new)),
           bindings={str(p.resolve()):sha(p) for p in (Path(__file__),path,SOURCE,BASE,args.candidate)})
    (out/'irq.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))


if __name__=='__main__':
    main()
