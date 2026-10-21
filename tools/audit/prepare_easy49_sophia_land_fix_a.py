"""Fork immutable source-c and correct only the new landing effect's retriggers."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
C = R / 'build/verification/agent-lsr-sophia-feet-implementation-a'
D = R / 'build/verification/root49-sophia-land-fix-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

WRAPPER = '''
; RemainingAudioTick deliberately keeps its original24 effects unchanged.
; Landing25 alone must not reload sweep/length/phase on silent source updates.
; The genuine21-byte stream is active only at pointer offsets9..20; writes
; occur at offsets9/update1 and19/update7. Full source progression is guarded
; independently. A paused held pointer must not produce another retrigger.
.pushseg
.segment "REMAINING_AUDIO"
.assert >(AvSfxSophiaLand+20) = >AvSfxSophiaLand, lderror, "Landing stream low-byte phase guard must stay in one page"
.proc SophiaLandAudioTick
  jsr RemainingAudioTick
  php
  pha
  lda AvAudioId
  cmp #AV_SFX_SOPHIALAND
  bne Done
  lda GamePauseStatus
  and #1
  bne Quiet
  lda AvAudioPtr
  cmp #<(AvSfxSophiaLand+9)
  beq Done
  cmp #<(AvSfxSophiaLand+19)
  beq Done
Quiet:
  lda #0
  sta GuestNativeDirty+4
  sta GuestNativeDirty+5
  sta GuestNativeDirty+6
  sta GuestNativeDirty+7
Done:
  pla
  plp
  rts
.endproc
.popseg
'''


def main():
    assert not D.exists()
    revision = C / 'revision-c.json'
    catalog = json.loads(revision.read_text())['source_sha256']
    assert len(catalog) == 455
    for name, digest in catalog.items():
        assert sha(C / 'source-c' / name) == digest, name
    S = D / 'source-d'
    S.mkdir(parents=True)
    for name in catalog:
        target = S / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(C / 'source-c' / name, target)
    generated = json.loads((R / 'build/verification/agent49-e-sophia-union-a/freeze-final-e.json').read_text())['generated11']
    for name, digest in generated.items():
        source = C / 'source-c/build/generated' / name
        assert sha(source) == digest, name
        target = S / 'build/generated' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    leaf = S / 'src/sophia_land_audio.s'
    leaf.write_text(leaf.read_text() + WRAPPER)
    call = S / 'src/music_drivers/audio.s'
    original = call.read_text()
    assert original.count('  jsr RemainingAudioTick\n') == 1
    call.write_text(original.replace('  jsr RemainingAudioTick\n', '  jsr SophiaLandAudioTick\n'))
    driver = (C / 'build-c.py').read_text()
    old_line = next(line for line in driver.splitlines() if line.startswith('ROOT = Path('))
    driver = driver.replace(old_line, "ROOT = Path(__file__).resolve().parent / 'source-d'", 1)
    (D / 'build.py').write_text(driver)
    after = {name: sha(S / name) for name in catalog}
    changes = {name: dict(before=catalog[name], after=digest) for name, digest in after.items() if catalog[name] != digest}
    assert set(changes) == {'src/sophia_land_audio.s', 'src/music_drivers/audio.s'}
    (D / 'source-catalog-d.json').write_text(json.dumps(after, indent=2) + '\n')
    report = dict(status='PREPARED_LANDING_RETRIGGER_FIX_NOT_BUILT_OR_ADMITTED',
        script_sha256=sha(__file__), parent_revision_sha256=sha(revision),
        source_files=455, source_catalog_sha256=sha(D / 'source-catalog-d.json'),
        changes=changes, generated11=generated,
        phase_cap_bytes=250000000, final_reserve_bytes=50000000,
        global_cap_bytes=70000000000,
        source_c_immutable=True, no_added_RAM=True, main_changed=False,
        limits=['Source update register images and intended retrigger frames; not subframe write-order/waveform identity.',
                'Low-pointer guards apply to the bound genuine21-byte active landing stream, not arbitrary malformed state.',
                'Final actual landing, pause/resume, shared effects, old24 and layout/ABI checks remain required.'],
        accepted_release=False, goal_complete=False)
    (D / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], changes=list(changes), source_catalog_sha256=report['source_catalog_sha256'])))


if __name__ == '__main__':
    main()
