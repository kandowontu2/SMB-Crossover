"""Materialize one private, strictly source-bound right-moving helper candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
BASE=R/'build/getsu-fast-head-native-1110/candidate.nes'
PARENT='66a7b9325d90efb7751387e0c1c95a756fde57d92f13d6180178ade3e535090c'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def reconstruct(proof):
 q=json.loads(proof.read_text())
 assert q['passed'] and not q['ROM_written'] and q['parent_SHA256']==PARENT
 assert sha(BASE)==PARENT
 for name,digest in q['bindings'].items():assert sha(R/name)==digest,name
 raw=bytearray(BASE.read_bytes());used=set()
 for row in q['patches']:
  at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
  assert len(old)==len(new) and raw[at:at+len(old)]==old
  extent=set(range(at,at+len(old)));assert not used&extent;used|=extent
  raw[at:at+len(old)]=new
 assert hashlib.sha256(raw).hexdigest()==q['expected_memory_only_SHA256']
 assert all(a==b for i,(a,b) in enumerate(zip(BASE.read_bytes(),raw)) if i not in used)
 return bytes(raw),q


def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--proof',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();proof=a.proof.resolve()
 assert out.is_relative_to(R/'build') and not out.exists()
 raw,q=reconstruct(proof);out.mkdir();rom=out/'candidate.nes';rom.write_bytes(raw)
 subprocess.run([sys.executable,'-B',str(R/'tools/audit/prepare_manual_right_native_1110.py'),
  '--output',str(out/'native'),'--rom',str(rom),'--proof',str(proof)],check=True)
 subprocess.run([sys.executable,'-B',str(R/'tools/audit/prepare_manual_dual_regression_1110.py'),
  '--output',str(out/'regression'),'--rom',str(rom),'--proof',str(proof)],check=True)
 print('Private rightward candidate:',q['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':main()
