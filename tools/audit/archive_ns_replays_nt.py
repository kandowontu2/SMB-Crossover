"""Retain the finished NS fixed replays outside the capped workspace."""
from pathlib import Path
import datetime
import json
import os
from archive_workspace_hz import ROOT, ARCHIVE, inventory, bounded, sha


def main():
    out = ROOT/'build/verification/little-mac-star-nt/archive-ns-replays'
    out.mkdir(parents=True, exist_ok=False)
    receipt = json.loads((ROOT/'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve() == ARCHIVE.resolve()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    assert ARCHIVE.drive.lower() == ROOT.drive.lower()
    checkpoint = ROOT/'build/checkpoints/parodius-performance-ns'
    wanted = sha(checkpoint/'candidate.nes')
    moves = []
    for pilot in ('octopus', 'twinbee', 'pentarou'):
        for mode in ('easy', 'hard'):
            source = bounded(ROOT/f'build/verification/parodius-performance-ns/replay-{pilot}-{mode}-v4', ROOT/'build/verification/parodius-performance-ns')
            relative = source.relative_to(ROOT)
            target = bounded(ARCHIVE/relative, ARCHIVE)
            assert source.is_dir() and not target.exists()
            manifest = json.loads((source/'manifest.json').read_text())
            assert manifest['ROM_sha256'] == wanted and manifest['exit'] == 0
            assert manifest['fixed_replay'] and manifest['result']['cleared'] and manifest['result']['deaths'] == 0
            assert manifest['chr_commit']['passed']
            for field, name in [('inputs_sha256', 'inputs.csv'), ('policy_sha256', 'policy.lua'), ('harness_sha256', 'harness.lua')]:
                assert sha(source/name) == manifest[field]
            files = {p.relative_to(source).as_posix(): dict(bytes=n, mtime_ns=t, sha256=sha(p)) for p, n, t in inventory(source)}
            item = dict(relative=relative.as_posix(), bytes=sum(v['bytes'] for v in files.values()), files=len(files))
            moves.append((source, target, item, files))
    (out/'plan.json').write_text(json.dumps([dict(source=str(s), target=str(t), move=i, files=f) for s,t,i,f in moves], indent=2)+'\n')
    for source, target, item, files in moves:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.rename(source, target)
        assert {p.relative_to(target).as_posix(): dict(bytes=n, mtime_ns=t, sha256=sha(p)) for p,n,t in inventory(target)} == files
    items = [i for _,_,i,_ in moves]
    report = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), archive=str(ARCHIVE), moves=items,
                  archived_bytes=sum(i['bytes'] for i in items), all_files_sha256_verified=True, deleted_files=0,
                  checkpoint_rom_source_and_top_level_route_proof_remain_local=True)
    receipt['directories'].extend(items)
    receipt['archived_bytes'] += report['archived_bytes']
    receipt['archived_files'] += sum(i['files'] for i in items)
    receipt.setdefault('additional_archives', []).append(report)
    (ROOT/'workspace-archive.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (out/'receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
