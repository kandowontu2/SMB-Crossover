"""Check the earlier palette work optimization on the repaired dispatcher."""

import argparse
from functools import cache
import json

import check_contra_force_fast_ingress_1122 as Fast
import check_contra_force_fast_route_1122 as Route
import compose_contra_force_p1_work_marker_1116 as Palette


Layout, Current = Fast.Layout, Fast.Layout.Current
PAYLOAD_START = Current.P.CHR + 935 * 1024
RAM3_START = PAYLOAD_START + 16384
HEADER = slice(Fast.COOKIE, Fast.COOKIE + 16)
WORK_BYTE = 0x2DF
BASE_SHA = '79fd089f80b06038e68b968d2ff80d09caba72a133735b3fef6bb86ffa3ed2df'
COMBINED_SHA = 'a6d91e368657a0ee1458391542e98adafcec45991ebecbe4521a648513cfa4df'
# Exact code preimages allow the model to reconstruct its comparison baseline
# from the repaired nightly after delivery, without keeping a second ROM file.
BASE_PREIMAGES = (
    # main
    (1032937, bytes.fromhex(
        'a9ff8d39012056838d6a01a9978d6c01a9a28d6d01a9d6205a01ada007290285034da1072902c9016ea007'
        'a201a0067ea007e888d0f9ea8d6a01a93f8d6c01a9b88d6d01a983205a01ad77074ab028ad4a07f005ce4a'
        '07d019a212ce7c071007a9148d7c07a222bd7d07f003de7d07ca10f5e60e209887a9004c5683608d6a01a9'
        '008d6c01a9b48d6d01a9bf4c5a01eaa9348d6c01a9bf8d6d01a9ca205a0160eaea'
    )),
    # graphics operand
    (32785, bytes.fromhex(
        '69'
    )),
    # guard
    (573271, bytes.fromhex(
        '0848ad0260c91ff01468288d6a01a9c08d6c01a9ad8d6d01a9dd4c5a018a48ada17d48a9028da17d8d1651'
        'a20fe002f008bde0dfddadbfd018ca10f1ade85f4a4a4a2903cde2dfd008babd04010901d006babd040129'
        'fe9d0401688da17d8d165168aa682860a71f00053a7d2d9a77d5accd30e797660848ada17d48a9028da17d'
        '8d1651ade1dfc91fd005a9008de0df688da17d8d16516828600848ad0260c91ff00568284cbdbf682860ff'
        'ffffffffffffffffffffffffff'
    )),
    # public router
    (716848, bytes.fromhex(
        '4c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c'
        '8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8e'
        'b04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb04c8eb0186008488a489848ad026038e91bc907b0454ab042'
        'a8ad6c0138e920aa8a8d6a01c003d0128a29b3c913f02be033f032e04ef032a2ad38a9998d6c01a9b78d6d'
        '01a9e0205a01900f8d620168a868aa688d6a01284c5d0168a868aa688d6a01281860a911d002a9918d6c01'
        'a9b08d6d01a9c8d0d4'
    )),
    # carrier router
    (2022062, bytes.fromhex(
        'd05cca10f1ade85f4a4a4a2903cde2bfd04ca9028da17d8d1651ad6c01a200c9039005e903e8d0f7e024b0'
        '32bd49bf8deca2bd6dbf8deda2a9038deea2babd0301a8bd04019d0301bd05019d0401989d050168a868aa'
        '6828200bca4c18bfbabd0301a8bd04019d0301bd05019d0401989d050168a868aa68281808488a489848ba'
        'bd05018da17d8d1651bd04019d0501bd03019d0401bd02019d0301bd01019d0201e89a68a868aa6828601b'
        '617161947153fefe4cd67f8b8fe308927f0173fefefefe225686febf8e54fef3fe94fea9b3b3b3b6abbeb8'
        'b8b3aaaaaaaaaaa8aab3bda8b8b8b8b8b8abbcb8aabcbdb8bcb8b6b8ffffffffffffffffffffffffffffff'
        'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
        'ffffffffffffffffffffffffffffffffffffffffff'
    )),
)


def comparison_base(raw):
    pin = Fast.Hud.H(raw)
    if pin == BASE_SHA:
        return raw
    assert pin == COMBINED_SHA, 'Require the paired baseline or verified combined image'
    parent = bytearray(raw)
    for at, old in BASE_PREIMAGES + Palette.preimages():
        parent[at:at + len(old)] = old
    parent = bytes(parent)
    assert Fast.Hud.H(parent) == BASE_SHA
    assert compose(parent, repair_pickup=True)[1] == raw
    return parent


