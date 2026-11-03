"""Compile the actual stomp event and genuine native head-range policy."""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A

R, O, W = A.R, A.O, A.W


def main():
    previous = json.loads((O / 'native-bbox-v65-layout.json').read_text())
    source = (O / 'native-bbox-v65.s').read_text()
    native = W.scoped_load(R / 'build/excitebike-pose-1101-v3/current4.nes')
    head = W.address(native, 'PlayerHeadWithinTerrain')
    head_at = W.location(native, 'PlayerHeadWithinTerrain')
    current = R / 'build/bub-initial-tier-1103-v87/bub-initial-tier.nes'
    assert current.read_bytes()[head_at:head_at + 32] == native['raw'][head_at:head_at + 32]
    assert head >= 0xe000 and ((head_at - 16) // 8192) == 127
    source = ('.export DkjrJumpRestart,DkNativeHeadWithin\n'
        'DkjrJumpRestart=D_d257\nDkNativeHeadWithin=$%04x\n' % head) + source
    leaf = '''
.export DkNativeBounce
; Only actual native stomp dispatch reaches this service. An ordinary native
; vertical speed never restarts donor motion. The donor's actual D257 jump
; transition retains latched direction and all original displacement/timing.
; Its equal-state guard is deliberately bypassed for a real second stomp.
DkNativeBounce:
 php
 pha
 txa
 pha
 tya
 pha
 lda $c8fe
 beq DkBounceNo
 lda $c068
 bne DkBounceNo
 lda $c06b
 cmp #5
 beq DkBounceNo
 lda #3
 sta $c06b
 jsr DkjrJumpRestart
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
DkBounceNo:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
'''
    marker = 'DkNativePortsEnd:\n'
    assert source.count(marker) == 1
    source = source.replace(marker, leaf + marker)
    targets = dict(previous['implemented_vector_rows'])
    targets.update({'27': 'DkNativeBounce', '28': 'DkNativeHeadWithin'})
    at = source.index('DkServices:\n') + len('DkServices:\n')
    lines = source[at:].splitlines(True)
    for i in range(38):
        assert lines[i].startswith(' jmp ')
        lines[i] = ' jmp ' + targets.get(str(i), 'DkUnavailable') + '\n'
    source = source[:at] + ''.join(lines)
    cfg = (O / 'native-bbox-v65.cfg').read_text().replace('native-bbox-', 'native-event-').replace('-v65.bin', '-v74.bin')
    blob, labels = A.assemble('native-event-v74', source, cfg)
    assert len(blob) == previous['body_bytes'] and labels['DkPauseThaw'] == 0xd60c
    assert labels['DkNativePortsEnd'] <= 0xd800
    before = (O / 'native-bbox-v65.bin').read_bytes()
    differences = [i for i, (a, b) in enumerate(zip(before, blob)) if a != b]
    assert set(differences) <= set(range(27 * 3, 29 * 3))
    q = dict(previous)
    q.update(labels=labels, body_bytes=len(blob), body_end=labels['DkjrComponentEnd'],
        header_spare=8160-len(blob), metadata_end=labels['DkNativePortsEnd'],
        metadata_spare=0xd800-labels['DkNativePortsEnd'],
        implemented_vector_rows=targets,
        unimplemented_rows=[i for i in range(38) if str(i) not in targets],
        actual_native_bounce='Actual native event27 calls original D257 exactly once; no speed inference, no mutable event flag, no extra motion step. Guarded during source hitstop/defeat/unconstructed state.',
        native_head_range=dict(row=28, target=head, physical_PRG=127,
            source='Unchanged fixed PlayerHeadWithinTerrain; original donor solid/vine movement queries remain separate.'),
        private_event_bytes=labels['DkNativePortsEnd']-labels['DkNativeBounce'],
        scope='Compiled private event/head policies only; actual public/raw40 classifier authority and full source/native/IRQ/lifetime qualification still required. No shared source or ROM mutation.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [Path(__file__),
            O / 'native-bbox-v65.s', O / 'native-bbox-v65-layout.json',
            O / 'native-event-v74.s', O / 'native-event-v74.bin',
            O / 'native-event-ports-v74.bin', R / 'src/collision.s', current]})
    (O / 'native-event-v74-layout.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps({k: q[k] for k in ['passed', 'body_bytes', 'header_spare', 'metadata_end', 'metadata_spare', 'private_event_bytes', 'unimplemented_rows']}))


if __name__ == '__main__':
    main()
