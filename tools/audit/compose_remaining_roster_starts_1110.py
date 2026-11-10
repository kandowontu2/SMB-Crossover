"""Rebase authentic Prince/DK Jr prototypes onto exact74fde, CPU qualification only.

No cartridge is written.  Original private source receipts fund every byte.
Known full-stage failures remain disclosed; root owns native replay/delivery.
"""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_remaining_roster_starts_1110 as Menu
import check_prince_current_cold_1102_v98 as Cold

R, I, W = Menu.R, Menu.I, Menu.W
PARENT = R / 'build/manual-wide-floor-native-1110/candidate.nes'
PIN = '74fde1dba64b17f7f9028c3da1d5948c041e9af11fb37fca4d241d834724318e'
PRINCE = R / 'build/prince-camera-framing-native-1110/prince-private.nes'
PRINCE_PIN = 'bd9f111d79adb0700b968cd0b10459818ef28669ac21c9ede1aa5ebca6ea79dc'
PRINCE_BASE = R / 'build/mini-contact-platform-combo-native-1110/candidate.nes'
PRINCE_MANIFEST = R / 'build/prince-roof-scroll-native-1110/candidate.json'
PRINCE_QUALIFIED = R / 'build/prince-camera-framing-1110/proof.json'
DK = R / 'build/dkjr-first-pipe-getsu-1110/rebase-proof.json'
DK_ROM = R / 'build/dkjr-getsu-native-1110/candidate.nes'
PRINCE_COOKIE_OLD = 535476
PRINCE_COOKIE_CURRENT = 535469
OUT = R / 'build/remaining-roster-compose-1110'

# The authentic Prince loader costs7.84M CPU cycles, so the older UI-only
# call bound is too small for the first real native GameLoop.  Reuse the same
# instruction executor/BRK/stack assertions with a finite4M-instruction bound.
_invoke_source = inspect.getsource(I.F.invoke)
assert _invoke_source.count('range(500000)') == 1
_invoke_env = dict(vars(I.F))
exec(compile(_invoke_source.replace('range(500000)', 'range(4000000)'),
             str(Path(__file__)), 'exec'), _invoke_env)
invoke_game = _invoke_env['invoke']


def digest(raw):
    return sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def apply(raw, rows):
    image = bytearray(raw)
    occupied = set()
    for row in rows:
        at = row['file_offset']
        old, new = (bytes.fromhex(row[key]) for key in ('old_hex', 'new_hex'))
        assert old and len(old) == len(new) and image[at:at + len(old)] == old, at
        claimed = set(range(at, at + len(old)))
        assert not claimed & occupied, at
        occupied |= claimed
        image[at:at + len(new)] = new
    return bytes(image)


def compose():
    base = PARENT.read_bytes()
    assert digest(base) == PIN
    private, original = PRINCE.read_bytes(), PRINCE_BASE.read_bytes()
    assert digest(private) == PRINCE_PIN
    manifest, qualified = read(PRINCE_MANIFEST), read(PRINCE_QUALIFIED)
    assert manifest['passed'] and qualified['passed']
    assert digest(original) == manifest['parent_SHA256']
    assert qualified['expected_memory_only_SHA256'] == PRINCE_PIN
    domains = set()
    prince = []
    for row in manifest['patches']:
        source_at = row['offset']
        before = bytes.fromhex(row['preimage'])
        assert original[source_at:source_at + len(before)] == before
        domains.update(range(source_at, source_at + len(before)))
        at = PRINCE_COOKIE_CURRENT if source_at == PRINCE_COOKIE_OLD else source_at
        replacement = private[source_at:source_at + len(before)]
        assert base[at:at + len(before)] == before, (source_at, at)
        if before != replacement:
            prince.append(dict(file_offset=at, old_hex=before.hex(), new_hex=replacement.hex(),
                               source_private_offset=source_at,
                               role='Prince typed cookie relocated with current descriptor' if at != source_at
                               else row.get('role', 'Existing shared right-overflow scroll predicate repair')))
    assert all(a == b or at in domains for at, (a, b) in enumerate(zip(original, private, strict=True)))
    cookie = private[PRINCE_COOKIE_OLD:PRINCE_COOKIE_OLD + 16]
    assert cookie.hex() == qualified['Prince_cookie'] and cookie[:3] == bytes((167, 38, 2))
    assert base.count(original[PRINCE_COOKIE_OLD:PRINCE_COOKIE_OLD + 16]) == 1
    assert len(prince) == 25
    dk = read(DK)
    assert dk['passed'] and digest(DK_ROM.read_bytes()) == dk['expected_memory_only_SHA256']
    dkjr = dk['patches']
    assert len(dkjr) == 20
    for row in dkjr:
        at = row['file_offset']
        new = bytes.fromhex(row['new_hex'])
        assert DK_ROM.read_bytes()[at:at + len(new)] == new
    prince_only = apply(base, prince)
    dk_only = apply(base, dkjr)
    combined = apply(base, prince + dkjr)
    assert apply(prince_only, dkjr) == apply(dk_only, prince) == combined
    return base, combined, prince + dkjr, cookie, bytes.fromhex(dk['cookie'])


def state(model):
    get = lambda name: I.N.get(model, name)
    return dict(x=get('Player_X_Position') + 256 * get('Player_PageLoc'),
                y=get('Player_Y_Position'), state=get('Player_State'),
                engine=get('GameEngineSubroutine'), lives=get('NumberofLives'),
                source_owner=model.ram[2][0x1fe1])


