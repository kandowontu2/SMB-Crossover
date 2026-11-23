"""Exact06336 source-only proposal: one native1-1 Mushroom-access lift.

Uses the retained14-row table recipe inside the existing ROWS/PIPE/REFRESH
envelopes. All13 installed placements, the original motor and the current
off-left retirement path remain exact. No ROM/file/emulator writer exists.
"""
from functools import lru_cache
from pathlib import Path
import json

import compose_dkjr_head_bridge_current_1123 as Head
import compose_dkjr_head_bridge_1113 as Old

M, H, R = Head.M, Head.H, Head.R
PIN = Head.CANDIDATE
CANDIDATE = '656c91db62c6c7825b00de8c349be991017941b2d0ced1e0c23d943f284b8339'
PARENT_COOKIE = bytes.fromhex('a72801e22510d5b842cdf64324d6a962')
GIRDER_SHA = '38495b2a882e2a0a319a9d14a5d3b565b506996aead61e911b8df19e9c925f61'
OLD_COMPOSER_SHA = '2c0617ef61f61d858af4f6d5690c528912e5b2aeb1fb84a1c6e79a0a003e75fa'
LAYOUT = dict(ROWS=(0xd2c4, 14), PIPE=(0xd18b, 117), REFRESH=(0xb624, 129))
OLD_COLUMNS = (26, 30, 35, 39, 43, 47, 55, 59, 88, 161, 165, 177, 190)
OLD_CENTERS = (128, 128, 177, 177, 169, 169, 161, 161, 0, 177, 128, 177, 128)


@lru_cache(maxsize=1)
def programs():
    assert H(Old.GIRDER.read_bytes()) == GIRDER_SHA
    assert H(Path(Old.__file__).read_bytes()) == OLD_COMPOSER_SHA
    old, new = Old.girder_images()
    # A narrow native oscillator starting at192 about188 rises only far
    # enough for the original jump. The broad128 oscillator can carry the
    # collector into the authored low row after the authentic underside hit.
    image = bytearray(new['images']['REFRESH'])
    image[new['symbols']['OscillatorY']-LAYOUT['REFRESH'][0]] = 188
    new['images']['REFRESH'] = bytes(image)
    assert old['used']['ROWS'] == 13 and new['used']['ROWS'] == 14
    assert old['used']['REFRESH'] == 128 and new['used']['REFRESH'] == 129
    assert old['used']['PIPE'] == new['used']['PIPE'] == 117
    assert tuple(old['images']['ROWS']) == OLD_COLUMNS
    assert tuple(new['images']['ROWS']) == (21,)+OLD_COLUMNS
    off = old['symbols']['OscillatorY']-LAYOUT['REFRESH'][0]
    assert new['symbols']['OscillatorY'] == old['symbols']['OscillatorY']
    assert old['images']['REFRESH'][off:] == bytes(OLD_CENTERS)
    assert new['images']['REFRESH'][off:] == bytes((188,)+OLD_CENTERS)
    refresh_changes = [(i, a, b) for i, (a, b) in enumerate(zip(old['images']['REFRESH'][:off], new['images']['REFRESH'][:off], strict=True)) if a != b]
    assert len(refresh_changes) == 1 and refresh_changes[0][1:] == (8, 9)
    assert old['symbols']['DkAfterNativeConstructor'] == new['symbols']['DkAfterNativeConstructor'] == 0xd1f0
    changes = [(i, a, b) for i, (a, b) in enumerate(zip(old['images']['PIPE'], new['images']['PIPE'], strict=True)) if a != b]
    assert len(changes) == 1 and changes[0][1:] == (12, 13)
    return old, new


def old_images():
    old, _ = programs()
    # Both tail bytes are in retained owned table envelopes. The13-row
    # indexed domains never read the newly used entries; carry starts B6A5.
    return dict(ROWS=old['images']['ROWS']+b'\xa9', PIPE=old['images']['PIPE'],
                REFRESH=old['images']['REFRESH']+b'\xff')


def chunks(pc, data):
    yield from Head.chunks(pc, data)


def proposal(parent):
    assert isinstance(parent, bytes) and len(parent) == 2097168 and H(parent) == PIN
    Head.inverse(parent)
    assert parent[Head.COOKIE_AT:Head.COOKIE_AT+16] == PARENT_COOKIE
    old, new = programs()
    body, out, owned, spans = Head.payload(parent), bytearray(parent), set(), []
    for name, (pc, size) in LAYOUT.items():
        before, after = old_images()[name], new['images'][name]
        assert len(before) == len(after) == size
        assert body[Old.offset(pc):Old.offset(pc)+size] == before, (name, body[Old.offset(pc):Old.offset(pc)+size].hex(), before.hex())
        for (at, a), (other, b) in zip(chunks(pc, before), chunks(pc, after), strict=True):
            assert at == other and parent[at:at+len(a)] == a
            assert not owned.intersection(range(at, at+len(a)))
            owned.update(range(at, at+len(a)));out[at:at+len(b)] = b
            spans.append(dict(role=name, file=at, bytes=len(b), old_SHA256=H(a), new_SHA256=H(b)))
    payload = Head.payload(out)
    cookie = b'\xa7\x28\x01'+bytes.fromhex(H(payload))[:13]
    out[Head.COOKIE_AT:Head.COOKIE_AT+16] = cookie
    owned.update(range(Head.COOKIE_AT, Head.COOKIE_AT+16))
    candidate = bytes(out)
    changed = {i for i, (a, b) in enumerate(zip(parent, candidate, strict=True)) if a != b}
    assert changed <= owned and len(owned) == 276
    # The new row shifts indices, preserving type/position/travel data for
    # every existing helper including the horizontal1408 actor at index9.
    for old_index, column in enumerate(OLD_COLUMNS):
        index = old_index+1
        assert new['images']['ROWS'][index] == column
        assert new['images']['REFRESH'][new['symbols']['OscillatorY']-0xb624+index] == OLD_CENTERS[old_index]
    if CANDIDATE is not None:
        assert H(candidate) == CANDIDATE
    return candidate, dict(parent_SHA256=PIN, candidate_SHA256=H(candidate),
        packet_SHA256=H(payload), cookie=cookie.hex(), changed_bytes=len(changed), owned_bytes=len(owned),
        spans=spans, source_SHA256=GIRDER_SHA, composer_SHA256=H(Path(__file__).read_bytes()),
        added_helper=dict(character='Donkey Kong Jr. (Donkey Kong, Select once)', stage='1-1',
            left=336, center=352, initial_top=192, collision_width=32, native_ID=37, motion_center=188),
        original13_helpers_preserved=True, native_retirement_code_unchanged=True,
        original_jump_and_head_bridge_unchanged=True, native_dynamic_six_slot_allocator_unchanged=True,
        new_capacity=0, new_RAM=0, outputs=0, native_qualified=False)


def inverse(candidate):
    assert CANDIDATE is not None and isinstance(candidate, bytes) and H(candidate) == CANDIDATE
    out = bytearray(candidate)
    for name, (pc, _) in LAYOUT.items():
        for at, data in chunks(pc, old_images()[name]):
            out[at:at+len(data)] = data
    out[Head.COOKIE_AT:Head.COOKIE_AT+16] = PARENT_COOKIE
    parent = bytes(out)
    assert H(parent) == PIN and proposal(parent)[0] == candidate
    return parent


if __name__ == '__main__':
    _, q = proposal(M.ROM.read_bytes())
    print('DK MUSHROOM HELPER '+json.dumps(q, separators=(',', ':')), flush=True)
