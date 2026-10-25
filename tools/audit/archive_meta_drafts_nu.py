"""Keep earlier NU failures/captures intact outside the30GB workspace."""
import datetime
import json
import os
from pathlib import Path
from archive_workspace_hz import ROOT,ARCHIVE,inventory,bounded,sha


def record(p):
    if p.is_file():
        s=p.stat();return{'':dict(bytes=s.st_size,mtime_ns=s.st_mtime_ns,sha256=sha(p))}
    return{q.relative_to(p).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(q))for q,n,t in inventory(p)}


def main():
    qa=ROOT/'build/verification/meta-knight-source-nu'
    out=qa/'archive-drafts';out.mkdir(exist_ok=False)
    receipt=json.loads((ROOT/'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
    assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())and ARCHIVE.drive.lower()==ROOT.drive.lower()
    assert sha(qa/'candidate-v4.nes')=='eb6bcdd133f344538362d35f6b913dc0d5c43446c16c8c7b9e864a64e2905b07'
    names=['candidate-v4.nes','candidate-v4.lbl','candidate-v4.map','candidate-v4.dbg.gz',
           'candidate-v4-objects','entry-v4','entry-v5','discover-easy-v1','discover-easy-v2','discover-hard-v2',
           'moves-easy-v4','moves-easy-v5','moves-easy-v6','moves-easy-v7','moves-easy-v8',
           'moves-hard-v6','moves-hard-v7','moves-hard-v8','physical-hard-v1','physical-hard-v2','physical-easy-v2']
    moves=[]
    for n in names:
        source=bounded(qa/n,qa);assert source.exists()
        rel=source.relative_to(ROOT);target=bounded(ARCHIVE/rel,ARCHIVE);assert not target.exists()
        files=record(source)
        item=dict(relative=rel.as_posix(),bytes=sum(v['bytes']for v in files.values()),files=len(files),kind='file'if source.is_file()else'directory')
        moves.append((source,target,item,files))
    (out/'plan.json').write_text(json.dumps([dict(source=str(s),target=str(t),move=i,files=f)for s,t,i,f in moves],indent=2)+'\n')
    for source,target,item,files in moves:
        target.parent.mkdir(parents=True,exist_ok=True);os.rename(source,target)
        assert record(target)==files
    items=[i for _,_,i,_ in moves]
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(ARCHIVE),moves=items,
                archived_bytes=sum(i['bytes']for i in items),all_files_sha256_verified=True,deleted_files=0,
                failed_and_superseded_evidence_retained=True,current_v7_checks_remain_local=True)
    receipt['directories'].extend(items);receipt['archived_bytes']+=report['archived_bytes'];receipt['archived_files']+=sum(i['files']for i in items)
    receipt.setdefault('additional_archives',[]).append(report)
    (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(archived_bytes=report['archived_bytes'],files=sum(i['files']for i in items),all_files_sha256_verified=True,deleted_files=0)))


if __name__=='__main__':main()