def startup(raw, slot, owner, cookie, confirm):
    bundle = W.bundle(raw)
    previous = I.N.Bus
    I.N.Bus = I.C.C.C.C.V.ControllerBus
    try:
        model = I.UI.seed(bundle, slot)
        I.UI.key(model, 32)
        name = Menu.menu_name(model)[0]
        result = I.UI.key(model, confirm)
        assert I.N.get(model, 'SelectedCharacter') == owner
        assert I.N.get(model, 'CrossoverMenuState') == 0
        I.F.invoke(model, 'ChkContinue',
                   a=result['A'], x=result['X'], y=result['Y'], p=result['P'])
        I.N.invoke(model, 'PauseRoutine', a=0)
    finally:
        I.N.Bus = previous

    def frame(keys=0):
        I.N.put(model, SavedJoypadBits=keys, SavedJoypad1Bits=keys, SavedJoypad2Bits=0,
                A_B_Buttons=keys & 192, Left_Right_Buttons=keys & 3,
                Up_Down_Buttons=keys & 12, NmiDisable=255)
        invoke_game(model, 'GameLoop')
        I.N.consume(model)
        Cold.clear(model)

    for entrance in range(600):
        if (I.N.get(model, 'OperMode_Task'), I.N.get(model, 'GameEngineSubroutine')) == (3, 8):
            break
        frame()
    else:
        raise AssertionError(('Real menu/newgame entrance bound', owner))
    assert all(bytes(model.ram[bank][0x1fe0:0x1ff0]) == cookie for bank in (2, 3))
    samples = {}
    ys = []
    for epoch in range(150):
        pad = 0 if epoch < 24 else 1 if epoch < 84 else 129 if epoch < 102 else 1 if epoch < 138 else 0
        frame(pad)
        current = state(model)
        assert current['engine'] == 8 and current['lives'] == 2 and current['source_owner'] == owner, (owner, epoch, current)
        ys.append(current['y'])
        if epoch in (0, 23, 83, 101, 137, 149):
            samples[epoch] = current
    assert samples[137]['x'] >= samples[23]['x'] + 16, (owner, samples)
    assert min(ys[84:]) < samples[23]['y'] - 3, (owner, samples)
    return dict(name=name, owner=owner, confirm=confirm, entrance_updates=entrance,
                gameplay_updates=150, both_complete_headers=True, moved=True, jumped=True,
                minimum_y=min(ys), samples=samples,
                scope='Actual menu confirmation, native newgame/parser/entrance and150ordinary '
                      'idle/right/jump/release GameLoop+NMI calls. CPU/peripheral model only.')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', required=True, type=Path)
    args = cli.parse_args()
    assert args.output.resolve() == OUT.resolve() and not OUT.exists()
    base, raw, patches, prince_cookie, dk_cookie = compose()
    print('Exact memory composition', digest(raw), len(patches), flush=True)
    old_menu, new_menu = Menu.inventory(base), Menu.inventory(raw)
    assert old_menu['distinct_named_entries'] == 96 and old_menu['confirmable_named_entries'] == 95
    assert new_menu['distinct_named_entries'] == new_menu['confirmable_named_entries'] == 97
    assert not new_menu['locked']
    cold = {}
    for owner, cookie in ((38, prince_cookie), (40, dk_cookie)):
        model, result = Cold.cold(W.bundle(raw), owner)
        assert all(bytes(model.ram[bank][0x1fe0:0x1ff0]) == cookie for bank in (2, 3))
        cold[owner] = dict(CPU=result['CPU'], minimum_SP=result['minSP'], cookie=cookie.hex())
    print('Menu and authentic cold passed', cold, flush=True)
    starts = [startup(raw, slot, owner, cookie, confirm)
              for slot, owner, cookie in ((29, 38, prince_cookie), (27, 40, dk_cookie))
              for confirm in (16, 128)]
    print('Four real CPU startup/input paths passed', flush=True)
    refs = (Path(__file__), Path(Menu.__file__), PARENT, PRINCE, PRINCE_BASE, PRINCE_MANIFEST,
            PRINCE_QUALIFIED, DK, DK_ROM)
    result = dict(passed=True, parent_SHA256=PIN, expected_memory_only_SHA256=digest(raw),
                  ROM_written=False, Mesen_run=False, native_pending=True, patches=patches,
                  cold=cold, startup=starts, menu=new_menu,
                  source_domains=dict(Prince_full_manifest_extents=25, DK_source_extents=20,
                                      Prince_cookie_old=PRINCE_COOKIE_OLD,
                                      Prince_cookie_current=PRINCE_COOKIE_CURRENT,
                                      shared_scroll_PRG=1, shared_scroll_CPU_half_open=[0xaa44, 0xaa52],
                                      bank26_untouched=True, compose_order_identical=True),
                  known_limits=dict(Prince='Natural Easy landing contact can still kill at X891; full1-1 incomplete.',
                                    DK_Jr='First pipe jump/detach can still fall fatally; full1-1 incomplete.',
                                    other_missing=['Sonic (Master System reference)', 'Jay McCray', 'Steve Hermann']),
                  scope='Source-funded private opening prototypes only. Root native startup/input, '
                        'shared-scroll regression and Downloads launch required before publication.',
                  bindings={path.relative_to(R).as_posix(): digest(path.read_bytes()) for path in refs})
    OUT.mkdir()
    (OUT / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
