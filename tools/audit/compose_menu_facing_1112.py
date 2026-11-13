"""Composable menu-only direction edits and actual all-Select pixel checks."""

import argparse
from hashlib import sha256
import json

from PIL import Image

import check_menu_facing_1112 as Audit
from check_steve_shatterhand_upgrade_transport_1111 import H


SOURCE = Audit.R/'tools/reference/menu_facing_1112.s'
PREFIX = bytes.fromhex(
    'a91dae0260f002a9918de106a912ae0260f002a9388d4701ee4601'
    'adecb385bdadedb38d3e05adeeb38d8705adefb38575ad1d07855ca90185a4')
SLOTS = (14, 16, 24, 26)


def prg(bank, pc):
    return 16+bank*8192+(pc & 8191)


def proposal(raw):
    """Return an in-memory image and authenticated edits; write no ROM or patch."""
    bundle = Audit.Host.C.Start.W.bundle(raw)
    fields = {name: Audit.address(bundle, name) for name in
              ('SelectedCharacter', 'ObjectMetasprite', 'PlayerChrBank', 'ReloadCHRBank',
               'Player_Y_Position', 'ScreenLeft_PageLoc', 'Player_PageLoc',
               'Player_Y_HighPos', 'Player_SprAttrib', 'Player_X_Position',
               'PlayerFacingDir', 'Z2Variant')}
    assert fields['PlayerFacingDir'] == 0x053e and fields['Z2Variant'] == 0x73f8
    definitions = ''.join(f'{name}=${value:04x}\n' for name, value in fields.items())
    linked = H.assemble(definitions+SOURCE.read_text(encoding='ascii'),
                        {'LINK_PORTRAIT_PREFIX': (0xb345, 58),
                         'SONIC_PORTRAIT_FACING': (0xbc94, 3)})
    assert len(PREFIX) == len(linked['images']['LINK_PORTRAIT_PREFIX']) == 58
    assert Audit.location(bundle, 'DrawPlayer_Intermediate') == prg(3, 0xb345)
    assert raw[prg(3, 0xb345):prg(3, 0xb37f)] == PREFIX
    # Keep the original selector/farcall tail and the independent Getsu status
    # packet at B3DD intact. The old four-byte constant table is retained too.
    assert raw[prg(3, 0xb37f):prg(3, 0xb386)] == bytes.fromhex('ad0260c9069013')
    assert raw[prg(3, 0xb3ec):prg(3, 0xb3f0)] == bytes.fromhex('58010060')
    old_source = (Audit.R/'tools/reference/super_sonic_roster_1111.s').read_text(encoding='ascii')
    portrait = '.segment "PORTRAIT"'+old_source.split('.segment "PORTRAIT"', 1)[1].split('.segment "PALETTE"', 1)[0]
    old_sonic = H.assemble(portrait, {'PORTRAIT': (0xbc77, 51)})['images']['PORTRAIT']
    assert len(old_sonic) == 51
    assert raw[prg(9, 0xbc77):prg(9, 0xbcaa)] == old_sonic
    needle = bytes.fromhex('8d4601')
    assert old_sonic.count(needle) == 1
    sonic_at = prg(9, 0xbc77)+old_sonic.index(needle)
    assert sonic_at == prg(9, 0xbc94)
    assert raw[prg(3, 0xb35d):prg(3, 0xb360)] == bytes.fromhex('ee4601')
    edits = [(prg(3, 0xb345), PREFIX, linked['images']['LINK_PORTRAIT_PREFIX']),
             (sonic_at, needle, linked['images']['SONIC_PORTRAIT_FACING'])]
    # The screen's real BuildScreen and NMI publish physical4..7. Each of
    # these24 icon tiles has one menu-cell owner and no alias outside the
    # selected four icons. Keep every tile ID, nametable byte and font cell.
    model = Audit.seed(bundle)
    assert model.chr_latches[8:] == [4, 5, 6, 7]
    nt = bytes(model.vram[0x2000:0x23c0])
    reverse = bytes(int(f'{value:08b}'[::-1], 2) for value in range(256))
    desired, positions = {}, set()

    def tile_bytes(tile):
        page = model.chr_latches[8+tile//64]
        offset = Audit.CHR+page*1024+(tile % 64)*16
        return raw[offset:offset+16], offset

    for slot in SLOTS:
        top, left = 4+(slot//8)*4, 4+(slot % 8)*3
        for row in range(3):
            pair = [(top+row)*32+left+x for x in (0, 1)]
            positions.update(pair)
            for x, position in enumerate(pair):
                tile = nt[position]
                assert 64 <= tile < 252
                wanted = tile_bytes(nt[pair[1-x]])[0].translate(reverse)
                assert tile not in desired or desired[tile] == wanted
                desired[tile] = wanted
    assert len(desired) == len(positions) == 24
    assert all(index in positions for index, tile in enumerate(nt) if tile in desired)
    for tile, replacement in sorted(desired.items()):
        old, offset = tile_bytes(tile)
        edits.append((offset, old, replacement))
    output = bytearray(raw)
    last = 16
    for offset, old, new in sorted(edits):
        assert len(old) == len(new) and offset >= last
        assert raw[offset:offset+len(old)] == old
        output[offset:offset+len(new)] = new
        last = offset+len(old)
    return bytes(output), dict(source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
                               edits=edits, shared_silhouette_slots=list(SLOTS),
                               silhouette_tiles=sorted(desired),
                               prefix_bytes=58, sonic_bytes=3, silhouette_bytes=384)


def interrupts(candidate):
    """Check real menu/lives prefix registers and live fields at every cut."""
    import check_steve_throw_controls_live_1111 as Controls
    from audit_bub_menu_frontend_1102_v1 import invoke

    vector = Controls.C.Vector
    bundle = Audit.Host.C.Start.W.bundle(candidate)
    checked, cuts = set(), dict(NMI=0, IRQ=0)
    live = ('SelectedCharacter', 'PlayerFacingDir', 'Player_X_Position',
            'Player_Y_Position', 'Player_PageLoc', 'Player_Y_HighPos',
            'Player_SprAttrib', 'Z2Variant')
    for mode in (0, 1):
        for slot, cycle in ((0, 0), (1, 0), (2, 0), (4, 0), (4, 1), (25, 3), (25, 4)):
            model = Audit.UI.seed(bundle, slot)
            for _ in range(cycle):
                Audit.UI.key(model, 32)
            Audit.M.put(model, OperMode=mode, NmiDisable=255, FamilyMainCommit=1)

            def observe(cpu):
                bank = model.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc >= 0x8000 else -1
                if not ((bank == 0x83 and 0xb345 <= cpu.pc < 0xb37f) or
                        (bank == 0x89 and cpu.pc == 0xbc94)):
                    return
                key = mode, slot, cycle, cpu.pc
                if key in checked:
                    return
                checked.add(key)
                for kind in ('NMI', 'IRQ'):
                    copy, pending = vector.clone(model, cpu)
                    expected = tuple(Audit.M.get(copy, name) for name in live)
                    mapping = tuple(copy.rawtags)
                    assert vector.isr(copy, pending, kind) == 'returned', (key, kind)
                    assert expected == tuple(Audit.M.get(copy, name) for name in live), (key, kind)
                    assert mapping == tuple(copy.rawtags), (key, kind)
                    cuts[kind] += 1

            invoke(model, 'DrawPlayer_Intermediate', watch=observe)
    assert cuts['NMI'] == cuts['IRQ'] and cuts['NMI'] > 300, cuts
    return cuts


def registers(raw, candidate):
    """Check the public preview call's registers for four incoming flag sets."""
    from audit_bub_menu_frontend_1102_v1 import invoke

    bundles = [Audit.Host.C.Start.W.bundle(image) for image in (raw, candidate)]
    cases = 0
    for slot in range(32):
        models = [Audit.UI.seed(bundle, slot) for bundle in bundles]
        seen = set()
        for cycle in range(32):
            names = [Audit.menu_name(model)[0] for model in models]
            assert names[0] == names[1]
            if names[0] in seen:
                break
            assert names[0]
            seen.add(names[0])
            for flags in (0x30, 0x31, 0x71, 0xf1):
                results = [invoke(Audit.M.fork(model), 'DrawSelectionPreview', p=flags)
                           for model in models]
                assert {name: results[0][name] for name in ('A', 'X', 'Y', 'P')} == {
                    name: results[1][name] for name in ('A', 'X', 'Y', 'P')}, (slot, cycle, flags, results)
                assert results[0]['minimum_SP'] == results[1]['minimum_SP'], (slot, cycle, flags)
                cases += 1
            for model in models:
                Audit.UI.key(model, 32)
        else:
            raise AssertionError(('register Select cycle bound', slot))
    assert cases == 404, cases
    return cases


def gameplay_parity(raw, candidate):
    """Check that changed menu facing cannot leak into three native1-1 starts."""
    from unittest.mock import patch
    import check_current_roster_stage_ingress_1110 as Stage
    import prepare_kirby_contacts_current_1108_v1 as Authority

    # The ordinary compact bundle omits scoped local names. Read the exact
    # retained native authority once; add only the required scoped Continue
    # entry, with its current instruction preimage authenticated.
    assert Authority.sha(Authority.AUTHORITY) == Authority.AUTHORITY_ROM
    assert Authority.sha(Authority.AUTHORITY.with_suffix('.dbg')) == Authority.AUTHORITY_DBG
    native = Authority.scoped_load(Authority.AUTHORITY)

    def full_bundle(image):
        result = Audit.Host.C.Start.W.bundle(image)
        name = 'NativeRareGameMenuRoutineCore::ChkContinue'
        symbol = dict(native['syms'][name])
        segment = 'menu_facing_native_continue'
        result['segs'][segment] = native['segs'][symbol['seg']]
        symbol['seg'] = segment
        result['syms'][name] = symbol
        offset = Audit.location(result, name)
        assert image[offset:offset+8] == native['raw'][offset:offset+8]
        return result

    results = []
    for slot, cycle, name, owner in ((4, 0, 'LINK', 4), (25, 3, 'SONIC', 43),
                                     (25, 4, 'SUPER SONIC', 43)):
        pair = []
        for image in (raw, candidate):
            frames = []
            consume = Stage.N.consume

            def capture(model):
                consume(model)
                if tuple(Audit.M.get(model, field) for field in
                         ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8):
                    frames.append((Audit.M.get(model, 'PlayerFacingDir'),
                                   bytes(model[0x200:0x300]), tuple(model.chr_latches)))

            with patch.object(Stage.N, 'consume', capture):
                proof = Stage.stage(full_bundle(image),
                                    dict(slot=slot, cycle=cycle, name=name, raw=owner))
            assert frames and frames[0][0] == 1, (name, 'initial gameplay facing', frames[:1])
            pair.append((proof, frames))
        assert pair[0] == pair[1], name
        results.append(dict(name=name, initial_facing=1,
                            opening_updates=pair[0][0]['opening_updates'],
                            equal_gameplay_DMA_inputs=len(pair[0][1])))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gameplay', action='store_true')
    args = parser.parse_args()
    raw = Audit.NIGHTLY.read_bytes()
    candidate, info = proposal(raw)
    before, before_images = Audit.audit(raw, include_images=True)
    after, after_images = Audit.audit(candidate, include_images=True)
    changed_portraits, changed_icons = [], []
    for old, new, (old_thumb, old_pic), (new_thumb, new_pic) in zip(
            before, after, before_images, after_images, strict=True):
        identity = old['slot'], old['cycle'], old['name'], old['owner']
        assert identity == (new['slot'], new['cycle'], new['name'], new['owner'])
        if old['name'] in ('LINK', 'SONIC', 'SUPER SONIC'):
            assert old_pic.size == new_pic.size
            assert new_pic.tobytes() == old_pic.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(), identity
            changed_portraits.append(old['name'])
        else:
            assert old_pic.size == new_pic.size and old_pic.tobytes() == new_pic.tobytes(), identity
        if old['slot'] in SLOTS:
            assert new_thumb.tobytes() == old_thumb.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(), identity
            changed_icons.append(old['name'])
        else:
            assert new_thumb.tobytes() == old_thumb.tobytes(), identity
    assert len(changed_portraits) == 3 and len(changed_icons) == 17
    interrupt_cuts = interrupts(candidate)
    register_cases = registers(raw, candidate)
    gameplay = gameplay_parity(raw, candidate) if args.gameplay else None
    print(json.dumps(dict(passed=True, parent_SHA256=sha256(raw).hexdigest(),
                          candidate_SHA256=sha256(candidate).hexdigest(),
                          named_Select_identities=len(after), changed_colored_previews=changed_portraits,
                          changed_shared_silhouette_identities=changed_icons,
                          edit_bytes=sum(len(old) for _, old, _ in info['edits']),
                          prefix_and_static_portrait_interrupt_cuts=interrupt_cuts,
                          exact_public_preview_register_cases=register_cases,
                          gameplay_start_parity=gameplay,
                          source_SHA256=info['source_SHA256'], output_files=0,
                          scope='Actual native menu, Select, portrait, NMI and IRQ CPU checks; '
                                'optional native1-1 startup/60-update parity. No Mesen or full-stage route.')),
          flush=True)


if __name__ == '__main__':
    main()
