"""Preserve two exact, bounded source-only packets without expanding their trees."""
import hashlib
import json
from pathlib import Path
import zipfile

from prepare_selected_native_packet_v1 import R
from build_storage_guard_v1 import preflight

O = R / 'build/roster-source-checkpoint-1102-v3'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def freeze(manifest, archive, checkpoint, archive_hash, files, members):
    raw = archive.read_bytes()
    assert digest(raw) == archive_hash
    assert len(raw) < 100000
    with zipfile.ZipFile(archive) as z:
        for name, info in members.items():
            data = z.read(name)
            assert len(data) == info['bytes'] and digest(data) == info['SHA256'], name
        for name in files:
            assert (R / name).read_bytes() == z.read(name), name
    assert not checkpoint.exists(), checkpoint
    checkpoint.mkdir(parents=True)
    (checkpoint / 'inputs.zip').write_bytes(raw)
    (checkpoint / 'manifest.json').write_bytes(manifest.read_bytes())
    (checkpoint / 'commit-files.txt').write_text('\n'.join(files) + '\n', encoding='utf-8', newline='\n')
    return dict(checkpoint=str(checkpoint.relative_to(R)), SHA256=archive_hash,
                bytes=len(raw), source_files=files, native_gameplay=False)


def main():
    preflight(private_root=O, reserved_bytes=1000000, reserved_files=12, fresh=True)
    O.mkdir(exist_ok=True)
    bub = R / 'build/bubble-bobble-source-1101-v1/native-ingress-qualified-1102-v4.json'
    q = read(bub)
    rows = [freeze(bub, R / q['archive'],
                   R / 'docs/qa/checkpoints/2026-11-02/bubble-native-ingress-v4',
                   q['archive_SHA256'], q['source_files'], q['files'])]
    prince = R / 'build/prince-actor-1101-v1/source-supplement-v2-manifest.json'
    q = read(prince)
    with zipfile.ZipFile(R / q['ZIP']) as z:
        embedded = json.loads(z.read('manifest.json'))
    assert q['explicit_commit_files'] == embedded['explicit_commit_files']
    rows.append(freeze(prince, R / q['ZIP'],
                       R / 'docs/qa/checkpoints/2026-11-02/prince-source-supplement-v2',
                       q['SHA256'], q['explicit_commit_files'], embedded['members']))
    doc = R / 'docs/qa/bubble-bobble-readiness-1101.md'
    text = doc.read_text(encoding='utf-8')
    old = ('Status: original normal-play source recovered and CPU-checked. **No host bytes,\n'
           'raw character ID, menu entry, cache page, CHR page or resident span allocated.**\n'
           'No Mesen run, candidate ROM, installation or commit was performed by this work.\n'
           'Shinobi v29/v30 inputs were left intact.')
    assert old in text
    new = ('Current status (November 2): original-source and host-ingress CPU proofs are\n'
           'preserved in the source-only checkpoints. Conditional private storage and\n'
           'static menu resources have been granted; the private menu candidate passes\n'
           'all 33 positions in Mesen. Bub/Bob gameplay is not admitted or installed.\n'
           'The newer service/contact and trapped-enemy lifecycle work remains under\n'
           'review before a native gameplay candidate can be qualified. See the current\n'
           'continuation note and allocation receipts for exact ownership.\n\n'
           'The recovery narrative below records the original November 1 scope; its\n'
           'earlier “unallocated” proposals are historical, not current allocation status.')
    doc.write_text(text.replace(old, new, 1), encoding='utf-8', newline='\n')
    receipt = dict(passed=True, checkpoints=rows, ROM_written=False, native_gameplay=False)
    (O / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, checkpoint_bytes=sum(r['bytes'] for r in rows),
                          source_files=sum(len(r['source_files']) for r in rows))))


if __name__ == '__main__':
    main()
