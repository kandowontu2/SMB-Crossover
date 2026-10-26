"""Fresh canonical and two ordinary build controls for the private pivot."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((a.candidate / 'source-manifest.json').read_text())
    for rel, h in manifest.items():
        assert sha(a.candidate / 'source' / rel) == h
    rows = []
    expected = [('canonical', None, sha(a.candidate / 'candidate.nes')),
                ('ordinary-mmc3', 'mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                ('ordinary-mmc5', 'mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]
    for name, flag, h in expected:
        cmd = [sys.executable, '-B', str(a.candidate / 'source/tools/build_mmc5_expanded.py'),
               '--workspace', str(a.candidate / 'source'), '--compiler', str(R / 'tools/Windows/cc65/bin/cl65.exe'),
               '--output', str(a.output / (name + '.nes'))]
        if flag:
            cmd += ['--flag-off', flag]
        z = subprocess.run(cmd, capture_output=True, text=True)
        row = dict(name=name, command=cmd, exit=z.returncode, stdout=z.stdout, stderr=z.stderr)
        rows.append(row)
        (a.output / 'launches.json').write_text(json.dumps(rows, indent=2) + '\n')
        assert z.returncode == 0, row
        row['ROM_sha256'] = sha(a.output / (name + '.nes'))
        assert row['ROM_sha256'] == h, row
    proof = dict(passed=True, source_only=True, native_launches=0,
                 candidate_ROM_sha256=expected[0][2], canonical_exact=True,
                 ordinary_MMC3_exact=True, ordinary_MMC5_exact=True,
                 builds=rows, source_manifest_sha256=sha(a.candidate / 'source-manifest.json'),
                 tool_sha256=sha(__file__))
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k != 'builds'}, indent=2))


if __name__ == '__main__':
    main()
