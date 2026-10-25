"""Compare actual two-call routing up to the first existing render owner.

Render bodies are explicitly opaque in this component. Native measured arenas
must independently compare complete game loops before any acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, Memory, address, location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU

ENTRIES = {
    'graphics': dict(caller='PlayerGfxHandler', local=('PlayerGfxHandler', 'GuestDeathGraphicsReady'), skip=7,
                     targets=['RlGraphics', 'LmGraphicsGate', 'JnGraphics', 'M3Graphics', 'VvGraphics',
                              'TnGraphics', 'CdGraphics', 'KbGraphics', 'ExpandedGraphics']),
    'draw': dict(caller='KbDrawDispatch', local=('KbDrawDispatch',), skip=7,
                 targets=['RlDraw', 'LmDrawGate', 'JnDraw', 'M3DrawWorld', 'VvDraw', 'TnDraw',
                          'CdDrawWorld', 'KbDrawShots']),
}


def run(bundle, entry, spec):
    char, variant, accumulator, flags, x, y = spec
    desc = ENTRIES[entry]
    q = qualified(bundle['path'])
    offset = location(bundle, desc['caller']) + q[desc['local']] - address(bundle, desc['caller']) + desc['skip']
    caller_bank = (offset - 16) // 8192
    m = Memory(bundle)
    m.page(1, caller_bank)
    m[address(bundle, 'CurrentBank')] = caller_bank | 128
    for name, value in [('SelectedCharacter', char), ('RlVariant', variant)]:
        m[address(bundle, name)] = value
    code = bundle['raw'][offset:offset + 18]
    assert code[0] == 0x8d and code[3] == code[8] == code[13] == 0xa9
    assert code[-3] == (0x20 if entry == 'graphics' else 0x4c)
    m[0x7000:0x7013] = code + bytes([0x60])
    m[0x1fe] = 0xef
    m[0x1ff] = 0xff
    m.writes = []
    c = NesMPU(memory=m, pc=0x7000)
    c.sp, c.a, c.p, c.x, c.y = 0xfd, accumulator, flags, x, y
    if char == 9 and variant:
        owner = 'RlGraphics' if entry == 'graphics' else 'RlDraw'
    elif char == 15:
        owner = 'LmGraphicsGate' if entry == 'graphics' else 'LmDrawGate'
    elif char == 16:
        owner = 'JnGraphics' if entry == 'graphics' else 'JnDraw'
    elif char == 17:
        owner = 'M3Graphics' if entry == 'graphics' else 'M3DrawWorld'
    elif char == 18:
        owner = 'VvGraphics' if entry == 'graphics' else 'VvDraw'
    elif char == 19:
        owner = 'TnGraphics' if entry == 'graphics' else 'TnDraw'
    elif char == 14:
        owner = 'CdGraphics' if entry == 'graphics' else 'CdDrawWorld'
    elif char == 13:
        owner = 'KbGraphics' if entry == 'graphics' else 'KbDrawShots'
    else:
        owner = 'ExpandedGraphics' if entry == 'graphics' else 'KbDrawShots'
    assert owner in desc['targets']
    targets = {(address(bundle, owner), (location(bundle, owner) - 16) // 8192): owner}
    target = None
    minimum = c.sp
    for _ in range(4000):
        if c.pc == 0xfff0:
            break
        bank = m.banks[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else -1
        if (c.pc, bank) in targets:
            assert target is None
            target = (targets[(c.pc, bank)], c.a, c.x, c.y, c.p)
            # Explicit opaque-body RTS, preserving the actual admission state.
            c.pc = (c.stPopWord() + 1) & 65535
            c.processorCycles += 6
            continue
        c.step()
        minimum = min(minimum, c.sp)
    else:
        raise AssertionError(('router timeout', entry, spec, hex(c.pc), m.banks))
    assert target is not None
    ignored = set(range(0x100, 0x200)) | set(range(0x5114, 0x5118))
    for g in bundle['segs'].values():
        if g.get('name') == '"SMCCODE"':
            ignored.update(range(int(g['start'], 0), int(g['start'], 0) + int(g['size'], 0)))
    for name in ('safecall_a', 'SafecallA'):
        if name in bundle['syms']:
            ignored.add(address(bundle, name))
    application_writes = [(at, value) for at, value in m.writes if at not in ignored]
    assert not application_writes, application_writes
    assert c.sp == 0xff and m.banks == [126, caller_bank, 88, 127]
    assert m[address(bundle, 'CurrentBank')] == caller_bank | 128
    return dict(admission=target, result=(c.a, c.x, c.y, c.p, c.sp), cycles=c.processorCycles,
                stack=0xfd - minimum, mapper_writes=sum(at == 0x5115 for at, value in m.writes))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('rom', 'baseline', 'output'):
        p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    old['path'], new['path'] = a.baseline, a.rom
    # Cache qualified maps: the run helper deliberately accepts linked bundles.
    global qualified
    maps = {a.baseline: qualified(a.baseline), a.rom: qualified(a.rom)}
    qualified = lambda path: maps[path]
    cases = 0
    summaries = {}
    failures = []
    specs = set(itertools.product(range(20), (0, 1, 255), (0, 0x55, 255), (0x30, 0x71), (3, 254), (7, 129)))
    specs.update((char, variant, char, 0x71, 254, 129) for char, variant in itertools.product(range(256), (0, 255)))
    for entry in ENTRIES:
        by_char = {}
        for spec in sorted(specs):
            before, after = run(old, entry, spec), run(new, entry, spec)
            if before['admission'] != after['admission'] or before['result'] != after['result']:
                failures.append(dict(entry=entry, spec=spec, old=before, new=after))
            if spec[0] < 20:
                v = by_char.setdefault(str(spec[0]), dict(cases=0, saved_cycles_min=10000, saved_cycles_max=-10000,
                                                        old_max_stack=0, new_max_stack=0))
                saving = before['cycles'] - after['cycles']
                v['cases'] += 1
                v['saved_cycles_min'] = min(v['saved_cycles_min'], saving)
                v['saved_cycles_max'] = max(v['saved_cycles_max'], saving)
                v['old_max_stack'] = max(v['old_max_stack'], before['stack'])
                v['new_max_stack'] = max(v['new_max_stack'], after['stack'])
            cases += 1
        summaries[entry] = by_char
    q = dict(passed=not failures, accepted=False, cases=cases, failures=failures, summaries=summaries,
             ROM_sha256=hashlib.sha256(new['raw']).hexdigest(), baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
             driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             scope='Two actual assembled18-byte public calls and all bank/SMC wrappers execute. First existing render owner is explicitly an opaque RTS body. Exact owner/A/X/Y/fullP admission, return registers/SP, no application writes and final bank mappings are required. Legal IDs include original and Roll alternate, arbitrary input A, flags and register seeds; all256selected IDs are sampled including fallback. Isolated router savings are not full renderer, IRQ/NMI, native timing, physical-frame or campaign evidence.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(dict(passed=q['passed'], cases=cases, mismatches=len(failures), first_failure=failures[:1]), indent=2))
    return 0 if q['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
