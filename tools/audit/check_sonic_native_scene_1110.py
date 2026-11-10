"""Memory-only Sonic scripted-scene derivative and qualification API."""
from hashlib import sha256
from unittest.mock import patch

import check_sonic_native_effects_aligned_1110 as Aligned
import check_sonic_public_admission_1110 as Public
import sonic_sms_native_scene_1110 as Scene

T, E, C, O = Aligned.T, Aligned.E, Aligned.C, Aligned.O
PIN = '7de72fb7d315cd78288790e84ff0ff988e9f62906470edeb43a8ccf3104bf2ef'
OLD_COOKIE = bytes.fromhex('a72b0148fc67939017476de86f7ce64f')
META_OFFSET = 1048592 + 328 * 1024
COOKIE_OFFSET = 1034472


def proposal(raw, aligned):
    """Apply only scene metadata and its exact existing physical cookie."""
    old = aligned['packet']
    assert old['cookie'] == OLD_COOKIE
    assert raw[META_OFFSET:META_OFFSET + 1024] == old['metadata']
    for row, page in enumerate((321, 322, 323, 324, 325, 326, 327, 330)):
        start = 1048592 + page * 1024
        assert raw[start:start + 1024] == old['kernel'][row * 1024:(row + 1) * 1024]
    p = Scene.build(aligned, C.Current.W.bundle(raw))
    cookie_offset = raw.index(OLD_COOKIE, 16, 1048592)
    assert cookie_offset == COOKIE_OFFSET and raw.count(OLD_COOKIE, 16, 1048592) == 1
    image = bytearray(raw)
    image[META_OFFSET:META_OFFSET + 1024] = p['packet']['metadata']
    image[cookie_offset:cookie_offset + 16] = p['packet']['cookie']
    changed = [i for i, (a, b) in enumerate(zip(raw, image)) if a != b]
    assert all(cookie_offset <= i < cookie_offset + 16 or
               META_OFFSET <= i < META_OFFSET + 1024 for i in changed)
    record = dict(parent_SHA256=sha256(raw).hexdigest(), image_SHA256=sha256(image).hexdigest(),
                  cookie=p['packet']['cookie'].hex(), cookie_offset=cookie_offset,
                  scene_metadata_half_open=p['scene_metadata_half_open'],
                  exact_changed_bytes=len(changed), rows=sorted(Scene.ROWS))
    return bytes(image), p, record


def combined():
    raw, program, p, _ = Public.combined()
    assert sha256(raw).hexdigest() == PIN
    image, p, record = proposal(raw, p)
    return image, program, p, record
