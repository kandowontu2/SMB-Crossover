"""Preserve the qualified original Bub/Bob core without ROM or capture copies."""
import hashlib
import json
import zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha


def main():
    source = R / 'build/bubble-bobble-source-1101-v1/core-inputs.zip'
    assert sha(source) == 'd728361d2e88a0c4a0ee3a479331f795208fc28e4694f9d41d94ea1451f467d7'
    with zipfile.ZipFile(source) as archive:
        members = archive.infolist()
        assert len(members) == 16 and sum(row.file_size for row in members) == 1442912
        assert not any(Path(row.filename).suffix.lower() in ['.nes', '.dbg', '.png', '.mp4'] for row in members)
        rows = [dict(path=row.filename, bytes=row.file_size,
                     SHA256=hashlib.sha256(archive.read(row.filename)).hexdigest()) for row in members]
    destination = R / 'docs/qa/checkpoints/2026-11-02/bubble-bobble-source-v1'
    destination.mkdir(parents=True, exist_ok=True)
    assert not (destination / 'inputs.zip').exists()
    (destination / 'inputs.zip').write_bytes(source.read_bytes())
    manifest = dict(source_only=True, native_playable=False, archive_SHA256=sha(source),
                    archive_bytes=source.stat().st_size, expanded_bytes=1442912,
                    members=rows, allocation='docs/qa/allocations/bubble-bobble-1102-v1.json',
                    scope='Qualified original instruction/core/CHR source and aggregate CPU proofs only. '
                          'In-progress native leaves/frame/camera/service wiring excluded. '
                          'Resident loader/router, raw identity, menu and native gameplay remain incomplete.')
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    p = R / 'docs/qa/continuation-current.json'
    q = json.loads(p.read_text(encoding='utf-8'))
    q['Bub_Bob_resource_followup'] = dict(
        allocation=manifest['allocation'], source_checkpoint=str(destination.relative_to(R)),
        code_pages=[301, 305, 337, 362, 363, 440, 819, 666], art_pages=[441],
        conditional_RAM_only=True, resident_loader_granted=False, menu_admitted=False,
        native_playable=False, private_code_used_bytes=7906,
        remaining='Compile remaining update/camera/service glue within8160B body; source-fund resident '
                  'loader/auth/foreign-retirement/router. New base roster slot required, no existing family replacement. '
                  'Native owner enemy/trap/AI/contact wiring and actual gameplay still need qualification.')
    q['previous_goal_turn_classification'] = 'progress'
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(source_checkpoint=True, archive_bytes=source.stat().st_size,
                          members=len(members), native_playable=False)))


if __name__ == '__main__':
    main()
