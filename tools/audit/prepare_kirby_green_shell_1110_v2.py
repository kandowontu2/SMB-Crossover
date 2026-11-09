"""Keep the natural green-shell controls and trace the exact contact predicates."""

import argparse
import json
from pathlib import Path
import re
import sys

import prepare_kirby_first_inhale_1110 as V1
from prepare_kirby_contacts_current_1108_v1 import plain


PRIOR = V1.R / 'build/kirby-green-shell-1110'
READY = '7783db01a1e1732f0bd6aefbbacee3a32c8deb24a8e93bc991ec22accba8f8da'
OBSERVER = V1.R / 'tools/playthroughs/kirby_green_shell_contact_1110_v2.lua'
COLLISION = V1.R / 'src/collision.s'


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready, controller = (PRIOR / n for n in ('ready.json', 'controller.lua'))
    binding, result = (PRIOR / 'capture' / n for n in ('binding.json', 'result.json'))
    assert V1.sha(ready) == READY
    prior = json.loads(ready.read_text())
    assert prior['ROM_sha256'] == V1.PIN
    for path, digest in prior['bindings'].items():
        assert V1.sha(path) == digest, path
    assert json.loads(binding.read_text()) == dict(ROM_sha256=V1.PIN, ready_sha256=READY, exit_code=1)
    negative = json.loads(result.read_text())
    assert not negative['passed'] and negative['reason'] == 'unexpected-green-shell-contact'
    assert negative['terminal']['x'] == 1764 and negative['terminal']['copy'] == 2
    assert negative['terminal']['hp'] == 6 and negative['terminal']['lives'] == 2

    sys.path.insert(0, str(V1.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    config, body = controller.read_text(encoding='utf-8').split('\n', 1)
    c = plain(lua.execute(config + '\nreturn C'))
    assert c['ram'] == prior['observer_RAM'] and c['hooks'] == prior['hooks'] and c['sha'] == V1.PIN
    authority, target = map(V1.scoped_load, (V1.AUTHORITY, V1.ROM))
    for label, value in (('BlockBuffer_X_Adder', 8), ('BlockBuffer_Y_Adder', 24)):
        at = V1.location(authority, label) + 0x15
        assert target['raw'][at] == authority['raw'][at] == value, label
    symbol = 'KbWeapons::EnemyContacts'
    at = V1.location(authority, symbol)
    data = target['raw'][at:at + 8]
    assert data == authority['raw'][at:at + 8]
    c['hooks']['probe'] = dict(pc=V1.address(authority, symbol), offset=at - 16, bytes=list(data))
    for name in ('Enemy_Y_Speed', 'Enemy_Y_MoveForce'):
        c['ram'][name] = V1.address(authority, name)
        if name in target['syms']:
            assert c['ram'][name] == V1.address(target, name), name

    # Keep the original controller through input polling byte-for-byte.
    start = body.index("hook('contact',function(s)")
    end = body.index("hook('injury',function()", start)
    observer = OBSERVER.read_text(encoding='utf-8')
    declarations, hooks = observer.split('local function supportAt(', 1)
    body = body[:start] + 'local function supportAt(' + hooks + body[end:]
    body = once(body, 'local function finish(reason)', declarations + '\nlocal function finish(reason)')
    body = once(body, '  injury_at_encounter=combatInjury,terminal=last',
                '  injury_at_encounter=combatInjury,contact_preconditions=contactAttempts,projectile_probes=probes,terminal=last')
    body = once(body, "  if hit and r('KbShotType',hit.shell.slot)==0 then finish('natural-green-shell-hit');return end",
                "  if hit and r('KbShotType',hit.shell.slot)==0 then\n"
                "   local outcome=hit.genuine_natural_goomba and 'natural-green-shell-hit'\n"
                "      or (hit.target_class=='wrong-target' and 'green-shell-hit-wrong-target' or 'unqualified-green-shell-hit')\n"
                "   finish(outcome);return\n  end")
    assert body.split('local function naturalControls()', 1)[1].split('emu.eventType.inputPolled)', 1)[0] == (
        controller.read_text(encoding='utf-8').split('local function naturalControls()', 1)[1].split('emu.eventType.inputPolled)', 1)[0])
    names = set(re.findall(r"\br\('([\w]+)'", body))
    names.update(n for pair in re.findall(r"\bpos\('([\w]+)','([\w]+)'", body) for n in pair)
    assert names <= c['ram'].keys()
    assert not any(banned in body for banned in ('emu.write', 'emu.setState', 'emu.loadSavestate'))
    text = 'local C=' + V1.lua(c) + '\n' + body
    ok, error = lua.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    V1.prepare(args.output, V1.ROM, text, [Path(__file__), ready, controller, binding, result, OBSERVER,
                                           COLLISION, V1.AUTHORITY, V1.AUTHORITY.with_suffix('.dbg'),
                                           Path(c['policy'])], expected=V1.PIN, timeout=220,
               allow_interactive=True, scope=prior['scope'])
    output = args.output / 'ready.json'
    q = json.loads(output.read_text())
    q.update(observer_RAM=c['ram'], hooks=c['hooks'], original_controls_unchanged=True,
             previous_negative_SHA256=V1.sha(result), max_raw_contact_rows=16, max_projectile_probe_rows=16)
    output.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
