"""Prepare the existing controller replay against the actual 32-slot menu."""
from pathlib import Path
import runpy
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import roster_expansion_native_prepare_v2 as menu
import current_roster_compact_11_v1 as base


def navigation(raw, location, target):
    edges = {key: list(raw[location('X5Menu' + key.title()):location('X5Menu' + key.title()) + 32])
             for key in ['left', 'right', 'up', 'down']}
    result = []
    for start in range(32):
        todo, visited = [(start, [])], {start}
        for node, path in todo:
            if node == target:
                result.append(path[0] if path else '')
                break
            for key, table in edges.items():
                n = table[node]
                assert 0 <= n < 32
                if n not in visited:
                    visited.add(n)
                    todo.append((n, path + [key]))
        else:
            raise AssertionError('Compiled menu has unreachable target')
    return result


def main():
    menu.navigation = navigation
    v4 = runpy.run_path(str(R / 'tools/audit/kamikaze_mario_native_prepare_v4.py'))
    v4['main']()
    # The actual navigation is compiled into run.lua/config; bind this adapter
    # too so a later controller run cannot lose its 32-slot provenance.
    import json
    at = sys.argv.index('--output')
    ready = Path(sys.argv[at + 1]).resolve() / 'ready.json'
    data = json.loads(ready.read_text())
    data['bindings'][str(Path(__file__).resolve())] = base.sha(Path(__file__))
    data['navigation_contract'] = 'BFS over all four actual32-byte native menu edge tables; removed X5MenuPresent is never read.'
    ready.write_text(json.dumps(data, indent=2) + '\n')


if __name__ == '__main__':
    main()
