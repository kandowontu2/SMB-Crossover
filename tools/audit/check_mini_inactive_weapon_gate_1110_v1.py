"""Link and verify the local inactive-Mini weapon dispatch on exact 03c0."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import re
import subprocess

from check_mini_funded_actor_1108_v3 import run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at
import profile_mini_mario_matched_1110 as Match


R, P, N = Match.R, Match.P, Match.N
SOURCE = R/'tools/reference/mini_inactive_weapon_gate_1110_v1.s'
START, END, AIR = 0xadc0, 0xae27, 0xae68
OLD = bytes.fromhex(
    'ad0260c90690158d6a01a9588d6c01a9ad8d6d01a9fc4c5a01eaeaea'
    'c90390158d6a01a9008d6c01a9a08d6d01a9d4205a014c68ae'
    'c902d0158d6a01a9578d6c01a9ae8d6d01a9f9205a014c68ae'
    'c901d0158d6a01a9938d6c01a9a08d6d01a988205a014c68ae')
SHOTS = ((0, 0), (1, 0), (0, 1), (0x80, 0), (0, 0x81), (1, 1))


def offset(bank, pc):
    return 16+bank*8192+(pc&8191)


def require(raw, bank, pc, word):
    a = offset(bank, pc)
    assert raw[a:a+len(word)] == word, (bank, hex(pc))


def link(raw, out):
    assert P.sha(raw) == Match.PIN and len(OLD) == END-START
    require(raw, 0, START, OLD)
    require(raw, 0, 0xad9b, bytes.fromhex('ad0260c902901ec9069008c90af004c90bd0128d6a01a9858d6c01a9bf8d6d01a9cf205a01'))
    require(raw, 0, END, bytes.fromhex('ad0260d019ad0a73c904d0128d6a01a9118d6c01a9be8d6d01a9d14c5a01'))
    require(raw, 79, 0xaada, bytes.fromhex('d00ec022d00dad5b074a05250526f0134c3db5'))
    require(raw, 79, 0xb542, bytes.fromhex('68a828ad6a013860'))
    require(raw, 124, 0xad72, bytes.fromhex('205a012060a7a9688d6c01a9ae8d6d01a9804c5a01'))
    require(raw, 124, 0xa760, bytes.fromhex('8d6a01903608ad0260c9264c95a7'))
    # The old private legacy branch entries are internal to this router.
    prg = raw[16:1048592]
    bank0 = raw[16:8208]
    for target in (0xaddc, 0xadf5, 0xae0e):
        for opcode in (0x20, 0x4c):
            assert bytes((opcode,target&255,target>>8)) not in bank0
        packet = bytes.fromhex(f'a9{target&255:02x}8d6c01a9{target>>8:02x}8d6d01a980')
        assert packet not in prg
    out.mkdir(exist_ok=True)
    cfg, obj, code, labels = [out/f'router.{ext}' for ext in ('cfg','o','bin','lbl')]
    cfg.write_text('MEMORY{R:start=$ADC0,size=$67,file=%O;}SEGMENTS{ROUTER:load=R,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe', SOURCE, '-o', obj], check=True)
    subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', code, '-Ln', labels], check=True)
    obj.unlink()
    names = {n:int(pc,16) for pc,n in re.findall(r'al ([0-9A-F]+) \.(\w+)',labels.read_text())}
    new = code.read_bytes()
    assert len(new) == len(OLD) and names['WeaponOwnerRouterEnd'] == END
    at = offset(0, START)
    image = raw[:at]+new+raw[at+len(new):]
    return image, names, dict(physical_PRG=0,CPU_half_open=[START,END],file_offset=at,
                              old_hex=OLD.hex(),new_hex=new.hex())


def root_cpu(m, pc, flags=0x21):
    m[0x5115] = 128
    N.put(m, CurrentBank=128)
    return cpu_at(m, pc, 252, flags, x=3, y=91)


def router_inputs(images, seeds):
    cases = 0
    for owner, flags in product(range(256), (0x21,0x26,0x69,0xe4)):
        rows = []
        for b, seed in zip(images,seeds,strict=True):
            m = slim_fork(seed)
            m.bundle = b
            N.put(m, SelectedCharacter=owner, PlayerStatus=2)
            c = root_cpu(m, START, flags)
            run(c,lambda z:z.pc in (END,0x15a))
            rows.append((c.pc,c.a,c.x,c.y,c.p,c.sp,bytes(m[0x16a:0x16e]),list(m.rawtags)))
        assert rows[0] == rows[1], (owner,flags,rows)
        cases += 1
    return cases


def semantic(c):
    m = c.memory
    bus = tuple((a,v) for a,v in m.writes
                if 0x2000<=a<0x4020 or 0x5100<=a<=0x5206 and a!=0x5115)
    return (c.a,c.x,c.y,c.p&0xef,c.sp,bytes(m[:0x100]),bytes(m[0x200:0x8000]),
            tuple(m.rawtags),tuple(map(bytes,m.ram)),tuple(m.chr_latches),bytes(m.vram),
            m.ppuctrl,m.ppu_addr,m.toggle,m.buffer,tuple(m.protection),m.ppu_reads,
            tuple(m.ppu_log),bus,tuple(m.ram_writes))


def pipe(m, status, states, swimming):
    N.put(m, PlayerStatus=status, SwimmingFlag=swimming, A_B_Buttons=0,
          Player_Y_Position=152, Player_Y_HighPos=1, TimerControl=0,
          VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0, ObjectOffset=2)
    for slot,state in enumerate(states):
        for name,value in (('Fireball_State',state),('FireballMetasprite',0x31+slot),
                           ('Fireball_X_Position',38+32*slot),('Fireball_PageLoc',0),
                           ('Fireball_Y_Position',152),('Fireball_Y_HighPos',1),
                           ('Fireball_X_Speed',0x20),('Fireball_Y_Speed',1),
                           ('Fireball_BoundBoxCtrl',8)):
            Match.place(m,name,slot,value)
    for slot, y in enumerate((248,170,190)):
        Match.place(m,'Bubble_Y_Position',slot,y)
        Match.place(m,'Bubble_PageLoc',slot,0)


def mini_cases(images, seeds, names):
    results = Counter()
    for status, states, swim, flags in product(range(4),SHOTS,(0,1),(0x21,0x25,0x61,0xe0)):
        pair = []
        for b, seed in zip(images,seeds,strict=True):
            m = slim_fork(seed)
            m.bundle = b
            pipe(m,status,states,swim)
            c = root_cpu(m, START, flags)
            before = len(m.writes)
            run(c,lambda z:(z.pc,z.sp)==(STOP,252))
            maps = [value for addr,value in m.writes[before:] if addr == 0x5115]
            pair.append((c,maps))
        a,b = (p[0] for p in pair)
        expected_fast = status < 2 and states == (0,0)
        # With inactive Mini, the original final air-bubble tail may leave a
        # different last-written mapper packet. Its work and return are exact.
        if semantic(a) != semantic(b):
            left,right = semantic(a),semantic(b)
            print('DIFF',status,states,swim,hex(flags),
                  [i for i,(x,y) in enumerate(zip(left,right)) if x!=y],flush=True)
            print('flags',hex(left[3]),hex(right[3]),'memory',
                  [(hex(i+0x200),v,w) for i,(v,w) in enumerate(zip(left[6],right[6])) if v!=w][:32],
                  'writes',left[18][-15:],right[18][-15:],flush=True)
            raise AssertionError('mini gameplay state')
        saved = a.processorCycles-b.processorCycles
        assert (saved>200 if expected_fast else saved<=0)
        results['fast' if expected_fast else 'retained',saved] += 1
    return [[role,cycles,cases] for (role,cycles),cases in sorted(results.items())]


def whole(raw, after):
    scene = json.loads(Match.WITNESS.read_text())['scene']
    image = [P.bundle(q) for q in (raw,after)]
    cold = [Match.cold(b,41)[0] for b in image]
    rows = []
    for crowd in (False,True):
        pair = [Match.arena(slim_fork(m),scene,crowd) for m in cold]
        for key in (0,0,193,193,1,1):
            cpus = []
            for m in pair:
                Match.controls(m,key)
                c = cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
                run(c,lambda z:(z.pc,z.sp)==(STOP,252))
                cpus.append(c)
            assert semantic(cpus[0]) == semantic(cpus[1]),(crowd,key)
            rows.append([crowd,key,cpus[0].processorCycles-cpus[1].processorCycles])
            for m in pair:
                N.consume(m)
    return rows


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    raw = Match.ROM.read_bytes()
    after,names,patch = link(raw,args.output)
    images = [P.bundle(q) for q in (raw,after)]
    seeds = [Match.cold(b,41)[0] for b in images]
    dispatch = router_inputs(images,seeds)
    mini = mini_cases(images,seeds,names)
    loops = whole(raw,after)
    print(dispatch,mini,loops,flush=True)
    out = dict(passed=True,ROM_written=False,parent_SHA256=Match.PIN,
               expected_memory_only_SHA256=P.sha(after),patches=[patch],
               ingress_cases=dispatch,mini_cases=mini,whole_GameLoop=loops,symbols=names,
               bindings={str(p):P.sha(p.read_bytes()) for p in
                         (Path(__file__),SOURCE,Match.ROM,Path(Match.__file__),R/'src/object.s')})
    (args.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n')


if __name__ == '__main__':
    main()
