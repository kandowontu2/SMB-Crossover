"""Source-build the corrected V1 art as a normal Mario rendering skin."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from prepare_cv3_dmc_mirror import prepare
from finalize_ff_current_component_v3 import dependencies

ART = R / 'build/kamikaze-v1-skin-art-1030-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def execute(d, cmd, name):
    r = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
    (d / (name + '.json')).write_text(json.dumps(dict(command=cmd, returncode=r.returncode,
        stdout=r.stdout, stderr=r.stderr), indent=2) + '\n')
    assert r.returncode == 0, r.stderr[-2500:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    p, o = a.parent.resolve(), a.output.resolve()
    assert not o.exists()
    report = json.loads((p / 'source-closure.json').read_text())
    bindings = report['bindings']
    for f, h in bindings.items():
        assert sha(f) == h, f
    art = json.loads((ART / 'art.json').read_text())
    assert art['passed'] and art['matched_tiles'] == 240
    for f, h in art['bindings'].items():
        assert sha(f) == h, f
    old = scoped_load(p / 'candidate.nes')
    o.mkdir(parents=True)
    for f in p.rglob('*'):
        if f.is_file() and f.suffix in ['.s', '.inc', '.cfg', '.bin', '.chr']:
            target = o / f.relative_to(p)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(f.read_bytes())
    skin = o / 'src/kamikaze_mario_render_v2.inc'
    text = skin.read_text()
    for name, end, body_bytes, replacement in [
        ('KmSelect', 'KmPortrait', 33, ''' lda SelectedCharacter
 bne Done
 lda MarioVariant
 cmp #3
 bne Done
 lda X5ChrMode
 cmp #$84
 beq ModeReady
 lda #$84
 sta X5ChrMode
 inc ReloadCHRBank
ModeReady:
 lda #1
 sta X5WideChrActive
Done:rts
'''),
        ('KmPortrait', 'KmFrameMap', 21, ''' jsr KmSelect
 farcall CmHostPortraitRender,jmp
'''),
    ]:
        start = text.index('.proc ' + name + '\n')
        stop = text.index('.endproc', start) + len('.endproc')
        length = address(old, end) - address(old, name)
        replacement = ('.proc ' + name + '\n' + replacement
                       + f' .res {length-body_bytes},$ea\n'
                       + f' .assert *-{name}={length},lderror,"Keep original Kamikaze entry PCs"\n.endproc')
        text = text[:start] + replacement + text[stop:]
    skin.write_text(text, newline='\n')
    gfx = o / 'src/samus.s'
    text = gfx.read_text()
    needle = 'Kamikaze:\n  lda #62|MMC5_PRG_ROM'
    assert text.count(needle) == 1
    text = text.replace(needle, 'Kamikaze:\n  lda #.bank(MmMM_HAIR_STANDRight)|MMC5_PRG_ROM')
    gfx.write_text(text, newline='\n')
    chrsource = R / 'build/kamikaze-mario-host-v4/kamikaze_chr.s'
    text = chrsource.read_text()
    needle = '.incbin "chr/characters/kamikaze-mario-source-v2.chr"'
    assert text.count(needle) == 1
    text = text.replace(needle, '.incbin "' + (ART / 'kamikaze-mario-v1.chr').as_posix() + '"')
    (o / 'skin.s').write_text(text, newline='\n')
    phases = ['main', 'rogue-component', 'union', 'bbox-local', 'gm-nmi', 'dk-component', 'reader']
    for name in phases:
        cmd = json.loads((p / (name + '-build.json')).read_text())['command']
        execute(o, [x.replace(str(p), str(o)) for x in cmd], name + '-build')
    cmd = [str(R / 'tools/Windows/cc65/bin/ca65.exe'), '-g', '--cpu', '6502x',
           '--create-full-dep', str(o / 'skin.dep'), '-o', str(o / 'skin.o'), str(o / 'skin.s')]
    execute(o, cmd, 'skin-build')
    cmd = json.loads((p / 'link-build.json').read_text())['command']
    cmd = [x.replace(str(p), str(o)) for x in cmd]
    source_object = str(R / 'build/character-host-union-v13/skin.o')
    assert cmd.count(source_object) == 1
    cmd[cmd.index(source_object)] = str(o / 'skin.o')
    execute(o, cmd, 'link-build')
    prepare(R, o / 'candidate.nes')
    new = scoped_load(o / 'candidate.nes')
    moved = [n for n, s in old['syms'].items() if 'seg' in s and '::' not in n
             and n in new['syms'] and s['val'] != new['syms'][n]['val']]
    assert not moved, moved
    spans = [(location(old, 'KmSelect'), location(old, 'KmFrameMap')),
             (location(old, 'CrossoverGraphicsBank') + 58, location(old, 'CrossoverGraphicsBank') + 59),
             (1048592 + 696 * 1024, 1048592 + 700 * 1024)]
    diffs = [i for i, (x, z) in enumerate(zip(old['raw'], new['raw'])) if x != z]
    # The one CrossoverGraphicsBank immediate is found from its actual opcode,
    # rather than accepting the whole resident capsule as a change allowance.
    bankdiff = [i for i in diffs if location(old, 'CrossoverGraphicsBank') <= i
                < location(old, 'CrossoverGraphicsBank') + 68]
    assert len(bankdiff) == 1 and old['raw'][bankdiff[0]] == 190
    assert new['raw'][bankdiff[0]] == ((location(old, 'MmMM_HAIR_STANDRight') - 16) // 8192 | 128)
    spans[1] = (bankdiff[0], bankdiff[0] + 1)
    # The existing native DMC mirror duplicates fixed127 code in physical125.
    # Require both complete capsules byte-identical before and after, allowing
    # only this same single immediate in the genuine mirror copy.
    mirror = bankdiff[0] - 2 * 8192
    capsule = location(old, 'CrossoverGraphicsBank')
    assert old['raw'][capsule:capsule + 68] == old['raw'][capsule - 16384:capsule - 16384 + 68]
    assert new['raw'][capsule:capsule + 68] == new['raw'][capsule - 16384:capsule - 16384 + 68]
    spans.append((mirror, mirror + 1))
    assert all(any(lo <= i < hi for lo, hi in spans) for i in diffs), 'Foreign bytes changed'
    files = set(map(Path, bindings))
    for f in o.glob('*.dep'):
        files.update(dependencies(f))
    files |= {f for f in o.rglob('*') if f.is_file()}
    files |= {Path(__file__), p / 'source-closure.json', ART / 'art.json', ART / 'kamikaze-mario-v1.chr', chrsource}
    result = dict(passed=True, native=False, ROM_sha256=sha(o / 'candidate.nes'),
                  parent_sha256=sha(p / 'candidate.nes'), source_Kamikaze_ROM=art['source_ROM'],
                  changed_bytes=len(diffs), all_old_global_entry_PCs_exact=True,
                  changes=['Native Mario descriptors/CHR animation pages retained, replacing custom four-part renderer.',
                           'V1 original sprite tile indices and ordinary Mario palette preserved.',
                           'Only Kamikaze rendering adapters, its bank immediate and existing four CHR pages change.'],
                  controls_pending=True, bindings={str(f.resolve()): sha(f) for f in sorted(files)})
    (o / 'source-closure.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'bindings'}))


if __name__ == '__main__':
    main()
