"""Retain IJ's assembly negative and lengthen its one out-of-range branch."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'root49-sophia-source-terrain-ij';D=V/'root49-sophia-source-terrain-ik';S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not D.exists();prior=json.loads((P/'preparation.json').read_text())
 for n,h in prior['source_sha256'].items():
  assert sha(P/'source'/n)==h,n
  p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
 shutil.copytree(P/'source/build/generated',S/'build/generated')
 p=S/'src/sophia_source_terrain.s';raw=p.read_bytes();eol=b'\r\n'if b'\r\n'in raw else b'\n'
 a=eol.join((b'  jsr SophiaTerrainQuery',b'  beq Next',b'  cmp #$c2'))
 b=eol.join((b'  jsr SophiaTerrainQuery',b'  jeq Next',b'  cmp #$c2'))
 assert raw.count(a)==1;p.write_bytes(raw.replace(a,b))
 driver=(P/'build-driver.py').read_text();assert driver.count(repr(str(P/'source')))==1
 (D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
 record=dict(prior);record.update(status='PRIVATE_TERRAIN_BRICK_NONE_COIN_BRANCH_CORRECTION_PREPARED',parent_IJ_sha256=sha(P/'preparation.json'),source_sha256={n:sha(S/n)for n in prior['source_sha256']},script_sha256=sha(__file__),retained_IJ_negative={m:sha(P/('build-'+m+'.log'))for m in ('mmc3','mmc5')},branch_correction='IJ both assembler negatives: first BEQ Next displacement147. Expand only this branch to JEQ; retain all source behavior and failed logs.')
 (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(record['status'])


if __name__=='__main__':main()
