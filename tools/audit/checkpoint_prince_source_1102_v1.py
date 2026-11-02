"""Preserve the exact original Prince source proposal and its reviewed grant."""
import hashlib
import json
import zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

P = R / 'build/prince-actor-1101-v1'
O = R / 'build/prince-resources-1102-v1'
PIN = '2d9ec3124b61ccfb8a06fe616206d09ca5d0fd8d2b97a014a778db2d98b62e21'


def main():
    source = P / 'source-checkpoint.zip'
    assert sha(source) == PIN
    description = json.loads((P / 'source-checkpoint-manifest.json').read_text(encoding='utf-8'))
    assert description['passed'] and description['sha256'] == PIN
    with zipfile.ZipFile(source) as archive:
        members = archive.infolist()
        assert len(members) == 20
        assert not any(Path(row.filename).suffix.lower() in ['.nes', '.dbg', '.png', '.mp4'] for row in members)
        rows = [dict(path=row.filename, bytes=row.file_size,
                     SHA256=hashlib.sha256(archive.read(row.filename)).hexdigest()) for row in members]
        for row in rows:
            # The readiness note can acquire a later status addendum. Frozen
            # compiler/recovery source and the allocation remain exact.
            if row['path'].startswith('tools/') or row['path'].startswith('docs/qa/allocations/'):
                assert sha(R / row['path']) == row['SHA256'], row['path']
    cp = R / 'docs/qa/checkpoints/2026-11-02/prince-source-core-v1'
    cp.mkdir(parents=True, exist_ok=True)
    assert not (cp / 'inputs.zip').exists()
    (cp / 'inputs.zip').write_bytes(source.read_bytes())
    manifest = dict(source_only=True, native_playable=False, archive_SHA256=PIN,
                    archive_bytes=source.stat().st_size, members=rows,
                    explicit_commit_files=description['explicit_commit_files'],
                    allocation='docs/qa/allocations/prince-1102-v1.json',
                    scope='Original actor, control, script, world and art recovery plus finite consumer proofs. '
                          'Conditional backing storage is granted; resident bootstrap, real host callbacks, '
                          'menu confirmation and native stage traversal remain incomplete.')
    (cp / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (cp / 'commit-files.txt').write_text('\n'.join(description['explicit_commit_files']) + '\n', encoding='utf-8')
    p = R / 'docs/qa/continuation-current.json'
    q = json.loads(p.read_text(encoding='utf-8'))
    q['Prince_resource_followup'] = dict(
        allocation=manifest['allocation'], source_checkpoint=str(cp.relative_to(R)),
        physical_CHR_pages=42, payload_bytes=42579, physical_spare_bytes=429,
        conditional_RAM_only=True, resident_loader_granted=False,
        menu_admitted=False, native_playable=False,
        remaining='Original core has 20 explicit environment callbacks. Bind actual host services, '
                  'source-fund shared cold loader/routing and qualify controls, art, contacts and full 1-1.')
    q['Bub_Bob_resource_followup'].update(
        rebase='docs/qa/allocations/bubble-bobble-rebase-1102-v2.json',
        private_code_used_bytes=8155,
        remaining='Private whole-update/camera model passes. Actual host entry, per-owner enemy AI/contact '
                  'admission, common cold loader/authentication/retirement and new base menu slot remain incomplete.')
    q['previous_goal_turn_classification'] = 'progress'
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    (O / 'source-checkpoint.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(source_checkpoint=True, archive_bytes=source.stat().st_size,
                          members=len(members), native_playable=False)))


if __name__ == '__main__':
    main()
