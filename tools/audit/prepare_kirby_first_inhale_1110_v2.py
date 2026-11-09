"""Rebind every observer RAM dependency for the frozen Kirby 29aa replay."""

import argparse
import json
from pathlib import Path
import re
import sys

import prepare_kirby_first_inhale_1110 as V1
from prepare_kirby_contacts_current_1108_v1 import plain


PRIOR = V1.R / 'build/kirby-first-inhale-1110'
PRIOR_READY = '9ca3c7739fea79786df189486491cb635fc101843e875f7209587e8a519d5efe'
CHARACTERS = V1.R / 'src/characters.s'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready = PRIOR / 'ready.json'
    failed = PRIOR / 'capture/binding.json'
    log = PRIOR / 'capture/candidate-controller.log'
    assert V1.sha(ready) == PRIOR_READY
    prior = json.loads(ready.read_text())
    assert prior['ROM_sha256'] == V1.PIN
    assert json.loads(failed.read_text()) == dict(ROM_sha256=V1.PIN,
                                                   ready_sha256=PRIOR_READY, exit_code=1)
    assert 'FAIL SelectedCharacter' in log.read_text()
    for path, digest in prior['bindings'].items():
        assert V1.sha(path) == digest, path

    controller = PRIOR / 'controller.lua'
    config, body = controller.read_text(encoding='utf-8').split('\n', 1)
    assert body == V1.CONTROLLER.read_text(encoding='utf-8')
    sys.path.insert(0, str(V1.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    c = plain(lua.execute(config + '\nreturn C'))
    assert c['sha'] == V1.PIN and c['hooks'] == prior['hooks']

    direct = set(re.findall(r"\br\('([\w]+)'", body))
    pairs = re.findall(r"\bpos\('([\w]+)','([\w]+)'", body)
    needed = direct | {name for pair in pairs for name in pair}
    # Only pos() forwards dynamic names to r(). All actual callers use literals.
    assert re.findall(r"\br\(([^'\n][^)]*)\)", body) == ['name,index', 'lo,index', 'hi,index']
    assert re.findall(r"\bpos\(([^'\n][^)]*)\)", body) == ['lo,hi,index']
    assert needed - c['ram'].keys() == {'SelectedCharacter'}
    assert c['ram'].keys() - needed == {'KbFloat'}
    authority, target = map(V1.scoped_load, (V1.AUTHORITY, V1.ROM))
    ram = {name: V1.address(authority, name) for name in sorted(needed)}
    compact = {name: V1.address(target, name) for name in ram if name in target['syms']}
    assert all(ram[name] == addr for name, addr in compact.items())
    assert all(ram[name] == addr for name, addr in c['ram'].items() if name in needed)
    assert ram['SelectedCharacter'] == compact['SelectedCharacter'] == 0x6002
    assert re.search(r'^al 006002 \.SelectedCharacter$', V1.ROM.with_suffix('.lbl').read_text(), re.M)
    assert re.search(r'^\.segment "SRAM"\s+SelectedCharacter: \.res 1$', CHARACTERS.read_text(), re.M)
    authority['raw'] = target['raw']
    edges, routes = V1.menu_routes(authority, 0)
    assert c['menu'] == [routes[i][0] if routes[i] else '' for i in sorted(edges)]
    c['ram'] = ram

    text = 'local C=' + V1.lua(c) + '\n' + body
    ok, error = lua.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    V1.prepare(args.output, V1.ROM, text, [Path(__file__), ready, failed, log, controller,
                                           V1.CONTROLLER, V1.AUTHORITY, V1.AUTHORITY.with_suffix('.dbg'),
                                           CHARACTERS], expected=V1.PIN, timeout=160,
               allow_interactive=True, scope=prior['scope'])
    output = args.output / 'ready.json'
    q = json.loads(output.read_text())
    for key in ('menu_direction_cases', 'menu_route_from_zero', 'exact_owners', 'hooks',
                'original_enemy_stream_offset', 'original_enemy_stream', 'natural_first_goomba_x',
                'authored_green_koopa_x', 'authored_red_koopa'):
        q[key] = prior[key]
    q.update(observer_RAM=ram, compact_debug_verified_RAM=compact,
             observer_body_unchanged=True, supersedes_binding_failure=V1.sha(failed))
    output.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
