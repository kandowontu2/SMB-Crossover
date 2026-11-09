"""Profile delivered Mini audio and qualify a source-linked decoder factor."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from prepare_mini_mario_chr_override_1103_v39 import assemble
from prepare_mini_mario_native_power_1103_v56 import N, address, bundle, location


ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT/'build/mini-fireball-gbc-1108/candidate.nes'
PIN = 'fc7d4554fed204e8efa4c4489ee70cd5c6529ce95e0d606ffee1cda525188ec5'
SOURCE = ROOT/'src/expanded_audio.s'
END = 'KbAudioFamily'
sha = lambda data: hashlib.sha256(data).hexdigest()


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def decoder_patch(image, output):
    raw = image['raw']
    lo = address(image, 'Byte')
    hi = address(image, END)
    assert (lo, hi) == (0xcb03, 0xcbc5)
    assert location(image, 'Byte') == 16+38*8192+(lo&8191)
    source = SOURCE.read_text()
    body = source[source.index('\nByte:\n')+1:source.index('\n.endproc\n.popseg', source.index('\nByte:\n'))]
    # The current audio C bank uses a direct MMC5 $5115 write in RawByte.
    body = one(body, '.if ::MAPPER_MMC5\n  ora #MMC5_PRG_ROM\n.endif\n  BankPRGA a',
               '  ora #$80\n  sta $5115')
    symbols = sorted(set(re.findall(r'\bXg\w+', body)))
    prefix = '.export Byte,ResetLz,LzByte,RawByte,CopyLz,LzMatch,WriteHistory\n'
    prefix += ''.join(f'{name}=${address(image, name):04x}\n' for name in symbols)
    original, old_labels = assemble(output/'decoder-original', prefix+body+'\n', lo, hi-lo)
    off = location(image, 'Byte')
    assert len(original) == hi-lo and raw[off:off+len(original)] == original
    # No out-of-frame raw decoder or history writer ingress in the authored source.
    for name, expected in [('RawByte', 6), ('LzByte', 2), ('WriteHistory', 2), ('CopyLz', 2)]:
        actual = len(re.findall(rf'\b{name}\b', '\n'.join(line.split(';')[0] for line in source.splitlines())))
        assert actual == expected, (name, actual)
        external = [(p.name, line) for p in (ROOT/'src').rglob('*.s') if p != SOURCE
                    for line in p.read_text(encoding='utf-8', errors='replace').splitlines()
                    if re.search(rf'\bExpandedAudioTick\s*::\s*{name}\b', line.split(';')[0])]
        assert not external, external
    new = one(body, '  ldy XgLzSavedY\n  lda XgLzValue\n', '  ldy XgLzSavedY\n  ora #0\n')
    new = one(new, '  jsr RawByte\n  pha\n  and #7\n  sta XgLzDistance+1\n  pla\n',
              '  jsr RawByte\n  and #7\n  sta XgLzDistance+1\n  txa\n')
    new = one(new, 'WriteHistory:\n  ldy #0\n  sta (XgLzPosition),y\n  tax\n',
              'WriteHistory:\n  ; Both literal and backreference paths enter with X=A and Y=0.\n  sta (XgLzPosition),y\n')
    new = one(new, '  lda (XgAudioPtr),y\n  pha\n', '  lda (XgAudioPtr),y\n  tax\n')
    new = one(new, 'EndByte:\n  pla\n', 'EndByte:\n  txa\n')
    new += f'\n.res {hi-lo}-(*-Byte),$ea\n'
    successor, new_labels = assemble(output/'decoder-successor', prefix+new, lo, hi-lo)
    assert len(successor) == hi-lo
    assert all(old_labels[k] == new_labels[k] for k in ('Byte', 'ResetLz', 'LzByte'))
    image_after = raw[:off]+successor+raw[off+len(successor):]
    patch = dict(bank=38, pc=lo, offset=off, preimage=original.hex(), replacement=successor.hex(),
                 source_footprint_end=hi, old_labels=old_labels, new_labels=new_labels)
    return image_after, patch


def direct(m, name, cls=None):
    if cls is None:
        cls = N.NesMPU
    c = cls(memory=m, pc=address(m.bundle, name))
    c.a, c.x, c.y, c.p, c.sp = 173, 23, 61, 0x24, 224
    c.stPushWord(0x5aff)
    for _ in range(80000):
        if c.pc == 0x5b00:
            assert c.sp == 224
            return c.processorCycles, (c.a, c.x, c.y, c.p, c.sp)
        assert m[c.pc] != 0, ('Actual linked BRK', hex(c.pc), m.rawtags)
        c.step()
    raise AssertionError(('Actual linked audio bound', hex(c.pc)))


def seed(image, char, area=1):
    m = N.fresh(image)
    N.put(m, SelectedCharacter=char, OperMode=1, FamilyMainCommit=1, DisableScreenFlag=1,
          Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
    if char == 41:
        N.invoke(m, 'MiniScene')
    N.put(m, DisableScreenFlag=0, OperMode_Task=3, GameEngineSubroutine=8,
          AreaType=area, Player_Y_HighPos=1, Player_X_Position=80, Player_Y_Position=176,
          PlayerFacingDir=1, GamePauseStatus=0, TimerControl=0)
    m.writes.clear()
    return m


def hardware(m):
    return [(pc, value) for pc, value in m.writes if 0x4000 <= pc <= 0x4017 or 0x5000 <= pc <= 0x5015
            or 0x5114 <= pc <= 0x5130 or pc in (0x2000, 0x2001, 0x2005, 0x2006, 0x2007)]


def compare_state(a, b):
    flat = lambda m, lo, hi: list.__getitem__(m, slice(lo, hi))
    for lo, hi in [(0, 0x100), (0x200, 0x8000)]:
        x, y = flat(a, lo, hi), flat(b, lo, hi)
        if x != y:
            raise AssertionError(('Audio application state', [(hex(lo+i), p, q) for i, (p, q) in
                                                               enumerate(zip(x, y)) if p != q][:10]))
    assert hardware(a) == hardware(b)
    assert a.ram == b.ram and a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
    assert (a.ppuctrl, a.ppu_addr, a.toggle, a.upper, a.lastset) == (b.ppuctrl, b.ppu_addr, b.toggle, b.upper, b.lastset)


def profile(original, changed, patch):
    leaves = 'AudioUpdate RemainingAudioBegin GuestAudioBegin ExpandedAudioUpdate VgAudioDispatch ExpandedAudioTick SophiaLandAudioTick GuestAudioFinish SFXSoundEngine GuestAudioNativeFlush GuestExpansionFlush GuestNativeStatusSTA GuestDmcStatus CrossoverGraphicsBank Byte'.split()
    points = {((location(original, n)-16)//8192, address(original, n)):n for n in leaves}
    token_pcs = {patch['old_labels'][n]:n for n in ['RawByte', 'LzByte', 'CopyLz', 'LzMatch', 'WriteHistory']}
    inclusive = Counter()
    count = Counter()
    banks = Counter()
    stack = []

    class Trace(N.NesMPU):
        def step(self):
            pc, sp, before = self.pc, self.sp, self.processorCycles
            m = self.memory
            while stack and stack[-1][:2] == (pc, sp):
                _, _, name, first = stack.pop()
                inclusive[name] += before-first
            bank = m.rawtags[(pc-0x8000)//8192]&127 if pc >= 0x8000 else -1
            name = points.get((bank, pc))
            if name:
                ret = ((m[0x101+sp] | (m[0x102+sp]<<8))+1)&65535
                stack.append((ret, (sp+2)&255, name, before))
                count[name] += 1
            if bank == 38 and pc in token_pcs:
                count[token_pcs[pc]] += 1
            super().step()
            banks[bank] += self.processorCycles-before

    a, b = seed(original, 41), seed(changed, 41)
    rows = []
    for t in range(256):
        for m in (a, b):
            m.writes.clear()
            N.put(m, AreaMusicQueue=1 if t == 0 else 0, EventMusicQueue=4 if t == 112 else 0,
                  Square1SoundQueue=32 if t in (32, 48, 70, 155) else 0,
                  Square2SoundQueue=1 if t in (80, 140) else 0, NoiseSoundQueue=1 if t == 146 else 0,
                  GamePauseStatus=int(200 <= t < 204), FrameCounter=t)
        before = count.copy()
        assert not stack
        old, old_regs = direct(a, 'AudioUpdate', Trace)
        while stack and stack[-1][:2] == (0x5b00, 224):
            _, _, name, first = stack.pop()
            inclusive[name] += old-first
        assert not stack, stack
        new, new_regs = direct(b, 'AudioUpdate')
        assert old_regs == new_regs
        compare_state(a, b)
        visits = count-before
        prediction = 3*visits['RawByte'] + visits['Byte'] + 4*visits['WriteHistory'] + 5*visits['LzMatch']
        assert old-new == prediction, (t, old, new, prediction, visits)
        rows.append((old, new, visits['Byte'], visits['RawByte'], visits['LzMatch']))
    return dict(updates=len(rows), cycle_pairs=rows, old_range=[min(r[0] for r in rows), max(r[0] for r in rows)],
                new_range=[min(r[1] for r in rows), max(r[1] for r in rows)],
                old_average=sum(r[0] for r in rows)/len(rows), new_average=sum(r[1] for r in rows)/len(rows),
                saving_histogram=Counter(r[0]-r[1] for r in rows), inclusive_routine_cycles=inclusive.most_common(),
                original_cpu_by_bank=banks.most_common(), original_entry_counts=count.most_common(),
                actual_audio_family=N.get(a, 'XgAudioCharacter'))


def foreign(original, changed):
    rows = []
    for char in (0, 1, 2, 3, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 23, 24, 29, 32, 35, 36, 37, 38, 39, 40):
        a, b = seed(original, char), seed(changed, char)
        costs = []
        for t in range(40):
            for m in (a, b):
                m.writes.clear()
                N.put(m, AreaMusicQueue=(1 if t == 0 else 2 if t == 17 else 0),
                      EventMusicQueue=4 if t == 22 else 0, Square1SoundQueue=32 if t == 10 else 0,
                      Square2SoundQueue=1 if t == 15 else 0, NoiseSoundQueue=1 if t == 33 else 0,
                      GamePauseStatus=int(t == 30), FrameCounter=t)
            old, old_regs = direct(a, 'AudioUpdate')
            new, new_regs = direct(b, 'AudioUpdate')
            assert old_regs == new_regs, (char, t, old_regs, new_regs)
            compare_state(a, b)
            assert new <= old, (char, t, old, new)
            costs.append(old-new)
        rows.append(dict(selected=char, cycles_saved=[min(costs), max(costs)], sum=sum(costs)))
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(exist_ok=True)
    raw = ROM.read_bytes()
    assert sha(raw) == PIN
    original = bundle(raw)
    after, patch = decoder_patch(original, args.output)
    changed = bundle(after)
    timing = profile(original, changed, patch)
    rows = foreign(original, changed)
    receipt = dict(passed=True, parent_SHA256=PIN, expected_memory_only_SHA256=sha(after), patches=[patch],
                   Mini=timing, foreign_calls=40*len(rows), foreign=rows,
                   data=dict(ordered_APU_MMC5_and_mapper_writes=True, full_AXYP_SP=True,
                             application_RAM_overlay_and_HUD_CHR_exact=True,
                             returned_dead_stack_bytes_excluded=True),
                   bindings={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in (Path(__file__), SOURCE)},
                   scope='Actual linked AudioUpdate calls with explicit CPU queues and current Mini cold loader. '
                         'No audio cache, ROM output, emulator run, waveform comparison or video deadline claim.')
    (args.output/'result.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(passed=True, expected_SHA256=sha(after), foreign_calls=receipt['foreign_calls'],
                          Mini={k:v for k,v in timing.items() if k != 'cycle_pairs'})))


if __name__ == '__main__':
    main()
