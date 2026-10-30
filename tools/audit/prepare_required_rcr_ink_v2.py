"""Keep RCR's intrinsic black pixels regardless of the optional shadow setting."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
P = R/'build/character-host-union-resources-v1/ice'
O = R/'build/required-rcr-ink-v2'
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not O.exists(), 'Fresh source/build output only'
    proof = json.loads((P/'build-proof.json').read_text())
    assert sha(P/'candidate.nes') == proof['ROM_sha256'] == '3925aa18859df68958ff782e5acc6558f877f1c0e81f22bd1e1ae54db9746ddb'
    for path, digest in proof['source_bindings'].items():
        assert sha(path) == digest, path
    recipe = [q['command'] for q in proof['commands']]
    assert len(recipe) == 2
    O.mkdir()
    logs = []

    def build(name, overrides):
        out = O/name
        out.mkdir()
        for file, text in overrides.items():
            (out/file).write_text(text, newline='\n')
        commands = []
        for index, old in enumerate(recipe):
            cmd = [token.replace(str(P), str(out)) for token in old]
            if index == 0:
                # Existing PN/Ice producers must continue resolving from P.
                old_index = cmd.index('-I')
                cmd[old_index:old_index] = ['-I', str(out), '-I', str(P)]
                (out/'entrypoint.s').write_bytes((P/'entrypoint.s').read_bytes())
                (out/'private.cfg').write_bytes((P/'private.cfg').read_bytes())
            result = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
            commands.append(dict(command=cmd, returncode=result.returncode,
                                 stdout=result.stdout, stderr=result.stderr))
            (out/'compile-log.json').write_text(json.dumps(commands, indent=2)+'\n')
            assert result.returncode == 0, result.stderr[-8000:]
        prepare(R, out/'candidate.nes')
        logs.append(dict(stage=name, commands=commands, ROM_sha256=sha(out/'candidate.nes')))
        return out

    reproduce = build('reproduce', {})
    assert (reproduce/'candidate.nes').read_bytes() == (P/'candidate.nes').read_bytes()
    wrapper = (R/'src/river_city.s').read_text()
    ink = (R/'src/river_city_shared_palette_host_v8.inc').read_text()
    for target in ['Ready', 'Done']:
        needle = ' lda PlayerOutlinesOff\n bne '+target+'\n'
        assert ink.count(needle) == 1
        ink = ink.replace(needle,
            ' ; Intrinsic source black is part of Alex/Ryan, even with Shadows OFF.\n'
            ' .res 5,$ea                    ; Keep all existing PCs/layout fixed.\n')
    include = '.include "river_city_shared_palette_host_v8.inc"'
    assert wrapper.count(include) == 1
    wrapper = wrapper.replace(include, '.include "river_city_required_ink_v1.inc"')
    candidate = build('candidate', {'river_city.s': wrapper, 'river_city_required_ink_v1.inc': ink})
    dep = (candidate/'main.d').read_text().replace('\\ ', ' ').replace('\\', '/')
    assert (candidate/'river_city.s').as_posix() in dep
    assert (candidate/'river_city_required_ink_v1.inc').as_posix() in dep
    old, new = scoped_load(P/'candidate.nes'), scoped_load(candidate/'candidate.nes')
    assert old['raw'][:16] == new['raw'][:16]
    assert old['raw'][1048592:] == new['raw'][1048592:]
    assert set(old['syms']) == set(new['syms'])
    assert all(s['val'] == new['syms'][name]['val'] for name, s in old['syms'].items())
    changes = [i for i, (a, b) in enumerate(zip(old['raw'], new['raw'])) if a != b]
    assert len(changes) == 10
    blocks = [changes[:5], changes[5:]]
    for part in blocks:
        assert part == list(range(part[0], part[0]+5))
        assert old['raw'][part[0]] == 0xad and old['raw'][part[0]+3] == 0xd0
        assert new['raw'][part[0]:part[0]+5] == bytes([0xea])*5
    bindings = dict(proof['source_bindings'])
    for path in [Path(__file__).resolve(), P/'build-proof.json',
                 R/'src/river_city.s', R/'src/river_city_shared_palette_host_v8.inc',
                 *[q for f in [reproduce, candidate] for q in f.iterdir() if q.is_file()]]:
        bindings[str(path)] = sha(path)
    report = dict(passed=True, native=False, source_only=True,
                  parent_ROM_sha256=sha(P/'candidate.nes'), ROM_sha256=sha(candidate/'candidate.nes'),
                  exact_parent_reproduction=True, changed_file_offsets=changes,
                  unchanged_header_CHR_all_symbol_values=True,
                  change='Remove only both RCR shadow-option checks: always compose sourcebody+ink and publish its inkCHR window. Other characters and global toggle untouched.',
                  commands=logs, bindings=bindings,
                  pending=['Actual source pixel/pose comparisons for Alex/Ryan with both settings.',
                           'Controller-only native menu/lives/gameplay check; Arthur handled separately.'],
                  shared_installation=False)
    (O/'build-proof.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, ROM_sha256=report['ROM_sha256'], changed_bytes=len(changes))))


if __name__ == '__main__':
    main()
