"""Group unchanged MMC5 output checks and replay true nested IRQ cuts in audio NMI."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

import measure_mini_audio_1108_v1 as M


SOURCE = M.ROOT/'src/mmc5_sfx.s'


def mix_patch(image, output):
    lo = M.address(image, 'GuestExpansionFlush')
    hi = M.address(image, 'GuestExpansionSweepClock')
    assert (lo, hi) == (0xaab5, 0xac28)
    source = SOURCE.read_text().split('.proc GuestExpansionFlush\n', 1)[1].split('.endproc', 1)[0]
    names = sorted(set(re.findall(r'\bGuest\w+', '\n'.join(line.split(';')[0] for line in source.splitlines()))))
    prefix = ''.join(f'{n}=${M.address(image,n):04x}\n' for n in names)+'FlushStart:\n'
    old, _ = M.assemble(output/'mixer-original', prefix+source, lo, hi-lo)
    at = M.location(image, 'GuestExpansionFlush')
    assert len(old) == hi-lo and image['raw'][at:at+len(old)] == old
    head, original = source.split('Output:\n', 1)
    regs = original[original.index('  lda GuestExpansionApu+I'):original.index('Next:\n')+len('Next:\n')]
    tail = original[original.index('  ; Match the old exhausted loop'):]
    body = '''Output:
 ; The hardware channel mask is stable for all three registers in each group.
 .repeat 2, C
 .scope
  lda #(1 << C)
  and GuestMixMask
  beq ChannelDone
  .repeat 4, R
  .scope
  I = 4*C+R
  .if R <> 1
'''+regs+'''  .endif
  .endscope
  .endrepeat
ChannelDone:
 .endscope
 .endrepeat
'''+tail
    new, _ = M.assemble(output/'mixer-successor', prefix+head+body+f' .res {hi-lo}-(*-FlushStart),$ea\n', lo, hi-lo)
    assert len(new) == len(old) and new[-28:] == bytes([0xea])*28
    return dict(bank=29, pc=lo, offset=at, preimage=old.hex(), replacement=new.hex(),
                byte_end=hi, recovered_unused_tail=28)


def compose(raw, rows):
    result = bytearray(raw)
    for p in rows:
        old, new = bytes.fromhex(p['preimage']), bytes.fromhex(p['replacement'])
        at = p['offset']
        assert len(old) == len(new) and result[at:at+len(old)] == old
        result[at:at+len(old)] = new
    return bytes(result)


def exact_mixer(a, b):
    results = Counter()
    ms = [M.seed(image, 41) for image in (a, b)]
    for m in ms:
        m.page(1, 29)
    for bits in range(256):
        for changed in (0, 1, 2, 3):
            returns = []
            for m in ms:
                M.N.put(m, GuestMixMask=bits, GuestMixChanged=changed, GuestSweepControl=bits,
                        GuestSweepDivider=(bits>>2)&7, GuestSweepReload=bits&1)
                for name in ('GuestFxApu', 'GuestFxDirty', 'GuestExpansionApu', 'GuestExpansionLast'):
                    at = M.address(m.bundle, name)
                    m[at:at+8] = [(i*(bits+7) + changed*(name.endswith('Apu'))) & 255 for i in range(8)]
                m.writes.clear()
                returns.append(M.direct(m, 'GuestExpansionFlush'))
            assert returns[0][1] == returns[1][1], (bits, changed, returns)
            M.compare_state(*ms)
            results[returns[0][0]-returns[1][0]] += 1
    return results


def lag_path(m):
    code = bytes(m[0xe000:0x10000])
    at, = [i for i in range(len(code)-8) if code[i:i+4] == bytes.fromhex('ad390110')
           and code[i+5:i+8] == bytes.fromhex('ee3a01')]
    off = code[at+4]
    return 0xe000+at+5, 0xe000+at+5+(off-256 if off&128 else off)


def sound_writes(m):
    return [(pc, value) for pc, value in m.writes if 0x4000 <= pc <= 0x4017 or 0x5000 <= pc <= 0x5015]


def nmi(seed, cut=None):
    m = M.N.fork(seed)
    m.writes.clear()
    lag, regular = lag_path(m)
    c = M.N.NesMPU(memory=m, pc=0x5b00)
    c.a, c.x, c.y, c.p, c.sp = 173, 23, 61, 0x24, 214
    initial = (c.a,c.x,c.y,c.p&0xef,c.sp,c.pc)
    c.nmi()
    hits, irq, minimum = 0, False, 255
    cuts = {}
    for _ in range(80000):
        pc, sp = c.pc, c.sp
        if (pc, sp) == (0x5b00, 214):
            break
        hits += pc == lag
        assert pc != regular
        minimum = min(minimum, sp)
        if pc >= 0x8000:
            bank = m.rawtags[(pc-0x8000)//8192]&127
            if (bank == 38 and 0xcb03 <= pc < 0xcbc5) or (bank == 29 and 0xaab5 <= pc < 0xac28):
                key = (bank, pc, c.p&4)
                if key not in cuts or sp < cuts[key][3]:
                    cuts[key] = (*key, sp)
                if not irq and (*key, sp) == cut:
                    assert c.p&4 == 0
                    irq = True
                    registers = (c.a,c.x,c.y,c.p&0xef,c.sp,c.pc)
                    maps = m.rawtags[:]
                    scratch = bytes(m[0:0x100])+bytes(m[0x15a:0x17b])
                    overlay_writes = len(m.ram_writes)
                    at = len(m.writes)
                    c.irq()
                    for _ in range(4000):
                        minimum = min(minimum, c.sp)
                        if (c.sp,c.pc) == registers[-2:]:
                            break
                        assert m[c.pc] != 0
                        c.step()
                    else:
                        raise AssertionError(('Nested IRQ bound', cut))
                    assert (c.a,c.x,c.y,c.p&0xef,c.sp,c.pc) == registers
                    assert m.rawtags == maps and bytes(m[0:0x100])+bytes(m[0x15a:0x17b]) == scratch
                    assert len(m.ram_writes) == overlay_writes
                    assert any(pc == 0x2005 for pc, _ in m.writes[at:])
                    assert all(not (0x4000 <= pc <= 0x4017 or 0x5000 <= pc <= 0x5015)
                               for pc, _ in m.writes[at:])
        assert m[c.pc] != 0, (hex(c.pc), m.rawtags)
        c.step()
    else:
        raise AssertionError('Lag NMI did not return')
    assert (c.a,c.x,c.y,c.p&0xef,c.sp,c.pc) == initial
    assert hits == 1 and irq == (cut is not None)
    assert M.N.get(m, 'NmiSkipped') == (M.N.get(seed,'NmiSkipped')+1)&255
    return m, c.processorCycles, list(cuts.values()), minimum


def check_nmi(before, after):
    seeds = [M.seed(image,41) for image in (before,after)]
    for m in seeds:
        M.N.put(m, AreaMusicQueue=1, NmiDisable=255, Square1SoundQueue=32)
    old, old_cycles, _, _ = nmi(seeds[0])
    ref, new_cycles, cuts, low = nmi(seeds[1])
    M.compare_state(old,ref)
    domains = Counter()
    for cut in sorted(cuts):
        if cut[2]:
            domains['masked'] += 1
            continue
        actual, _, _, depth = nmi(seeds[1], cut)
        domains['decoder' if cut[0] == 38 else 'mixer'] += 1
        assert sound_writes(actual) == sound_writes(ref) and actual.ram == ref.ram
        assert actual.rawtags == ref.rawtags
        assert bytes(actual[0:0x100])+bytes(actual[0x15a:0x17b]) == bytes(ref[0:0x100])+bytes(ref[0x15a:0x17b])
        low = min(low,depth)
    assert min(domains['decoder'], domains['mixer']) > 10
    return dict(IRQ_cuts=domains, minimum_SP=low, negative_NMI_lag_PC=lag_path(seeds[1])[0],
                cold_cue_NMI_cycles=[old_cycles,new_cycles])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = M.ROM.read_bytes()
    assert M.sha(raw) == M.PIN
    baseline = M.bundle(raw)
    patch = mix_patch(baseline,args.output)
    decoder_receipt = args.output/'result.json'
    prior = json.loads(decoder_receipt.read_text())
    assert prior['parent_SHA256'] == M.PIN
    patches = prior['patches']+[patch]
    mixed_raw = compose(raw,[patch])
    both_raw = compose(raw,patches)
    mixed, both = M.bundle(mixed_raw), M.bundle(both_raw)
    cases = exact_mixer(baseline,mixed)
    print('Mixer leaf differential', cases, flush=True)
    foreign = M.foreign(baseline,both)
    interrupt = check_nmi(baseline,both)
    result = dict(passed=True, parent_SHA256=M.PIN, expected_memory_only_SHA256=M.sha(both_raw),
                  mixer_only_memory_SHA256=M.sha(mixed_raw), patches=patches,
                  original_decoder_receipt_SHA256=M.sha(decoder_receipt.read_bytes()),
                  mixer_leaf_cases=sum(cases.values()), mixer_saving_histogram=cases,
                  actual_foreign_AudioUpdate_cases=len(foreign)*40, foreign=foreign, nested_IRQ=interrupt,
                  bindings={path.relative_to(M.ROOT).as_posix():M.sha(path.read_bytes())
                            for path in (SOURCE, M.ROOT/'src/reset.s', Path(__file__))},
                  scope='Mapper5 grouped pulse-enable tests preserve both expansion images, ascending APU writes, '
                        'sweep state, flags, and all original public PCs. Decoder and mixer combined in memory. '
                        'Nested hardware IRQ runs in real negative-NmiDisable lag NMI and preserves active registers, '
                        'full zero page, SMC, bank windows, and audio writes. Source-only cycle measurement.')
    (args.output/'mixer-irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('patches','foreign')}))


if __name__ == '__main__':
    main()
