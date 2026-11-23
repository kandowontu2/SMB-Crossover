"""Reuse a successful Arthur cache check during the same Main update."""

from pathlib import Path

import compose_arthur_side_shortcut_1123 as Side


BANK, ADDRESS, SIZE = 70, 0xDF10, 105
HEADER = bytes.fromhex('a7200001cf57fa39c8a769b1c239f669')
SOURCE = Path(__file__).resolve().parents[1] / 'reference/arthur_foreground_epoch_1123.s'
PREIMAGE = '544d2833ab0c69bc9da3773f388d94f5eb0af7c7fed8e365630b4062d91a8087'


def compose(parent):
    base = Side.compose(parent)
    at = Side.at(BANK, ADDRESS)
    assert Side.sha256(base[at:at + SIZE]).hexdigest() == PREIMAGE
    header = Side.at(BANK, 0xDC6E)
    assert base[header:header + len(HEADER)] == HEADER
    jump = Side.at(BANK, 0xC7D3)
    assert base[jump:jump + 4] == bytes.fromhex('4c10df18')

    link = Side.Prior.Layout.M.assemble(SOURCE.read_text(), {'AUTH': (ADDRESS, SIZE)})
    code = link['images']['AUTH'].ljust(SIZE, b'\xea')
    return base[:at] + code + base[at + SIZE:]
