"""Retain HY assembler range negatives; correct explicit long branches."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'root49-sophia-source-terrain-hy';D=V/'root49-sophia-source-terrain-hz';S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(n,a,b):
 p=S/n;raw=p.read_bytes();eol='\r\n'if b'\r\n'in raw else'\n';aa,bb=(x.replace('\n',eol).encode()for x in [a,b]);assert raw.count(aa)==1,(n,a[:50]);p.write_bytes(raw.replace(aa,bb))


def main():
 assert not D.exists();prior=json.loads((P/'preparation.json').read_text())
 for n,h in prior['source_sha256'].items():
  assert sha(P/'source'/n)==h,n
  p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
 shutil.copytree(P/'source/build/generated',S/'build/generated')
 edit('src/collision.s','  beq SophiaHeadWithinTerrain','  jeq SophiaHeadWithinTerrain')
 edit('src/sophia_source_terrain.s','  cmp #3\n  bcc Loop','  cmp #3\n  jcc Loop')
 edit('src/characters.s','''  .byte "MARIO  ", "MEGAMAN", "SAMUS  ", "BILL   ", "LINK   ", "SIMON  "
.popseg
CharacterNames:
  .byte "PIT    ", "RYGAR  ",''','''  .byte "MARIO  ", "MEGAMAN", "SAMUS  ", "BILL   ", "LINK   ", "SIMON  ", "PIT    "
.popseg
CharacterNames:
  .byte "RYGAR  ",''')
 edit('src/characters.s','  cpx #42\n  bcc Prefix\n  lda CharacterNames-42,x','  cpx #49\n  bcc Prefix\n  lda CharacterNames-49,x')
 edit('src/characters.s','Only the existing bank3 status-text producer reads these42 bytes.','Only the existing bank3 status-text producer reads these49 bytes.')
 edit('src/megaman_environment.s','  .repeat 2\n    .byte $ea','  .repeat 7\n    .byte $ea')
 edit('src/megaman_environment.s','  .repeat 24\n    .byte $ea','  .repeat 29\n    .byte $ea')
 driver=(P/'build-driver.py').read_text();assert driver.count(repr(str(P/'source')))==1;(D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
 record=dict(prior);record.update(status='PRIVATE_TERRAIN_RANGE_CORRECTION_PREPARED',parent_HY_sha256=sha(P/'preparation.json'),source_sha256={n:sha(S/n)for n in prior['source_sha256']},script_sha256=sha(__file__),retained_negative='HY assembler found out-of-range head dispatch746 and head-queryloop−139. Use long branches; move all seven first names49B to existing bank3 producer, compensating resident padding. No assembled/native HY result was claimed.')
 (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'])))


if __name__=='__main__':main()
