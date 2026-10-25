"""Retain the superseded first-candidate routes outside the30GB workspace."""
from pathlib import Path
import datetime,json,os
from archive_workspace_hz import ROOT,ARCHIVE,inventory,bounded,sha


def main():
 qa=ROOT/'build/verification/parodius-death-nr';out=qa/'archive-v1-replays';out.mkdir(exist_ok=False)
 receipt=json.loads((ROOT/'workspace-archive.json').read_text());assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
 assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())and ARCHIVE.drive.lower()==ROOT.drive.lower()
 digest=sha(qa/'candidate-v1.nes');moves=[];trees={}
 for mode in('easy','hard'):
  for name in('octopus','twinbee','pentarou'):
   for phase in('discover','replay'):
    source=bounded(qa/f'{phase}-{name}-{mode}-v2',qa);rel=source.relative_to(ROOT).as_posix();target=bounded(ARCHIVE/rel,ARCHIVE)
    assert source.is_dir()and not target.exists();m=json.loads((source/'manifest.json').read_text());assert m['ROM_sha256']==digest and m['exit']==0
    files=list(inventory(source));trees[rel]={p.relative_to(source).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in files}
    moves.append(dict(relative=rel,bytes=sum(n for _,n,_ in files),files=len(files)))
 (out/'plan.json').write_text(json.dumps(dict(moves=moves,files=trees),indent=2)+'\n')
 for item in moves:
  source=bounded(ROOT/item['relative'],qa);target=bounded(ARCHIVE/item['relative'],ARCHIVE)
  assert source.is_dir()and not target.exists();target.parent.mkdir(parents=True,exist_ok=True);os.rename(source,target)
  assert {p.relative_to(target).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(target)}==trees[item['relative']]
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(ARCHIVE),moves=moves,archived_bytes=sum(i['bytes']for i in moves),all_files_sha256_verified=True,deleted_files=0,checkpoint_roms_and_source_zips_remain_local=True)
 receipt['directories'].extend(moves);receipt['archived_bytes']+=report['archived_bytes'];receipt['archived_files']+=sum(i['files']for i in moves);receipt.setdefault('additional_archives',[]).append(report)
 (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n');(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(archived_bytes=report['archived_bytes'],files=sum(i['files']for i in moves),all_files_sha256_verified=True)))


if __name__=='__main__':main()
