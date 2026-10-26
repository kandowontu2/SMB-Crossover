"""Build a private source-derived Luigi dry movement proposal; no native/install."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
SHA = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, z):
    assert not p.exists(), p
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')
def edit(p, old, new):
    raw = p.read_bytes();eol = '\r\n' if b'\r\n' in raw else '\n'
    old = old.replace('\n', eol).encode();new = new.replace('\n', eol).encode()
    assert raw.count(old) == 1, (p, raw.count(old));p.write_bytes(raw.replace(old, new))
def proc(text, old, new):
    value = '.proc ' + old + text.split('.proc ' + old, 1)[1].split('.endproc', 1)[0] + '.endproc\n'
    return value.replace('.proc ' + old, '.proc ' + new, 1)


def derive(s):
    text = (s / 'src/mario_source.s').read_text();physics = (s / 'src/megaman_physics.s').read_text()
    movement = proc(text, 'MarioSourceMovement', 'LuigiSourceMovement')
    movement = movement.replace('  jsr MarioSourceShotTick\n', '  ; RgShootPose remains owned by the unchanged Luigi weapons/graphics path.\n', 1)
    for old, new in [('farcall MarioSourceJump', 'jsr LuigiSourceJump'),
                     ('farcall MarioSourceFriction', 'jsr LuigiSourceFriction'),
                     ('farcall MarioSourceClamp', 'jsr LuigiSourceClamp'),
                     ('farcall MegaManMovement::Horizontal', 'jsr LuigiSourceIntegrate')]:movement = movement.replace(old, new)
    friction = proc(text, 'MarioSourceFriction', 'LuigiSourceFriction').replace('jsr MarioSourceMagnitude', 'farcall MarioSourceMagnitude')
    friction = friction.replace('Apply:\n', 'Apply:\n  jsr LuigiSourceBrakeBlend\n', 1)
    clamp = proc(text, 'MarioSourceClamp', 'LuigiSourceClamp').replace('jsr MarioSourceMagnitude', 'farcall MarioSourceMagnitude').replace('jsr MarioSourceFriction', 'jsr LuigiSourceFriction')
    jump = proc(text, 'MarioSourceJump', 'LuigiSourceJump')
    jump = jump.replace('Launch:\n', '''Launch:
  ; Exactly51/256 extra upward velocity. Hard's existing rise targets remain.
  sec
  lda MmVY+1
  sbc #$33
  sta MmVY+1
  lda MmVY+2
  sbc #0
  sta MmVY+2
''', 1)
    horizontal = physics.split('IntegrateX:', 1)[1].split('  lda Player_State\n  jeq Done', 1)[0]
    horizontal = horizontal[horizontal.index('\n'):]
    release = physics.split('  lda MmFrictionYActive\n', 1)[1].split('BeforeGravity:', 1)[0]
    release = '  lda MmFrictionYActive\n' + release
    first = release.index('  lda SelectedCharacter\n');last = release.index('AppliedFriction:\n')
    release = release[:first] + '''  lda CrossoverBehaviorVersion
  beq SamusFriction
  farcall MmFrictionY
  jmp AppliedFriction
SamusFriction:
  farcall SamusFrictionY
''' + release[last:]
    release = release.replace('jsr NegateY', 'farcall MegaManMovement::NegateY')
    vertical = 'Vertical:\n' + physics.split('\nVertical:\n', 1)[1].split('::MegaMan202Integrated:', 1)[0]
    native = (s / 'src/luigi_native.s').read_text()
    traction = proc(native, 'LuigiNativeTraction', 'LuigiSourceNativeTractionBody')
    prefix = '  lda SelectedCharacter\n  cmp #CHARACTER_LUIGI\n  bne Done\n'
    assert traction.count(prefix) == 1;traction = traction.replace(prefix, '', 1)
    gate = '''; Source-derived current Mario dry profile for Luigi; no new RAM.
; Source producer binds every copied primitive to the exact731 input hashes.
.pushseg
.segment "X5_PROFILES"
.proc LuigiSourceMovementDispatch
  jsr LuigiNativePrepare
  lda SwimmingFlag
  beq Dry
  lda GameEngineSubroutine
  cmp #8
  bne Native
  farcall MarioWaterMovement,jmp
Dry:
  lda #0
  sta MarioWaterActive
  lda GameEngineSubroutine
  cmp #8
  bne Native
  lda Player_State
  cmp #3
  beq Native
  lda JumpspringAnimCtrl
  bne Native
  jmp LuigiSourceMovement
Native:
  farcall CrossoverVanillaMovement,jmp
.endproc
'''
    blend = '''; Keep7/8 of Mario's actual grounded deceleration, rounding once.
; MmProduct is already-clobbered multiplier scratch, not new owner RAM.
.proc LuigiSourceBrakeBlend
  php
  lda Player_State
  jne Done
  lda SwimmingFlag
  jne Done
  txa
  pha
  lda MmSign
  bmi Negative
  ldx #2
Copy:
  lda MmVX,x
  sta MmProduct,x
  dex
  bpl Copy
  bmi Difference
Negative:
  sec
  lda #0
  sbc MmVX
  sta MmProduct
  lda #0
  sbc MmVX+1
  sta MmProduct+1
  lda #0
  sbc MmVX+2
  sta MmProduct+2
Difference:
  sec
  lda MmProduct
  sbc MmMul
  sta MmProduct
  lda MmProduct+1
  sbc MmMul+1
  sta MmProduct+1
  lda MmProduct+2
  sbc MmMul+2
  sta MmProduct+2
  .repeat 3
    lsr MmProduct+2
    ror MmProduct+1
    ror MmProduct
  .endrepeat
  clc
  lda MmMul
  adc MmProduct
  sta MmMul
  lda MmMul+1
  adc MmProduct+1
  sta MmMul+1
  lda MmMul+2
  adc MmProduct+2
  sta MmMul+2
  pla
  tax
Done:
  plp
  rts
.endproc
'''
    integrator = '.proc LuigiSourceIntegrate\n  lda Player_X_Position\n  sta MmOldX\n' + horizontal + '''  lda Player_State
  jne Air
  jmp Finish
Air:
''' + release + '''BeforeGravity:
  farcall MarioSourceGravity
  clc
  adc MmVY
  sta MmVY
  tya
  adc MmVY+1
  sta MmVY+1
  lda MmVY+2
  adc #0
  sta MmVY+2
  bmi Vertical
  cmp #5
  bcc Vertical
  lda #0
  sta MmVY
  sta MmVY+1
  lda #5
  sta MmVY+2
''' + vertical + '''Finish:
  farcall MegaManMovement::Done,jmp
.endproc
'''
    release = integrator.replace('jeq BeforeGravity', 'jeq BeforeGravity')
    result = gate + movement + friction + clamp + jump + blend + release + traction + '.popseg\n'
    assert '.proc MarioSource' not in result and 'SelectedCharacter\n' not in movement
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--output', type=Path, required=True);a = p.parse_args()
    out = a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True, exist_ok=False)
    assert sha(BASE / 'candidate.nes') == SHA
    inventory = json.loads((BASE / 'source-manifest.json').read_text())
    for n, h in inventory.items():assert sha(BASE / 'source' / n) == h, n
    s = out / 'source';shutil.copytree(BASE / 'source', s)
    edit(s / 'src/player.s', '    jsr LuigiNativePrepare\n    jmp CrossoverMarioMovement', '''.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
    jmp LuigiSourceMovementBridge
    .res 3,$ea
.else
    jsr LuigiNativePrepare
    jmp CrossoverMarioMovement
.endif''')
    old = (s / 'src/luigi_native.s').read_text().split('.proc LuigiNativeTraction\n', 1)[1].split('.endproc', 1)[0]
    new = '''.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  ; Foreign callers execute the exact original prefix and original Done RTS.
  lda SelectedCharacter
  cmp #CHARACTER_LUIGI
  bne Done
  farcall LuigiSourceNativeTractionBody,jmp
::LuigiSourceMovementBridge:
  ; Genuine local entry, only called by Luigi's actual movement selector.
  farcall LuigiSourceMovementDispatch,jmp
  .res 83-(*-::LuigiNativeTraction),$ea
Done:
  rts
  .assert *-LuigiNativeTraction=84,error,"Retained native traction public span"
.else
''' + old + '.endif\n'
    edit(s / 'src/luigi_native.s', '.proc LuigiNativeTraction\n' + old + '.endproc', '.proc LuigiNativeTraction\n' + new + '.endproc')
    code = derive(BASE / 'source');(s / 'src/luigi_source_profile.s').write_text(code, encoding='utf-8', newline='\n')
    e = s / 'src/entrypoint.s';raw = e.read_bytes();eol = b'\r\n' if b'\r\n' in raw else b'\n'
    e.write_bytes(raw + ('\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "luigi_source_profile.s"\n.endif\n').replace('\n', eol.decode()).encode())
    changes = ['src/player.s','src/luigi_native.s','src/entrypoint.s','src/luigi_source_profile.s']
    diff = []
    for n in changes:
        before = (BASE / 'source' / n).read_text().splitlines(keepends=True) if (BASE / 'source' / n).exists() else []
        diff += list(difflib.unified_diff(before, (s / n).read_text().splitlines(keepends=True), fromfile='a/' + n, tofile='b/' + n))
    (out / 'implementation.patch').write_text(''.join(diff), encoding='utf-8', newline='\n')
    for n in changes:inventory[n] = sha(s / n)
    put(out / 'source-manifest.json', inventory)
    command = [sys.executable,'-B',str(s / 'tools/build_mmc5_expanded.py'),'--workspace',str(s),
               '--compiler',str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out / 'candidate.nes')]
    r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (out / 'build-host.log').write_text(r.stdout + r.stderr)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-5000:]
    before = (BASE / 'candidate.nes').read_bytes();after = (out / 'candidate.nes').read_bytes()
    assert len(before) == len(after) and before[:16] == after[:16] and before[1048592:] == after[1048592:]
    banks = {k:sum(x != y for x,y in zip(before[16+k*8192:16+(k+1)*8192],after[16+k*8192:16+(k+1)*8192])) for k in range(128)}
    banks = {k:v for k,v in banks.items() if v};assert set(banks) == {1,78}, banks
    put(out / 'preparation.json', dict(prepared=True, native_executed=False, adopted=False, parent_ROM_sha256=SHA,
        ROM_sha256=sha(out / 'candidate.nes'), changed_source=changes, changed_PRG_banks=banks,
        original_header_CHR_RAM_fixed_DMC_all_other_banks_exact=True, game_source_or_installed_mutation=False,
        new_RAM=False, boost='51/256 extra upward speed, same mode-specific Mario rise/release/gravity',
        braking='Mario base output + floor((original magnitude - base output)/8), only dry ground',
        source_derived_current_primitives=True, source_files={n:sha(s / n) for n in changes},
        original_input_source_files={n:sha(BASE / 'source' / n) for n in ['src/mario_source.s','src/megaman_physics.s','src/luigi_native.s']},
        patch_sha256=sha(out / 'implementation.patch'), source_manifest_sha256=sha(out / 'source-manifest.json'),
        tool_sha256=sha(__file__), command=command,
        scope='First private dry movement proposal. Full source/ABI/foreign/IRQ/pickup/graphics/terrain controls pending. Legacy water/climb/spring/stomp/gap dispatch intentionally unchanged; no native/art/hardware/lag qualification.'))
    print(json.dumps(json.loads((out / 'preparation.json').read_text()), indent=2))


if __name__ == '__main__':main()
