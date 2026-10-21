"""Turn on the middle bank before its left edge and wait for actual right velocity."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent = V / 'root49-gq-sophia-hc-driver.py'
    text = parent.read_text().replace('root49-gq-sophia-route-hc', 'root49-gq-sophia-route-hd')
    text = text.replace('root49hc-sophia-live', 'root49hd-sophia-live')
    old = 'if c.x<=1032 then phase=1 end'
    assert text.count(old) == 1
    text = text.replace(old, 'if c.x<=1052 then phase=1 end')
    old = 'if c.x>=1050 and c.grounded and not c.lastA then'
    assert text.count(old) == 1
    text = text.replace(old, 'if c.x>=1050 and c.vx>=16 and c.vx<128 and c.grounded and not c.lastA then')
    driver = V / 'root49-gq-sophia-hd-driver.py'
    assert not driver.exists()
    compile(text, str(driver), 'exec');driver.write_text(text)
    negative = R / 'build/roster-through-2-2/root49hc-sophia-live-11-v0-mmc3/result.json'
    (V / 'root49-gq-sophia-hd-preparation.json').write_text(json.dumps(dict(
        parent_sha256=sha(parent), driver_sha256=sha(driver), retained_HC_negative_sha256=sha(negative),
        correction='HC retreat reached1032 but left momentum carried it past the actual left bank edge1024. Turn earlier at1052 and require positive right velocity before launching; unchanged cold prefix/current ROM, no state loads or runtime edits.'), indent=2) + '\n')
    raise SystemExit(subprocess.run([sys.executable, str(driver)], cwd=R).returncode)


if __name__ == '__main__':
    main()
