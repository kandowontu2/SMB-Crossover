"""Run the established roster oracles against a composed traversal-fix ROM."""
from pathlib import Path
import argparse
import importlib.util
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('part', choices=('entry', 'features', 'adapters', 'scroll'))
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cv3-fixtures', type=Path)
    args = parser.parse_args()
    rom, output = args.rom.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if args.part == 'entry':
        return subprocess.call([sys.executable, str(ROOT/'tools/audit/check_full_roster_entry.py'),
            '--rom', str(rom), '--output', str(output/'roster'), '--complete'], cwd=ROOT)
    if args.part == 'scroll':
        return subprocess.call([sys.executable,
            str(ROOT/'build/verification/new-roster-scroll-native-agent/run.py'),
            str(rom), '--output', str(output/'scroll')], cwd=ROOT)
    filename = 'check_character_features_mz.py' if args.part == 'features' else 'check_final_adapters_mz.py'
    spec = importlib.util.spec_from_file_location('nc_'+args.part, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.O, module.P = output, rom
    if args.part == 'features':
        assert args.cv3_fixtures, 'Use the frozen adapted CV3 feature oracles'
        source = args.cv3_fixtures.resolve()
        core = (source/'native_core_adapted.lua').read_text()
        features = (source/'native_features_adapted.lua').read_text()
        features, count = re.subn(r'dofile\(\[\[[^\]]*/native_core_adapted\.lua\]\]\)',
            lambda _: core, features)
        assert count == 1, 'Bind exactly the frozen feature/core pair'
        folder = output/'adapted-cv3-fixtures'
        folder.mkdir(exist_ok=True)
        for name, variant in (('sypha', 2), ('alucard', 3)):
            fixture = folder/(name+'.lua')
            fixture.write_text('CV3_VARIANT='+str(variant)+'\n'+features)
            module.FIXTURE_OVERRIDES[name] = fixture
        # Movement now publishes the camera cache before native scrolling.
        # Reach the real question column by position rather than assuming a
        # fixed number of video frames always ends at the same world X.
        turtle = (ROOT/'build/verification/vic-adoption-mp/final-turtle-natural/turtle-natural.lua').read_text()
        old = '(f>=550 and f<810)'
        assert turtle.count(old) == 1
        turtle = turtle.replace(old, "(f>=550 and f<840 and (r('Player_PageLoc')*256+r('Player_X_Position'))<330)")
        point = "local x=r('Player_PageLoc')*256+r('Player_X_Position')"
        assert turtle.count(point) == 1
        turtle = turtle.replace(point, point+"\n if f==849 then assert(x>=330 and x<=335,'Controller reaches the real mushroom question column')end")
        fixture = folder/'turtles.lua'
        fixture.write_text(turtle)
        module.FIXTURE_OVERRIDES['turtles'] = fixture
    module.main()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
