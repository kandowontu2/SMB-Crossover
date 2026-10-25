"""Retain two superseded checkpoints externally before the next private freeze."""
from pathlib import Path
import datetime
import json
import os
from archive_workspace_hz import ROOT, ARCHIVE, bounded, inventory, sha


def records(folder):
    return {p.relative_to(folder).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))
            for p,n,t in inventory(folder)}


def main():
    qa=ROOT/'build/verification/proto-hurt-of';qa.mkdir(exist_ok=True)
    assert not(qa/'historical-archive-receipt.json').exists()
    receipt=json.loads((ROOT/'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    protected={str(p):sha(p)for p in [ROOT/'build/checkpoints/tmnt-hud-probes-oe/candidate.nes',
        ROOT/'build/checkpoints/tmnt-hud-probes-oe/source.zip',
        *[ROOT/f'build/smb-crossover-{n}.nes'for n in ['mmc3','mmc5','mmc3-oversized','mmc5-expanded']]]}
    plans=[]
    for name in ['tmnt-empty-render-nz','tmnt-world-render-oa']:
        relative='build/checkpoints/'+name
        source=bounded(ROOT/relative,ROOT/'build/checkpoints')
        target=bounded(ARCHIVE/relative,ARCHIVE)
        assert source.is_dir()and not target.exists()and source.drive.lower()==target.drive.lower()
        assert not any(q['relative']==relative for q in receipt['directories'])
        files=records(source)
        plans.append(dict(relative=relative,source=str(source),target=str(target),
                          bytes=sum(q['bytes']for q in files.values()),files=files))
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),moves=plans,deleted_files=0,
                reason='Closed NZ/OA checkpoints are superseded by accepted OE. Active sources, guide, published ROMs and current routes stay put. Historical build tools can locate the retained files through workspace_storage.py; one-shot finalizers must not be rerun.')
    (qa/'historical-archive-plan.json').write_text(json.dumps(report,indent=2)+'\n')
    additions=[]
    for plan in plans:
        source=Path(plan['source']);target=Path(plan['target'])
        target.parent.mkdir(parents=True,exist_ok=True);os.rename(source,target)
        assert records(target)==plan['files']
        additions.append(dict(relative=plan['relative'],bytes=plan['bytes'],files=len(plan['files'])))
    assert all(sha(Path(p))==digest for p,digest in protected.items())
    receipt['directories'].extend(additions)
    receipt['archived_bytes']+=sum(q['bytes']for q in additions)
    receipt['archived_files']+=sum(q['files']for q in additions)
    receipt.setdefault('additional_archives',[]).append(dict(utc=report['utc'],archive=str(ARCHIVE),moves=additions,
        archived_bytes=sum(q['bytes']for q in additions),all_files_sha256_verified=True,deleted_files=0))
    (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
    report.update(all_files_sha256_verified=True,protected_files=protected)
    (qa/'historical-archive-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(archived_bytes=sum(q['bytes']for q in additions),files=sum(q['files']for q in additions),deleted_files=0,all_files_sha256_verified=True)))


if __name__=='__main__':main()
