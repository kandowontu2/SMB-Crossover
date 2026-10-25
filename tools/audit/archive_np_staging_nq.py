"""Retain completed NP roundtrip staging in the verified external archive."""
from pathlib import Path
import datetime,json,os
from archive_workspace_hz import ROOT,ARCHIVE,inventory,bounded,sha


def main():
 output=ROOT/'build/verification/parodius-render-nq/archive-np-staging'
 output.mkdir(exist_ok=False)
 receipt=json.loads((ROOT/'workspace-archive.json').read_text())
 assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
 assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())and ARCHIVE.drive.lower()==ROOT.drive.lower()
 source=bounded(ROOT/'build/verification/chr-publication-np/snapshot-v2',ROOT/'build/verification/chr-publication-np')
 relative=source.relative_to(ROOT);target=bounded(ARCHIVE/relative,ARCHIVE)
 assert source.is_dir()and not target.exists()
 found=list(inventory(source))
 records={p.relative_to(source).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in found}
 item=dict(relative=relative.as_posix(),bytes=sum(n for _,n,_ in found),files=len(found))
 (output/'plan.json').write_text(json.dumps(dict(source=str(source),target=str(target),move=item,files=records),indent=2)+'\n')
 # Both absolute paths have been bounded and checked before this directory move.
 target.parent.mkdir(parents=True,exist_ok=True)
 os.rename(source,target)
 after={p.relative_to(target).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(target)}
 assert after==records,'Every retained staging file must match its pre-move hash'
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(ARCHIVE),moves=[item],
             archived_bytes=item['bytes'],all_files_sha256_verified=True,deleted_files=0,
             checkpoint_rom_and_source_zip_remain_local=True)
 receipt['directories'].append(item);receipt['archived_bytes']+=item['bytes'];receipt['archived_files']+=item['files']
 receipt.setdefault('additional_archives',[]).append(report)
 (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
 (output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
