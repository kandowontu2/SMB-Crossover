"""Preserve superseded source-rebuild staging outside the30GB workspace."""
import datetime,json,os
from pathlib import Path
from archive_workspace_hz import ROOT,ARCHIVE,inventory,bounded,sha


def main():
 output=ROOT/'build/verification/parodius-render-nq/archive-completed-sources';output.mkdir(exist_ok=False)
 receipt=json.loads((ROOT/'workspace-archive.json').read_text())
 assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
 assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())and ARCHIVE.drive.lower()==ROOT.drive.lower()
 moves=[];trees={}
 for rel in('build/verification/roll-performance-no/snapshot-v4','build/verification/roll-roster-nn/snapshot-v18'):
  source=bounded(ROOT/rel,ROOT/'build/verification');target=bounded(ARCHIVE/rel,ARCHIVE)
  assert source.is_dir()and not target.exists()
  found=list(inventory(source));trees[rel]={p.relative_to(source).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in found}
  moves.append(dict(relative=rel,source=str(source),target=str(target),bytes=sum(n for _,n,_ in found),files=len(found)))
 (output/'plan.json').write_text(json.dumps(dict(moves=moves,files=trees),indent=2)+'\n')
 for item in moves:
  source=bounded(ROOT/item['relative'],ROOT/'build/verification');target=bounded(ARCHIVE/item['relative'],ARCHIVE)
  assert source.is_dir()and not target.exists()
  target.parent.mkdir(parents=True,exist_ok=True);os.rename(source,target)
  after={p.relative_to(target).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(target)}
  assert after==trees[item['relative']]
 report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(ARCHIVE),moves=moves,
             archived_bytes=sum(i['bytes']for i in moves),all_files_sha256_verified=True,deleted_files=0,
             checkpoint_roms_and_source_zips_remain_local=True)
 receipt['directories'].extend({k:i[k]for k in('relative','bytes','files')}for i in moves)
 receipt['archived_bytes']+=report['archived_bytes'];receipt['archived_files']+=sum(i['files']for i in moves)
 receipt.setdefault('additional_archives',[]).append(report)
 (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
 (output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
