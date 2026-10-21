"""Keep the original NMI address by dispatching from the rare caller site."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
P=V/'root49-sophia-source-terrain-ia';D=V/'root49-sophia-source-terrain-ib';S=D/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def edit(n,a,b):
 p=S/n;raw=p.read_bytes();eol='\r\n'if b'\r\n'in raw else'\n';aa,bb=(x.replace('\n',eol).encode()for x in [a,b]);assert raw.count(aa)==1,(n,a[:50]);p.write_bytes(raw.replace(aa,bb))


def main():
 assert not D.exists();prior=json.loads((P/'preparation.json').read_text())
 for n,h in prior['source_sha256'].items():
  assert sha(P/'source'/n)==h,n
  p=S/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/'source'/n,p)
 shutil.copytree(P/'source/build/generated',S/'build/generated')
 edit('src/collision.s','  cmp #CHARACTER_SOPHIA\n  jeq SophiaHeadWithinTerrain\n','')
 edit('src/collision.s','  jsr PlayerHeadWithinTerrain','  jsr CrossoverHeadWithinTerrain')
 edit('src/characters.s','.proc SophiaHeadWithinTerrain\n  lda MmYFraction+1','''.proc CrossoverHeadWithinTerrain
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  beq Sophia
  jmp PlayerHeadWithinTerrain
Sophia:
  lda MmYFraction+1''')
 edit('src/megaman_environment.s','  .repeat 7\n    .byte $ea','  .repeat 4\n    .byte $ea')
 edit('src/megaman_environment.s','  .repeat 29\n    .byte $ea','  .repeat 26\n    .byte $ea')
 edit('src/megaman_environment.s','MegaManSpringVelocity = 233','MegaManSpringVelocity = 230')
 driver=(P/'build-driver.py').read_text();assert driver.count(repr(str(P/'source')))==1;(D/'build-driver.py').write_text(driver.replace(repr(str(P/'source')),repr(str(S))))
 record=dict(prior);record.update(status='PRIVATE_TERRAIN_NMI_PLACEMENT_CORRECTION_PREPARED',parent_IA_sha256=sha(P/'preparation.json'),source_sha256={n:sha(S/n)for n in prior['source_sha256']},script_sha256=sha(__file__),retained_IA_negative='IA compiled both mappers, Vine continuation exact, but adding7 bytes to early FIXED head cutoff shifted NMI+7. Move the rare cutoff dispatch to the callsite/late resident helper and restore early routine literally; compensate3 bytes in old spring padding. Actual NMI/IRQ/audio PC/bytes remain mandatory.')
 (D/'preparation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'])))


if __name__=='__main__':main()
