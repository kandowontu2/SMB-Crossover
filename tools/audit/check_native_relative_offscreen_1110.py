"""Qualify shared relative position and X offscreen defaults on exact 6bd5."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import measure_mini_shared_offscreen_1110_v1 as O
from check_mini_funded_actor_1108_v3 import install, registers, run
from compose_mini_frame_budget_1108 import check_full_cpu


P,N,R = O.P,O.N,O.R
BASE = R/'build/mini-platform-firebar-native-1110/candidate.nes'
PIN = '6bd5e4b1976e26ecccd9b7c0512944020d6eb7a6e2c8c35ab50c53d0441e7491'
PROFILE = R/'build/mini-platform-actor-profile-1110/capture/instruction-sample.json'
SRC = R/'tools/reference/native_relative_offscreen_1110_v1.s'
SPANS = ((0x8a8c,0x8ace),(0x8b1a,0x8b73))
OLD_RELATIVE = bytes.fromhex('a200a0004c9a8aa00020df8aa00220bf8aa60d60a901a0014cb38a'
    'a909a00420b38ae8e8a909c88603186503aa20bf8aa60d60b5bd997c05b57538ed1f0799710560')
ENTRIES = {'RelativePlayerPosition':0x8a8c,'RelativeFireballPosition':0x8a93,
           'RelWOfs':0x8a9a,'RelativeEnemyPosition':0x8aa0,'RelativeBlockPosition':0x8aa7,
           'VariableObjOfsRelPos':0x8ab3}


def absolute_census(raw):
    prg = raw[16:1048592]
    at = lambda pc:O.offset(pc)-16
    offsets = {0x8a9a:[0x567,at(0x8a90)],0x8ab3:[at(0x8aa4),at(0x8aab)],
               0x8abf:[at(0x8a9a),at(0x8ab9)]}
    for target,sites in offsets.items():
        literal = target.to_bytes(2,'little')
        actual = [i for i in range(len(prg)-2) if prg[i] in (0x20,0x4c) and prg[i+1:i+3]==literal]
        assert actual==sites,(hex(target),actual)
    data = {'bd608b':0x8b51,'be708b':0x8b4e,'be718b':0x8b49}
    for signature,pc in data.items():
        marker = bytes.fromhex(signature)
        assert prg.count(marker)==1 and prg.index(marker)==at(pc)
    common = (R/'src/common.s').read_text()
    for name,uses in (('GetObjRelativePosition',3),('VariableObjOfsRelPos',3),
                      ('XOffscreenBitsData',2),('DefaultXOnscreenOfs',3)):
        assert common.count(name)==uses,name
    assert (R/'src/object.s').read_text().count('jmp RelWOfs')==1
    return dict(old_relative_absolute_ingress=offsets,old_X_table_loads=data,
                stable_relative_entries=ENTRIES,source_private_table_references=True)


def compose(raw,out):
    assert P.sha(raw)==PIN
    census = absolute_census(raw)
    old = (OLD_RELATIVE,O.OLD[0])
    # X's parent is the previously shipped optimized arithmetic rather than
    # the older preimage in O.OLD. Bind the exact checked-in source output.
    old_x = bytes.fromhex('8607a001b91f0738f575850ab91d07f55c3021d01aa9388509a9088508a50ac938'
                         'b00c4a4a4ac001b0026908aa1008be718bd003be708bbd608ba607c900d0038810c160eaea')
    old = (old[0],old_x+bytes.fromhex(O.TABLES[0x8b60]))
    with tempfile.TemporaryDirectory(prefix='link-',dir=out) as name:
        work = Path(name)
        cfg,obj,binary,lbl = (work/f'native.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { A:start=$8A8C,size=$42,file=%O; B:start=$8B1A,size=$59,file=%O; } '
                       'SEGMENTS { RELATIVE:load=A,type=ro; OFFSCREEN:load=B,type=ro; }\n')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SRC,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        data = binary.read_bytes()
        labels = {line.split()[2][1:]:int(line.split()[1],16) for line in lbl.read_text().splitlines()}
    assert all(labels[name]==pc for name,pc in ENTRIES.items())
    assert labels['GetXOffscreenBits']==0x8b1a and labels['XOffscreenBitsData']==0x8b63
    assert data[-16:]==old[1][0x46:0x46+16]
    patches = []
    for (lo,hi),expected in zip(SPANS,old,strict=True):
        at = O.offset(lo)
        length = hi-lo
        assert len(expected)==length and raw[at:at+length]==expected
        new,data = data[:length],data[length:]
        patches.append(dict(file_offset=at,physical_PRG=126,CPU_half_open=[lo,hi],
                            old_hex=expected.hex(),new_hex=new.hex()))
    assert not data
    return install(raw,patches),patches,labels,census


def relative_leaves(before,after):
    cpus = []
    for raw in (before,after):
        ram = bytearray(65536)
        first = O.offset(0x8000)
        ram[0x8000:0xa000] = raw[first:first+8192]
        cpus.append(N.NesMPU(memory=ram))
    counts = Counter()
    for (name,pc),x,y,p in product(ENTRIES.items(),range(256),(0,1,2,5,6,255),
                                   (0x20,0x25,0x63,0xec)):
        regs = []
        initial = bytes((i*17+x*29+y*5+p*3)&255 for i in range(0x800))
        for cpu in cpus:
            m = cpu.memory
            m[:0x800] = initial
            cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp = pc,(x+y)&255,x,y,p,252
            cpu.processorCycles = 0
            cpu.stPushWord(0x5aff)
            run(cpu,lambda z:(z.pc,z.sp)==(0x5b00,252))
            regs.append((registers(cpu),bytes(m[:256])+bytes(m[0x200:0x800]),cpu.processorCycles))
        a,b = regs
        assert a[:2]==b[:2],(name,x,y,p,a[0],b[0])
        expected = {'RelativeEnemyPosition':19,'RelativeBlockPosition':24,
                    'VariableObjOfsRelPos':12,'RelativePlayerPosition':12,
                    'RelativeFireballPosition':9,'RelWOfs':9}[name]
        assert a[2]-b[2]==expected,(name,x,y,p,a[2]-b[2])
        counts[name,expected] += 1
    return [[name,cycles,n] for (name,cycles),n in sorted(counts.items())]


def exact_native_witness():
    q = json.loads(PROFILE.read_text())
    assert json.loads(PROFILE.with_name('binding.json').read_text())['ROM_sha256']==PIN
    f = q['foreground_opcodes']
    scene = q['scene']
    assert (scene['frame'],scene['x'],scene['cycles'])==(1452,694,30862)
    cycles = lambda pc:f.get(f'126:{pc:04x}',0)
    player,enemy = cycles(0x8a8c)//2,cycles(0x8aa0)//2
    edges = cycles(0x8b1e)//4
    negative,far,near = (cycles(pc)//n for pc,n in ((0x8b4e,4),(0x8b49,4),(0x8b46,2)))
    zeros = cycles(0x8b5a)//2
    assert (player,enemy,edges,negative,far,near,zeros)==(2,9,17,7,7,3,12)
    # Three near tests are nonzero. The remaining two nonzero returns are
    # the original default FF cases. The profile does not distinguish which
    # of the two signed edge paths produced each.
    outside = edges-near-zeros
    x_savings = [14*far+9*negative+6*near-4*pos-2*(outside-pos)
                 for pos in range(outside+1)]
    relative = player*12+enemy*19
    return dict(frame=scene['frame'],world_x=scene['x'],foreground=scene['cycles'],
                relative_cycles_saved=relative,X_cycles_saved=[min(x_savings),max(x_savings)],
                combined_cycles_saved=[relative+min(x_savings),relative+max(x_savings)])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    candidate,patches,labels,census = compose(raw,out)
    relative = relative_leaves(raw,candidate)
    offscreen = O.leaves((raw,candidate))
    whole = check_full_cpu(raw,candidate,{})
    witness = exact_native_witness()
    q = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(candidate),
             patches=patches,labels=labels,census=census,relative=relative,offscreen=offscreen,
             whole_GameCore=whole,actual_peak=witness,
             bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in
                       (Path(__file__),SRC,BASE,PROFILE,PROFILE.with_name('binding.json'),
                        R/'src/common.s',R/'src/object.s',O.SOURCE)})
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('expected_memory_only_SHA256','relative','actual_peak','whole_GameCore')}),flush=True)


if __name__=='__main__':
    main()
