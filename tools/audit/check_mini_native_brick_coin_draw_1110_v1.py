"""Qualify the two observed native static descriptors and reclaim their bank4 backing."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at
from check_mini_visibility_dispatch_1110_v1 import memory
from measure_mini_shared_offscreen_1110_v1 import N, P, PIN, R, ROM


SOURCE = R / 'tools/reference/mini_native_brick_coin_draw_1110_v1.s'
SAMPLE = R / 'build/mini-final-peak-detail-1110/capture/instruction-sample.json'
DRAW_ENTRY, DEATH_ENTRY, RECLAIM, RECLAIM_END = 0xbe92, 0xb897, 0xbae0, 0xbb89
STOP = 0x5b00
BRICK, COIN = 0xadec, 0xadae
OLD_GENERIC = bytes.fromhex('aede06ad0b6cf0068a186d086caa981012')
NEW_GENERIC = bytes.fromhex('ad0b6cf0058a6d086caa9810164ce9a5ea')
OLD_GUARD = bytes.fromhex('a504c9aff0034cbaa5a503c92ff00cc938f008c941f004c94ad0eba508d0e7a50ac901d0e1'
                          'a507c9f8b0dba509c9f8b0d5')
NEW_GUARD = bytes.fromhex('a50429fdc9add0344ce0bac92ff00cc938f008c941f004c94ad021a508d01da50ac901d017'
                          'a507c9f8b011a509c9f8b00b')


def offset(pc):
    return 16 + 4 * 8192 + (pc & 8191)


def preimage(raw, pc, old):
    at = offset(pc)
    assert raw[at:at + len(old)] == old, (hex(pc), raw[at:at + len(old)].hex(), old.hex())
    return at


def compose(raw, out):
    for pc, descriptor in ((BRICK, '086200000062000008'), (COIN, '046c020800')):
        preimage(raw, pc, bytes.fromhex(descriptor))
    table = bytes([0]) * 128 + bytes([1]) * 41
    preimage(raw, RECLAIM, table)
    assert all((5 + max(0, age - 18) * 55 // 24) >> 8 == v for age, v in enumerate(table))
    assert table[:87] == bytes(87)
    bank4 = raw[offset(0xa000):offset(0xa000)+8192]
    assert bank4.count(bytes.fromhex('b9e0ba')) == 1
    preimage(raw,0xbf77,bytes.fromhex('4c22a4')+bytes([0xea])*12)
    preimage(raw,0xbece,bytes.fromhex('4cbaa5'))
    rejected_edges = []
    for i in range(len(bank4)-2):
        op, rel = bank4[i:i+2]
        if op in (0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
            pc = 0xa000+i
            if pc+2+(rel if rel<128 else rel-256)==0xbe98:
                rejected_edges.append(pc)
    assert rejected_edges == [0xbeab,0xbeaf,0xbeb5,0xbebb,0xbec1]
    # Only the entry sequence uses the second cursor load. All published
    # renderer dispatch/loop/reject/finish addresses stay fixed. BCS at
    # $A5D6 also proves the carry input to the optional rotation ADC.
    preimage(raw,0xa5d1,bytes.fromhex('98186dde06b0f2'))
    for pc in range(0xa5d8, 0xa5e9):
        assert not any(bank4.startswith(bytes((op, pc & 255, pc >> 8)), i)
                       for i in range(len(bank4)-2) for op in (0x20, 0x4c)), hex(pc)
    with tempfile.TemporaryDirectory(prefix='static-draw-', dir=out) as folder:
        tmp = Path(folder)
        cfg, obj, binary, labels = (tmp / f'draw.{ext}' for ext in ('cfg', 'o', 'bin', 'lbl'))
        cfg.write_text('MEMORY{ B:start=$bae0,size=$a9,file=%O,fill=yes,fillval=$ea; '
                       'P:start=$b8e4,size=9,file=%O; S:start=$bf7a,size=12,file=%O,fill=yes,fillval=$ea; } '
                       'SEGMENTS{ DRAW_TAIL:load=B,type=ro; DEATH_PRIME:load=P,type=ro; DEATH_SPILL:load=S,type=ro; }\n')
        cc = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
        code = binary.read_bytes()
        symbols = {parts[2][1:]:int(parts[1], 16) for line in labels.read_text().splitlines()
                   if len(parts := line.split()) == 3}
    assert len(code) == len(table)+9+12 and symbols['StaticDraw'] == RECLAIM
    start = symbols['PrimeDeathDistance']
    assert start==0xb8e4
    worker,prime,spill=code[:169],code[169:178],code[178:]
    patches = []
    for pc, old, new in (
        (0xa5d8, OLD_GENERIC, NEW_GENERIC),
        (DRAW_ENTRY, OLD_GUARD, NEW_GUARD),
        (0xb8c8, bytes.fromhex('8d1160'), bytes((0x20, start & 255, start >> 8))),
        (0xb8d5, bytes.fromhex('b00ab98eb98d0f60a900f009b937ba8d0f60b9e0ba8d1060'),
         bytes.fromhex('b016b98eb98d0f60a9008d10609009') + prime),
        (RECLAIM, table, worker),
        (0xbf7a, bytes([0xea])*12, spill),
    ):
        at = preimage(raw, pc, old)
        assert len(old) == len(new)
        patches.append(dict(physical_PRG=4, start=pc, end_exclusive=pc+len(old), file_offset=at,
                            old_hex=old.hex(), new_hex=new.hex()))
    return install(raw, patches), patches, symbols, len(code)


def draw(seed, entry, pointer, pos, cursor, rotation, mode, attr, p, descriptor=None):
    m = slim_fork(seed)
    if descriptor is not None:
        m[pointer:pointer+len(descriptor)] = descriptor
    xlo, xhi, ylo, yhi = pos
    N.put(m, R0=pointer & 255, R1=pointer >> 8, R3=attr, R4=xlo, R5=xhi, R6=ylo, R7=yhi,
          CurrentOAMOffset=cursor, GuestOamRotationActive=mode, RgOamRotation=rotation,
          NmiDisable=255, RlOutlineBypass=0)
    cpu = cpu_at(m, entry, 227, p, x=0x4d, y=9)
    run(cpu, lambda c:(c.pc,c.sp)==(STOP,227))
    ordered = [(a,v) for a,v in m.writes if 0x200<=a<0x300]
    return (registers(cpu), live_stack(cpu), memory(m), ordered), cpu.processorCycles


def render(seeds):
    samples = json.loads(SAMPLE.read_text())['renderer_entries']
    assert [(row['pointer'], row['return_pc']) for row in samples] == [(BRICK,0xa4f1),(COIN,0xa4f1)]
    timings = Counter()

    def compare(label, *case):
        a,b = [draw(seed,*case) for seed in seeds]
        assert a[0] == b[0], (label,case,a[0][:2],b[0][:2],a[0][3],b[0][3])
        saved = a[1]-b[1]
        timings[label,saved] += 1
        return dict(case=label,old=a[1],new=b[1],saved=saved)

    observed = []
    for row in samples:
        pos = tuple(row[n] for n in ('x_low','x_high','y_low','y_high'))
        observed.append(compare(hex(row['pointer']), DRAW_ENTRY, row['pointer'], pos,
                        row['oam_cursor'],row['rotation'],row['rotation_active'],row['attribute'],0x61))
    for ptr,pos,cursor,(rot,mode),attr,p in product((BRICK,COIN,0xade3,0xada9,0xaf2f,0xaf30,0xa976),
            ((0,0,0,1),(128,0,128,1),(247,0,247,1),(248,0,248,1),(255,0,255,1),
             (1,255,1,0),(32,0,1,2),(255,1,255,255)),
            (0,4,12,247,248,251,252,255),((0,0),(0,1),(5,1),(249,0x81)),(0,3,0x8b,0xff),(0x20,0xe5)):
        compare('descriptor',DRAW_ENTRY,ptr,pos,cursor,rot,mode,attr,p)
    for header,pos,mode in product((0,1,4,8,12,127,128,132,252),
            ((0,0,0,1),(254,0,254,1),(127,0x80,127,0x7f)),(0,1)):
        descriptor = bytes([header]) + bytes((i*37) & 255 for i in range(header))
        compare('generic_direct',0xa5ba,0x5c80,pos,0,251,mode,0x12,0x21,descriptor)
    assert all(row['saved']>0 for row in observed), observed
    return dict(observed=observed,peak_saved=sum(row['saved'] for row in observed),
                timing_histogram=[[k[0],k[1],v] for k,v in sorted(timings.items())],cases=sum(timings.values()))


def death(seeds):
    timings = Counter()
    for age,(mode,rotation),x,initial in product(range(256),((0,0),(1,251)),(0x0f,0xf4),(0,0x70)):
        results = []
        for seed in seeds:
            m = slim_fork(seed)
            N.put(m, MmDeathAge=age, MmDeathPit=0, MmDeathX=x, MmDeathPage=0,
                  MmDeathY=178, MmDeathYHigh=1, ScreenLeft_X_Pos=33, ScreenLeft_PageLoc=0,
                  CurrentOAMOffset=initial, GuestOamRotationActive=mode, RgOamRotation=rotation,
                  NmiDisable=255)
            cpu = cpu_at(m, DEATH_ENTRY, 227, 0xe1)
            run(cpu, lambda c:(c.pc,c.sp)==(STOP,227))
            ordered = [(a,v) for a,v in m.writes if 0x200<=a<0x300 or a in (0x5115,0x5116)]
            results.append(((registers(cpu),live_stack(cpu),memory(m),ordered),cpu.processorCycles))
        a,b = results
        assert a[0] == b[0], (age,mode,rotation,x,initial,a[0][:2],b[0][:2],a[0][3],b[0][3])
        timings[a[1]-b[1]] += 1
    assert min(timings)>0
    return dict(cases=sum(timings.values()),minimum_saved=min(timings),maximum_saved=max(timings),
                indexed_ages=256,invalid_spill_ages=87)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--rom',type=Path,default=ROM)
    parser.add_argument('--sha256',default=PIN)
    args=parser.parse_args()
    args.output.mkdir(exist_ok=True)
    raw=args.rom.read_bytes()
    assert P.sha(raw)==args.sha256
    image,patches,symbols,size=compose(raw,args.output)
    seeds=[N.fresh(P.bundle(data)) for data in (raw,image)]
    for m in seeds:
        m.raw_page(1,132)
        N.put(m,CurrentBank=132)
    render_q=render(seeds)
    print('Measured exact witnessed inputs:',render_q['observed'],flush=True)
    death_q=death(seeds)
    print('Full indexed native death:',death_q,flush=True)
    q=dict(passed=True,ROM_written=False,parent_SHA256=args.sha256,expected_memory_only_SHA256=P.sha(image),
           patches=patches,symbols=symbols,linked_bytes=size,renderer=render_q,death=death_q,
           bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),SOURCE,args.rom,SAMPLE)},
           scope='Two exact observed static descriptors, unchanged generic fallback, shared header shrink and same-bank '
                 'death table arithmetic. Native direct CPU application and ordered OAM parity. No emulator.')
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,peak_saved=render_q['peak_saved'],renderer_cases=render_q['cases'],
                          death=death_q,linked_bytes=size,image=q['expected_memory_only_SHA256'])),flush=True)


if __name__=='__main__':
    main()
