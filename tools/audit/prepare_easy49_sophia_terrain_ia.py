"""Update the scoped span assertion after explicit compensating padding."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'root49-sophia-source-terrain-hz';D=V/'root49-sophia-source-terrain-ia';S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not D.exists();prior=json.loads((P/'preparation.json').read_text())
 for n,h in prior['source_sha256'].items():
  assert sha(P/'source'/n)==h,n
  p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
 shutil.copytree(P/'source/build/generated',S/'build/generated')
 p=S/'src/megaman_environment.s';raw=p.read_bytes();a=b'.assert *-MegaManSpringVelocity = 230';assert raw.count(a)==1;p.write_bytes(raw.replace(a,b'.assert *-MegaManSpringVelocity = 233'))
 driver=(P/'build-driver.py').read_text();assert driver.count(repr(str(P/'source')))==1;(D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
 record=dict(prior);record.update(status='PRIVATE_TERRAIN_PAD_ASSERTION_CORRECTION_PREPARED',parent_HZ_sha256=sha(P/'preparation.json'),source_sha256={n:sha(S/n)for n in prior['source_sha256']},script_sha256=sha(__file__),retained_HZ_negative='HZ compensated3 extra resident bytes after the function start moved3 earlier, but retained old230-byte relative span assertion. New233 is an explicit layout hypothesis; actual old audio continuation addresses remain mandatory.')
 (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'])))


if __name__=='__main__':main()
