"""Apply only the reviewed visible-Water consumer to the current feature set."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=R/'build/verification/water-visible-merge-cj';assert not O.exists();O.mkdir()
P=R/'build/verification/agent49-water-visible-j-a/source-h'
parent=R/'build/checkpoints/firebar-budget-ci/manifest.json';cp=json.loads(parent.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for m,v in cp['ROMs'].items():assert sha(R/'build'/f'smb-crossover-{m}.nes')==v
names=['src/special_weapons.s','src/entrypoint.s','smb1base.cfg','src/bill_native_rare.s','src/metasprite_engine.s','src/game.s']
for n in names:
 p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
private_meta=json.loads((P.parent/'preparation-h.json').read_text())
helper=P/'src/water_shield_enemies.s';key=next(k for k in private_meta['source_catalog']if k.replace('\\','/')=='src/water_shield_enemies.s');assert sha(helper)==private_meta['source_catalog'][key]
p=R/'src/special_weapons.s';s=p.read_text()
start=s.index('EnemyCandidates:\n');end=s.index('  lda SsBodyStop\n',start)
old=s[start:end]
new='''EnemyCandidates:
  lda Enemy_Flag,x
  beq EnemyNext
  bmi EnemyNext                  ; Bowser duplicate is not another target.
  lda Enemy_State,x
  and #$20
  bne EnemyNext
  lda Enemy_ID,x
  cmp #$15
  bcc EnemyFound
  cmp #Bowser
  beq EnemyFound
  cmp #BulletBill_CannonVar
  bne EnemyNext
EnemyFound:
  ; Same field the native consumer rejects, read live again for each ball.
  lda EnemyOffscrBitsMasked,x
  bne EnemyNext
  inc SsEnemies
EnemyNext:
  dex
  bpl EnemyCandidates
  jmp EnemyCandidatesDone
WaterEnemyTargetLo: .byte <MegaManWeapons::Enemies,<WaterShieldEnemies
WaterEnemyTargetHi: .byte >MegaManWeapons::Enemies,>WaterShieldEnemies
.if ::MAPPER_MMC5
WaterEnemyTargetBank: .byte .bank(MegaManWeapons::Enemies)|MMC5_PRG_ROM,.bank(WaterShieldEnemies)|MMC5_PRG_ROM
.else
WaterEnemyTargetBank: .byte .bank(MegaManWeapons::Enemies),.bank(WaterShieldEnemies)
.endif
  .res 50-(*-EnemyCandidates),$ea
EnemyCandidatesDone:
'''
assert old.count('inc SsEnemies')==1 and s.count('WaterEnemyTargetLo')==0;s=s[:start]+new+s[end:]
old='''  jsr Bridge
  farcall MegaManWeapons::Enemies
'''
new='''  jsr Bridge
  ; Only the Water50 proxy selects the direct, live native enemy consumer.
  SMC_StoreValue SafecallA, a
  lda WaterEnemyTargetLo,y
  SMC_StoreLowByte FarcallJmpTarget, a
  lda WaterEnemyTargetHi,y
  SMC_StoreHighByte FarcallJmpTarget, a
  lda WaterEnemyTargetBank,y
  jsr FarCallCommon
.if ::MAPPER_MMC5
::_FARCALL_COUNT .set ::_FARCALL_COUNT + 1
.endif
'''
assert s.count(old)==1;s=s.replace(old,new)
start=s.index('Bridge:\n');end=s.index('DamageTypes:',start)
piece=s[start:end];old='''  sta MmBulletType
  lda #0
  sta MmSlot
''';new='''  sta MmBulletType
  ldy #0
  cmp #50
  bne :+
    iny
  :
  lda #0
  sta MmSlot
''';assert piece.count(old)==1
s=s[:start]+piece.replace(old,new)+s[end:];p.write_text(s)
shutil.copyfile(helper,R/'src/water_shield_enemies.s')
p=R/'src/entrypoint.s';s=p.read_text();anchor='.include "cheats.s"\n';assert s.count(anchor)==1;s=s.replace(anchor,anchor+'.include "water_shield_enemies.s"\n');p.write_text(s)
p=R/'smb1base.cfg';s=p.read_text();anchor='    SCORE_POPUP_COLD: load=XG_SOPHIA_A_TAIL_MEM, type=ro, optional=yes, start=$bfc0;';assert s.count(anchor)==1;s=s.replace(anchor,'    WATER_ENEMY_COLD: load=XG_SOPHIA_A_TAIL_MEM, type=ro, optional=yes, start=$b600; # Water reserves B600-B6FF; Ryu B700-BFBF.\n'+anchor);p.write_text(s)
for n in('src/bill_native_rare.s','src/metasprite_engine.s','src/game.s'):assert sha(R/n)==sha(O/'before'/n)
report=dict(status='SOURCE_MERGE_ONLY_BUILD_AND_CURRENT_NATIVE_VERIFICATION_PENDING',parent_checkpoint_sha256=sha(parent),private_helper_sha256=sha(helper),preserved=['Claude Sophia head origin','firebar fairness','cannon cooldown','terrain publication','score anchors','Cheats'],changed=['src/special_weapons.s','src/entrypoint.s','src/water_shield_enemies.s','smb1base.cfg'],scope='Three specific SPECIAL_ROSTER hunks, direct208-byte helper and existing reserved A-window segment. No old whole-file or bill_native_rare overwrite. BridgeY is a private consumer selector, not an original public ABI claim.',goal_complete=False)
(O/'preparation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
