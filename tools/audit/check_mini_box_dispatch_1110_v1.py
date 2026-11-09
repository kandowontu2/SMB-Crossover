"""Check the exact Mini box-control shortcut and its native interrupt seams."""

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_floor_pair_fast_1108_v1 as F
import check_mini_lift_admission_async_1108_v1 as A
from check_mini_adder_current_async_1110_v1 import CANDIDATE as PIN
from check_mini_native_side_single_map_1109_v1 import N, R, locations, offset, sha
from prepare_mini_mario_native_power_1103_v56 import address, bundle
from prepare_mini_side_alias_1108 import compare_memory


BASE=R/'build/mini-current-peak-1110/adder/candidate.nes'
SOURCE=R/'tools/reference/mini_native_collision_box_1110_v1.s'
MIRRORS=(119,120,125,127)
SPANS=(('BOX_GATE',0xed7a,'8d6a01a90c8d6c01a9af8d6d01a9e24c5a01'),
       ('BOX_MINI',0xedaa,'ea'*7))
BOX_CALL=0xa12b
BOX_RETURN=0xa12e


def assemble(out,raw):
    assert locations(raw,'4c7aed')==[offset(126,0x8fdd)] and not locations(raw,'207aed')
    assert not locations(raw,'4caaed') and not locations(raw,'20aaed')
    assert raw[offset(126,0x8fd6):offset(126,0x8fe0)]==bytes.fromhex('ad0260c90690034c7aed')
    assert raw[offset(1,0xa127):offset(1,0xa131)]==bytes.fromhex('ad0260ea2078b98c4506')
    assert raw[offset(1,0xb978):offset(1,0xb991)]==bytes.fromhex('c902f0054cd68feaeaa9e68d6c01a9b58d6d01a9df4c5a01ea')
    for bank in MIRRORS:
        assert raw[offset(bank,0xed5b):offset(bank,0xed65)]==bytes.fromhex('a9af8d6d01a9e24c5a01')
        assert raw[offset(bank,0xeda7):offset(bank,0xeda7)+13]==bytes.fromhex('4c1c90eaeaeaeaeaeaea8d6a01')
    with tempfile.TemporaryDirectory(prefix='asm-',dir=out) as work:
        work=Path(work)
        cfg,obj,binary=(work/f'box.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY {\n'+''.join(
            f'{name}:start=${pc:04x},size={len(old)//2},file=%O;\n'
            for name,pc,old in SPANS)+'}\nSEGMENTS {\n'+''.join(
            f'{name}:load={name},type=ro;\n' for name,*_ in SPANS)+'}\n')
        cc=R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
        code=binary.read_bytes()
    assert len(code)==25
    patches=[]
    after=bytearray(raw)
    start=0
    for _,pc,old in SPANS:
        size=len(old)//2
        new=code[start:start+size]
        start+=size
        for bank in MIRRORS:
            site=offset(bank,pc)
            assert raw[site:site+size].hex()==old,(bank,pc)
            after[site:site+size]=new
            patches.append(dict(bank=bank,pc=pc,file_offset=site,old_hex=old,new_hex=new.hex()))
    return bytes(after),patches


def drive_box(bus,x,y,p):
    c=N.NesMPU(memory=bus,pc=0xa127)
    c.a,c.x,c.y,c.p,c.sp=0x95,x,y,p,230
    visited=Counter()
    for _ in range(5000):
        if c.pc==BOX_RETURN and A.tags(c)==129:
            break
        assert bus[c.pc],(hex(c.pc),bus.rawtags)
        visited[A.tags(c),c.pc]+=1
        c.step()
    else:
        raise AssertionError(('Box-control caller did not return',hex(c.pc)))
    assert c.sp==230 and visited[129,BOX_CALL]==1
    return A.registers(c),c.processorCycles,visited


def measure_leaves(old,new):
    seeds=[N.fresh(bundle(raw)) for raw in (old,new)]
    costs=defaultdict(list)
    for owner,engine,(x,y,p),bank in product(range(43),(4,8),
            ((0,0,0x20),(1,1,0x61),(5,2,0x24)),MIRRORS):
        pair=[N.fork(m) for m in seeds]
        returns=[]
        for m in pair:
            N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,PlayerStatus=y&1,
                  PlayerSize=y&1,Player_State=x&3,CrouchingFlag=y>>1,CurrentBank=129)
            m[0x5115]=129
            m[0x5117]=bank|128
            returns.append(drive_box(m,x,y,p))
        assert returns[0][0]==returns[1][0],(owner,engine,x,y,p,bank,returns[0][0],returns[1][0])
        compare_memory(*pair)
        if owner==2:
            assert all(trace[129,0xb981]==1 and not trace[bank|128,0xed7a] for _,_,trace in returns)
            assert returns[0][1]==returns[1][1]
        elif owner==41:
            assert returns[0][2][212,0xb447]==1 and returns[1][2][bank|128,0xedaa]==1
            assert not returns[1][2][212,0xb447] and returns[1][0][3]==1
        costs[owner].append(returns[0][1]-returns[1][1])
    assert min(costs[41])>150
    return {owner:dict(cases=len(values),cycles_saved=[min(values),max(values)]) for owner,values in costs.items()}


