"""Acquire only pinned SMB3 assembly leaves, including nested object/level includes."""
import hashlib
import io
import json
from pathlib import Path
import tarfile

from acquire_nesasm_source_v1 import ROOT, bind, fetch

BASE=ROOT/'build/source-acquisition/dk-bowser-2026-10-29/smb3'
COMMIT='09b1bd81a788de8ceec664a34094e84ddb463117'


def main():
    target=BASE/'assembly-closure-v1.json'
    assert not target.exists(), 'Preserve the frozen source acquisition'
    tree_path=BASE/'tree.json'
    tree=json.loads(tree_path.read_text())
    assert tree['sha']==COMMIT and not tree['truncated']
    leaves={r['path']:r for r in tree['tree'] if r['type']=='blob' and Path(r['path']).suffix.lower() in ['.asm','.inc']}
    assert len(leaves)==727 and sum(r['size']for r in leaves.values())==3967005
    url='https://codeload.github.com/captainsouthbird/smb3/tar.gz/'+COMMIT
    archive=fetch(url,12_000_000)
    files=[]
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz')as tar:
        for member in tar:
            if not member.isfile():continue
            name=member.name.split('/',1)[-1]
            if name not in leaves:continue
            row=leaves[name]
            assert 0<=member.size<=300000 and member.size==row['size']
            data=tar.extractfile(member).read()
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['sha'],name
            path=BASE/'source'/name
            assert path.resolve().is_relative_to((BASE/'source').resolve())
            if path.exists():assert path.read_bytes()==data
            else:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(data)
            files.append(dict(**bind(path),source_path=name,git_blob_sha1=row['sha']))
    assert len(files)==len(leaves)
    result=dict(repository='https://github.com/captainsouthbird/smb3',commit=COMMIT,
        tree=bind(tree_path),tool=bind(__file__),files=sorted(files,key=lambda r:r['source_path']),
        source_bytes=sum(r['bytes']for r in files),source_files=len(files),
        transport=dict(url=url,compressed_bytes=len(archive),sha256=hashlib.sha256(archive).hexdigest(),persisted=False),
        scope='All assembly include leaves only; no PCX graphics, ROM, downloaded executable, clone or archive file persisted.')
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(proof=bind(target),source_files=len(files),source_bytes=result['source_bytes'])))


if __name__=='__main__':main()
