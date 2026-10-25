"""Build a private current-source MMC3 candidate using a pinned proposed recipe."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--compact-sophia', action='store_true',
                   help='Place the new capacity helper in its same-bank branch-skipped24-byte span')
    p.add_argument('--cv3-noise', action='store_true',
                   help='Carry the expanded CV3 generated noise-cache hook into the private full-roster port')
    args = p.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    recipe = ROOT / 'tools/mmc3_oversized/proposals/parser-v42/repairs.proposed.json'
    assert sha(recipe) == 'e319cc3ae572c81b8f3ff26c4e236d07bafd7140ac5bbcef2075b73b8d28ccab'
    tools = out / 'tools'
    tools.mkdir()
    for name in ['prepare_mmc3_oversized.py', 'mmc3_current_repairs.py']:
        shutil.copyfile(ROOT / 'tools' / name, tools / name)
    assets = tools / 'mmc3_oversized'
    assets.mkdir()
    shutil.copyfile(recipe, assets / 'repairs.json')
    proposed = json.loads(recipe.read_text())
    if args.compact_sophia:
        helper = (ROOT / 'src/sophia_missile_capacity.s').read_text()
        body = helper.split('.proc SophiaTripletAdmission\n', 1)[1].split('.endproc', 1)[0]
        replacement = ('  jmp HighByte\n::SophiaTripletAdmission:\n'
                       '.scope M3SophiaTripletPad\n'+body+'.endscope\n'
                       '  .assert *-::SophiaTripletAdmission<=24,lderror,"Capacity helper fits skipped span"\n'
                       '  .res 24-(*-::SophiaTripletAdmission),$ea\nHighByte:\n')
        proposed['text_repairs'] += [
            dict(path='src/remaining_weapons.s', chunks=[dict(
                old='  jmp HighByte\n  .res 24, $ea\nHighByte:\n', new=replacement)]),
            dict(path='src/sophia_missile_capacity.s', chunks=[dict(
                old=helper, new='; MMC3 capacity helper is in the branch-skipped AvHomeFriction span.\n')])]
    if args.cv3_noise:
        # Keep the port's profile-reset alias repair while retaining the new
        # real scene-stop call, rather than reintroducing the old LDA tail.
        reset_rows = [row for row in proposed['text_repairs'] if row['path'] == 'src/cv3_core.s']
        assert len(reset_rows) == 1
        row = reset_rows[0]
        assert len(row['chunks']) == 1
        for key in ['old', 'new']:
            assert row['chunks'][0][key].endswith('  lda Cv3Variant\n')
            row['chunks'][0][key] = row['chunks'][0][key].replace(
                '  lda Cv3Variant\n', '  jsr Cv3NoiseSceneReset\n')
        row.pop('baseline_sha256', None)
        row.pop('repaired_sha256', None)
        # The normal preparation only converts source .s/.inc flags. This
        # generated driver also needs its original same-size noise-store hook;
        # otherwise music's unmarked volume write bypasses the CV3 cache.
        proposed['text_repairs'].append(dict(
            path='build/generated/guest-audio/castlevania.inc', chunks=[dict(
                old='.if ::ENABLE_MMC5_EXPANDED\n  JSR ::Cv3NoiseVolumeStore\n.else\n',
                new='.if ::ENABLE_FULL_ROSTER\n  JSR ::Cv3NoiseVolumeStore\n.else\n')]))
    if args.compact_sophia or args.cv3_noise:
        (assets / 'repairs.json').write_text(json.dumps(proposed, indent=2)+'\n', encoding='utf-8')
        (out / 'repairs.proposed.json').write_bytes((assets / 'repairs.json').read_bytes())
    shutil.copyfile(ROOT / 'tools/mmc3_oversized/mmc3-menu-previews.chr',
                    assets / 'mmc3-menu-previews.chr')
    report = dict(passed=False, prepared=False, compiled=False, adopted=False,
                  goal_complete=False, parent_MMC5_SHA256=sha(args.reference),
                  base_recipe_sha256=sha(recipe), recipe_sha256=sha(assets / 'repairs.json'),
                  compact_sophia=args.compact_sophia, cv3_noise=args.cv3_noise,
                  runner_sha256=sha(Path(__file__)),
                  scope='Private current-source build compatibility only; no native gameplay, graphics, interrupt, performance or release qualification.')
    with (out / 'prepare.log').open('w') as log:
        result = subprocess.run([sys.executable, str(tools / 'prepare_mmc3_oversized.py'),
                                 '--source-root', str(ROOT), '--reference-rom', str(args.reference),
                                 '--output', str(out / 'source')], stdout=log, stderr=subprocess.STDOUT)
    report.update(prepare_exit=result.returncode, prepared=result.returncode == 0)
    if result.returncode == 0:
        helper = ROOT / 'tools/mmc3_oversized/proposals/parser-v42/mmc3_parser_build_v1.py'
        spec = importlib.util.spec_from_file_location('parser_compile', helper)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            module.compile_rom(out / 'source', out / 'candidate.nes')
        except AssertionError as error:
            report['compile_error'] = str(error)
        else:
            report.update(passed=True, compiled=True, candidate_sha256=sha(out / 'candidate.nes'))
    (out / 'proof.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    if not report['prepared']:
        print((out / 'prepare.log').read_text()[-6500:])
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
