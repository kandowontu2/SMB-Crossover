"""Prepare a natural Green Koopa copy and shell-hit replay on published 29aa."""

import argparse
import json
from pathlib import Path
import re
import sys

import prepare_kirby_first_inhale_1110 as V1
from prepare_kirby_contacts_current_1108_v1 import plain


FIRST = V1.R / 'build/kirby-first-inhale-1110-v2'
FULL = V1.R / 'build/kirby-current-1109/full11'
POLICY = V1.R / 'tools/playthroughs/full_roster_policy_og.lua'
WITNESS = V1.R / 'tools/playthroughs/kirby_green_shell_1110.lua'


def successful_native(root, expected):
    ready = root / 'ready.json'
    binding = root / 'capture/binding.json'
    result = root / 'capture/result.json'
    assert json.loads(binding.read_text()) == dict(ROM_sha256=expected, ready_sha256=V1.sha(ready), exit_code=0)
    report = json.loads(result.read_text())
    assert report['ROM_sha256'] == expected and report['passed'] and report['controller_only']
    return json.loads(ready.read_text()), report, [ready, binding, result]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert V1.sha(V1.ROM) == V1.PIN and V1.sha(V1.AUTHORITY) == V1.AUTHORITY_ROM
    assert V1.sha(V1.AUTHORITY.with_suffix('.dbg')) == V1.AUTHORITY_DBG
    first, inhale, first_refs = successful_native(FIRST, V1.PIN)
    assert inhale['native_first_goomba']['x'] == 352 and inhale['terminal']['hp'] == 6
    full, clear, full_refs = successful_native(FULL, 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2')
    assert clear['full_stage'] and clear['level'] == 1 and clear['final_lives'] == 2
    assert V1.sha(POLICY) == full['bindings'][str(POLICY)]
    frozen = FIRST / 'controller.lua'
    assert V1.sha(frozen) == first['bindings'][str(frozen)]

    sys.path.insert(0, str(V1.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    config, body = frozen.read_text(encoding='utf-8').split('\n', 1)
    c = plain(lua.execute(config + '\nreturn C'))
    assert c['ram'] == first['observer_RAM'] and c['hooks'] == first['hooks'] and c['sha'] == V1.PIN
    source, target = map(V1.scoped_load, (V1.AUTHORITY, V1.ROM))
    raw = target['raw']
    assert raw.count(V1.STREAM) == 1 and raw.find(V1.STREAM) == 19023 and V1.STREAM[17:19] == bytes.fromhex('bb00')

    def hook(name, count):
        at = V1.location(source, name)
        data = raw[at:at + count]
        assert data == source['raw'][at:at + count], name
        return dict(pc=V1.address(source, name), offset=at - 16, bytes=list(data))

    c['hooks'].update(greenInit=hook('InitNormalEnemy', 8), swallow=hook('KbWeapons::Swallow', 8),
                      attack=hook('KbWeapons::CopyAttack', 8), contact=hook('KbWeapons::Defeat', 3),
                      defeat=hook('ShellOrBlockDefeat', 11), consumed=hook('KbWeapons::Consumed', 8))
    defeat = c['hooks']['defeat']['pc']
    assert c['hooks']['contact']['bytes'] == [0x20, defeat & 255, defeat >> 8]
    assert c['hooks']['consumed']['pc'] == c['hooks']['contact']['pc'] + 3
    c['policy'] = POLICY.as_posix()
    helpers = body.split('local function r(', 1)[1].split('local function finish(', 1)[0]
    helpers = 'local function r(' + helpers
    menu = body.split('local function wait(n)', 1)[1].split('emu.addEventCallback', 1)[0]
    menu = 'local function wait(n)' + menu
    test = WITNESS.read_text(encoding='utf-8')
    assert test.count('-- FIRST-INHALE HELPERS') == test.count('-- FIRST-INHALE MENU') == 1
    text = test.replace('-- FIRST-INHALE HELPERS', helpers).replace('-- FIRST-INHALE MENU', menu)
    names = set(re.findall(r"\br\('([\w]+)'", text))
    names.update(n for pair in re.findall(r"\bpos\('([\w]+)','([\w]+)'", text) for n in pair)
    # The policy's only indirect RAM reads on the Kirby path are its common
    # actor/item scans and Kirby's mouth query. Bind all literal policy reads.
    names.update(re.findall(r"\bc\.r\('([\w]+)'", POLICY.read_text()))
    c['ram'] = {name: V1.address(source, name) for name in sorted(names)}
    assert all(V1.address(target, name) == addr for name, addr in c['ram'].items() if name in target['syms'])
    assert c['ram']['SelectedCharacter'] == 0x6002
    text = 'local C=' + V1.lua(c) + '\n' + text
    for banned in ('emu.write', 'emu.setState', 'emu.loadSavestate'):
        assert banned not in text + POLICY.read_text(), banned
    ok, error = lua.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    V1.prepare(args.output, V1.ROM, text, [Path(__file__), WITNESS, POLICY, frozen,
                                           *first_refs, *full_refs, V1.AUTHORITY, V1.AUTHORITY.with_suffix('.dbg')],
               expected=V1.PIN, timeout=220, allow_interactive=True,
               scope='Natural Easy Kirby 1-1 Green Koopa inhale, Down swallow and grounded shell defeat. '
                     'Authentic native constructors and no emulator state writes. Prepared only.')
    ready = args.output / 'ready.json'
    q = json.loads(ready.read_text())
    q.update(observer_RAM=c['ram'], hooks=c['hooks'], natural_green_koopa_x=1712,
             authored_red_koopa=False, prior_inhale_exact_SHA256=inhale['ROM_sha256'],
             existing_full_route_SHA256=clear['ROM_sha256'])
    ready.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
