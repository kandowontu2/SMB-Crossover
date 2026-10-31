"""Freeze the verified private frontend; this does not install SMB2J."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
S = R / 'build/smb2j-campaign-menu-source-1031-v7'
C = R / 'build/smb2j-campaign-menu-controls-1031-v3/controls.json'
N = R / 'build/smb2j-campaign-menu-native-1031-v1/peach'
D = R / 'docs/qa/checkpoints/2026-10-31/smb2j-campaign-frontend-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(name, data):
    (D / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    assert not D.exists()
    stage = json.loads((S / 'source-stage.json').read_text())
    checks = json.loads(C.read_text())
    ready = json.loads((N / 'ready.json').read_text())
    binding = json.loads((N / 'capture/binding.json').read_text())
    native = json.loads((N / 'capture/result.json').read_text())
    assert stage['passed'] and checks['passed'] and native['passed']
    assert binding['exit_code'] == 0 and native['SMB2J_implemented'] is False
    digest = stage['candidate']
    assert digest == checks['candidate'] == ready['ROM_sha256'] == native['ROM_sha256']
    bound = {}
    for receipt in [stage, checks, ready, binding]:
        for name, expected in receipt['bindings'].items():
            assert sha(name) == expected, name
            bound[name] = expected
    refs = [Path(__file__), S / 'source-stage.json', C, N / 'ready.json',
            N / 'run.py', N / 'controller.lua', *sorted((N / 'capture').glob('*'))]
    refs += list(S.glob('*-build.json')) + list(S.glob('*-link.json'))
    refs += [p for p in (S / 'joint/src').glob('*') if p.suffix in ['.s', '.inc']]
    refs += [S / 'joint/entrypoint.s', S / 'joint/candidate.cfg']
    refs += sorted((R / 'tools/audit').glob('prepare_smb2j_campaign_menu_1031_v*.py'))
    refs += sorted((R / 'tools/audit').glob('check_smb2j_campaign_menu_1031_v*.py'))
    refs += sorted((R / 'tools/reference').glob('smb2j_campaign_*1031_v*.inc'))
    refs += [R / 'tools/reference/smb2j_campaign_menu_native_1031_v1.lua']
    refs += [R / 'build/smb2j-campaign-menu-controls-1031-v2/controls.json']
    assert len(list((N / 'capture').glob('*.png'))) == 4
    assert all(p.suffix.lower() not in ['.nes', '.fds', '.chr', '.o', '.exe', '.dbg'] for p in refs)
    refs = sorted(set(refs))
    D.mkdir(parents=True)
    save('scope.json', dict(passed=True, source_CPU=True, bounded_native=True,
         installed=False, campaign_complete=False, candidate=digest,
         menu_profiles=86, playable_profiles=74, pending_profiles=12,
         behavior=['Character confirm opens two named game choices.',
                   'B returns to the character page retaining the selected alternate.',
                   'The SMB1 choice follows the existing real start and gameplay path.',
                   'The SMB2J choice is guarded until its actual engine is connected.'],
         native='Cold AllZeros controller-only Peach sequence, both actual PPU text rows/cursor, guarded2J confirm, B return, actual SMB1 parser/entrance and180controlled video frames.',
         source_checks=checks['counters'], new_global_and_ZP_bytes=0,
         private_resources=['Bank29 B640..<B830 (496B), old menu helper405B mask funding.',
                            'Bank66 B0C0..<B130 (112B), original116B source-declared tail.'],
         negative_ledger=['v1/v3 did not assemble: relocatable padding and macro-name collision.',
                          'v2/v4/v5 checks failed on private debug aliases or inherited405B mask shifts.',
                          'v6 revealed a real unbanked near-call defect: PROTO_MENU is physical66 while the new body is29. Never installed or native-run.',
                          'v7 places all tiny near helpers in66 and uses genuine FarCallCommon for every edge into29 and back.',
                          'controls-v2 expected18 glyphs for the19-character second title; the emitted command was correct. v3 corrects the fixture length.'],
         limits=['No SMB2J loader, campaign, new mechanics, ending or save is installed.',
                 'Native coverage is one Peach frontend/SMB1 opening sequence, not every character or a full-level clear.']))
    refs.append(D / 'scope.json')
    members = {p.relative_to(R).as_posix(): sha(p) for p in refs}
    with zipfile.ZipFile(D / 'source-and-native.zip', 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in refs:
            z.write(path, path.relative_to(R).as_posix())
    with zipfile.ZipFile(D / 'source-and-native.zip') as z:
        assert set(z.namelist()) == set(members)
        for name, expected in members.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == expected
    save('source-members.json', members)
    save('handoff.json', dict(passed=True, source=True, bounded_native=True,
         installed=False, campaign_complete=False, candidate=digest,
         parent=stage['parent'], native_updates=native['main_updates'],
         source_counters=checks['counters'], archive_sha256=sha(D / 'source-and-native.zip'),
         archive_members=len(members), archive_bytes=(D / 'source-and-native.zip').stat().st_size,
         bindings={**bound, **{str(p.resolve()): sha(p) for p in refs}}))
    (D / 'README.md').write_text(
        '# Private SMB1 / SMB2J frontend\n\n'
        'The two-choice screen passes86 source menu profiles and a cold controller-only '
        'Mesen sequence. Four reviewed PNGs show each game choice, return to Peach and '
        'real SMB1 gameplay. The original unbanked prototype was caught before any '
        'installation; the qualified version uses actual bank transports.\n\n'
        'This is an uninstalled frontend component. SMB2J deliberately declines launch '
        'until its campaign engine, level objects, progression, save conversion and '
        'character compatibility are connected and verified. The installed build '
        'remains a441 /74playable identities.\n', encoding='utf-8', newline='\n')
    owned = [p.relative_to(R).as_posix() for p in refs if p.is_relative_to(R / 'tools')]
    owned += [p.relative_to(R).as_posix() for p in D.iterdir() if p.is_file()]
    owned.append((D / 'owned-files.json').relative_to(R).as_posix())
    save('owned-files.json', dict(files=sorted(set(owned))))
    print(json.dumps(dict(passed=True, installed=False, campaign_complete=False,
          handoff_sha256=sha(D / 'handoff.json'), archive_bytes=(D / 'source-and-native.zip').stat().st_size)))


if __name__ == '__main__':
    main()
