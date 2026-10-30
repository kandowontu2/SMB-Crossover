"""Apply the qualified mandatory RCR ink source to the installed menu lineage."""
from pathlib import Path
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
P = R/'build/full-roster-menu-v5'
O = R/'build/required-rcr-ink-shared-v3'
Q = R/'build/required-rcr-ink-v2'
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
from prepare_required_rcr_ink_v2 import sha
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load


def main():
    assert not O.exists()
    closure = json.loads((P/'source-closure.json').read_text())
    controls = json.loads((Q/'controls.json').read_text())
    assert controls['passed'] and len(controls['actual_original_pixel_pose_pairs']) == 144
    assert sha(P/'candidate.nes') == '5b09a3ed02aa678fb1d6fca57d905224e95c7b8f0f4e12f13901bf3f41f12d1e'
    for path, digest in closure['actual_ASM_dependencies'].items():
        assert sha(path) == digest, path
    for path, digest in controls['bindings'].items():
        assert sha(path) == digest, path
    O.mkdir()
    logs = []
    previous_output = R/'build/full-roster-menu-independent-v5'
    for stage in ['reproduce', 'candidate']:
        out = O/stage
        out.mkdir()
        if stage == 'candidate':
            for name in ['river_city.s', 'river_city_required_ink_v1.inc']:
                (out/name).write_bytes((Q/'candidate'/name).read_bytes())
        commands = []
        for index, old in enumerate(closure['commands']):
            cmd = [token.replace(str(previous_output), str(out)) for token in old]
            if index == 0:
                cmd[1:1] = ['-I', str(out)]
            result = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
            commands.append(dict(command=cmd, returncode=result.returncode,
                                 stdout=result.stdout, stderr=result.stderr))
            (out/'compile-log.json').write_text(json.dumps(commands, indent=2)+'\n')
            assert result.returncode == 0, result.stderr[-8000:]
        prepare(R, out/'candidate.nes')
        logs.append(dict(stage=stage, commands=commands, ROM_sha256=sha(out/'candidate.nes')))
    assert (O/'reproduce/candidate.nes').read_bytes() == (P/'candidate.nes').read_bytes()
    old, new, qualified = [scoped_load(p) for p in [P/'candidate.nes', O/'candidate/candidate.nes',
                                                  Q/'candidate/candidate.nes']]
    assert set(old['syms']) == set(new['syms'])
    assert all(s['val'] == new['syms'][name]['val'] for name, s in old['syms'].items())
    differences = [i for i, (a,b) in enumerate(zip(old['raw'],new['raw'])) if a != b]
    expected = json.loads((Q/'build-proof.json').read_text())['changed_file_offsets']
    assert differences == expected and len(differences) == 10
    for at in differences:
        assert new['raw'][at] == qualified['raw'][at] == 0xea
    bindings = dict(closure['actual_ASM_dependencies'])
    for path in [Path(__file__).resolve(), P/'source-closure.json', Q/'build-proof.json', Q/'controls.json',
                 Q/'candidate/river_city.s', Q/'candidate/river_city_required_ink_v1.inc',
                 *[p for name in ['reproduce','candidate'] for p in (O/name).iterdir() if p.is_file()]]:
        bindings[str(path)] = sha(path)
    report = dict(passed=True, native=False, parent_ROM_sha256=sha(P/'candidate.nes'),
                  ROM_sha256=sha(O/'candidate/candidate.nes'),
                  exact_parent_reproduction=True, changed_file_offsets=differences,
                  exact_same_qualified_ten_source_bytes=True,
                  header_CHR_all_other_code_and_all_symbol_values_exact=True,
                  source_pixel_proof=str(Q/'controls.json'), source_pixel_proof_sha256=sha(Q/'controls.json'),
                  commands=logs, bindings=bindings, shared_installation=False,
                  reason='Small source repair for the current downloadable build, independent of the unfinished host-integration branch.')
    (O/'build-proof.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, ROM_sha256=report['ROM_sha256'], changed_bytes=10)))


if __name__ == '__main__':
    main()
