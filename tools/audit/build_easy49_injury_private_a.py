"""Add source1.0 guest damage rules to the isolated inventory foundation.

Never modifies the working ROM or the user's Easy/Hard menu labels.
"""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
B = R / 'build/verification/root49-easy-hard-user-baseline-a'
P = R / 'build/verification/root49-easy-inventory-base-a'
H = R / 'build/verification/root49-easy-injury-private-a'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

LEGACY = r'''; Character.as takeDamageStart/End, freezeTmrDur1000/noDamageTmrDur2500.
; Tail allocation leaves every existing RAM address stable.
.pushseg
.segment "SRAM"
GuestLegacyHurt: .res 1       ;0=off,1=frozen swap,2=protection.
.segment "INVENTORY"
.proc GuestLegacyInjuryTry
  phx
  phy
  jsr InventoryLegacyClassic
  bcc Modern
  lda PlayerStatus
  sta GuestPowerupOld
  sta GuestPowerupDisplay
  lda #0
  sta GuestPowerupTarget
  sta GuestPowerupAge
  sta GuestHurtTicks
  sta GuestInvulTicks
  sta GuestFlickerPhase
  sta PlayerChangeSizeFlag
  lda SelectedCharacter
  sta GuestHurtKind
  cmp #CHARACTER_MEGAMAN
  bne Samus
  ; MegaMan.takeDamageStart releases charge without firing it.
  lda #0
  sta MmCharging
  sta MmChargeFrames
  lda #15                    ;Character.hitAnimation: takeDamage for MegaMan.
  bne Pose
Samus:
  cmp #CHARACTER_SAMUS
  bne Roster
  lda SmPose
  jmp Pose
Roster:
  cmp #CHARACTER_SIMON
  bne SavedPose
  lda #RG_POSE_HURT           ;Character.hitAnimation: takeDamage for Simon.
  bne Pose
SavedPose:
  lda RgPose
Pose:
  sta GuestPowerupPose
  lda #1
  sta GuestLegacyHurt
  sta GuestHurtVisible
  sta InjuryTimer
  sta GuestPowerupActive
  lda #$ff
  sta TimerControl
  lda #9
  sta GameEngineSubroutine
  lda #Sfx_PipeDown_Injury
  sta Square1SoundQueue
  ply
  plx
  sec
  rts
Modern:
  ply
  plx
  clc
  rts
.endproc

.proc GuestLegacyInjuryTick
  phx
  phy
  lda GameEngineSubroutine
  cmp #9
  bne Playing
  lda GuestPowerupActive
  bne Done                   ;World and protection clock freeze during swaps.
Playing:
  lda GameEngineSubroutine
  cmp #8
  bne Clear                  ;Death, area transfer and scripted life changes.
  lda GamePauseStatus
  and #1
  bne Done
  lda GuestLegacyHurt
  cmp #1
  bne Count
  lda #2
  sta GuestLegacyHurt
  lda #150                   ;2500ms, starts after the1000ms frozen shrink.
  sta GuestInvulTicks
  lda #7
  sta GuestFlickerPhase
  bne Protected
Count:
  dec GuestInvulTicks
  beq Clear
Protected:
  lda #1
  sta InjuryTimer
  ; NES opacity is binary. Approximate source alpha0.65 over20updates,
  ; using the existing LSR visual cadence without Link's Hard color cycle.
  lda GuestFlickerPhase
  clc
  adc #13
  cmp #20
  bcc Hide
  sbc #20
  sta GuestFlickerPhase
  lda #1
  bne Store
Hide:
  sta GuestFlickerPhase
  lda #0
Store:
  sta GuestHurtVisible
Done:
  ply
  plx
  rts
Clear:
  lda #0
  sta GuestLegacyHurt
  sta GuestHurtKind
  sta GuestHurtTicks
  sta GuestInvulTicks
  sta InjuryTimer
  lda #1
  sta GuestHurtVisible
  bne Done
.endproc
.popseg
'''

def edit(name, old, new):
    p=S/name; text=p.read_text(); assert text.count(old)==1, (name,old)
    p.write_text(text.replace(old,new))

