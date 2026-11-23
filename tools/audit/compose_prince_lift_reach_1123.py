"""Bind the Prince's supported upward reach and translated fall to native terrain."""

import json
from types import SimpleNamespace

import compose_prince_oneup_lift_1123 as C
import prince_pickup_reach_1112 as Projection
import probe_prince_lift_swept_plane_1123 as Sweep


L = C.Lift
NATIVE_HEAD = 0x9BCC
HEAD_BANK = 126
NATIVE_HEAD_OFFSET = 16 + HEAD_BANK * 8192 + NATIVE_HEAD - 0x8000
LIFT_CENTRE_Y = 166
OLD_HEAD = bytes.fromhex(
    'a48e1031a407c004902b8d6a01a9118d6c01a9bb8d6d01a9be205a01'
    'b013c000d00620f59e4c019c2902f005a9028d05014c74e6ea')
GROUND_CHECK = 0xA62C
OLD_GROUND = bytes.fromhex('ad11c6c9c4')
NEW_GROUND = bytes.fromhex('ad85c0c901')
PICKUP_ENTRY = 0xC7B3
PICKUP_STAGE = 0xC65F + PICKUP_ENTRY - 0xC766
OLD_PICKUP = bytes.fromhex('adcfc6f031b5344ad032b51f1028b00c')
NEW_PICKUP = bytes.fromhex('adcfc6f031b51f102db5344ad02eb00c')

REACH = '''
Head:
 lda Player_Y_Position
 pha
 lda $c617
 cmp #78
 bne HeadNative
 lda Player_Y_Position
 cmp #48
 bcc HeadNative
 sbc #16
 sta Player_Y_Position
HeadNative:
 jsr $9587
 pla
 sta Player_Y_Position
 lda R3
 php
 cmp #$60
 bne HeadReturn
 cmp R2
 bne HeadReturn
 lda $c616
 cmp #28
 bne HeadReturn
 lda R4
 cmp #4
 bcc HeadReturn
 txa
 pha
 tya
 pha
 jsr Eligible
 bcc HeadRestore
 jsr Actor
 bcc HeadRestore
 txa
 cmp PlatformCollisionFlag,x
 bne HeadRestore
 lda Enemy_Y_Speed,x
 bpl HeadRestore
 ; The carry comparison leaves carry set. Only the high bit is consumed before the
 ; native head transaction or the next probe overwrites this scratch byte.
 ror R4
HeadRestore:
 pla
 tay
 pla
 tax
HeadReturn:
 plp
 lda R3
 rts
'''


def compact_import(text):
    once = L.F.Q.P.G.First.once
    text = once(text, ' lda $c0ab\n cmp #167\n bne SkipAdmission\n jsr Allocator\nSkipAdmission:',
                ' jsr Allocator')
    text = once(text, ' cmp Enemy_Y_Position,x\n bne SupportNo\n lda Enemy_Y_Position,x\n sec\n rts',
                ' cmp Enemy_Y_Position,x\n bne SupportNo\n rts')
    text = once(text, ' bcc SweepNo\n lda Enemy_Y_Position,x\n sec\n rts',
                ' bcc SweepNo\n lda Enemy_Y_Position,x\n rts')
    text = once(text, 'SupportNo:\n clc\n rts\nSweep:', 'Sweep:')
    text = once(text, 'EligibleNo:\n clc\n rts\nActor:', 'Actor:')
    text = text.replace('SupportNo', 'SweepNo').replace('EligibleNo', 'SweepNo')
    text = once(text, ' jsr $015a\n rts\nMaterialAccept:', ' jmp $015a\nMaterialAccept:')
    # X=1008 is already authenticated. Adding 29 to the player's low byte
    # computes (world X + 13 - 1008) relative to page four in one carry.
    text = once(text, ''' lda Player_X_Position
 clc
 adc #13
 tay
 lda Player_PageLoc
 adc #0
 pha
 tya
 sec
 sbc Enemy_X_Position,x
 tay
 pla
 sbc Enemy_PageLoc,x
 bne ActorNext
''', ''' lda Player_X_Position
 clc
 adc #29
 tay
 lda Player_PageLoc
 adc #0
 cmp #4
 bne ActorNext
''')
    start = text.index(' sta $c086\n')
    end = text.index(' lda $c611\n sta $c08b', start)
    # Support proves top >=32 via its non-wrapping player Y+32 equality.
    # Subtracting the donor's three-pixel anchor first preserves the full
    # signed lift top - source Y - 3 result without two high-byte adjustments.
    return text[:start] + ''' sta $c086
 sec
 sbc #3
 sbc $c611
 sta $c089
 lda #0
 sta $c087
 sbc #0
 sta $c08a
''' + text[end:] + REACH


