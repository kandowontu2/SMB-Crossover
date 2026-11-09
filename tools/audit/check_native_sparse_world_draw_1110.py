"""Qualify sparse world rendering and the separate empty projectile CHR scan."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from check_mega_giant_compound_1110 import HOST, PIN, bundle, vector
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_visibility_dispatch_1110_v1 import memory
import check_native_firebar_admission_1110_v1 as Fire
import check_native_firebar_irq_1110_v1 as FireIRQ
import profile_mini_mario_matched_1110 as Match


R, P, N = Fire.R, Fire.P, Fire.N
SOURCE = R/'tools/reference/native_sparse_world_draw_1110.s'
STOP = 0x5b00
WORLD_LO, WORLD_HI = 0xa24b, 0xa276
SHOT_LO, SHOT_HI = 0xbc9a, 0xbcab
FIXED_LO, FIXED_HI = 0x85b2, 0x85b5
OLD_WORLD = bytes.fromhex('684a850b4a650b692c850ba9a36900850ca9f84cb585'
                          'a206b516c91b29dc4904d006cad0f34ca4be4c23ba')
OLD_SHOT = bytes.fromhex('c903f008c906d00ca908d002a900186970')
SHOT_WRITES = {0x689b, 0x014b, 0x0146}
SPECIAL_IDS = set(range(0x1b, 0x23)) | {0x2b, 0x2c}
NEW_FAST = Fire.FAST_IDS | set(range(0x1b))


def compose(raw, output):
    cfg_text = '''MEMORY {
    W:start=$a24b,size=$2b,file=%O;
    F:start=$85b2,size=3,file=%O;
    S:start=$bc9a,size=$11,file=%O;
}
SEGMENTS { WORLD:load=W,type=ro; FIXED:load=F,type=ro; SHOT:load=S,type=ro; }
'''
    with TemporaryDirectory(dir=output, prefix='sparse-link-') as directory:
        directory = Path(directory)
        cfg, obj, binary, lbl = (directory/f'world.{x}' for x in ('cfg','o','bin','lbl'))
        cfg.write_text(cfg_text)
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        code = binary.read_bytes()
        labels = {row.split()[2][1:]:int(row.split()[1],16) for row in lbl.read_text().splitlines()}
    assert labels == dict(LegacyTailClear=WORLD_LO, WorldFirebarAdmission=Fire.ENTRY, LegacyWorldDraw=0xa25d)
    spans = [(4, WORLD_LO, OLD_WORLD, code[:43]), (126, FIXED_LO, b'\xea'*3, code[43:46]),
             (78, SHOT_LO, OLD_SHOT, code[46:])]
    rows = []
    for bank, pc, old, new in spans:
        at = 16+8192*bank+(pc&8191)
        assert raw[at:at+len(old)] == old and len(new) == len(old)
        rows.append(dict(physical_PRG=bank, CPU_half_open=[pc, pc+len(old)],
                         file_offset=at, old_hex=old.hex(), new_hex=new.hex()))
    assert code[46:].hex() == 'f012c903f008c906d00aa978d002a970b8'
    bank4 = raw[16+8192*4:16+8192*5]
    assert [0xa000+i for i in range(8190) if bank4[i:i+3]==bytes.fromhex('2061a2')] == [0xa06d,0xa08d,0xa195,0xa1bf]
    assert bank4[0x237:0x239] == bytes.fromhex('f012')
    assert bank4[0x276:0x279] == bytes.fromhex('4c33bf')
    fixed_at = rows[1]['file_offset']
    assert raw[fixed_at-2:fixed_at+6] == bytes.fromhex('3860eaeaea20d085')
    fixed = raw[16+8192*126:16+8192*127]
    assert not any(fixed[i] in (0x20,0x4c) and fixed[i+1] in range(0xb2,0xb5)
                   and fixed[i+2]==0x85 for i in range(8190))
    return rows, labels


def bank_pc(cpu):
    return (cpu.memory.rawtags[(cpu.pc-0x8000)//8192],cpu.pc) if cpu.pc>=0x8000 else (-1,cpu.pc)


def tail(seed, offset, p, watch=None):
    m = slim_fork(seed)
    c = Fire.cpu_at(m,WORLD_LO,247,p,x=87,y=51)
    c.stPush(offset)
    run(c, lambda q:bank_pc(q)==(254,0x85b5), watch)
    return registers(c,0xef),bytes(m[0x0b:0x0d]),c.processorCycles


def world_leaf(old, new):
    seeds = [Fire.setup(b) for b in (old,new)]
    for n, flags in product(range(256),(0x20,0x61,0xa0,0xe5)):
        a,b = [tail(seed,n,flags) for seed in seeds]
        assert a[:2]==b[:2] and a[2]==b[2], (n,flags,a,b)
        assert a[1] == bytes(((n>>1)+(n>>2)+((n>>1)&1)+0x2c,0xa3))

    histories = Counter()

    def draw(m, role, expect_special=False):
        rows = [Fire.render(Fire.fork_image(m,b)) for b in (old,new)]
        a,b = rows
        ids = [N.get(m,'Enemy_ID',i) for i in range(6)]
        newly_fast = all(i in NEW_FAST for i in ids) and not all(i in Fire.FAST_IDS for i in ids)
        Fire.equal(a[0],b[0],newly_fast)
        if expect_special:
            assert a[0][3] and a[0][3]==b[0][3], (ids,a[0][3],b[0][3])
        histories[role,a[1]-b[1]] += 1

    for value, index, flag in product(range(256), range(6), (0,1,0x80)):
        m = Fire.setup(old)
        Fire.slot(m,'Enemy_ID',index,value)
        Fire.slot(m,'Enemy_Flag',index,flag)
        draw(m,'all_IDs_and_slots')
    for value, index in product(sorted(SPECIAL_IDS), (1,4)):
        draw(Fire.positive_seed(old,value,index),'actual_firebar' if value<0x23 else 'actual_small_lift',True)
    for values, role in (((0,)*6,'empty'), ((6,0,0,0,0,0),'one_Goomba'), ((0x25,)*6,'six_lifts'),
                         ((6,6,6,0x25,0x25,0x25),'three_Goombas_three_lifts')):
        m = Fire.setup(old)
        for i, value in enumerate(values):
            Fire.slot(m,'Enemy_ID',i,value)
            Fire.slot(m,'Enemy_Flag',i,int(value!=0))
        draw(m,role)
    assert not SPECIAL_IDS & NEW_FAST
    return dict(offset_tail_cases=1024,draw_pairs=sum(histories.values()),
                timings=[[role,cycle,count] for (role,cycle),count in sorted(histories.items())])


def cold(image, raw, rogue=False):
    m = N.fresh(image)
    N.put(m,CrossoverMenuIndex=raw)
    for entry in ('MenuResolveCharacter','QueueSelection','DrawSelectionPreview'):
        N.invoke(m,entry)
    if rogue:
        Match.menu_key(m,32)
    assert N.get(m,'SelectedCharacter')==raw and bool(m[0x5fee])==rogue, (raw,m[0x5fee])
    start = Match.menu_key(m,16)
    N.invoke(m,'ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(600):
        if (N.get(m,'OperMode_Task'),N.get(m,'GameEngineSubroutine'))==(3,8):
            return m
        Match.controls(m,0)
        N.invoke(m,'GameLoop',x=0,y=0)
        N.consume(m)
    raise AssertionError(('Cold owner did not enter 1-1',raw,rogue))


def without_world_transport(writes):
    start = [(0x16a,0),(0x16c,1),(0x16d,0xad),(0x162,199),(0x145,199),(0x5115,199)]
    cleaned = []
    i = 0
    while i < len(writes):
        if writes[i:i+len(start)]==start:
            end = i+len(start)
            assert writes[end:end+1] == [(0x7eb4,255)]
            assert writes[end+1][0]==0x179 and writes[end+2:end+4]==[(0x145,132),(0x5115,132)]
            cleaned.append(writes[end]); i = end+4
        else:
            cleaned.append(writes[i]); i += 1
    return cleaned


def play(seed, key, witness=None):
    Match.controls(seed,key)
    seed.writes.clear()
    seed.ram_writes.clear()
    c = Fire.cpu_at(seed,P.address(seed.bundle,'GameLoop'),252,0x21,x=0,y=0)
    run(c,lambda q:(q.pc,q.sp)==(STOP,252),witness)
    writes = [(addr,val) for addr,val in seed.writes if not 0x17b<=addr<0x200]
    return registers(c,0xef),memory(seed),writes,tuple(seed.ram_writes),c.processorCycles


def whole(before, after):
    images = [bundle(x) for x in (before,after)]
    results = []
    for owner, rogue in ((0,False),(2,False),(2,True),(3,False)):
        scenes = [cold(b,owner,rogue) for b in images]
        for role, key, frames in (('opening_idle',0,24),('first_enemy_walk',1,112)):
            hist = Counter()
            for _ in range(frames):
                a,b = [play(m,key) for m in scenes]
                assert a[:2] == b[:2] and a[3]==b[3], (owner,rogue,role,a[0],b[0])
                assert a[2]==b[2] or without_world_transport(a[2])==b[2],(owner,rogue,role)
                hist[a[4]-b[4]] += 1
                for m in scenes:
                    N.consume(m)
            results.append(dict(owner=owner,rogue=rogue,role=role,updates=frames,cycles_saved=dict(hist)))
    return results


def shots(before, after):
    images = [bundle(x) for x in (before,after)]
    tests = set(product((0,3,6,11),repeat=4))
    for slot, value in product(range(4),range(256)):
        for fill in (0,3,6):
            pattern = [fill]*4
            pattern[slot] = value
            tests.add(tuple(pattern))
    # This leaf has no bank call; use the actual linked instructions with
    # an ordered write observer. Hardware-vector coverage uses the full bus.
    class Trace(list):
        def __setitem__(self, address, value):
            if address in SHOT_WRITES:
                self.writes.append((address,value))
            super().__setitem__(address,value)

    memories = [Trace(b'\0'*65536) for _ in images]
    for m,b in zip(memories,images,strict=True):
        at = 16+78*8192
        m.writes = []
        m[0xa000:0xc000] = b['raw'][at:at+8192]
    hist = Counter()
    for values, current in product(sorted(tests),(0x17,0x71,0x79,0xff)):
        rows = []
        for m in memories:
            m[0x601f:0x6023] = values
            m[0x014b],m[0x0146] = current,0xff
            m.writes.clear()
            c = Fire.cpu_at(m,0xbc90,240,0xe1,x=27,y=75)
            run(c,lambda q:(q.pc,q.sp)==(STOP,240))
            rows.append((registers(c,0xef),tuple(m.writes),c.processorCycles))
        a,b = rows
        assert a[:2]==b[:2],(values,current,a,b)
        hist[values.count(0),a[2]-b[2]] += 1
    return dict(pairs=sum(hist.values()),timings=[[zero,delta,n] for (zero,delta),n in sorted(hist.items())])


def vectors(before, after, component):
    old,new = [bundle(x) for x in (before,after)]
    results = Counter()
    sites = set()
    minimum = 255

    def watch(c):
        nonlocal minimum
        tag,pc = bank_pc(c)
        if component=='shot':
            reached = tag==206 and 0xbc97<=pc<=0xbcc6
        else:
            reached = (tag==132 and WORLD_LO<=pc<WORLD_HI) or (tag==254 and FIXED_LO<=pc<=FIXED_HI)
        if not reached or (tag,pc,c.sp) in seen:
            return
        seen.add((tag,pc,c.sp))
        sites.add((tag,pc))
        minimum = min(minimum,c.sp)
        for kind in ('lag','irq'):
            if kind=='irq' and c.p&4:
                continue
            pair = []
            for image in (old,new):
                m = slim_fork(c.memory)
                m.bundle = image
                for win, rawtag in enumerate(m.rawtags):
                    m.raw_page(win,rawtag)
                q = N.NesMPU(memory=m,pc=c.pc)
                q.a,q.x,q.y,q.p,q.sp = registers(c)
                vector(q,kind)
                pair.append((memory(m),m.writes,m.ram_writes,q.processorCycles))
            assert pair[0]==pair[1], (component,kind,tag,hex(pc),c.sp)
            results[kind] += 1

    for owner in (0,2,3,9,41):
        for pattern in ((0,)*6,(6,0,0,0,0,0),(0x25,)*6,(6,0x25,0x1b,0x2b,0,0)):
            m = Fire.setup(new)
            N.put(m,SelectedCharacter=owner,GuestAudioCharacter=owner)
            seen = set()
            if component=='world':
                for index, value in enumerate(pattern):
                    Fire.slot(m,'Enemy_ID',index,value)
                    Fire.slot(m,'Enemy_Flag',index,int(value!=0))
                Fire.render(m,visit=watch)
                tail(m,0x84,0x21,watch)
            else:
                m.raw_page(1,206)
                N.put(m,CurrentBank=206)
                m[0x601f:0x6023] = tuple(value%7 for value in pattern[:4])
                c = Fire.cpu_at(m,0xbc90,236,0x21)
                run(c,lambda q:(q.pc,q.sp)==(STOP,236),watch)
    assert results['lag'] and results['irq'] and minimum>0x7a
    return dict(cuts=dict(results),sites=[[tag,pc] for tag,pc in sorted(sites)],min_SP=minimum)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--rom',type=Path,default=HOST)
    args = cli.parse_args()
    raw = args.rom.read_bytes()
    assert P.sha(raw)==PIN
    args.output.mkdir(exist_ok=True)
    rows, labels = compose(raw,args.output)
    for name, patches in (('shot',rows[2:]),('world',rows[:2])):
        candidate = install(raw,patches)
        report = shots(raw,candidate) if name=='shot' else world_leaf(bundle(raw),bundle(candidate))
        print(name,'leaf',report,flush=True)
        v = vectors(raw,candidate,name)
        print(name,'vector',v['cuts'],flush=True)
        result = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(candidate),
                      patches=patches,foreground=report,vectors=v,
                      bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),SOURCE,args.rom,
                                R/'src/metasprite_engine.s',R/'src/roll_shot_bank.inc',
                                R/'src/z2_platform_late_render.s',R/'src/z2_platform_late_legacy.inc',
                                R/'src/world_firebars.s',Path(Fire.__file__),Path(FireIRQ.__file__))})
        if name=='world':
            result.update(symbols=labels,whole=whole(raw,candidate))
        (args.output/f'{name}.json').write_text(json.dumps(result,indent=2)+'\n')
        print(name,result['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
