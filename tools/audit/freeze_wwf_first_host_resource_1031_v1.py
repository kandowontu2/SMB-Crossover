"""Preserve the current-cart source proof and conditional first-Hogan lease."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
P = R / 'build/wwf-ready74-first-host-resource-v1'
O = R / 'docs/qa/checkpoints/2026-10-31/wwf-ready74-first-host-resource-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    assert not O.exists()
    contract = json.loads((P / 'resource-contract.json').read_text())
    assert contract['passed'] and contract['exact_current_layout_reproduced'] and contract['all_labels_exact']
    for path, digest in contract['bindings'].items():
        assert sha(path) == digest, path
    files = [P / name for name in ['resource-contract.json', 'candidate.cfg', 'link.json',
                                  'candidate.map', 'candidate.cv3-mirror.json']]
    files += [Path(__file__), R / 'tools/audit/rebind_wwf_first_host_resources_1031_v1.py']
    O.mkdir(parents=True)
    archive = O / 'source-proof.zip'
    members = {}
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in files:
            relative = path.relative_to(R).as_posix()
            bundle.write(path, relative)
            members[relative] = sha(path)
    with zipfile.ZipFile(archive) as bundle:
        assert set(bundle.namelist()) == set(members)
        for name, digest in members.items():
            assert hashlib.sha256(bundle.read(name)).hexdigest() == digest
    dump(O / 'resource-contract.json', contract)
    dump(O / 'archive-members.json', members)
    (O / 'README.md').write_text(
        'Root rechecked the retained CHR owner tails and existing Mike bank on installed Ready74, '
        'then reproduced every ROM byte and public/private label with explicit retained-tail CFG splits. '
        'The contract grants only a private first-Hogan source integration:43 CHR pages, the5834-byte '
        'Mike tail at physical96 A936..<C000 and conditional selected RAM1/2/3. '
        'All existing Mike code/data/endpoints remain fixed. The other88 tail pages remain unallocated. '
        'No new hooks, audio gate, native launch, character admission or installation is authorized by this source proof.\n',
        encoding='utf-8', newline='\n')
    dump(O / 'handoff.json', dict(status='SOURCE_PROVEN_CONDITIONAL_FIRST_HOGAN_RESOURCES',
         native=False, installed=False, current_ROM_sha256=contract['current_sha256'],
         root_first_host_grant=contract['root_first_host_grant'],
         bindings={**contract['bindings'], **{str(path): sha(path) for path in files}},
         archive=dict(path=str(archive), sha256=sha(archive), bytes=archive.stat().st_size,
                      members=len(members))))
    print(json.dumps(dict(passed=True, handoff_sha256=sha(O / 'handoff.json'),
                         members=len(members), archive_bytes=archive.stat().st_size)))


if __name__ == '__main__':
    main()