@cache
def compose(parent, *, repair_pickup=False):
    repaired, _, old_cookie = Fast.candidate_image(parent, repair_death=True, repair_pickup=repair_pickup)
    cb95 = Fast.Hud.inverse(parent)
    a2 = Current.reference(cb95)
    bc5, _ = Current.Previous.reference(a2)
    assert Fast.Hud.H(bc5) == Palette.Plan.C.CANDIDATE
    palette_parent, _ = Palette.Plan.Audit.Current.proposal(bc5)
    historical, _ = Palette.proposal(palette_parent)
    assert Fast.Hud.H(historical) == Palette.CANDIDATE
    combined = bytearray(repaired)
    spans = []
    for at, size in Palette.CODE_SPANS:
        assert RAM3_START <= at < at + size <= RAM3_START + 8192
        assert combined[at:at + size] == palette_parent[at:at + size]
        combined[at:at + size] = historical[at:at + size]
        spans.append(slice(at - RAM3_START, at - RAM3_START + size))
    digest = Fast.Hud.H(combined[PAYLOAD_START:PAYLOAD_START + 24576])
    cookie = old_cookie[:4] + bytes.fromhex(digest)[:12]
    for at in Palette.COOKIE_SITES:
        assert combined[at:at + 16] == old_cookie
        combined[at:at + 16] = cookie
    return repaired, bytes(combined), tuple(spans), (old_cookie, cookie)


def compare(original, candidate, spans, label):
    comparable = Layout.N.fork(candidate)
    for span in spans:
        comparable.ram[3][span] = original.ram[3][span]
    comparable.ram[2][HEADER] = original.ram[2][HEADER]
    old, new = (model.ram[2][WORK_BYTE] for model in (original, candidate))
    assert (old ^ new) in (0, 0x40), (label, 'Palette phase changed', old, new)
    comparable.ram[2][WORK_BYTE] = old
    Route.compare(original, comparable, label, repair_death=True)


def verify(parent, identities, *, repair_pickup=False):
    original, combined, spans, cookies = compose(parent, repair_pickup=repair_pickup)
    bundle = Current.bindings(Fast.Hud.inverse(parent))['bundle']
    syms = dict(bundle['syms'])
    pause = syms['PauseRoutine']
    assert int(pause['val'], 0) == Layout.PAUSE
    syms['PauseRoutine'] = dict(pause, val=hex(Layout.NEW_PAUSE))
    print('COMBINED ' + json.dumps(dict(repaired=Fast.Hud.H(original), combined=Fast.Hud.H(combined),
                                      changes=sum(a != b for a, b in zip(original, combined, strict=True)),
                                      cookie=cookies[1].hex())), flush=True)
    for identity in identities:
        name, variant = Route.Frozen.IDENTITIES[identity]
        models = tuple(Fast.cold_menu(dict(bundle, raw=raw, syms=syms), name, 30,
                                     [4] * 3 + [1] * 6, variant) for raw in (original, combined))
        for epoch in range(700):
            stage = Fast.position(models[0])
            assert Fast.position(models[1]) == stage, ('Cold state', identity, epoch)
            if stage[:3] == (1, 3, 8):
                break
            for m in models:
                m.controller_pad = 0
                Layout.Frames.frame(m, cold=True)
        else:
            raise AssertionError(('Cold stage entry bound', identity))
        for m, cookie in zip(models, cookies, strict=True):
            assert bytes(m.ram[2][HEADER]) == cookie[:2] + bytes((variant,)) + cookie[3:]
            carrier = m.bundle['raw'][RAM3_START:RAM3_START + 8192]
            assert all(m.ram[3][span] == carrier[span] for span in spans)
        compare(*models, spans, ('Stage entry', identity))
        for phase, masks in (('idle', [0] * 8), ('walk', [1] * 8),
                             ('crouch fire', [4] * 6 + [68, 68] + [4] * 18)):
            totals = [0, 0]
            projectile_updates = 0
            for frame, pad in enumerate(masks):
                for i, m in enumerate(models):
                    m.controller_pad = pad
                    totals[i] += Layout.Frames.frame(m, whole_pass=True)
                compare(*models, spans, ('Play', identity, phase, frame))
                projectile_updates += any(models[1].ram[2][0x382 + i] for i in range(10, 22))
            print('PHASE ' + json.dumps(dict(identity=identity, phase=phase, updates=len(masks),
                                             repaired_cycles=totals[0], combined_cycles=totals[1],
                                             projectile_updates=projectile_updates)), flush=True)
            if phase in ('idle', 'walk'):
                assert totals[1] < totals[0]
            else:
                assert projectile_updates > 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--identity', nargs='+', default=['burns'], choices=Route.Frozen.IDENTITIES)
    parser.add_argument('--repair-pickup', action='store_true')
    args = parser.parse_args()
    parent = comparison_base(Fast.Hud.ROM.read_bytes())
    verify(parent, args.identity, repair_pickup=args.repair_pickup)
