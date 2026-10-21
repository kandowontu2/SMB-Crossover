"""Begin the same pillar approach before forward inertia can leave the floor."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent = R / 'tools/audit/continue_easy49_sophia_gq_hb.py'
    text = parent.read_text().replace('root49-gq-sophia-route-hb', 'root49-gq-sophia-route-hc')
    text = text.replace('root49hb-sophia-live', 'root49hc-sophia-live')
    anchor = '    H.mkdir(exist_ok=False)'
    assert text.count(anchor) == 1
    text = text.replace(anchor, anchor + '''
    original_prefix = prefix
    prefix = H / 'prefix.csv'
    prefix.write_text('\\n'.join(line for line in original_prefix.read_text().splitlines()
        if line.startswith('poll,') or int(line.split(',')[0]) <= 8797) + '\\n')
''')
    text = text.replace("controller_sha256=sha(control), policy_sha256=sha(policy), command=command,",
        "controller_sha256=sha(control), policy_sha256=sha(policy), command=command, prefix_sha256=sha(prefix), prefix_polls=8797,")
    driver = V / 'root49-gq-sophia-hc-driver.py'
    assert not driver.exists()
    compile(text, str(driver), 'exec')
    driver.write_text(text)
    negative = R / 'build/roster-through-2-2/root49hb-sophia-live-11-v0-mmc3/result.json'
    (V / 'root49-gq-sophia-hc-preparation.json').write_text(json.dumps(dict(
        retained_HB_negative_sha256=sha(negative), parent_sha256=sha(parent), driver_sha256=sha(driver),
        correction='HB began retreat at1112 with full right velocity and walked off the floor before reversing. Start the same controller20polls earlier on actual supported floor; the GY all-RAM ancestor remains unchanged. No state loads, grants or runtime edits.'), indent=2) + '\n')
    raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)


if __name__ == '__main__':
    main()
