"""Materialize one private candidate from an exact qualified patch manifest."""
import argparse,hashlib,json
from pathlib import Path

R=Path(__file__).resolve().parents[2]
def sha(raw):return hashlib.sha256(raw).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--output',type=Path,required=True)
 p.add_argument('--base',type=Path,required=True)
 p.add_argument('--proof',type=Path,required=True)
 a=p.parse_args();out=a.output.resolve();assert out.is_relative_to(R/'build') and out!=R/'build'
 q=json.loads(a.proof.read_text());raw=bytearray(a.base.read_bytes())
 assert q['passed'] and not q['ROM_written'] and sha(raw)==q['parent_SHA256']
 for name,digest in q['bindings'].items():assert sha((R/name).read_bytes())==digest,name
 used=set()
 for row in q['patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex'])
  assert len(before)==len(after) and raw[at:at+len(before)]==before
  span=set(range(at,at+len(before)));assert not used&span;used.update(span)
  raw[at:at+len(before)]=after
 digest=sha(raw);assert digest==q['expected_memory_only_SHA256']
 out.mkdir(exist_ok=True);rom=out/'candidate.nes';assert not rom.exists();rom.write_bytes(raw)
 (out/'materialized.json').write_text(json.dumps(dict(ROM=str(rom),ROM_SHA256=digest,
   proof=str(a.proof.resolve()),proof_SHA256=sha(a.proof.read_bytes()),native_verified=False),indent=2)+'\n')
 print(digest)

if __name__=='__main__':main()
