"""Retain completed NL source-rebuild staging in the verified archive."""
import json,os,datetime
from archive_workspace_hz import ROOT,ARCHIVE,inventory,bounded,sha


def main():
 out=ROOT/'build/verification/parodius-death-nr/archive-nl-staging';out.mkdir(parents=True,exist_ok=False)
 receipt=json.loads((ROOT/'workspace-archive.json').read_text())
 assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
 assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())and ARCHIVE.drive.lower()==ROOT.drive.lower()
 source=bounded(ROOT/'build/verification/parodius-integration-nl/snapshot-v8',ROOT/'build/verification/parodius-integration-nl')
 relative=source.relative_to(ROOT);target=bounded(ARCHIVE/relative,ARCHIVE)
 assert source.is_dir()and not target.exists()
 checkpoint=ROOT/'build/checkpoints/parodius-integration-nl'
 assert sha(source/'source.zip')==sha(checkpoint/'source.zip')
 assert sha(source/'roundtrip.nes')==sha(checkpoint/'candidate.nes')
 files=list(inventory(source));records={p.relative_to(source).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in files}
 item=dict(relative=relative.as_posix(),bytes=sum(n for _,n,_ in files),files=len(files))
 (out/'plan.json').write_text(json.dumps(dict(source=str(source),target=str(target),move=item,files=records),indent=2)+'\n')
 target.parent.mkdir(parents=True,exist_ok=True);os.rename(source,target)
 assert {p.relative_to(target).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(target)}==records
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(ARCHIVE),moves=[item],archived_bytes=item['bytes'],all_files_sha256_verified=True,deleted_files=0,checkpoint_rom_and_source_zip_remain_local=True)
 receipt['directories'].append(item);receipt['archived_bytes']+=item['bytes'];receipt['archived_files']+=item['files'];receipt.setdefault('additional_archives',[]).append(report)
 (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':
 from pathlib import Path
 main()
