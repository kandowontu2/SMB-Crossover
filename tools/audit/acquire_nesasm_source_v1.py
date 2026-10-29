"""Acquire the source-recommended NESASM from a pinned commit, no downloaded executable."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/source-acquisition/nesasm-2026-10-29'
COMMIT='229033a4b76466b447ad47704808a4d03c493cee'


def fetch(url,limit):
    request=urllib.request.Request(url,headers={'User-Agent':'SMBCrossover-source-port'})
    with urllib.request.urlopen(request,timeout=30) as response:
        data=response.read(limit+1)
    assert len(data)<=limit,url
    return data


def bind(path):
    path=Path(path).resolve();data=path.read_bytes()
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def main():
    OUT.mkdir(exist_ok=True)
    tp=OUT/'tree.json'
    if not tp.exists():
        tp.write_bytes(fetch('https://api.github.com/repos/camsaul/nesasm/git/trees/'+COMMIT+'?recursive=1',500000))
    tree=json.loads(tp.read_text())
    assert tree['sha']==COMMIT and not tree['truncated']
    leaves=[row for row in tree['tree'] if row['type']=='blob' and
        (row['path'].startswith('source/') and (Path(row['path']).suffix in ['.c','.h']or row['path']=='source/Makefile')
         or row['path'] in ['README.md','usage.txt'])]
    assert len(leaves)<=30 and sum(row['size']for row in leaves)<300000
    def acquire(row):
        path=OUT/row['path'];url='https://raw.githubusercontent.com/camsaul/nesasm/'+COMMIT+'/'+row['path']
        data=path.read_bytes()if path.exists()else fetch(url,row['size'])
        assert len(data)==row['size']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['sha']
        path.parent.mkdir(exist_ok=True)
        if not path.exists():path.write_bytes(data)
        return dict(**bind(path),url=url,git_blob_sha1=row['sha'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as executor:
        files=list(executor.map(acquire,leaves))
    result=dict(repository='https://github.com/camsaul/nesasm',commit=COMMIT,tree=bind(tp),
        tool=bind(__file__),files=files,
        reason='Pinned SMB3 README explicitly recommends this NESASM source. Compile locally with existing GCC; do not fetch repository executable.',
        downloaded_executable=False,source_bytes=sum(row['bytes']for row in files))
    text=json.dumps(result,indent=2)+'\n';target=OUT/'acquisition.json'
    if target.exists():assert target.read_text()==text
    else:target.write_text(text)
    print(json.dumps(dict(acquisition=bind(target),files=len(files),source_bytes=result['source_bytes'])))


if __name__=='__main__':
    main()
