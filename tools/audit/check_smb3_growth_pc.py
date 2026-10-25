"""Compare every growth/shrink phase to actual authenticated original code."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import itertools
import json
import re
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / 'build/verification/smb3-mario-candidate-agent/auth-source'
ORIGINAL = Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def original_case(rom, symbols, form, timer, face):
    memory = [0] * 65536
    prg = rom[16:16 + 262144]
    for base, bank in ((0x8000, 30), (0xa000, 8), (0xc000, 29), (0xe000, 31)):
        memory[base:base + 8192] = prg[bank * 8192:(bank + 1) * 8192]
    memory[0x200:0x300] = [248 if i % 4 == 0 else 0 for i in range(256)]
    for n, v in dict(Player_X=64, Player_Y=64, Player_Grow=timer, Player_Suit=form,
                     Player_FlipBits=64 if face == 1 else 0).items():
        memory[symbols[n]] = v
    memory[0x1fe], memory[0x1ff] = 0xef, 0xff
    cpu = NesMPU(memory=memory, pc=symbols['PRG029_D224'])
    cpu.sp = 0xfd
    for _ in range(10000):
        if cpu.pc == 0xfff0:
            break
        cpu.step()
    else:
        raise AssertionError(('Original growth did not return', form, timer, face, hex(cpu.pc)))
    oam = Counter((memory[0x200 + i * 4], memory[0x201 + i * 4] & 254,
                   memory[0x202 + i * 4], memory[0x203 + i * 4]) for i in range(64) if memory[0x200 + i * 4] < 240)
    return dict(frame=memory[symbols['Player_Frame']], timer=memory[symbols['Player_Grow']],
                original_CHR=memory[symbols['PatTable_BankSel'] + 2], oam=oam)


def candidate_case(bundle, form, timer, face, variant):
    memory = Memory(bundle)
    values = dict(SelectedCharacter=17, M3Variant=variant, M3Marker=0xb3, M3Ready=0xb3,
                  M3Form=form, M3Growth=timer, OperMode=1, GameEngineSubroutine=8,
                  PlayerFacingDir=face, Player_Rel_XPos=64, Player_Y_Position=64, Player_Y_HighPos=1,
                  M3PaletteValid=0xb3, M3PaletteForm=1, M3PaletteVariant=variant)
    for n, v in values.items():
        memory[address(bundle, n)] = v
    memory[0x200:0x300] = [248 if i % 4 == 0 else 0 for i in range(256)]

    def call(name, x=0):
        pc = address(bundle, name)
        if 0xa000 <= pc < 0xe000:
            slot = (pc - 0x8000) // 8192
            bank = (location(bundle, name) - 16) // 8192
            memory.page(slot, bank)
            memory[address(bundle, 'CurrentBank' if slot == 1 else 'CurrentBankC')] = bank | 128
        memory[0x1fe], memory[0x1ff] = 0xef, 0xff
        cpu = NesMPU(memory=memory, pc=pc)
        cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p = 0xfd, 0, x, 0, 0x30
        for _ in range(50000):
            if cpu.pc == 0xfff0:
                return
            cpu.step()
        raise AssertionError(('Candidate did not return', name, form, timer, face, hex(cpu.pc)))

    call('M3Graphics')
    page = memory[address(bundle, 'SmChrBank')] + 256 * memory[address(bundle, 'M3SpritePageHi')]
    pointer = memory[address(bundle, 'SmPosePtr')] + 256 * memory[address(bundle, 'SmPosePtr') + 1]
    for n, v in dict(R0=pointer & 255, R1=pointer >> 8, R4=64, R5=0, R6=64, R7=1, R3=0).items():
        memory[address(bundle, n)] = v
    call('MetaspriteRenderLoop')
    oam = Counter(tuple(memory[0x200 + i * 4:0x204 + i * 4]) for i in range(64) if memory[0x200 + i * 4] < 240)
    return dict(frame=memory[address(bundle, 'M3RenderFrame')], timer=memory[address(bundle, 'M3Growth')],
                physical_CHR=page, oam=oam)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ('rom', 'baseline', 'output'):
        p.add_argument('--' + n, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(ORIGINAL) == '1ddc4b429490e298c05fa70389034107c0cb50f671c7c1baaa3f228224afc2e9'
    rom = ORIGINAL.read_bytes()
    rebuilt = (AUTH / 'smb3.nes').read_bytes()
    assert rom[16:] == rebuilt[16:]
    symbols = {n: int(v, 16) for n, v in re.findall(r'^(\w+)\s*=\s*\$([0-9A-Fa-f]+)', (AUTH / 'smb3.fns').read_text(), re.M)}
    old, new = load(a.baseline), load(a.rom)
    original_chr = rom[16 + 262144:]
    cases = 0
    prior_failures = []
    for form, timer, face, variant in itertools.product((0, 1), range(1, 48), (1, 2), (0, 1)):
        reference = original_case(rom, symbols, form, timer, face)
        results = [candidate_case(bundle, form, timer, face, variant) for bundle in (old, new)]
        for actual in results:
            assert actual['frame'] == reference['frame'] and actual['timer'] == reference['timer']
            assert actual['oam'] == reference['oam'], (form, timer, face, variant, actual['oam'], reference['oam'])
        pages = []
        expected = original_chr[reference['original_CHR'] * 1024:(reference['original_CHR'] + 1) * 1024]
        for bundle, actual in zip((old, new), results):
            at = 16 + 1048576 + actual['physical_CHR'] * 1024
            pages.append(bundle['raw'][at:at + 1024] == expected)
        if not pages[0]:
            prior_failures.append(dict(form=form, timer=timer, face=face, variant=variant,
                                       original_CHR=reference['original_CHR'], old_page=results[0]['physical_CHR'],
                                       new_page=results[1]['physical_CHR']))
        assert pages[1], (form, timer, face, variant, reference['original_CHR'], results[1]['physical_CHR'])
        cases += 1
    assert len(prior_failures) == 188 and all(r['form'] == 0 for r in prior_failures)
    q = dict(passed=True, accepted=False, ROM_sha256=sha(a.rom), baseline_ROM_sha256=sha(a.baseline), cases=cases,
             prior_wrong_CHR_cases=len(prior_failures), new_wrong_CHR_cases=0, prior_failures=prior_failures,
             actual_original_growth_and_renderer=True, original_ROM_sha256=sha(ORIGINAL),
             original_source_symbols_sha256=sha(AUTH / 'smb3.fns'), driver_sha256=sha(Path(__file__)),
             scope='Actual authenticated original PRG029_D224 growth/shrink block and Player_Draw execute for all47remaining timer values, two suit directions, both facings and both port identities. Both candidates execute their actual M3Graphics and linked metasprite renderer. Final frame, decremented timer, exact canonical OAM geometry/pattern/attributes and byte-identical original selected1KCHR must match. Original code is not replaced with a host phase formula. This component excludes native PPU timing, invulnerability blinking/palette and natural damage/pickup delivery, which require independent emulator checks.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps({k: q[k] for k in ('passed', 'cases', 'prior_wrong_CHR_cases', 'new_wrong_CHR_cases')}, indent=2))


if __name__ == '__main__':
    main()
