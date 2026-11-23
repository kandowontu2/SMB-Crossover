"""Call Karnov's authenticated side service from the shared side gate."""

import compose_arthur_side_shortcut_1123 as Side
import compose_karnov_foreground_cookie_1123 as Cookie


CANDIDATE = 'cb6fcb50dc9db8dda53eb542078c92226d8fd2942a275bf02497e4efd1e41de7'


def side_edits():
    # This is the same branch envelope used to trial Arthur's side route.
    # Karnov's target is his regular public service, including admission.
    edits = (('cmp #32', 'cmp #34'), ('beq Arthur', 'beq Karnov'),
             ('Arthur:', 'Karnov:'), ('lda #$e0', 'lda #$2a'),
             ('lda #$b6', 'lda #$b4'), ('lda #$cf', 'lda #$9d'))
    source = Side.SOURCE
    for before, after in edits:
        assert source.count(before) == 1, before
        source = source.replace(before, after, 1)
    link = Side.Prior.Layout.M.assemble(source, Side.LAYOUT)
    assert link['used'] == {role: size for role, (pc, size) in Side.LAYOUT.items()}
    assert link['symbols']['MacUnwind'] == 0xBCAD
    for role, (pc, _) in Side.LAYOUT.items():
        yield Side.BANK, pc, bytes.fromhex(Side.PREIMAGE[role]), link['images'][role]


def compose(raw):
    image = Cookie.compose(raw)
    stock_route = bytes.fromhex('8d6a01089848a00e4c40b8')
    at = Side.at(79, 0xB6E0)
    assert image[at:at + len(stock_route)] == stock_route
    at = Side.at(29, 0xB42A)
    assert image[at:at + 3] == b'\x4c\x6e\xb8'
    candidate = Side.Prior.Epoch.apply(image, side_edits())
    assert Cookie.sha256(candidate).hexdigest() == CANDIDATE
    return candidate


def inverse(raw):
    assert Cookie.sha256(raw).hexdigest() == CANDIDATE
    edits = (*Cookie.edits(), *side_edits())
    parent = Side.Prior.Epoch.apply(raw, (
        (bank, pc, new, old) for bank, pc, old, new in reversed(edits)
    ))
    assert Cookie.sha256(parent).hexdigest() == Cookie.PIN
    return parent
