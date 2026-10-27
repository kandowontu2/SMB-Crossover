"""Private expanded-MMC5 ColorRotation backpressure: one CPX operand only."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import traceback
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'robot-base-palette-candidate-v2'
P_SHA = 'dfbdca24019776262c4388e3ea782fb989e24b8fc0e3cf0bfe0bbb84a9f480ad'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(R)
    out.mkdir(parents=True, exist_ok=False)
    try:
        assert sha(P / 'candidate.nes') == P_SHA
        original = json.loads((P / 'source-manifest.json').read_text())
        assert len(original) == 870
        source = out / 'source'
        for rel, h in original.items():
            f = P / 'source' / rel
            assert sha(f) == h, rel
            target = source / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, target)
        f = source / 'src/game.s'
        before = f.read_bytes()
        needle = b'  cpx #$31                  ;check if offset is greater than 49'
        lines = [line for line in before.splitlines(keepends=True) if b'cpx #$31' in line]
        assert len(lines) == 1, lines
        oldline = lines[0]
        assert b'49' in oldline
        nl = b'\r\n' if oldline.endswith(b'\r\n') else b'\n'
        replacement = (b'.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5' + nl
                       + b'  cpx #$29                  ;defer seven-byte world palette when offset >=41' + nl
                       + b'.else' + nl + oldline + b'.endif' + nl)
        f.write_bytes(before.replace(oldline, replacement))
        manifest = {rel: sha(source / rel) for rel in original}
        changed = [rel for rel in original if manifest[rel] != original[rel]]
        assert changed == ['src/game.s']
        put(out / 'source-manifest.json', manifest)
        (out / 'source.patch').write_text(''.join(difflib.unified_diff(
            before.decode().splitlines(True), f.read_text().splitlines(True),
            fromfile='df/src/game.s', tofile='private/src/game.s')))
        cmd = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
               '--workspace', str(source), '--compiler', str(R / 'tools/Windows/cc65/bin/cl65.exe'),
               '--output', str(out / 'candidate.nes')]
        z = subprocess.run(cmd, cwd=source, capture_output=True, text=True)
        put(out / 'build.json', dict(command=cmd, exit=z.returncode, stdout=z.stdout, stderr=z.stderr))
        assert z.returncode == 0, z.stdout + z.stderr
        old = (P / 'candidate.nes').read_bytes()
        new = (out / 'candidate.nes').read_bytes()
        b = scoped_load(out / 'candidate.nes')
        at = location(b, 'ColorRotation') + 10
        assert address(b, 'ColorRotation') == 0x86e0
        assert at == 16 + 126 * 8192 + (0x86ea & 8191)
        assert old[at - 1:at + 1] == bytes([0xe0, 49])
        assert new[at - 1:at + 1] == bytes([0xe0, 41])
        delta = [i for i, (x, y) in enumerate(zip(old, new)) if x != y]
        assert len(old) == len(new) and delta == [at], delta
        q = qualified(P / 'candidate.nes')
        assert qualified(out / 'candidate.nes') == q
        put(out / 'proof.json', dict(passed=True, source_only=True, native_run=False,
            baseline_ROM_sha256=P_SHA, candidate_ROM_sha256=sha(out / 'candidate.nes'),
            source_count=len(manifest), changed_source=changed, exact_ROM_delta=[dict(
                file_offset=at, physical_bank=126, CPU_address='0x86EA', old=49, new=41)],
            all_qualified_labels_RAM_CHR_NMI_other_PRG_exact=True, qualified_symbols=len(q),
            new_RAM_bytes=0, source_manifest_sha256=sha(out / 'source-manifest.json'),
            patch_sha256=sha(out / 'source.patch'), tool_sha256=sha(__file__),
            behavior='Expanded MMC5 only: existing busy/defer path now applies to offsets41..48 too. Counter does not advance on defer; no source clock or caller changes.',
            limits='Build/layout only. Original df native993 strict failure is retained. No native recovery claim.'))
        print((out / 'proof.json').read_text())
    except BaseException as e:
        put(out / 'failure.json', dict(passed=False, error=repr(e), traceback=traceback.format_exc()))
        shutil.copyfile(__file__, out / 'failed-tool.py')
        raise


if __name__ == '__main__':
    main()
