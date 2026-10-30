"""Source-build Rogue's missing native level-exit contact without new RAM."""
from pathlib import Path
import difflib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R/'build/rogue-dawn-side-v1'
U = R/'build/rogue-dawn-host-ui-v1'
O = R/'build/rogue-dawn-flagpole-v1'


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


CONTACT = """; Actual source-radius contact, followed by SMB's own flagpole transaction.
; No X threshold, forced engine outcome, borrowed RAM or speculative latch.
; Called only by the raw2/variant1 PLAYER background call. During automatic
; victory/pipe/death movement the player uses SMB motion, so use its terrain
; owner too. Source movement has already resolved solids during engine8.
.pushseg
.segment "ROGUE_DAWN_HOST"
.export RdBoxOrExit,RdNonSolidBG,RdNonSolidBGEnd
RdBoxOrExit:
 php
 pha
 txa
 pha
 tsx
 ; Real stack: original JSR return, resident saved bank, SMC JSR return,
 ; then the three saves above. Both existing callers remain genuine JSRs.
 lda $0107,x
 cmp #<(RdAfterBGCall-1)
 bne Box
 lda $0108,x
 cmp #>(RdAfterBGCall-1)
 bne Box
 pla
 tax
 pla
 plp
 jmp RdNonSolidBG
Box:
 pla
 tax
 pla
 plp
 jmp RdBodySelectBox
.assert * <= $bf00,lderror,"Dispatch fits verified pre-descriptor fill"
.popseg
"""

WORKER = """.pushseg
.segment "ROGUE_DAWN_HOST"
.assert *=$bf32,lderror,"Frozen death descriptors end unchanged"
.proc RdNonSolidBG
 lda GameEngineSubroutine
 cmp #8
 beq SourceContact
 jmp PlayerBGCollision
SourceContact:
 ; Same complete six-byte scratch/register save as source terrain services.
 RdHsSave
 lda Player_Y_HighPos
 cmp #1
 bne Done
 ; The actual source body center must reach the four-pixel flagpole shaft.
 ; This avoids activating a sixteen-pixel metatile from its empty edges.
 lda RdX
 and #$0f
 cmp #6
 bcc Done
 cmp #10
 bcs Done
 lda RdX
 sta Rh4
 lda RdRoomHi
 sta Rh2
 lda #2
 sta Rh5
 lda #0
 sta Rh6
Sample:
 lda RdY
 ldx Rh6
 beq Top
 dex
 beq Query
 clc
 adc RdRadiusY
 sec
 sbc #1
 jmp Query
Top:
 sec
 sbc RdRadiusY
Query:
 sta Rh3
 jsr RdHsReadCell
 cmp #$24
 beq Flag
 cmp #$25
 beq Flag
 inc Rh6
 lda Rh6
 cmp #3
 bne Sample
Done:
 clc
 jmp RdHsRestoreC
Flag:
 ; Reconstruct the real native column pointer from the authenticated query.
 ; The fixed owner performs sound, score, enemy cleanup and vine anchoring.
 lda Rh2
 and #1
 lsr
 lda Rh4
 ror
 lsr
 lsr
 lsr
 jsr GetBlockBufferAddr
 jsr FlagpoleCollision
 jmp Done
.endproc
RdNonSolidBGEnd:
.assert * <= $c000,lderror,"Approved A95 host tail exhausted"
.popseg
"""


