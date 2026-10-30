"""Reproduce the frozen DK/CF menu over its genuine full source tree."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from finalize_ff_current_component_v3 import dependencies
from prepare_cv3_dmc_mirror import prepare

P = R / 'build/character-host-union-unlock-v3/joint'
Q = R / 'build/dk-cf-roster-menu-v3'
HP = R / 'build/dk-cf-roster-menu-qualified-v1/handoff.json'
O = R / 'build/expanded-playable-menu-parent-1030-v1/joint'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rewrite(value):
    for source in [P, Q]:
        value = value.replace(str(source), str(O)).replace(source.as_posix(), O.as_posix())
    return value


def execute(cmd, name):
    cmd = [rewrite(x) for x in cmd]
    r = subprocess.run(cmd, cwd=R, capture_output=True, text=True)
    (O / (name + '.json')).write_text(json.dumps(dict(command=cmd, returncode=r.returncode,
        stdout=r.stdout, stderr=r.stderr), indent=2) + '\n')
    assert r.returncode == 0, r.stderr[-2500:]


def main():
    assert not O.exists()
    assert sha(HP) == 'fa326b96dcf8a6dad0a586469cf648d39d1b2cae9ddedd4145da266752cc9313'
    handoff = json.loads(HP.read_text())
    files = set()
    for f, h in handoff['bindings'].items():
        assert sha(f) == h, f
        files.add(Path(f))
    O.mkdir(parents=True)
    for source in [P, Q]:
        for f in source.rglob('*'):
            if not f.is_file() or f.suffix not in ['.s', '.inc', '.cfg', '.bin', '.chr', '.rle', '.nam']:
                continue
            out = O / f.relative_to(source)
            out.parent.mkdir(parents=True, exist_ok=True)
            if f.suffix in ['.s', '.inc', '.cfg']:
                out.write_text(rewrite(f.read_text()), newline='\n')
            else:
                out.write_bytes(f.read_bytes())
    for name in ['main', 'rogue-component', 'union', 'bbox-local', 'gm-nmi', 'dk-component', 'reader']:
        source = Q if name == 'main' else P
        execute(json.loads((source / (name + '-build.json')).read_text())['command'], name + '-build')
    execute(json.loads((Q / 'link-build.json').read_text())['command'], 'link-build')
    prepare(R, O / 'candidate.nes')
    assert (O / 'candidate.nes').read_bytes() == (Q / 'candidate.nes').read_bytes()
    for f in O.glob('*.dep'):
        files.update(dependencies(f))
    files |= {f for f in O.rglob('*') if f.is_file()}
    files |= {Path(__file__), HP, P / 'source-closure.json'}
    result = dict(passed=True, ROM_sha256=sha(O / 'candidate.nes'),
                  exact_frozen_DK_CF_source_reproduction=True,
                  playable_identities=52, pending_identities=28,
                  bindings={str(f.resolve()): sha(f) for f in sorted(files)})
    (O / 'source-closure.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'bindings'}))


if __name__ == '__main__':
    main()
