"""One frozen ordinary-input Link F attempt; retain the earlier stopped preflight."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
from roster_run import workspace_bytes

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sys.version_info[:2] == (3, 12), 'Use bundled Python3.12 for the pinned parser'
    output = ROOT / 'build/verification/root48-link-f-first21-b'
    output.mkdir(exist_ok=False)
    policy = ROOT / 'build/verification/link47-route-combat-batch3/link47-first21-combat-f.lua'
    prefix = ROOT / 'build/verification/link47-route-lifts-batch2/current47-e-prefix-before-first21-koopa.csv'
    rom = ROOT / 'build/checkpoints/roster-audit-v47/smb-crossover-mmc3.nes'
    parser = ROOT / 'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime/lupa/lua54.cp312-win_amd64.pyd'
    assert sha(policy) == 'dcc4bc240665c8817059f687381281b32d3929344bfe4e66a454f66a1386e210'
    assert sha(rom) == 'e9c1a98961d26389bc54eefc4c63e725f8ddd91c0e801cf9c553bdf774ece1f1'
    assert sha(parser) == '2d9ba19524d979a641eefba073607b5b87628f9a3bf2e208c4f1aeeb08163800'
    sys.path.insert(0, str(parser.parents[1]))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    compile_lua = lua.eval('function(s,n) local f,e=load(s,n); return f~=nil,e end')
    dependencies = {}

    def freeze(path):
        path = path.resolve(strict=True)
        assert path.is_relative_to(ROOT)
        name = path.relative_to(ROOT).as_posix()
        if name in dependencies:
            return
        content = path.read_text(encoding='utf-8-sig')
        ok, error = compile_lua(content, str(path))
        assert ok, (name, error)
        assert not re.search(r'emu\.(?:write|loadState|setState|setRegister)\s*\(', content), name
        dependencies[name] = sha(path)
        for match in re.finditer(r'dofile\(\s*([\'\"])(.*?)\1\s*\)', content):
            target = Path(match[2])
            freeze(target if target.is_absolute() else ROOT / target)

    freeze(policy)
    freeze(ROOT / 'tools/playthroughs/roster_harness.lua')
    freeze(ROOT / 'tools/playthroughs/roster_audit.lua')
    used = workspace_bytes(ROOT)
    assert used + 50_000_000 < 28_950_000_000, used
    command = [sys.executable, 'tools/playthroughs/roster_run.py', '--character', '4',
               '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root48-link-first21-f-a',
               '--policy', str(policy), '--prefix', str(prefix), '--frames', '26000',
               '--timeout', '240', '--workspace-cap-gb', '28.95']
    report = dict(status='prepared-not-launched', controller_only=True, full_frame_audit=True,
                  no_emulated_memory_register_or_PC_writes=True,
                  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  rom_sha256=sha(rom), prefix_sha256=sha(prefix), parser_sha256=sha(parser),
                  dependencies=dependencies, workspace_before_bytes=used,
                  max_native_calls=1, frame_limit=26000, timeout_seconds=240,
                  additional_budget_bytes=50_000_000, command=command,
                  script_sha256=sha(Path(__file__)), final_traversal_proof=False)
    receipt = output / 'receipt.json'

    def save():
        receipt.write_text(json.dumps(report, indent=2) + '\n')

    save()
    with (output / 'native.log').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    report.update(status='native-completed', exit=result.returncode,
                  workspace_after_bytes=workspace_bytes(ROOT),
                  dependencies_unchanged=all(sha(ROOT / n) == h for n, h in dependencies.items()))
    save()
    print(json.dumps(report, indent=2), flush=True)
    assert report['dependencies_unchanged']
    assert report['workspace_after_bytes'] < 30_000_000_000


if __name__ == '__main__':
    main()
