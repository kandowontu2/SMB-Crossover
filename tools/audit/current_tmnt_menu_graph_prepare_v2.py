"""Repair only the frozen turtle fixture's menu navigation; never launch Mesen."""
from pathlib import Path
import argparse
import hashlib
import json

import current_roster_compact_11_v1 as route

ROOT = Path(__file__).resolve().parents[2]
SHA = '9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
OLD = ROOT/'tests/current-tmnt-powerups.lua'
NEW = ROOT/'tests/current-tmnt-powerups-menu-v2.lua'
ANCHOR = " local i=r('CrossoverMenuIndex');if i~=18 then return{down=true}end"
REPLACEMENT = " local i=r('CrossoverMenuIndex');if i~=18 then local key=assert(C.navigation[i+1]);assert(key~='','Nonterminal menu direction');return{[key]=true}end"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity', choices=['leonardo', 'raphael', 'michelangelo', 'donatello'], required=True)
    a = ap.parse_args()
    parent = ROOT/'build'/f'current-9ea-{a.identity}-hard-items-v1'
    out = ROOT/'build'/f'current-9ea-{a.identity}-hard-items-v2'
    assert not out.exists(), 'Fresh one-shot output only'
    old_ready = json.loads((parent/'prepared-not-run.json').read_text())
    assert old_ready['ROM_sha256'] == SHA
    for f in old_ready['bindings']:
        assert sha(f['path']) == f['sha256'], f['path']
    raw = OLD.read_bytes()
    source = raw.decode('utf-8')
    assert source.count(ANCHOR) == 1
    revised = source.replace(ANCHOR, REPLACEMENT, 1)
    assert revised.replace(REPLACEMENT, ANCHOR, 1) == source
    if NEW.exists():
        assert NEW.read_bytes() == revised.encode('utf-8')
    else:
        NEW.write_bytes(revised.encode('utf-8'))
    rom = ROOT/'build/bill_early_cache.nes'
    assert sha(rom) == SHA
    binary, _, _, location, _ = route.linked(rom)
    nav = route.navigation(binary, location, 18)
    tables = {key:list(binary[location('X5Menu'+key.title()):location('X5Menu'+key.title())+19])
              for key in ('left', 'right', 'up', 'down')}
    controls = []
    for start in range(19):
        node, path = start, []
        for _ in range(19):
            if node == 18:
                break
            key = nav[node]
            assert key in tables
            node = tables[key][node]
            path.append(dict(key=key, arrived=node))
        assert node == 18
        controls.append(dict(start=start, path=path))
    assert binary[location('X5MenuCharacters')+18] == 19
    config = json.loads((parent/'config.json').read_text())
    config['navigation'] = nav
    out.mkdir()
    put(out/'config.json', config)
    (out/'run.lua').write_text('CURRENT_TMNT_POWERUPS='+route.lua(config)+'\n'+
        'dofile('+route.lua(NEW.as_posix())+')\n', encoding='utf-8')
    command = json.loads((parent/'command.json').read_text())
    command['argv'] = [x.replace(str(parent), str(out)) for x in command['argv']]
    put(out/'command.json', command)
    proof = dict(passed=True, native_run=False, ROM_sha256=SHA,
        one_menu_line_replaced=True, reverse_replacement_exact=True,
        original_fixture_sha256=sha(OLD), successor_fixture_sha256=sha(NEW),
        menu_target=18, compiled_character=19, all19_menu_graph_controls=controls,
        original_source_controls_sha256=sha(parent/'source-controls.json'),
        source_campaign_reuse='Same ROM and byte-identical mechanics, input phases, setup and complete hardware guards. Original compiled 15-component source campaign reused; only cold menu direction changes.',
        original_negative='Leo v1 hit8000 wall cap with header-only CSV, zero gameplay/item coverage. Other3 v1 profiles remain unrun.',
        limits='No native launch or result transfer. All original gameplay assertions/caps remain unchanged. Pilot Leonardo before other variants.')
    put(out/'menu-graph-controls.json', proof)
    dependencies = {Path(f['path']) for f in old_ready['bindings']}
    dependencies.update([Path(__file__).resolve(), route.SCRIPT, Path(route.__file__).resolve(), NEW,
        parent/'prepared-not-run.json', parent/'source-controls.json', out/'config.json',
        out/'run.lua', out/'command.json', out/'menu-graph-controls.json'])
    ready = dict(status='PREPARED_DO_NOT_RUN', native_run=False, passed=False,
        goal_complete=False, ROM_sha256=SHA, identity=a.identity,
        variant=config['variant'], actual_numeric_mode=config['mode'], caps=old_ready['caps'],
        menu_only_successor=True, original_readiness_sha256=sha(parent/'prepared-not-run.json'),
        bindings=[dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted(dependencies)],
        scope='Graph-derived menu navigation only; all original tested mechanics/guards remain exact.')
    put(out/'prepared-not-run.json', ready)
    assert OLD.read_bytes() == raw
    print(json.dumps(dict(prepared=True, native_run=False, identity=a.identity,
        ready=str(out/'prepared-not-run.json'), ready_sha256=sha(out/'prepared-not-run.json'),
        bindings=len(dependencies), direction_from_zero=nav[0])))


if __name__ == '__main__':
    main()