def allocator(origin, labels, bundle):
    old = L.Admission.ASM
    camera = old[old.index(' lda ScreenLeft_PageLoc'):old.index('Finish:')]
    body = old[old.index(' ldx #5'):old.index('Restore:\n')]
    body = L.F.Q.P.G.First.once(body, ' sta Enemy_BoundBoxCtrl,x\n',
                               ' sta Enemy_BoundBoxCtrl,x\n lda #CentreY\n sta YPlatformCenterYPos,x\n')
    # The enclosing Import saves all four registers. Use its shared in-stage
    # eligibility check and keep the allocator's ObjectOffset save.
    source = ' jsr SharedEligible\n bcc Finish\n' + camera
    source += 'Finish:\n rts\nEligible:\n' + body + 'Restore:\n rts\n'
    original = L.Admission.machine_code
    assemble = original.__globals__['assemble']

    def relocated(_text, fields, _origin):
        camera_range = fields['AfterCameraLow'] - fields['FirstCameraLow']
        tightened = source.replace(' cmp #FirstCameraLow\n bcc Finish\n cmp #AfterCameraLow',
                                   ' sec\n sbc #FirstCameraLow\n cmp #CameraRange')
        return assemble(tightened, dict(fields, SharedEligible=labels['Eligible'],
                                        CameraRange=camera_range, CentreY=LIFT_CENTRE_Y,
                                        YPlatformCenterYPos=C.W.address(bundle, 'YPlatformCenterYPos')), origin)

    make = L.F.Q.P.clone(original, dict(assemble=relocated, ORIGIN=origin))
    return make(SimpleNamespace(bundle=bundle))


def rewrite_core(core, labels, bundle):
    at = Projection.CODE - 0xA000
    assert core[at:at + 33] == Projection.WORKER + bytes(2)
    # Only the original reach action and projected pose pay a bank round trip.
    gate, _ = L.assemble('''
 lda $c616
 cmp #28
 beq Project
 lda $c617
 cmp #78
 beq Project
 jmp $9587
Project:
''', {}, Projection.CODE)
    worker = gate + L.gateway(labels['Head'], bundle)
    assert len(worker) == 32
    core[at:at + len(worker)] = worker
    at = GROUND_CHECK - 0xA000
    assert core[at:at + len(OLD_GROUND)] == OLD_GROUND
    core[at:at + len(NEW_GROUND)] = NEW_GROUND


def plan(raw):
    def build(parent):
        return L.plan(parent, extend=compact_import, build_allocator=allocator,
                      rewrite_core=rewrite_core)

    body, labels, parts, packed, detail = Sweep.compact_plan(
        raw, width=48, logical_history=True, builder=build)
    # This routine is staged below C766 before being published at C7B3.
    # Check the live item's maturity before dispatching any reward type.
    state = parts[2]
    at = PICKUP_STAGE - 0xC100
    end = at + len(OLD_PICKUP)
    assert state[at:end] == OLD_PICKUP
    state = state[:at] + NEW_PICKUP + state[end:]
    encoded = C.Packet.encode(state)
    assert C.Packet.decode(encoded, len(state)) == state
    packed[2] = encoded
    return body, labels, parts[:2] + (state,), packed, detail