def check_game_loop(old,new):
    seeds=[F.F.fixture(bundle(raw),0,False,False) for raw in (old,new)]
    b=seeds[1].bundle
    idle,game_loop,game_core=(address(b,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine'))
    lag,regular=A.lag_pcs(seeds[1])
    stop=idle+12
    assert bytes(seeds[1][0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(seeds[1][idle+9:stop])==bytes((0x20,game_loop&255,game_loop>>8))
    counts=Counter()
    nested={}
    min_sp=255
    cpu=A.CPU

    def interrupt(c,kind,role):
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
                if not c.p&4:
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
        counts[kind,role]+=1

    def finish(c):
        for _ in range(42000):
            if c.pc==stop:
                m=c.memory
                return A.final(c),bytes(m[0x300:0x4a0]),bytes(m[0x600:0x73f])
            assert c.memory[c.pc],hex(c.pc)
            cpu.step(c)
        raise AssertionError(('Native continuation did not return',hex(c.pc)))

    summaries={}
    for label,owner,x,y,status,keys in (('MiniPeak',41,750,107,0,0xc1),
            ('MiniPowered',41,1513,135,2,0x41),('ForeignProto',2,750,107,0,0),
            ('ForeignMario',0,750,107,0,0),('ForeignSamus',6,750,107,0,0)):
        pair=[N.fork(seed) for seed in seeds]
        returns=[]
        records=[]
        resumes=[]
        for index,bus in enumerate(pair):
            F.setup(bus,x,y,0,0,actor=owner)
            N.put(bus,NmiDisable=255,PlayerStatus=status,SavedJoypadBits=keys,SavedJoypad1Bits=keys)
            entries={}
            reached=set()
            visits=Counter()
            owned=[False]

            class Trace(cpu):
                def step(self):
                    tag,pc=A.tags(self),self.pc
                    if tag==254 and pc in (game_loop,game_core):
                        entries[pc]=self.sp
                    if tag==129 and pc==BOX_CALL:
                        owned[0]=True
                    if tag==129 and pc==BOX_RETURN:
                        assert owned[0]
                        owned[0]=False
                        visits['return']+=1
                    role=None
                    if owned[0] and tag in (247,248,253,255):
                        if 0xed7a<=pc<0xed8c or 0xedaa<=pc<0xedb1:
                            role='box_gate'
                        elif 0xed5b<=pc<0xed65:
                            role='shared_tail'
                    elif owned[0] and tag==129 and 0xb981<=pc<0xb990:
                        role='proto'
                    if role:
                        visits[role]+=1
                        if index and (tag,pc) not in reached:
                            reached.add((tag,pc))
                            for kind in ('IRQ','lag_FF'):
                                fork=A.clone(self)
                                interrupt(fork,kind,role)
                                resumes.append(fork)
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
            assert entries=={game_loop:250,game_core:248} and c.sp==252 and not owned[0]
            assert visits['return']==1,(label,visits)
            records.append(dict(visits))
            returns.append(c)
        compare_memory(*pair)
        assert A.registers(returns[0])==A.registers(returns[1]),label
        old_counts,new_counts=records
        if owner==2:
            assert new_counts.get('proto',0)>0 and old_counts==new_counts and len(resumes)>0
        elif owner==41:
            assert new_counts.get('box_gate',0)>0 and not new_counts.get('shared_tail',0)
        elif owner==6:
            assert new_counts.get('shared_tail',0)>0
        expect=finish(returns[1])
        assert all(finish(fork)==expect for fork in resumes),(label,'Complete interrupt continuation')
        summaries[label]=dict(cycles_saved=returns[0].processorCycles-returns[1].processorCycles,
                              old_visits=old_counts,new_visits=new_counts,resumed=len(resumes))
    for cut in nested.values():
        interrupt(cut,'nested_IRQ','lag_handler')
    assert min_sp>0x7a and nested
    return dict(scenarios=summaries,min_ISR_SP=min_sp,exact_entries=dict(GameLoop=250,GameCoreRoutine=248),
                cuts={kind:{role:n for (k,role),n in counts.items() if k==kind}
                      for kind in ('IRQ','lag_FF','nested_IRQ')})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    raw=BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==PIN
    out.mkdir(exist_ok=True)
    new,patches=assemble(out,raw)
    cases=measure_leaves(raw,new)
    digest=hashlib.sha256(new).hexdigest()
    paths=(Path(__file__),SOURCE,BASE,R/'src/expanded.s',R/'src/player.s',
           R/'tools/reference/mini_mario_direct_native_1103.s',Path(F.__file__),Path(A.__file__))
    proof=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=digest,ROM_written=False,
               source_CPU_only=True,patches=patches,cases=cases,
               funding='All four resident E mirrors. ED7A native box veneer, EDAA seven source-owned post-JMP EAs after Cv3BoxOther. ED5B exact shared native tail.',
               bindings={str(path):sha(path) for path in paths})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,candidate=digest,Mini=cases[41],Proto=cases[2])),flush=True)
    irq=dict(passed=True,parent_SHA256=PIN,memory_only_SHA256=digest,source_CPU_only=True,
             ROM_written=False,**check_game_loop(raw,new),
             proof_SHA256=sha(out/'proof.json'))
    (out/'irq.json').write_text(json.dumps(irq,indent=2)+'\n')
    print(json.dumps(irq))


if __name__=='__main__':
    main()
