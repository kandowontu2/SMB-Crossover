"""Prototype an exact direct terrain pointer calculation in a private copy."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'agent49-e-sophia-union-a';D=V/'root49-sophia-query-perf-ip';S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not D.exists()
 f=P/'source-only-snapshot-e.json';assert sha(f)=='d89b4a1b0c585dee022dbaa59536eb3ed3688a47c4ef4d3256088146c13d435e'
 cat=json.loads((P/'source-catalog-e.json').read_text());assert len(cat)==449
 for n,h in cat.items():
  assert sha(P/'source-e'/n)==h,n
  p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source-e'/n,p)
 shutil.copytree(P/'source-e/build/generated',S/'build/generated',dirs_exist_ok=True)
 p=S/'src/sophia_source_terrain.s';raw=p.read_bytes();eol=b'\r\n'if b'\r\n'in raw else b'\n'
 a=eol.join(x.encode()for x in ['  lda RgTempPage','  and #1','  lsr','  ora R5','  ror','  lsr','  lsr','  lsr','  jsr GetBlockBufferAddr'])
 b=eol.join(x.encode()for x in ['  ; Same native low/high table and final carry semantics, without','  ; packing page/column and immediately unpacking them in a callee.','  lda RgTempPage','  and #1','  tay','  lda BlockBufferAddr+2,y','  sta R7','  lda R5','  lsr','  lsr','  lsr','  lsr','  clc','  adc BlockBufferAddr,y','  sta R6'])
 assert raw.count(a)==1;p.write_bytes(raw.replace(a,b))
 driver=(P/'build-driver-e.py').read_text();assert driver.count(repr(str(P/'source-e')))==1
 (D/'build-driver.py').write_text(driver.replace(repr(str(P/'source-e')),repr(str(S))))
 record=dict(status='PRIVATE_DIRECT_QUERY_PROTOTYPE_PREPARED',source_catalog={n:sha(S/n)for n in cat},parent_source_snapshot_sha256=sha(f),script_sha256=sha(__file__),main_changed=False,scope='Pointer-only optimization prototype; exact old/new full registers, allRAM with individually enumerated removed push residues, ordered semantic writes and measured cycles required. Not actual native/route/interrupt proof; source feet candidate is separate.')
 (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'])


if __name__=='__main__':main()
