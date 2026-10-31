"""Verify and copy the frozen, non-admitted two-Bowser source packet for Git."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
P = R / 'build/bowser-source-core-v5'
O = R / 'docs/qa/checkpoints/2026-10-30/bowser-original-source-core'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    h = P / 'handoff.json'
    assert sha(h) == '320978b43bad08b58c4b4f9b9718df5a1a1e66bb9b4251abad327794646460a3'
    q = json.loads(h.read_text())
    assert len(q['bindings']) == 80
    for p, expected in q['bindings'].items():
        assert sha(p) == expected, p
    with zipfile.ZipFile(P / 'source-only.zip') as z:
        assert z.testzip() is None
        assert len(z.namelist()) == 71
        for rel in z.namelist():
            assert hashlib.sha256(z.read(rel)).hexdigest() == sha(R / rel), rel
    assert not O.exists()
    O.mkdir(parents=True)
    for name in ['handoff.json', 'source-only.zip', 'HANDOFF.txt',
                 'resource-proposal.json', 'host-API-proposal.json', 'controls-v5.json',
                 'bowser1-right.png', 'bowser1-left.png']:
        shutil.copyfile(P / name, O / name)
    own_tools = sorted({Path(p) for p in q['bindings'] if Path(p).suffix == '.py'
                        and Path(p).parent == R / 'tools/audit'} | {Path(__file__).resolve()})
    receipt = dict(status='VERIFIED_ORIGINAL_SOURCE_CORE_NOT_HOST_ADMISSION',
                   source=True, host=False, native=False, admitted=False,
                   source_handoff=sha(h), source_bindings=80, archive_members=71,
                   parent=q['parent'], measured=q['measured'],
                   controls='Actual original integrator/gravity instruction comparisons and abstract controller sequences; no native world/contact claim.',
                   bindings={str(p.resolve()): sha(p) for p in sorted(O.iterdir())},
                   tools={str(p.resolve()): sha(p) for p in own_tools})
    (O / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    owned = [p.relative_to(R).as_posix() for p in own_tools]
    owned += [p.relative_to(R).as_posix() for p in sorted(O.iterdir())]
    owned += [(O / 'owned-files.txt').relative_to(R).as_posix()]
    (O / 'owned-files.txt').write_text('\n'.join(owned) + '\n')
    print(json.dumps(dict(checkpoint=str(O), receipt=sha(O / 'receipt.json'),
                          owned_files=len(owned), verified_bindings=80,
                          native=False, admitted=False)))


if __name__ == '__main__':
    main()
