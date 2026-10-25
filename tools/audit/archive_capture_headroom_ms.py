"""Preserve two deferred Rygar capture packets outside the30GB workspace."""
from pathlib import Path
import datetime,json,os
from archive_workspace_hz import ROOT,ARCHIVE,inventory,bounded,sha

def main():
    output=ROOT/'build/verification/workspace-headroom-ms'
    assert not output.exists();output.mkdir(parents=True)
    receipt=json.loads((ROOT/'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
    assert ARCHIVE.drive.lower()==ROOT.drive.lower()
    moves=[];records={}
    for name in ('root-rygar-palette-av-fy-7-v0-mmc3','root-rygar-current-fl-av-fq-7-v0-mmc3'):
        source=bounded(ROOT/'build/roster-through-2-2'/name,ROOT/'build/roster-through-2-2')
        relative=source.relative_to(ROOT);target=bounded(ARCHIVE/relative,ARCHIVE)
        assert source.is_dir() and not target.exists()
        found=list(inventory(source))
        records[name]={p.relative_to(source).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p)) for p,n,t in found}
        moves.append(dict(relative=relative.as_posix(),bytes=sum(n for _,n,_ in found),files=len(found)))
    (output/'plan.json').write_text(json.dumps(dict(moves=moves,files=records),indent=2)+'\n')
    for item in moves:
        source=bounded(ROOT/item['relative'],ROOT/'build/roster-through-2-2')
        target=bounded(ARCHIVE/item['relative'],ARCHIVE)
        assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
        os.rename(source,target)
        after={p.relative_to(target).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p)) for p,n,t in inventory(target)}
        assert after==records[source.name]
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(ARCHIVE),moves=moves,archived_bytes=sum(x['bytes'] for x in moves),all_files_sha256_verified=True,deleted_files=0,lossless_recordings_retained=True)
    receipt['directories'].extend(moves)
    receipt['archived_bytes']+=report['archived_bytes'];receipt['archived_files']+=sum(x['files'] for x in moves)
    receipt.setdefault('additional_archives',[]).append(report)
    (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
