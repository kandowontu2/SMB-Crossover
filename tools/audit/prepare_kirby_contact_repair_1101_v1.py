"""Pure narrow Kirby source repair; does not edit the production owner."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];O=R/'build/kirby-inhale-shell-fix-1101-v1'
H=R/'tools/reference/kirby_shell_contact_1101_v1.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def once(text,old,new):
    assert text.count(old)==1,(old[:100],text.count(old));return text.replace(old,new)
def repair_source(source):
    # Six local branches stay well inside signed8-bit range; ca65 proves
    # their actual displacement. Save18B without adding hot-path work.
    head,sep,tail=source.partition('.endproc');assert sep
    for old,new in[('jcs No','bcs No'),('jeq No','beq No'),('jmi No','bmi No'),('jne No','bne No'),('jne Other','bne Other')]:head=head.replace(old,new)
    source=head+sep+tail
    source=once(source,'Other:\n  tay\n  lda Families,y\n  rts','''Other:
  tay
  ; The highest admitted native family is cannon Bullet Bill ($33).
  ; Preserve incoming C/V/D/I and original A/X/Y/N/Z while funding the
  ; shell contact adapter with the192+ provably zero table entries.
  php
  cpy #52
  bcc FamilyLow
  lda #0
  bcs FamilyFlags
FamilyLow:
  lda Families,y
FamilyFlags:
  plp
  ora #0
  rts''')
    source=once(source,'  .repeat 256,I','  .repeat 52,I')
    source=once(source,'  ; Only an edible enemy in front of an active mouth is protected. Back,\n  ; startup, released-B, hazard and Meta Knight contacts remain ordinary.\n  lda KbActionAge\n  jne No','''  ; Active inhale protects the edible front target during mouth opening,
  ; while Suction retains its eight-update capture startup. Back,
  ; released-B, hazard and Meta Knight contacts remain ordinary.''')
    source=once(source,'  sta KbShotKind,x\n  cmp #5','''  sta KbShotKind,x
  cmp #2
  beq ShellSpeed
  cmp #3
  bne NotShell
ShellSpeed:
  ; Native kicked shells use $30/$d0 in4.4, exactly3px/update.
  lda #3
  ldy KbShotDir,x
  cpy #2
  bne :+
  lda #$fd
: sta KbShotVXHi,x
  jmp NotBubble
NotShell:
  cmp #5''')
    source=once(source,'OrdinaryEnemy:\n  ldy KbSavedSlot\n  lda Enemy_X_Position,x','''OrdinaryEnemy:
  ldy KbSavedSlot
  lda KbShotType,y
  cmp #3
  bne LegacyContact
  lda KbShotKind,y
  cmp #2
  beq ShellContact
  cmp #3
  bne LegacyContact
ShellContact:
  jsr KbShellEnemyContact
  jcc NextEnemy
  jmp EnemyHit
LegacyContact:
  lda Enemy_X_Position,x''')
    source=once(source,'  stx ObjectOffset\n  lda Enemy_ID,x\n  cmp #Bowser','EnemyHit:\n  stx ObjectOffset\n  lda Enemy_ID,x\n  cmp #Bowser')
    return source+'\n'+H.read_text()
def main():
    p=R/'src/kirby_weapons.s';q=json.loads((O/'current-witness.json').read_text());assert sha(p)==q['canonical_sources'][p.name]['sha256']
    source=repair_source(p.read_text());(O/'fixed-source.s').write_text(source)
    (O/'repair-proposal.json').write_text(json.dumps(dict(passed=True,production_modified=False,lease_granted=False,scope='Only current weapons island,52-entry exact family table funding, startup guard, shell2/3 speed and native bbox contact.',imports=['Enemy_BoundBoxCtrl','BoundBoxCtrlData'],bindings={str(x.resolve()):sha(x)for x in[Path(__file__),H,p,O/'fixed-source.s',O/'current-witness.json']}),indent=2)+'\n')
    print(json.dumps(dict(passed=True,production_modified=False,source_bytes=len(source))))
if __name__=='__main__':main()
