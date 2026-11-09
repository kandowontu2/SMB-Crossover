"""Check the shared graphics-column scratch and buffers across actual vectors."""

import argparse
from collections import Counter
import json
from pathlib import Path

from measure_column_graphics_1109 import M
from measure_mini_audio_1108_v1 import seed
from prepare_selected_native_packet_v1 import sha


def qualify(rom, proof):
    N = M.N
    image = M.bundle(rom.read_bytes())
    low, high = proof['patches'][0]['CPU_half_open']
    native_tag = proof['patches'][0]['physical_PRG'] | 128
    ranges = [('R0',6), ('MetatileBuffer',13), ('AttributeBuffer',7), ('VRAM_Buffer2',35)]
    watched = {a for name,n in ranges for a in range(M.address(image,name),M.address(image,name)+n)}
    timing_scratch = M.address(image,'R0')
    counts = Counter()

    def state(c):
        m = c.memory
        return (c.a,c.x,c.y,c.p&0xef,c.sp,c.pc,tuple(m.rawtags),bytes(m[0x15a:0x17b]),
                tuple(m[a] for a in sorted(watched)),bytes(m[0x101+c.sp:0x200]))

    def probe(original, nmi):
        m = N.fork(original.memory)
        c = N.NesMPU(memory=m,pc=original.pc)
        c.a,c.x,c.y,c.p,c.sp = original.a,original.x,original.y,original.p,original.sp
        before = state(c)
        m.writes.clear()
        if nmi:
            assert N.get(m,'NmiDisable') == 255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
        for _ in range(20000):
            if (c.pc,c.sp) == before[5:3:-1]:
                break
            assert m[c.pc] != 0, hex(c.pc)
            c.step()
        else:
            raise AssertionError(('Interrupt did not return',hex(original.pc),hex(c.pc),nmi))
        assert state(c) == before, (hex(original.pc),nmi)
        # The native HUD split writes PPUADDR. It must never publish an
        # incomplete terrain packet through PPUDATA or OAM DMA.
        assert all(a not in watched and a not in (0x2007,0x4014) for a,_ in m.writes)
        counts['lag_nmi' if nmi else 'irq'] += 1

    for owner in (0,7,41):
        m = seed(image,owner)
        m.raw_page(1,native_tag)
        N.put(m,NmiDisable=255,Sprite0HitDetectFlag=1,CurrentBank=native_tag,
              AreaMusicQueue=1,CurrentNTAddr_Low=0x9f,CurrentNTAddr_High=0x24)
        at = M.address(image,'MetatileBuffer')
        m[at:at+13] = bytes((i*31+owner)&255 for i in range(13))
        for column, task in ((0,7),(0,6),(1,3),(1,2)):
            N.put(m,CurrentColumnPos=column,AreaParserTaskNum=task,VRAM_Buffer2_Offset=0)
            c = N.NesMPU(memory=m,pc=low)
            c.a,c.x,c.y,c.p,c.sp = 23,17,31,0x21,197
            c.stPushWord(0x5aff)
            seen = set()
            for _ in range(800):
                if c.pc == 0x5b00:
                    break
                if low <= c.pc < high and c.pc not in seen:
                    seen.add(c.pc)
                    probe(c,True)
                    probe(c,False)
                c.step()
            else:
                raise AssertionError(('Foreground bound',hex(c.pc)))
    assert counts['lag_nmi'] > 450 and counts['irq'] == counts['lag_nmi']
    return dict(passed=True, ROM_SHA256=sha(rom), counts=counts,
                native_irq_timing_R0=timing_scratch,
                scope='Real vectors interrupt both renderer phases. Live scratch, terrain, attribute and VRAM buffers, '
                      'mapping, SMC and foreground register/stack context survive the cuts.')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--rom',type=Path,required=True)
    cli.add_argument('--proof',type=Path,required=True)
    args = cli.parse_args()
    proof = json.loads(args.proof.read_text())
    result = qualify(args.rom,proof)
    result['proof_SHA256'] = sha(args.proof)
    args.output.mkdir(exist_ok=True)
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
