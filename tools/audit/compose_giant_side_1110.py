"""Compose hash-bound sequential Giant repairs into one strict baseline patch manifest."""
import argparse,hashlib,json
from pathlib import Path
import check_mega_giant_impact_1110 as Q


def digest(data):return hashlib.sha256(data).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--base-proof',type=Path,required=True)
 p.add_argument('--side-proof',type=Path,required=True)
 a=p.parse_args();out=a.output.resolve();assert out.is_relative_to(Q.R/'build')
 original=Q.BASE.read_bytes();assert digest(original)==Q.PIN
 image=bytearray(original); spans=[];bindings={str(Path(__file__).resolve().relative_to(Q.R)):digest(Path(__file__).read_bytes())}
 for path in (a.base_proof.resolve(),a.side_proof.resolve()):
  q=json.loads(path.read_text());assert q['passed'] and not q['ROM_written'] and q['parent_SHA256']==digest(image)
  for name,h in q['bindings'].items():
   assert digest((Q.R/name).read_bytes())==h,name
   assert name not in bindings or bindings[name]==h
   bindings[name]=h
  bindings[str(path.relative_to(Q.R))]=digest(path.read_bytes())
  occupied=set()
  for row in q['patches']:
   at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex'])
   assert len(before)==len(after) and image[at:at+len(before)]==before
   indices=set(range(at,at+len(before)));assert not occupied&indices;occupied.update(indices)
   image[at:at+len(after)]=after;spans.append((at,at+len(after)))
  assert digest(image)==q['expected_memory_only_SHA256']
 merged=[]
 for lo,hi in sorted(spans):
  if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
  else:merged.append([lo,hi])
 patches=[dict(file_offset=lo,old_hex=original[lo:hi].hex(),new_hex=image[lo:hi].hex()) for lo,hi in merged]
 result=dict(passed=True,ROM_written=False,parent_SHA256=Q.PIN,expected_memory_only_SHA256=digest(image),
             patches=patches,bindings=bindings,scope='Sequential source-qualified impact and side-contact repairs; native validation separate.')
 out.mkdir(exist_ok=True);path=out/'proof.json';assert not path.exists();path.write_text(json.dumps(result,indent=2)+'\n')
 print(result['expected_memory_only_SHA256'])


if __name__=='__main__':main()
