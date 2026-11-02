"""Retain exact small compiler inputs and the installed patch recipe, no ROM."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from prepare_selected_native_packet_v1 import R,sha

O=R/'build/excitebike-pose-1101-v3'
D=R/'docs/qa/checkpoints/2026-11-02/excitebike-source-v1'


def main():
    # These are exact source/asset/link inputs, not a recursive historical tree.
    original=R/'build/excite-prince-component-1101-v2'
    original_names=['excitebike-component.s','component.cfg','component.lbl','state-799.bin',
                    'source-art.json','excitebike-body-patterns.bin']
    current_names=['excitebike-pose.s','pose.cfg','owner-loader.inc','owner-loader.s',
                   'dispatch.s','dispatch.cfg','scene.s','scene.cfg','host.s','host.cfg',
                   'host-recovery.s','host-background.bin','router.s','router.cfg',
                   'router-callback-tables.bin','shot-owner.s','shot-owner.cfg',
                   'host-cookie.bin','dispatch-cookie.bin','excitebike-cookie.bin',
                   'body-native.chr','body-native.json','scene.lbl','host.lbl','shot-owner.lbl',
                   'current2-composition.json','current3-composition.json',
                   'dispatch-lease.json','consumer-closure.json','upper2-finite-domains.json',
                   'writer-preservation.json','new-owner-pages.json','smb3-pages.json',
                   'router-CPU.json','dispatch-CPU.json','host-CPU.json','terrain-CPU.json',
                   'UI-ingress-CPU.json','shot-owner-CPU.json','cold2-CPU.json','current2-CPU.json',
                   'controller-windup-CPU.json']
    paths=[original/n for n in original_names]+[O/n for n in current_names]
    sh=R/'build/shinobi-bbox-design-1101-v29'
    paths += [sh/n for n in ['resident-design.s','resident-design.bin','resident-design.cfg',
                             'shinobi-damage-compact.inc','shinobi-cookie.bin']]
    # Runtime fragments can be reproduced by the retained sources. Preserve
    # their small exact bytes too, enabling independent image comparisons.
    paths += [O/n for n in ['host-kernel.bin','host-metadata.bin','dispatch-loader.bin',
              'dispatch-body.bin','dispatch-foreign.bin','dispatch-foreign-bank.bin',
              'dispatch-veneers.bin','scene-gate.bin','scene-own.bin','menu-gate.bin',
              'menu-body.bin','menu-done.bin','router-gate.bin','router-route.bin',
              'router-callback.bin','shot-owner.bin']]
    for name in ['native','native2','native3','native4','arthur-flower','shinobi-smoke']:
        paths += [O/name/'controller.lua',O/name/'ready.json']
        c=O/name/'capture'
        for file in ['result.json','binding.json']:
            if (c/file).exists():paths.append(c/file)
    assert all(p.is_file() and p.stat().st_size<100_000 for p in paths)
    recipes=sorted({*R.glob('tools/audit/*excitebike*.py'),
                    R/'tools/audit/excite_prince_component_1101_v2.py',
                    R/'tools/audit/freeze_excite_prince_component_1101_v2.py',
                    *R.glob('tools/reference/excitebike*'),
                    R/'tools/reference/metal_storm_union_funding_1101_v12.inc'})
    assert all(p.is_file()for p in recipes)
    # Source files are committed normally; the archive contains only required
    # generated inputs/receipts whose old expanded build roots can be pruned.
    rows=[];archive=O/'source-checkpoint.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in paths:
            data=p.read_bytes();name=p.relative_to(R).as_posix()
            rows.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
            z.writestr(name,data)
    with zipfile.ZipFile(archive)as z:
        for row in rows:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
    assert archive.stat().st_size<200_000
    D.mkdir(parents=True,exist_ok=True);shutil.copyfile(archive,D/'inputs.zip')
    q=dict(passed=True,source_only=True,ROM_included=False,archive_sha256=sha(archive),
           archive_bytes=archive.stat().st_size,input_bytes=sum(r['bytes']for r in rows),files=rows,
           source_recipes={p.relative_to(R).as_posix():sha(p)for p in recipes},
           exact_rebuild='Read current2-composition.json from inputs.zip and apply its ordered exact-preimage patches to authenticated b9e685 maturity-candidate.nes. Result must be37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c. No original ROM or historical source tree is bundled.',
           limits='Native4 controls/hardware, combined Arthur flower and Sh smoke only. Full1-1, all abilities/powerups/audio and every-character qualification remain open.')
    (D/'manifest.json').write_text(json.dumps(q,indent=2)+'\n')
    files=[p.relative_to(R).as_posix()for p in recipes]+[
        'docs/qa/excitebike-readiness-1101-v3.md',
        (D/'inputs.zip').relative_to(R).as_posix(),(D/'manifest.json').relative_to(R).as_posix(),
        (D/'commit-files.txt').relative_to(R).as_posix()]
    (D/'commit-files.txt').write_text('\n'.join(files)+'\n')
    print(json.dumps(dict(passed=True,checkpoint=D.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,
                          retained_inputs=len(rows),source_recipe_files=len(recipes),commit_file_list=str(D/'commit-files.txt'))))


if __name__=='__main__':main()
