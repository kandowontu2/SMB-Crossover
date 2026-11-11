"""Repack Prince's single signed world-row branch in the exact Jay nightly."""

from hashlib import sha256

import compose_prince_question_ledge_1111 as Question
from check_prince_wall_sweep_1110_v6 import assemble


PARENT = 'c8d328a27efbc900216985aeb86600a1f626f8cc76e93a91bb30b2c1f8c2e727'
CANDIDATE = '41bd1143994bfa1543da0b4b1032778be613a36a006f948762ca1dcfa57cc28c'
COOKIE = 'a72602c577b66c1ecc0545cfa4f7ffb1'
SUPPORT_PUBLICATION = 0xd74b
BRANCH = 0xbe06
ABOVE_ROW = 0xbe68
SOURCE = Question.Packet.R / 'tools/reference/prince_signed_world_row_1111.s'


def patch():
    branch, _ = assemble(SOURCE.read_text(encoding='utf-8'), BRANCH, {'AboveRow': ABOVE_ROW})
    assert branch == bytes.fromhex('3060')
    return (0, BRANCH, bytes.fromhex('9060'), branch),


def proposal(image):
    assert sha256(image).hexdigest() == PARENT
    candidate, layout = Question.replace(image, patch())
    assert sha256(candidate).hexdigest() == CANDIDATE
    assert layout['cookie'] == COOKIE
    assert layout['packed_bytes'] == layout['old_packed_bytes'] == (6400, 5939, 1233)
    assert layout['packed_bytes'][0] <= 0xdc00 - 0xc300
    return candidate, dict(layout, support_publication=SUPPORT_PUBLICATION)


def recover_parent(image):
    assert sha256(image).hexdigest() == CANDIDATE
    parent, _ = Question.replace(image, patch(), inverse=True)
    assert sha256(parent).hexdigest() == PARENT
    return parent
