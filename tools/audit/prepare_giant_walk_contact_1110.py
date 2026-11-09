"""Controller-only first-Goomba regression: no jump, cheats or state writes."""
import argparse
from pathlib import Path

import prepare_mega_giant_f33_native_1110 as G
from prepare_selected_native_packet_v1 import prepare, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha', required=True)
    a = p.parse_args()
    assert sha(a.rom) == a.expected_sha
    source = G.controller(a.expected_sha)
    start = source.index('local function choose()')
    end = source.index('\nemu.addEventCallback(function()\n frame=frame+1', start)
    source = source[:start] + '''local function choose()
 input={right=true}
 if x()>=400 then
  return finish(true,'walked through first Goomba; no jump input')
 end
end
''' + source[end:]
    prepare(a.output, a.rom, source,
            {Path(__file__), Path(G.__file__), G.SOURCE, G.PROOF, G.ROUTE},
            expected=a.expected_sha, timeout=120, allow_interactive=True,
            rom_symbols=(G.BASE.with_suffix('.lbl'), G.BASE.with_suffix('.dbg')),
            scope='First Goomba ground-contact regression; no A input or cheats. '
                  'Survival alone does not establish native enemy defeat or block destruction.')


if __name__ == '__main__':
    main()