def main():
    sys.dont_write_bytecode=True
    assert not H.exists()
    baseline=json.loads((B/'baseline.json').read_text())
    cat=baseline['current_source_hashes']
    assert all(sha(R/n)==h for n,h in cat.items())
    assert json.loads((P/'query-cpu-b.json').read_text())['status']=='PASS_COMPILED_LEGACY_INVENTORY_QUERY_BOUNDARY'
    H.mkdir(); shutil.copytree(P/'source',S,ignore=shutil.ignore_patterns('build','__pycache__'))
    review=json.loads((P/'build-review-b.json').read_text())
    assert all(sha(S/n)==h for n,h in review['actual_source_hashes'].items())
    edit('src/guest_body_contact.s','  ldx #0\nDone:\n  txa',
         '  lda CrossoverBehaviorVersion\n  beq Done                    ;Easy Bill retains the original powered extra hit.\n  ldx #0\nDone:\n  txa')
    edit('src/guest_injury.s','.proc GuestInjuryStart\n',
         '.segment "INVENTORY"\n.proc GuestInjuryStart\n  jsr GuestLegacyInjuryTry\n  bcc Modern\n  rts\nModern:\n')
    p=S/'src/guest_injury.s'; text=p.read_text()
    a=text.index('.proc GuestInjuryStart'); z=text.index('.endproc',a)
    part=text[a:z]
    for name in ['SamusHurtStart','GuestLsrInjury','MegaManHurtStart']:
        assert part.count('jsr '+name)==1
        part=part.replace('jsr '+name,'farcall '+name)
    text=text[:a]+part+text[z:]
    text=text.replace('.proc GuestInjuryTick\n', '.segment "SAMUS"\n.proc GuestInjuryTick\n  lda GuestLegacyHurt\n  beq Modern\n  farcall GuestLegacyInjuryTick, jmp\nModern:\n')
    p.write_text(text)
    edit('src/guest_powerups.s','  sta GuestPowerupAge\n  jmp RosterClearState',
         '  sta GuestPowerupAge\n  sta GuestLegacyHurt\n  jmp RosterClearState')
    edit('src/guest_powerups.s','  lda GuestPowerupOld\n  sta GuestPowerupDisplay\n  ; Mega Man',
         '  lda GuestPowerupOld\n  sta GuestPowerupDisplay\n  lda GuestLegacyHurt\n  cmp #1\n  beq Swap                    ;Old injury alternates both power forms at10Hz.\n  ; Mega Man')
    edit('src/guest_powerups.s','.proc GuestPowerupPalette\n  lda GuestPowerupAge',
         '.proc GuestPowerupPalette\n  lda GuestLegacyHurt\n  cmp #1\n  jeq Original                ;Damage swaps tiers without power-up rainbow.\n  lda GuestPowerupAge')
    with (S/'src/entrypoint.s').open('a')as f:
        f.write('\n; Easy damage lifecycle appended after all pre-existing RAM/code.\n.if ::ENABLE_CROSSOVER\n.include "guest_legacy_injury.s"\n.endif\n')
    (S/'src/guest_legacy_injury.s').write_text(LEGACY)
    changed=['src/guest_body_contact.s','src/guest_injury.s','src/guest_powerups.s','src/entrypoint.s','src/guest_legacy_injury.s']
    source=R/'reference/crossover/decompiled/scripts/com/smbc/characters/Character.as'
    report=dict(status='BUILDING_PRIVATE_LEGACY_DAMAGE',script_sha256=sha(__file__),
        parent_inventory_review_sha256=sha(P/'build-review-b.json'),
        parent_query_review_sha256=sha(P/'query-cpu-b.json'),
        original_source=dict(path=str(source.relative_to(R)),sha256=sha(source),
            functions=['takeDamageStart','hitAnimation','swapPs','takeDamageEnd','freezeTmrLsr'],
            constants={'freezeTmrDur_ms':1000,'noDamageTmrDur_ms':2500,'TD_ALPHA':0.65}),
        changes={n:sha(S/n)for n in changed},builds=[],main_changed=False,complete_Easy_behavior=False,
        accepted_release=False,goal_complete=False)
    def save():(H/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    code=(P/'compact-build-driver.py').read_text().replace(str(P/'source'),str(S))
    driver=H/'compact-build-driver.py'; driver.write_text(code)
    parser=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    spec=importlib.util.spec_from_file_location('injury_image',parser)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build.log')
        with log.open('wb')as f:
            rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save()
        assert rc==0,mapper
        rom=S/('build/smb-crossover-'+mapper+'.nes'); im=mod.Image(rom); old=mod.Image(R/('build/smb-crossover-'+mapper+'.nes'))
        assert all(im.ram[k]==v for k,v in old.ram.items()),'Old RAM must be exact'
        assert im.raw[16+64*8192:]==old.raw[16+64*8192:],'CHR unchanged'
        d=next(v for v in im.segs.values()if v['name']=='BASS_DPCM')
        assert im.raw[d['ooffs']:d['ooffs']+d['size']]==old.raw[d['ooffs']:d['ooffs']+d['size']]
        row.update(ROM_sha256=sha(rom),old_RAM_exact=True,CHR_exact=True,DPCM_exact=True,
            segments={k:next(v for v in im.segs.values()if v['name']==k)for k in ['INVENTORY','SAMUS','FIXED','SRAM']})
        save()
    assert all(sha(R/n)==h for n,h in cat.items())
    report['status']='PASS_PRIVATE_LEGACY_DAMAGE_BUILD_ONLY'
    report['limits']='Build/layout only; actual lifecycle, native freeze and Hard differential checks pending. Binary NES opacity approximates source alpha.'
    report['all_candidate_source_hashes']={n:sha(S/n)for n in cat}|{'src/guest_legacy_injury.s':sha(S/'src/guest_legacy_injury.s')}
    save();print(report['status'],sha(H/'report.json'),flush=True)

if __name__=='__main__':main()
