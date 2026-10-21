"""Switch the genuine EL Bass prefix to an existing responsive controller policy."""
from pathlib import Path
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-el-bass-route-fe'
FD = V / 'root49-el-bass-transfer-fd'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    fd = json.loads((FD / 'report.json').read_text())
    assert sha(FD / 'report.json') == '46825a9456104363de9209f2f053599adefad3bf5555d3edecb37f9f7086b2b9'
    base = R / 'tools/playthroughs/bass_v34_finish_policy.lua'
    queue, dependencies = [base], {}
    while queue:
        p = queue.pop()
        if p.relative_to(R).as_posix() in dependencies:
            continue
        text = p.read_text()
        assert not any(s in text for s in ('emu.write', 'loadSavestate', 'emu.setState'))
        dependencies[p.relative_to(R).as_posix()] = sha(p)
        queue.extend(R / n.lstrip('/') for n in re.findall(r"['\"](/tools/[^'\"]+\.lua)['\"]", text))
    H.mkdir(exist_ok=False)
    original = R / 'build/roster-through-2-2/root49fd-bass-fixed-9-v0-mmc3/inputs.csv'
    with original.open(newline='') as f:
        source = list(csv.DictReader(f))
    prefix = H / 'prefix.csv'
    with prefix.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['poll', 'frame', 'mask'], lineterminator='\n')
        writer.writeheader()
        writer.writerows(r for r in source if int(r['poll']) <= 7740)
    shutil.copyfile(FD / 'observer.lua', H / 'observer.lua')
    controller = H / 'controller.lua'
    controller.write_text('local guard=assert(dofile(' + json.dumps((FD / 'guard.lua').as_posix()) + '))\n' +
        'return dofile(' + json.dumps(base.as_posix()) + ')\n')
    # Existing FD wrapper contains the actual EL bank/eight-byte hook table.
    wrapper = (FD / 'policy.lua').read_text()
    wrapper = wrapper.replace((FD / 'observer.lua').as_posix(), (H / 'observer.lua').as_posix())
    wrapper = wrapper.replace((FD / 'guard.lua').as_posix(), controller.as_posix())
    policy = H / 'policy.lua'
    policy.write_text(wrapper)
    report = dict(status='PREPARED_CONTROLLER_ONLY_EL_BASS_RESPONSIVE_CONTINUATION',
        script_sha256=sha(__file__), parent_report_sha256=sha(FD / 'report.json'),
        actual_ROM_sha256='2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060',
        prefix_polls=7740, prefix_sha256=sha(prefix), source_inputs_sha256=sha(original),
        pure_controller_dependencies=dependencies, policy_sha256=sha(policy),
        controller_sha256=sha(controller), observer_sha256=sha(H / 'observer.lua'),
        emulated_writes=False, state_loads=False, runtime_changes=False, goal_complete=False)
    (H / 'binding.json').write_text(json.dumps(report, indent=2) + '\n')
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == report['actual_ROM_sha256']
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '9',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root49fe-bass-live',
        '--policy', str(policy), '--prefix', str(prefix), '--frames', '36000', '--timeout', '900',
        '--discovery-fast', '--workspace-cap-gb', '55']
    rc = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=rc, command=command), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
