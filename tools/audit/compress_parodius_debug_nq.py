"""Losslessly compact completed private NQ debug files inside its QA folder."""
from pathlib import Path
import gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/parodius-render-nq'


def main():
 receipt=QA/'debug-compression.json';rows=json.loads(receipt.read_text())if receipt.exists()else[]
 for name in('candidate-v1','candidate-v2','candidate-v3','standard-mmc3','standard-mmc5','snapshot-v3/roundtrip'):
  path=(QA/name).with_suffix('.dbg').resolve();assert path.is_relative_to(QA.resolve())
  if not path.exists():continue
  raw=path.read_bytes();target=path.with_suffix('.dbg.gz');target.write_bytes(gzip.compress(raw,mtime=0))
  assert gzip.decompress(target.read_bytes())==raw
  rows.append(dict(file=path.relative_to(QA).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),before=len(raw),after=target.stat().st_size))
  path.unlink()
 receipt.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(dict(files=len(rows),saved_bytes=sum(r['before']-r['after']for r in rows))))


if __name__=='__main__':main()
