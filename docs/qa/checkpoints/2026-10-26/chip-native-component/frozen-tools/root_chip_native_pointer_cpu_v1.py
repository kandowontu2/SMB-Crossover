"""Exercise original ROM reads across both windows and the $92ff boundary."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, address
from mike_native_music_cpu import MusicMemory
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True)
    b = load(a.rom)
    m = MusicMemory(b)
    m.page(1,62)
    m.page(2,94)
    c = NesMPU(memory=m)
    plan = json.loads((ROOT/'reference/new-roster-audio/playlist-plan.json').read_text())['chip']
    raw = (ROOT/plan['source']).read_bytes()
    refmem = [0]*65536
    refmem[0x8000:0xafb0] = raw[128:]
    ref = NesMPU(memory=refmem)
    zp = address(b,'ChNativeZp')
    helpers = [('ChNativeLDAC1',1,0xb1),('ChNativeLDAC5',5,0xb1),
               ('ChNativeLDAD0',16,0xb1),('ChNativeCMPC5',5,0xd1),('ChNativeORAC5',5,0x11)]
    flags = [0x20,0x21,0x60,0x61,0xe0,0xe1,0xee,0xff]
    reads, boundaries, maps = 0,0,0
    allowed_zp = {address(b,n)+i for n in ['ChNativePointer','ChNativeMappedC5'] for i in [0,1]}
    foreground = bytes(m[:256])

    def call(entry, av, xv, yv, pv):
        c.pc = address(b,entry)
        c.a,c.x,c.y,c.p,c.sp = av,xv,yv,pv,253
        m[510],m[511] = 255,126
        for _ in range(300):
            if c.pc == 0x7f00:
                break
            m.pc = c.pc
            c.step()
        else:
            raise AssertionError(('Helper timeout',entry,hex(c.pc)))
        assert c.sp == 255
        return c.a,c.x,c.y,c.p&0xcf

    for hi,lo,yv,pv in itertools.product(range(0x81,0xb0),[0,1,6,127,205,248,254,255],[0,1,7,50,255],flags):
        original = (hi<<8)|lo
        if original+yv >= 0xafb0:
            continue
        av = (original*17+pv)&255
        xv = [0,1,3,255][reads%4]
        for entry,slot,opcode in helpers:
            m[zp+slot],m[zp+slot+1] = lo,hi
            if slot == 5:
                mapped = address(b,'ChNativeMappedC5')
                m[mapped] = lo
                got = call('ChNativeMapC5High',hi,xv,yv,pv)
                assert got == (hi,xv,yv,pv&0xcf), ('Mapper changes source registers/physical flags',got)
                assert m[mapped+1] == hi+(0x2d if hi<0x93 else 0x30)
                maps += 1
            refmem[0xc1],refmem[0xc2] = lo,hi
            refmem[0x7f10],refmem[0x7f11] = opcode,0xc1
            ref.pc,ref.a,ref.x,ref.y,ref.p = 0x7f10,av,xv,yv,pv
            ref.step()
            got = call(entry,av,xv,yv,pv)
            expected = ref.a,ref.x,ref.y,ref.p&0xcf
            assert got == expected, (entry,hex(original),yv,hex(pv),got,expected)
            assert all(m[i] == foreground[i] for i in range(256) if i not in allowed_zp)
            reads += 1
            boundaries += hi == 0x92 and lo+yv >= 256
    q = dict(passed=True,accepted=False,native_run=False,candidate_ROM_sha256=sha(a.rom),
             source_sha256=sha(ROOT/plan['source']),compiled_helper_reads=reads,
             compiled_cache_setter_controls=maps,cross_window_boundary_reads=boundaries,
             complete_physical_CPU_flags_AXY_exact=True,foreground_ZP_exact_except_four_owned_audio_bytes=True,
             scope='Synthetic CPU pointer/read components. Original LDA/CMP/ORA instructions provide the independent result. Source gameplay, IRQ and cadence remain separate.',
             checker_sha256=sha(__file__))
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(q))


if __name__ == '__main__':
    main()
