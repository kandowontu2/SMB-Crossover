"""Fetch only pinned genuine CF source, verify git blobs; never fetch executables."""
from pathlib import Path
import hashlib,json,urllib.request
R=Path(__file__).resolve().parents[2]
O=R/'build/contra-force-source-v1';S=O/'source'
REPO='cyneprepou4uk/NES-Games-Disassembly'
TREE='f3266a6a293049abf6b54b3bdabc6fac16ae459e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SMB-Crossover-source-audit'}),timeout=30)as r:return r.read()
def main():
 assert not O.exists();S.mkdir(parents=True)
 commit=json.loads(get(f'https://api.github.com/repos/{REPO}/commits/main'))['sha']
 root=json.loads(get(f'https://api.github.com/repos/{REPO}/git/trees/{commit}'))
 assert next(x['sha']for x in root['tree']if x['path']=='Contra Force')==TREE
 raw=get(f'https://api.github.com/repos/{REPO}/git/trees/{TREE}?recursive=1')
 tree=json.loads(raw);assert not tree.get('truncated')
 (O/'tree.json').write_bytes(raw)
 entries=[]
 for row in tree['tree']:
  n=row['path']
  if row['type']!='blob' or '/'in n or Path(n).suffix not in{'.asm','.inc','.cfg','.lua','.sh','.bat'}:continue
  assert row['size']<=800000
  url=f'https://raw.githubusercontent.com/{REPO}/{commit}/Contra%20Force/{urllib.request.quote(n)}'
  data=get(url);assert len(data)==row['size']
  assert hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()==row['sha']
  p=S/n;p.write_bytes(data)
  entries.append(dict(path=str(p),source_url=url,git_blob=row['sha'],sha256=sha(p),bytes=len(data)))
 rom=Path('C:/NES/Contra Force (USA).nes')
 assert sha(rom)=='ba5337367a2140c72ae40826ff4fb9b86a38798ed129edc9bd519aec8818abfa'
 d=dict(status='PINNED_ORIGINAL_SOURCE_FETCH_ONLY_NO_HOST_OR_ADMISSION',repository=f'https://github.com/{REPO}',commit=commit,source_tree=TREE,original_ROM=str(rom),original_ROM_sha256=sha(rom),entries=entries,total_source_bytes=sum(x['bytes']for x in entries),downloaded_executables=False,compiled=False,native=False,bindings={str(Path(__file__).resolve()):sha(__file__),str(O/'tree.json'):sha(O/'tree.json')})
 p=O/'source-fetch.json';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(path=str(p),sha256=sha(p),commit=commit,files=len(entries),bytes=d['total_source_bytes'])),flush=True)
if __name__=='__main__':main()