def main():
    assert not (O/'build.json').exists(), 'Frozen successor'
    parent = json.loads((P/'handoff.json').read_text())
    for z in parent['bindings']:
        assert ref.binding(z['path']) == z, z['path']
    b = scoped_load(P/'candidate.nes')
    assert ref.digest(b['raw']) == '490a2e280dd475df265582efd18870ac4f3d09be4734ddc03fb3a8339b7c6a45'
    for start, end in [(0xbedd, 0xbf00), (0xbf32, 0xc000)]:
        at = 16+95*8192+(start & 8191)
        assert b['raw'][at:at+end-start] == bytes([255])*(end-start)
    O.mkdir(exist_ok=True)
    for name in ['main.c', 'private.cfg']:
        (O/name).write_bytes((P/name).read_bytes())
    player = (U/'player.s').read_text()
    player = once(player, '  jsr RdNativeBGGate         ; source Rogue already collided; exact foreign tail',
                  '  jsr RdNativeBGGate         ; source terrain plus native level-exit contact\n::RdAfterBGCall:')
    (O/'player.s').write_text(player)
    luigi = (U/'luigi_native.s').read_text()
    start = luigi.index('::RdNativeBGGate:')
    end = luigi.index('::RdBodyBoxSelectBridge:', start)
    new = """::RdNativeBGGate:
  .assert RdNativeBGGate=$b958,error,"Approved exact B1 padding"
  ; Incoming A is dead: both real background owners begin with LDA; the
  ; actual caller immediately loads SmCeilingHit. Keep P and fixed PCs.
  php
  lda SelectedCharacter
  cmp #2
  bne Native
  lda RdVariant
  cmp #1
  bne Native
  plp
  jmp RdBodyBoxSelectBridge
Native:
  plp
  jmp PlayerBGCollision
  .byte $ea
  .assert *-RdNativeBGGate=24,error,"Exact private gate footprint"
"""
    luigi = luigi[:start]+new+luigi[end:]
    luigi = once(luigi, 'lda #<RdBodySelectBox', 'lda #<RdBoxOrExit')
    luigi = once(luigi, 'lda #>RdBodySelectBox', 'lda #>RdBoxOrExit')
    (O/'luigi_native.s').write_text(luigi)
    (O/'contact-dispatch.s').write_text(CONTACT)
    (O/'contact-worker.s').write_text(WORKER)
    entry = (P/'entrypoint.s').read_text()
    entry = once(entry, '.include "rogue_dawn_live_cue_gate_v1.s"',
                 '.include "rogue_dawn_live_cue_gate_v1.s"\n.include "contact-dispatch.s"')
    entry = once(entry, '.include "rogue_dawn_death_art.inc"',
                 '.include "rogue_dawn_death_art.inc"\n.include "contact-worker.s"')
    (O/'entrypoint.s').write_text(entry)
    patch = ''
    for name, old in [('player.s', (U/'player.s').read_text()),
                      ('luigi_native.s', (U/'luigi_native.s').read_text()),
                      ('entrypoint.s', (P/'entrypoint.s').read_text())]:
        patch += ''.join(difflib.unified_diff(old.splitlines(True), (O/name).read_text().splitlines(True),
                                             fromfile='parent/'+name, tofile='flagpole/'+name))
    (O/'source.patch').write_text(patch)
    cmd = json.loads((P/'build.json').read_text())['executed_commands'][-1]
    cmd = [z.replace(str(P), str(O)) for z in cmd]
    k = cmd.index('--asm-include-dir')
    cmd[k:k] = ['--asm-include-dir', str(O), '--asm-include-dir', str(P)]
    z = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
    log = O/'build.log'
    if log.exists() and not (O/'build.json').exists():
        negative = O/'build-negative-1.log'
        if not negative.exists():
            negative.write_bytes(log.read_bytes())
    log.write_text(z.stdout+z.stderr)
    assert z.returncode == 0, (z.stdout+z.stderr)[-6000:]
    prepare(R, O/'candidate.nes')
    n = scoped_load(O/'candidate.nes')
    assert address(n, 'RdCueGateEnd') == 0xbedd
    assert address(n, 'RdDeathRecordA') == 0xbf00
    assert address(n, 'RdDeathRecordEnd') == 0xbf32
    assert address(n, 'RdNonSolidBGEnd') <= 0xc000
    assert n['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32] == b['raw'][16+95*8192+0x1f00:16+95*8192+0x1f32]
    assert n['raw'][16+1048576:] == b['raw'][16+1048576:]
    allowed = set(range(location(n, 'RdNativeBGGate'), location(n, 'RdNativeBGGate')+24))
    allowed.update(range(location(n, 'RdBodyBoxSelectBridge'), location(n, 'RdBodyBoxSelectBridge')+15))
    for start, end in [(0xbedd, 0xbf00), (0xbf32, 0xc000)]:
        allowed.update(range(16+95*8192+(start & 8191), 16+95*8192+(end & 8191))) if end != 0xc000 else allowed.update(range(16+95*8192+(start & 8191), 16+96*8192))
    changes = [i for i, (x, y) in enumerate(zip(b['raw'], n['raw'])) if x != y]
    assert set(changes) <= allowed, [hex(i) for i in changes if i not in allowed][:20]
    deps = dependencies(O/'assembler-full.dep')
    assert O/'player.s' in deps and O/'luigi_native.s' in deps
    proof = dict(passed=True, source_build_only=True, native_run=False, qualified=False,
                 ROM=ref.binding(O/'candidate.nes'), parent=ref.binding(P/'candidate.nes'),
                 executed_commands=[cmd], changed_bytes=len(changes), new_RAM=0,
                 new_code=dict(dispatch='BEDD..BF00', worker_end=hex(address(n, 'RdNonSolidBGEnd'))),
                 unchanged_originals_and_solid_collision=True,
                 bindings=[ref.binding(p) for p in dict.fromkeys(deps+[Path(__file__), P/'handoff.json',
                      O/'private.cfg', O/'source.patch', O/'candidate.nes', O/'candidate.dbg',
                      O/'candidate.lbl', O/'candidate.map'])])
    (O/'build.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ['ROM', 'changed_bytes', 'new_RAM', 'new_code']}))


if __name__ == '__main__':
    main()
