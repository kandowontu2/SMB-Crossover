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
    if args.compact_sophia:
        helper = (ROOT / 'src/sophia_missile_capacity.s').read_text()
        body = helper.split('.proc SophiaTripletAdmission\n', 1)[1].split('.endproc', 1)[0]
        replacement = ('  jmp HighByte\n::SophiaTripletAdmission:\n'
                       '.scope M3SophiaTripletPad\n'+body+'.endscope\n'
                       '  .assert *-::SophiaTripletAdmission<=24,lderror,"Capacity helper fits skipped span"\n'
                       '  .res 24-(*-::SophiaTripletAdmission),$ea\nHighByte:\n')
        proposed = json.loads(recipe.read_text())
        proposed['text_repairs'] += [
            dict(path='src/remaining_weapons.s', chunks=[dict(
                old='  jmp HighByte\n  .res 24, $ea\nHighByte:\n', new=replacement)]),
            dict(path='src/sophia_missile_capacity.s', chunks=[dict(
                old=helper, new='; MMC3 capacity helper is in the branch-skipped AvHomeFriction span.\n')])]
        (assets / 'repairs.json').write_text(json.dumps(proposed, indent=2)+'\n', encoding='utf-8')
        (out / 'repairs.proposed.json').write_bytes((assets / 'repairs.json').read_bytes())
    shutil.copyfile(ROOT / 'tools/mmc3_oversized/mmc3-menu-previews.chr',
                    assets / 'mmc3-menu-previews.chr')
    report = dict(passed=False, prepared=False, compiled=False, adopted=False,
                  goal_complete=False, parent_MMC5_SHA256=sha(args.reference),
                  base_recipe_sha256=sha(recipe), recipe_sha256=sha(assets / 'repairs.json'),
                  compact_sophia=args.compact_sophia, runner_sha256=sha(Path(__file__)),
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