def native_gate():
    # AND #2 already supplies A=2 on the nonzero sound path. The redundant
    # LDA #2 funds the two bytes for the scoped ascent flag.
    asm = '''
 ldy R4
 bmi Effect
 bit Player_Y_Speed
 bpl Foot
 cpy #4
 bcc Foot
Effect:
 sta $016a
 lda #$11
 sta $016c
 lda #$bb
 sta $016d
 lda #$be
 jsr $015a
 bcs Bounce
 cpy #0
 bne Sound
 jsr $9ef5
 jmp Foot
Sound:
 and #2
 beq Bounce
 sta $0105
Bounce:
 jmp $e674
 nop
'''
    data, _ = L.assemble(asm, dict(R4=7, Player_Y_Speed=0x8E, Foot=0x9C01), NATIVE_HEAD)
    assert len(data) == len(OLD_HEAD) == 0x9C01 - NATIVE_HEAD
    return data


def compose(raw):
    assert C.H(raw) == C.PARENT
    body, labels, previous, packed, detail = plan(raw)
    chunks = previous + (body,)
    head, _, _ = C.Packet.extract(raw)
    assert head[C.Packet.LOADER:] == C.PARENT_LOADER
    config = C._stage_spec(chunks, packed)
    use_stage_y = len(head) + 28 + sum(map(len, packed)) > len(C.Packet.PAGES) * 1024
    loader = C._loader(head[C.Packet.LOADER:], dict(C.W.Symbols.bundle(), raw=raw), config, use_stage_y)
    payload = head[:C.Packet.LOADER] + loader + b''.join(packed[i] for i in C.STREAM_ORDER)
    assert config[0][2] <= (0xDC00 - 0xC500) + (0xC500 - C.WRAP)
    assert config[1][0] >= 0xC900 and all(C.STAGING + config[i][2] < 0xC800 for i in (2, 3))
    assert len(payload) <= len(C.Packet.PAGES) * 1024, ('Carrier bytes', len(payload), detail)
    image, cookie = C._install_packet(raw, chunks, payload)
    at = NATIVE_HEAD_OFFSET
    assert image[at:at + len(OLD_HEAD)] == OLD_HEAD
    gate = native_gate()
    image = image[:at] + gate + image[at + len(gate):]
    assert C.extract(image) == (chunks, config, cookie, len(payload))
    overlay = dict(passed=True, parent_SHA256=C.PARENT, expected_memory_only_SHA256=C.H(image),
                   decoded=chunks, cookie=cookie.hex(), raw1_labels=labels, support=detail,
                   lift=dict(id=37, left=1008, width=48, initial_top=192, center_y=LIFT_CENTRE_Y),
                   spare_bytes=len(C.Packet.PAGES) * 1024 - len(payload), patches=[])
    spans = [(at, len(OLD_HEAD)), (C.Packet.COOKIE, 16)]
    spans.extend((C.Packet.CHR + page * 1024, 1024) for page in C.Packet.PAGES)
    for start, size in spans:
        old, new = raw[start:start + size], image[start:start + size]
        if old != new:
            overlay['patches'].append(dict(file_offset=start, old_hex=old.hex(), new_hex=new.hex()))
    assert C.inverse(image, overlay) == raw
    return image, overlay


def recover_parent(image):
    """Restore the precise Downloads parent using only the revised image."""
    (core, metadata, state, lift), _, _, _ = C.extract(image)
    core, state = bytearray(core), bytearray(state)
    at = Projection.CODE - 0xA000
    core[at:at + 32] = Projection.WORKER + b'\x00'
    at = GROUND_CHECK - 0xA000
    assert core[at:at + len(NEW_GROUND)] == NEW_GROUND
    core[at:at + len(OLD_GROUND)] = OLD_GROUND
    at = PICKUP_STAGE - 0xC100
    assert state[at:at + len(NEW_PICKUP)] == NEW_PICKUP
    state[at:at + len(OLD_PICKUP)] = OLD_PICKUP
    at = NATIVE_HEAD_OFFSET
    end = at + len(OLD_HEAD)
    assert image[at:end] == native_gate()
    return C.restore_original_packet(image[:at] + OLD_HEAD + image[end:],
                                     core, metadata, bytes(state), lift)


if __name__ == '__main__':
    from run_prince_oneup_lift_native_1123 import Timing

    raw = Timing.ROM.read_bytes()
    image, proof = compose(raw)
    keep = ('expected_memory_only_SHA256', 'spare_bytes', 'cookie', 'raw1_labels', 'support')
    print('PRINCE REACH COMPOSE ' + json.dumps({name: proof[name] for name in keep}), flush=True)
