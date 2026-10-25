from pathlib import Path
import subprocess,sys,shutil,json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'native-probes-qa-v1';O.mkdir(exist_ok=False);S=O/'source';(S/'src').mkdir(parents=True)
def once(t,a,b):
 assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
p=R/'src/characters.s';t=p.read_text();t=once(t,'.proc CrossoverHeadProbe\n  jmp BillHeadDispatch','''.proc CrossoverHeadProbe
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
  jmp MmNativeHeadShortcut
.else
  jmp BillHeadDispatch
.endif''')
a='  farcall TnFastSideGate,jmp\n  .res 10,$ea'
b=''' .if ::MAPPER_MMC5
  jmp MmNativeSideShortcut
::MmNativeHeadShortcut:
  ; Mega Man / Proto Man reach the ordinary query after the other families'
  ; exact-ID gates. Keep its actual native head cell and every later consumer.
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne OrdinaryHeadDispatch
  jmp BlockBufferColli_Head
OrdinaryHeadDispatch:
  jmp BillHeadDispatch
  .res 12,$ea
 .else
  farcall TnFastSideGate,jmp
  .res 10,$ea
 .endif'''
t=once(t,a,b);(S/'src/characters.s').write_text(t)
p=R/'src/megaman_weapons.s';t=p.read_text();a='  .res 37,$ea\n  .assert *-MegaManFullShotBank=55,error,"Original full-shot resident span"'
b=''' .if ::MAPPER_MMC5
::MmNativeSideShortcut:
  ; Preserve the original slow-path A/P and stack contract for every other
  ; family. This adds no state and never borrows a source-specific hitbox.
  php
  pha
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne OtherSide
  pla
  plp
  jmp BlockBufferColli_Side
OtherSide:
  pla
  plp
  farcall TnFastSideGate,jmp
  .res 3,$ea
 .else
  .res 37,$ea
 .endif
  .assert *-MegaManFullShotBank=55,error,"Original full-shot resident span"'''
t=once(t,a,b);(S/'src/megaman_weapons.s').write_text(t)
shutil.copy2(R/'smb1base-mmc5-expanded.cfg',S/'smb1base-mmc5-expanded.cfg')
with(O/'host-build.log').open('w')as f:p=subprocess.run([sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(S),'--output',str(O/'candidate.nes')],cwd=R,stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'host-build.log').read_text()[-2000:]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(O/'proposal.json').write_text(json.dumps(dict(ROM_sha256=sha(O/'candidate.nes'),parent_ROM_sha256=sha(D/'ryu-head-candidate-v5/candidate.nes'),source_changes={p.relative_to(S).as_posix():sha(p)for p in (S/'src').iterdir()},scope='Private native head/side dispatch shortcut for Mega Man/Proto only, no source collision changes, no added RAM or OAM, unchanged original resident footprints; differential/native/interrupt/performance admission pending.'),indent=2));print(sha(O/'candidate.nes'))
