"""Interrupt the faster delivered audio transport inside real normal/lag NMIs."""

import argparse
from collections import Counter
import json
from pathlib import Path

import measure_mini_audio_transport_1108_v4 as T


M = T.M
N = M.N


def state(m):
    return bytes(m[:0x100]),bytes(m[0x15a:0x17b]),tuple(map(bytes,m.ram)),m.rawtags[:]


def observed(seed, kind, watch, inject=None):
    m = N.fork(seed)
    m.writes.clear()
    N.put(m,NmiDisable=255 if kind == 'lag' else 0)
    lag, regular = T.lag_path(m)
    cpu = T.CURRENT_CPU(memory=m,pc=0x5b00)
    cpu.sp,cpu.p,cpu.a,cpu.x,cpu.y = 214,0x20,173,23,61
    initial = (cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)
    cpu.nmi()
    visits, cuts, nested = Counter(),{},False
    minimum=255
    for _ in range(80000):
        pc,sp=cpu.pc,cpu.sp
        minimum=min(minimum,sp)
        if (pc,sp) == (0x5b00,214):
            break
        if pc in (lag,regular):
            visits[pc] += 1
        if any(lo <= pc < hi for lo,hi in watch) and m.rawtags[2] == 0xa6:
            depth=N.get(m,'XgAudioDepth')
            key=(pc,cpu.p&4,min(depth,2))
            tag=(pc,sp,depth,m.rawtags[1],cpu.p&4)
            if key not in cuts or cuts[key][1] > sp:
                cuts[key]=tag
            if not nested and tag == inject:
                nested=True
                assert cpu.p&4 == 0
                resume=(cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc)
                before=state(m)
                hw_at=len(m.writes)
                cpu.irq()
                for _ in range(4000):
                    minimum=min(minimum,cpu.sp)
                    if (cpu.sp,cpu.pc) == resume[-2:]:
                        break
                    assert m[cpu.pc] != 0
                    cpu.step()
                else:
                    raise AssertionError(('Nested IRQ bound',tag))
                assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc) == resume
                assert state(m) == before
                irq_writes = m.writes[hw_at:]
                assert any(a == 0x2005 for a,_ in irq_writes)
                assert all(not (0x4000 <= a <= 0x4017 or 0x5000 <= a <= 0x5015 or 0x5114 <= a <= 0x5117)
                           for a,_ in irq_writes)
        assert m[cpu.pc] != 0, (hex(cpu.pc),m.rawtags)
        cpu.step()
    else:
        raise AssertionError(('Actual NMI execution bound',hex(cpu.pc)))
    assert visits == Counter({lag if kind == 'lag' else regular:1})
    assert nested == (inject is not None)
    assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp,cpu.pc) == initial
    return m,cuts,minimum


def sound(m):
    return [(a,v) for a,v in m.writes if 0x4000 <= a <= 0x4017 or 0x5000 <= a <= 0x5015]


def stress(image,watch,kind):
    m=M.seed(image,41)
    N.put(m,Sprite0HitDetectFlag=1)
    choices={}
    snapshots={}
    for t in range(64):
        N.put(m,AreaMusicQueue=1 if t == 0 else 0,Square1SoundQueue=32 if t%32 == 14 else 0,
              VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,FrameCounter=t)
        seed=m
        m,cuts,_=observed(seed,kind,watch)
        for key,tag in cuts.items():
            if key not in choices or tag[1]<choices[key][1][1]:
                choices[key]=(t,tag)
                if t not in snapshots:
                    snapshots[t]=(seed,N.fork(m))
    counts=Counter()
    low=255
    for (_,interrupt_mask,_),(tick,tag) in choices.items():
        if interrupt_mask:
            counts['masked']+=1
            continue
        seed,expected=snapshots[tick]
        actual,_,depth=observed(seed,kind,watch,tag)
        assert state(actual)==state(expected)
        assert sound(actual)==sound(expected)
        counts['IRQ']+=1
        counts['IRQ_while_macro_active']+=tag[2]>0
        counts['IRQ_while_nested_macro_active']+=tag[2]>1
        low=min(low,depth)
    assert counts['IRQ']>20 and counts['IRQ_while_nested_macro_active']>0,(kind,counts)
    return dict(kind=kind,cuts=counts,minimum_SP=low)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    receipt=args.output/'result.json'
    prior=json.loads(receipt.read_text())
    raw=T.ROM.read_bytes()
    assert M.sha(raw)==T.PIN==prior['parent_SHA256']
    final=T.compose(raw,prior['patches'])
    assert M.sha(final)==prior['expected_memory_only_SHA256']
    watch=[(p['pc'],p['pc']+len(bytes.fromhex(p['replacement']))) for p in prior['patches']]
    rows=[stress(M.bundle(final),watch,kind) for kind in ('normal','lag')]
    result=dict(passed=True,image_SHA256=M.sha(final),proof_SHA256=M.sha(receipt.read_bytes()),rows=rows,
                scope='Deepest reached IRQ-enabled instruction cuts in modified PRG38 ranges during actual normal and '
                      'negative lag NMIs. Verify immediate AXYP/SP, native zero page, full owned overlay and A/C maps, '
                      'then uninterrupted ordered APU/expansion writes and final decoder/mapping state. CPU fixture.')
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
