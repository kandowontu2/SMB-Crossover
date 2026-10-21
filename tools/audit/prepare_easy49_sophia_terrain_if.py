"""Preserve the original name-producer carry with an equal-size tail branch."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'root49-sophia-source-terrain-ib';D=V/'root49-sophia-source-terrain-if';S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not D.exists();prior=json.loads((P/'preparation.json').read_text())
 for n,h in prior['source_sha256'].items():
  assert sha(P/'source'/n)==h,n
  p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
 shutil.copytree(P/'source/build/generated',S/'build/generated')
 p=S/'src/characters.s';raw=p.read_bytes();eol=b'\r\n'if b'\r\n'in raw else b'\n'
 a=eol.join([b'  lda CharacterNames-49,x',b'  jmp WriteName']);b=eol.join([b'  lda CharacterNames-49,x',b'  clc',b'  bcc WriteName'])
 assert raw.count(a)==1;p.write_bytes(raw.replace(a,b))
 driver=(P/'build-driver.py').read_text();assert driver.count(repr(str(P/'source')))==1;(D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
 record=dict(prior);record.update(status='PRIVATE_TERRAIN_STATUS_CARRY_CORRECTION_PREPARED',parent_IB_sha256=sha(P/'preparation.json'),source_sha256={n:sha(S/n)for n in prior['source_sha256']},script_sha256=sha(__file__),retained_IB_status_negative_sha256=sha(P/'status-name-ie.json'),correction='IE proved all56 full name writes/RAM literal but30 return-status differences: CPX tail kept C1. Replace3-byte JMP with CLC/BCC equal-size tail, preserving original C0 without shifting code. This is the only change fromIB; head/side geometry remains identical.')
 (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'])))


if __name__=='__main__':main()
