"""Fresh canonical and ordinary flag-off builds of the private composed C87 trial."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from tmnt_native_storage_driver import ROOT, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    digest='53736e142c6cf568039a3c4927c9356077e3358b7c02fb7b69d3ca72985f2ff6'
    assert sha(a.experiment / 'candidate.nes') == digest
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    source = a.experiment / 'source'
    builds = {}
    for name, mapper, expected in [
        ('canonical', None, digest),
        ('ordinary-mmc3', 'mmc3', 'd444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
        ('ordinary-mmc5', 'mmc5', 'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        command = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
                   '--workspace', str(source), '--compiler', str(ROOT / 'tools/Windows/cc65/bin/cl65.exe'),
                   '--output', str(a.output / (name + '.nes'))]
        if mapper:
            command += ['--flag-off', mapper]
        result = subprocess.run(command, cwd=source, capture_output=True, text=True)
        log = a.output / (name + '-build.log')
        log.write_text(result.stdout + result.stderr)
        assert result.returncode == 0, (name, result.stdout[-2000:], result.stderr[-2000:])
        assert sha(a.output / (name + '.nes')) == expected, name
        builds[name] = dict(ROM_sha256=expected, log_sha256=sha(log))
        print(name + ' passed', flush=True)
    proof = dict(passed=True, source_only=True, native_run=False, accepted=False,
                 candidate_ROM_sha256=sha(a.experiment / 'candidate.nes'), builds=builds,
                 checker_sha256=sha(Path(__file__)), limits='Build reproducibility and ordinary flag-off controls only.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
