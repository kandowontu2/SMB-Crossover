"""Qualify same-footprint inlines of Mini's existing mapper-store pairs."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_movement_prefix_1110 as M
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at, lag_pcs


P, N, Q, D, R = M.P, M.N, M.Q, M.D, M.R
BASE, PIN, STOP = M.BASE, M.PIN, M.STOP
SOURCE = R / 'tools/reference/mini_box_map_inline_1110.s'
PROFILE = R / 'build/mini-seven-lift-edge-profile-1110/capture/instruction-sample.json'
SPANS = (
    ('BANK_GATE', 85, 0xa8dc, bytes.fromhex('ada17d48a902207cb0a50ef00dcdf0c3d008206bb090034cf0b8184c7bb0') + b'\xff'*6),
    ('BANK_CODE_HEADER', 85, 0xb8f0, bytes.fromhex('a903207cb0206bb04c7bb0') + b'\xff'*5),
    ('RESTORE86', 86, 0xa521, bytes.fromhex('6820c280ad790160') + b'\xea'*4),
)
ENTRANCE = (221, 0xa703)
STATE_MAP, CODE_MAP, FINAL_RESTORE = ((bank | 128, pc) for _, bank, pc, _ in SPANS)
VENEER, FULL_BOX, SOURCE_BOX = (213, 0xb0bc), (193, 0xb0bc), (3, 0xa030)
MODES = ('warm', 'epoch_zero', 'epoch_stale', 'state_marker', 'state_owner',
         'code_marker', 'code_owner', 'state_digest', 'code_digest')


def link(raw, output):
    assert P.sha(raw) == PIN
    producer = (R / 'tools/audit/build_mini_idle_fast.py').read_text()
    assert "('BANK_GATE', 85, 0xa8dc, 36, 0xff)" in producer
    assert "('BANK_CODE_HEADER', 85, 0xb8f0, 16, 0xff)" in producer
    old_auth = (R / 'tools/reference/mini_mario_idle_fast.s').read_text()
    old_box = (R / 'tools/reference/mini_box_transport_1110_v1.s').read_text()
    assert old_auth.count('jsr MapC') == 2
    assert 'pla\n    jsr MapC\n    lda ReturnA\n    rts\n    .res 12-(*-MiniBoxRestore),$ea' in old_box
    D.check_span(raw, 85, 0xb06b, bytes.fromhex('ade0dfc9a7d007ade1dfc929f0011860688da17d8d165160'))
    D.check_span(raw, 85, 0xb08c, bytes.fromhex('4cdca8')*38)
    D.check_span(raw, 126, 0x80c2, bytes.fromhex('8da17d8d165160'))
    D.check_span(raw, 86, 0xa36a, bytes.fromhex('a9d5205a01b0034c54a428ada17d48a90220c280a9308d6c01a9a08d6d01a903205a014c21a5'))
    D.check_span(raw, 86, 0xa51e, bytes.fromhex('4c2da5'))
    for _, bank, pc, old in SPANS:
        D.check_span(raw, bank, pc, old)
        page = raw[D.offset(bank, 0xa000):D.offset(bank, 0xa000)+8192]
        assert all(not any(bytes((op, dest & 255, dest >> 8)) in page for op in (0x20, 0x4c, 0x6c))
                   for dest in range(pc+1, pc+len(old)))
    cc = R / 'tools/Windows/cc65/bin'
    with tempfile.TemporaryDirectory(prefix='map-inline-', dir=output) as folder:
        t = Path(folder)
        cfg, obj, binary = (t / f'mapper.{ext}' for ext in ('cfg', 'o', 'bin'))
        cfg.write_text('MEMORY {\n'+''.join(f'{name}:start=${pc:x},size={len(old)},file=%O;\n'
            for name, _, pc, old in SPANS)+'}\nSEGMENTS {\n'+''.join(f'{name}:load={name},type=ro;\n'
            for name, *_ in SPANS)+'}\n')
        subprocess.run([cc/'ca65.exe', SOURCE, '-o', obj], check=True)
        subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
        code = binary.read_bytes()
    rows, at = [], 0
    for _, bank, pc, old in SPANS:
        rows.append(M.patch(bank, pc, old, code[at:at+len(old)]))
        at += len(old)
    assert at == len(code) == 64
    return install(raw, rows), rows


def poison(m, mode):
    frame = N.get(m, 'FrameCounter')
    m.ram[2][0x3f0] = frame
    if mode == 'epoch_zero':
        N.put(m, FrameCounter=0)
        m.ram[2][0x3f0] = 0
    elif mode == 'epoch_stale':
        m.ram[2][0x3f0] ^= 1
    elif mode != 'warm':
        bank, key = mode.split('_')
        m.ram[2 if bank == 'state' else 3][0x1fe0+('marker', 'owner', 'digest').index(key)] ^= 1


def make_cpu(seed, tag, pc, mode, old_c, flags):
    m = slim_fork(seed)
    m.raw_page(1, tag)
    m.raw_page(2, old_c)
    N.put(m, CurrentBank=tag, CurrentBankC=old_c, NmiDisable=255, FrameCounter=7)
    poison(m, mode)
    m[0x16a] = 0x61
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    c = cpu_at(m, pc, 232, flags, x=0, y=91)
    c.a = 0x61
    return c


def ingress_cases(seeds):
    rows = Counter()
    done = lambda q:(q.pc,q.sp)==(STOP,232)
    for index, mode, old_c, flags in product(range(38), MODES, (2,3,0x82), (0x21,0x65)):
        pair = [make_cpu(m, 213, 0xb08c+index*3, mode, old_c, flags) for m in seeds[41]]
        for c in pair:
            run(c, done)
        a,b = pair
        assert M.snapshot(a)==M.snapshot(b), (index,mode,old_c,flags)
        hits = mode in ('warm','state_digest','code_digest')
        assert bool(a.p&1)==hits and a.a==old_c and a.memory.rawtags[2]==old_c
        saving = a.processorCycles-b.processorCycles
        assert saving == (24 if hits or mode.startswith('code_') else 12)
        rows['D5',mode,saving] += 1
    for mode,old_c,flags in product(MODES,(2,3,0x82),(0x21,0x65)):
        pair = [make_cpu(m, 129, 0xb969, mode, old_c, flags) for m in seeds[41]]
        paths = []
        for c in pair:
            seen = Counter()
            run(c, done, lambda z:seen.update((D.bank_pc(z),)))
            paths.append(seen)
        a,b = pair
        watched = {ENTRANCE, VENEER, FULL_BOX, SOURCE_BOX, (214,0xa000), (254,0x9f4e)}
        assert all(paths[0][pc]==paths[1][pc] for pc in watched)
        assert {ENTRANCE,VENEER,(214,0xa000)} <= paths[0].keys()
        assert M.snapshot(a)==M.snapshot(b), (mode,old_c,flags)
        saving = a.processorCycles-b.processorCycles
        inlines = (STATE_MAP,CODE_MAP,FINAL_RESTORE)
        assert all(paths[0][pc]==paths[1][pc] for pc in inlines)
        assert saving==12*sum(paths[0][pc] for pc in inlines), (mode,old_c,flags,saving,paths)
        rows['box',mode,saving] += 1
    return [[*key,count] for key,count in sorted(rows.items())]


def whole(before, after):
    return M.whole(before, after)


def vectors(before, after):
    images = [P.bundle(raw) for raw in (before, after)]
    seeds = M.cold_seeds(before, after)
    scene = Q.read_scene(PROFILE)
    lag, normal = lag_pcs(seeds[41][1])
    counts, deepest, sites = Counter(), {}, set()
    minima = [255,255]

    def interrupt(c, q, kind, record=False):
        m = q.memory
        before_regs = registers(q,0xef), live_stack(q), bytes(m[0x15a:0x17b]), bytes(m[:11])
        before_maps = tuple(m.rawtags)
        skipped = N.get(m,'NmiSkipped')
        m.vector_floor, m.written_stack = 0x100+q.sp, set()
        if kind == 'IRQ':
            assert not q.p&4
            q.irq()
            assert D.bank_pc(q)==(254,0x8000)
        else:
            assert N.get(m,'NmiDisable')==(255 if kind=='FF' else 0)
            q.nmi()
        hits = Counter()

        def inspect(z):
            minima[1] = min(minima[1],z.sp)
            if z.pc in (lag,normal):
                hits[z.pc] += 1
            key = tuple(m.rawtags), z.pc
            if record and kind=='FF' and not z.p&4 and (key not in deepest or z.sp<deepest[key].sp):
                deepest[key] = fork(z)
                deepest[key].memory.vector_floor = None

        run(q,lambda z:(z.pc,z.sp)==(c.pc,c.sp),inspect)
        m.vector_floor = None
        assert before_regs==(registers(q,0xef),live_stack(q),bytes(m[0x15a:0x17b]),bytes(m[:11]))
        assert hits[lag]==int(kind=='FF') and hits[normal]==int(kind=='normal')
        assert N.get(m,'NmiSkipped')==(skipped+int(kind=='FF'))&255
        if tuple(m.rawtags) != before_maps:
            # An NMI can commit the shadow value while the next instruction
            # is the matching bus store. Check the actual interrupted code.
            assert kind!='IRQ' and bytes(c.memory[c.pc-3:c.pc+3])==bytes.fromhex('8da17d8d1651')
            assert tuple(m.rawtags)==before_maps[:2]+(c.a,)+before_maps[3:]
            assert m[0x7da1]==c.a
            counts['early_C_commit',kind] += 1

    def replay(c, kind, side, record=False):
        q = fork(c,images[side])
        m = q.memory
        if kind=='normal':
            N.put(m,NmiDisable=0)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        interrupt(c,q,kind,record)
        return q

    def same_cut(c, side, kind, record=False):
        a,b = [replay(c,kind,i,record and i==side) for i in (0,1)]
        assert M.snapshot(a)==M.snapshot(b) and a.processorCycles==b.processorCycles, (kind,D.bank_pc(c),side)

    def watch(c, side, seen):
        tag,pc = D.bank_pc(c)
        if not any(tag==bank|128 and start<=pc<start+len(old) for _,bank,start,old in SPANS):
            if (tag,pc) not in ((213,0xb07c),(213,0xb07f),(254,0x80c2),(254,0x80c5)):
                return
        key = tag,pc,c.sp,c.p&5,tuple(c.memory.rawtags)
        if key in seen:
            return
        seen.add(key)
        sites.add((side,tag,pc))
        minima[0] = min(minima[0],c.sp)
        same_cut(c,side,'FF',record=True)
        counts['same_cut','FF'] += 1
        if not c.p&4:
            same_cut(c,side,'IRQ')
            counts['same_cut','IRQ'] += 1

    def frame(seed, mode):
        c = Q.Edge.prepare(seed,scene,False)
        N.put(c.memory,NmiDisable=255)
        run(c,lambda z:D.bank_pc(z)==ENTRANCE)
        poison(c.memory,mode)
        return c

    for side,mode in product((0,1),MODES):
        c = frame(seeds[41][side],mode)
        seen = set()
        run(c,Q.at_end,lambda z:watch(z,side,seen))
        assert any((tag,pc)==STATE_MAP for tag,pc,*_ in seen)
        assert any((tag,pc)==CODE_MAP for tag,pc,*_ in seen)==(mode.startswith('code_') or mode in ('warm','state_digest'))
        assert any((tag,pc)==FINAL_RESTORE for tag,pc,*_ in seen)==(mode in ('warm','state_digest','code_digest'))

    # Pair the equivalent shadow/bus boundaries even though the old calls
    # hold a local JSR return address and the new inline does not.
    bus_points = (
        ((213,0xb07f,0xa8e4),(213,0xa8e5,None)),
        ((213,0xb07f,0xb8f4),(213,0xb8f5,None)),
        ((254,0x80c5,0xa524),(214,0xa525,None)),
    )

    def seek(c, point):
        tag,pc,caller = point
        def match(z):
            if D.bank_pc(z)!=(tag,pc):
                return False
            m = z.memory
            return caller is None or m[0x101+z.sp]+256*m[0x102+z.sp]==caller
        run(c,match)

    for pair_points,kind in product(bus_points,('FF','normal','IRQ')):
        pair = [frame(seed,'warm') for seed in seeds[41]]
        for c,point in zip(pair,pair_points,strict=True):
            seek(c,point)
        resumes = [replay(c,kind,side) for side,c in enumerate(pair)]
        assert M.IRQ.hardware(resumes[0])==M.IRQ.hardware(resumes[1]),(pair_points,kind)
        Q.through_frame(*resumes)
        counts['paired_bus_resume',kind] += 1

    for c in deepest.values():
        same_cut(c,0,'IRQ')
        counts['nested','IRQ'] += 1
    assert all(counts[key] for key in (('same_cut','FF'),('same_cut','IRQ'),('nested','IRQ'),
                                      ('early_C_commit','FF'),('paired_bus_resume','normal')))
    assert minima[1]>0x7a
    return dict(cuts=[[a,b,count] for (a,b),count in sorted(counts.items())],
                foreground_sites=sorted(sites),minimum_SP=minima,actual_lag_PC=lag,actual_normal_NMI_PC=normal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--vectors-only',action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build')
    out.mkdir(exist_ok=True)
    before = BASE.read_bytes()
    assert P.sha(before)==PIN
    proof = out/'proof.json'
    if args.vectors_only:
        result = json.loads(proof.read_text())
        assert result['passed'] and result['parent_SHA256']==PIN and not (out/'irq.json').exists()
        for path,digest in result['bindings'].items():
            assert P.sha(Path(path).read_bytes())==digest,path
        after = install(before,result['patches'])
        assert P.sha(after)==result['expected_memory_only_SHA256']
        result = vectors(before,after)
        target,refs = out/'irq.json',(Path(__file__),proof,R/'src/reset.s',PROFILE)
    else:
        assert not proof.exists()
        after,rows = link(before,out)
        result = dict(patches=rows,ingress=ingress_cases(M.cold_seeds(before,after)))
        print('All D5 entries and native Mini box cases passed.',flush=True)
        result['whole_GameLoop'] = whole(before,after)
        target,refs = proof,(Path(__file__),SOURCE,PROFILE,M.KERNEL,
                            R/'tools/reference/mini_mario_idle_fast.s',R/'tools/reference/mini_box_transport_1110_v1.s')
    result.update(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(target,result['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
