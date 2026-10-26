"""Private body-first Mega/Proto source experiment; never install it."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys, traceback
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
PARENT_HASH = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    Path(p).write_text(json.dumps(value, indent=2) + '\n')


def edit(p, old, new):
    raw = p.read_bytes()
    nl = b'\r\n' if b'\r\n' in raw else b'\n'
    a, b = [v.replace('\n', nl.decode()).encode() for v in (old, new)]
    assert raw.count(a) == 1, (str(p), old)
    p.write_bytes(raw.replace(a, b))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    try:
        assert sha(PARENT / 'candidate.nes') == PARENT_HASH
        manifest = json.loads((PARENT / 'source-manifest.json').read_text())
        source = a.output / 'source'
        for rel, expected in manifest.items():
            old, dest = PARENT / 'source' / rel, source / rel
            assert sha(old) == expected, rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(old, dest)
        engine = source / 'src/metasprite_engine.s'
        edit(engine, '''  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq RotateGuestOAM
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lda #0
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
RotateGuestOAM:''', '''.if ::ENABLE_MMC5_EXPANDED
  ; Check the already-rotated foreign families first. Their saved four
  ; cycles pay for the common-clear X setup below, retaining exact cost.
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lsr
  bcc NonMegaPriority
  jmp MmBodyPriorityBegin
NonMegaPriority:
  lsr                         ; Both Mario0 and Samus2 become zero.
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
.else
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  beq RotateGuestOAM
  cmp #CHARACTER_BILL
  bcs RotateGuestOAM
  lda #0
  sta GuestOamRotationActive
  jmp ClearReservedPlayer
.endif
RotateGuestOAM:''')
        edit(engine, '''  ; Give weapons the first OAM slots. Transparent portions of layered bodies''', '''.if ::ENABLE_MMC5_EXPANDED
  ldx #0
::MmBodyPriorityClearRing:
.endif
  ; Give weapons the first OAM slots. Transparent portions of layered bodies''')
        edit(engine, ''' .endrepeat
  ldx #0
  stx CurrentOAMOffset''', ''' .endrepeat
.if ::ENABLE_MMC5_EXPANDED
  inx
  dex                         ; Preserve the reserved X or foreign zero.
.else
  ldx #0
.endif
  stx CurrentOAMOffset''')
        edit(engine, '''  jsr MegaManDrawShots
  lda CurrentOAMOffset
  sta RgOamPlayerStart
::MegaManProjectileOamReady:
 .if ::ENABLE_MMC5_EXPANDED
  jsr ProtoOamReservation
 .else
  jsr PlayerOAMReservation
 .endif
  clc
  adc CurrentOAMOffset
  sta CurrentOAMOffset
  jmp InitObjectLoop
RosterShots:''', '''  jsr MegaManDrawShots
.if ::ENABLE_MMC5_EXPANDED
  jsr MmBodyPriorityFinish
  jmp InitObjectLoop
  .res 11,$ea                 ; Retain the following object-loop addresses.
.else
  lda CurrentOAMOffset
  sta RgOamPlayerStart
::MegaManProjectileOamReady:
  jsr PlayerOAMReservation
  clc
  adc CurrentOAMOffset
  sta CurrentOAMOffset
  jmp InitObjectLoop
.endif
RosterShots:''')
        edit(engine, '''  sta Sprite_Y_Position,x
  cpx #0
  bne ClearPlayerOAM

InitObjectLoop:''', '''  sta Sprite_Y_Position,x
.if !::ENABLE_MMC5_EXPANDED
  cpx #0
.endif
  bne ClearPlayerOAM
.if ::ENABLE_MMC5_EXPANDED
  sec                         ; DEX/STA already provide CPX0's final N/Z.
.endif

InitObjectLoop:''')
        weapons = source / 'src/megaman_weapons.s'
        edit(weapons, '''  .res 110,$ea
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''', '''::MmBodyPriorityBegin:
  lda #1
  sta GuestOamRotationActive
  farcall KbOamPriority         ; Retain the genuine whole-ring phase update.
  jsr MmBodyPriorityActive
  bcc PriorityLegacy
  lda #2                      ; Existing boolean owner, explicit body-first mode.
  sta GuestOamRotationActive
  jsr ProtoOamReservation
  tax                         ; Reserve40/44 before every nonbody admission.
  lda #0
  sta RgOamRotation
  jmp MmBodyPriorityClearRing
PriorityLegacy:
  ldx #0
  jmp MmBodyPriorityClearRing
::MmBodyPriorityFinish:
  lda GuestOamRotationActive
  cmp #2
  bcc LegacyPlayerStart
  lda #0
  sta RgOamPlayerStart
  bcs PlayerPointerReady
LegacyPlayerStart:
  lda CurrentOAMOffset
  sta RgOamPlayerStart
PlayerPointerReady:
::MegaManProjectileOamReady:
  bcs PriorityFinished
  jsr ProtoOamReservation
  clc
  adc CurrentOAMOffset
  sta CurrentOAMOffset
PriorityFinished:
  rts
  .res 139-(*-MegaManDrawShots),$ea
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''')
        # A separate source-declared segment fills only this verified linker
        # hole; no unrelated library/native/held music span is borrowed.
        raw = weapons.read_bytes()
        nl = b'\r\n' if b'\r\n' in raw else b'\n'
        addition = '''
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "MM_BODY_PRIORITY_GATE"
.proc MmBodyPriorityActive
  lda OperMode
  eor #1
  ora MmDeathFlag
  bne No
  lda OperMode_Task
  cmp #3
  bne No
  lda GameEngineSubroutine
  cmp #8
  bne No
  sec
  rts
No:
  clc
  rts
.endproc
.popseg
.endif
'''
        weapons.write_bytes(raw + addition.replace('\n', nl.decode()).encode())
        cfg = source / 'smb1base-mmc5-expanded.cfg'
        edit(cfg, '    METASPRITE: load = PRGA_04, type = ro;\n', '    METASPRITE: load = PRGA_04, type = ro;\n    MM_BODY_PRIORITY_GATE: load=PRGA_04,type=ro,start=$bf33;\n')
        changed = [rel for rel, h in manifest.items() if sha(source / rel) != h]
        assert sorted(changed) == ['smb1base-mmc5-expanded.cfg', 'src/megaman_weapons.s', 'src/metasprite_engine.s']
        put(a.output / 'source-manifest.json', {rel: sha(source / rel) for rel in manifest})
        patch = []
        for rel in changed:
            patch += list(difflib.unified_diff((PARENT / 'source' / rel).read_text().splitlines(True), (source / rel).read_text().splitlines(True), fromfile='clean731/' + rel, tofile='private/' + rel))
        (a.output / 'source.patch').write_text(''.join(patch))
        builds = []
        for mode in ['candidate', 'canonical', 'ordinary-mmc3', 'ordinary-mmc5']:
            command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'), '--workspace', str(source), '--compiler', str(R / 'tools/Windows/cc65/bin/cl65.exe'), '--output', str(a.output / (mode + '.nes'))]
            if mode.startswith('ordinary-'):
                command += ['--flag-off', mode.split('-')[1]]
            z = subprocess.run(command, cwd=source, capture_output=True, text=True)
            put(a.output / (mode + '.launch.json'), dict(command=command, exit=z.returncode, stdout=z.stdout, stderr=z.stderr))
            assert z.returncode == 0, z.stdout + z.stderr
            expected = sha(a.output / 'candidate.nes') if mode in ['candidate', 'canonical'] else {'ordinary-mmc3': 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb', 'ordinary-mmc5': 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}[mode]
            assert sha(a.output / (mode + '.nes')) == expected
            builds.append(dict(mode=mode, ROM_sha256=expected))
        old, new = [scoped_load(q / 'candidate.nes') for q in [PARENT, a.output]]
        deltas = {bank: sum(x != y for x,y in zip(old['raw'][16+bank*8192:16+(bank+1)*8192], new['raw'][16+bank*8192:16+(bank+1)*8192])) for bank in range(128)}
        deltas = {k:v for k,v in deltas.items() if v}
        assert set(deltas) == {4}, deltas
        assert old['raw'][:16] == new['raw'][:16] and old['raw'][16+128*8192:] == new['raw'][16+128*8192:]
        qb, qa = qualified(PARENT / 'candidate.nes'), qualified(a.output / 'candidate.nes')
        moves = [dict(name=list(n), old=v, new=qa.get(n)) for n,v in qb.items() if qa.get(n) != v]
        put(a.output / 'genuine-symbol-movement.json', moves)
        # The common world/body/capacity implementation is byte-for-byte fixed.
        for n in [('DrawAllMetasprites','InitObjectLoop'), ('DrawAllMetasprites','RosterShots'), ('DrawAllMetasprites','HandleFloateyNumbers'), ('MetaspriteRenderLoop',), ('ProtoOamReservation',)]:
            if n == ('DrawAllMetasprites','RosterShots'):
                continue
            assert qa[n] == qb[n], (n, qb.get(n), qa.get(n))
        assert old['raw'][16+4*8192+0x155:16+4*8192+0x180c] == new['raw'][16+4*8192+0x155:16+4*8192+0x180c]
        assert old['raw'][16+4*8192+0x1f33:16+4*8192+0x1f8b] == bytes([255])*88
        put(a.output / 'proof.json', dict(passed=True, source_only=True, native_run=False, installed=False, parent_ROM_sha256=PARENT_HASH, ROM_sha256=sha(a.output / 'candidate.nes'), changed_source=changed, changed_PRG_bytes=deltas, builds=builds, genuine_symbol_moves=moves, source_manifest_sha256=sha(a.output / 'source-manifest.json'), patch_sha256=sha(a.output / 'source.patch'), tool_sha256=sha(__file__), limits='Build/layout only. GuestOamRotationActive2 and physical mappings are intentional Mega/Proto changes. CPU/fullcaller/foreign/IRQ/capacity/cost and native physical visibility still unqualified. Body-first priority can starve shots/world sprites.'))
        print(json.dumps(dict(output=str(a.output), ROM_sha256=sha(a.output/'candidate.nes'), deltas=deltas, moves=moves), indent=2))
    except BaseException as error:
        put(a.output / 'failure.json', dict(passed=False, error=repr(error), traceback=traceback.format_exc(), tool_sha256=sha(__file__)))
        shutil.copyfile(__file__, a.output / 'failed-tool.py')
        raise


if __name__ == '__main__':
    main()
