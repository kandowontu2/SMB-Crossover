"""Retain superseded OD/OE snapshots externally within the user's30GB cap."""
from pathlib import Path
import datetime
import json
import os
from archive_workspace_hz import ROOT,ARCHIVE,bounded,inventory,sha


def records(folder):
    return {p.relative_to(folder).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(folder)}


def main():
    qa=ROOT/'build/verification/collision-dispatch-oj';qa.mkdir(exist_ok=True)
    assert not(qa/'historical-archive-receipt.json').exists()
    receipt=json.loads((ROOT/'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()and not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    protected={str(p):sha(p)for p in [
        ROOT/'build/checkpoints/inventory-stack-og/candidate.nes',ROOT/'build/checkpoints/inventory-stack-og/source.zip',
        ROOT/'build/checkpoints/injury-page-of/candidate.nes',ROOT/'build/checkpoints/injury-page-of/source.zip',
        *[ROOT/f'build/smb-crossover-{n}.nes'for n in ['mmc3','mmc5','mmc3-oversized','mmc5-expanded']]]}
    # Every target is resolved and bounded before the first directory rename.
    plans=[]
    for name in ['tmnt-host-render-od','tmnt-hud-probes-oe']:
        relative='build/checkpoints/'+name
        source=bounded(ROOT/relative,ROOT/'build/checkpoints');target=bounded(ARCHIVE/relative,ARCHIVE)
        assert source.is_dir()and not target.exists()and source.drive.lower()==target.drive.lower()
        assert not any(x['relative']==relative for x in receipt['directories'])
        files=records(source)
        plans.append(dict(relative=relative,source=str(source),target=str(target),bytes=sum(x['bytes']for x in files.values()),files=files))
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),moves=plans,deleted_files=0,
        reason='OD/OE are superseded by OF and current OG. Current/immediate-parent snapshots, live sources, guide and published ROMs stay local. Every archived byte remains discoverable with workspace_storage.py; historical one-shot finalizers must not be rerun.')
    (qa/'historical-archive-plan.json').write_text(json.dumps(report,indent=2)+'\n')
    additions=[]
    for plan in plans:
        source=Path(plan['source']);target=Path(plan['target']);target.parent.mkdir(parents=True,exist_ok=True)
        os.rename(source,target);assert records(target)==plan['files']
        additions.append(dict(relative=plan['relative'],bytes=plan['bytes'],files=len(plan['files'])))
    assert all(sha(Path(p))==h for p,h in protected.items())
    receipt['directories'].extend(additions);receipt['archived_bytes']+=sum(x['bytes']for x in additions);receipt['archived_files']+=sum(x['files']for x in additions)
    receipt.setdefault('additional_archives',[]).append(dict(utc=report['utc'],archive=str(ARCHIVE),moves=additions,
        archived_bytes=sum(x['bytes']for x in additions),all_files_sha256_verified=True,deleted_files=0))
    (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
    report.update(all_files_sha256_verified=True,protected_files=protected)
    (qa/'historical-archive-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(archived_bytes=sum(x['bytes']for x in additions),files=sum(x['files']for x in additions),deleted_files=0,all_files_sha256_verified=True),indent=2))


if __name__=='__main__':main()
