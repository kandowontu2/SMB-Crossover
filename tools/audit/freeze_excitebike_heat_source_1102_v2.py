"""Compact exact source continuation checkpoint, without ROMs or capture forest."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from prepare_selected_native_packet_v1 import R,sha
from prepare_excitebike_dispatch_1101_v1 import O
D=R/'docs/qa/checkpoints/2026-11-02/excitebike-continuation-v2'


def main():
    names=['heat-recovery.s','heat-host.lbl','heat-kernel.bin','heat-cookie.bin','heat-assembly.json',
           'heat-CPU.json','heat-ISR-CPU.json','current4-composition.json']
    paths=[O/n for n in names]
    for name in ['full11','native5','heat-native','heat-native2','full11-v3']:
        paths += [O/name/'controller.lua',O/name/'ready.json']
        for n in ['result.json','binding.json','heat.json']:
            p=O/name/'capture'/n
            if p.is_file():paths.append(p)
    assert all(p.is_file()and p.stat().st_size<100_000 for p in paths)
    source=[
        'tools/audit/prepare_excitebike_heat_1102_v2.py',
        'tools/audit/check_excitebike_heat_1102_v2.py',
        'tools/audit/check_excitebike_heat_ISR_1102_v2.py',
        'tools/audit/compose_excitebike_heat_1102_v2.py',
        'tools/audit/prepare_excitebike_heat_native_1102_v2.py',
        'tools/audit/prepare_excitebike_heat_native_1102_v3.py',
        'tools/audit/deliver_excitebike_heat_1102_v2.py',
        'tools/audit/prepare_excitebike_full11_1102_v1.py',
        'tools/audit/prepare_excitebike_full11_1102_v3.py',
        'tools/reference/excitebike_full11_1102_v1.lua',
        'tools/audit/freeze_excitebike_heat_source_1102_v2.py']
    assert all((R/n).is_file()for n in source)
    archive=O/'heat-source-checkpoint.zip';rows=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in paths:
            data=p.read_bytes();name=p.relative_to(R).as_posix();z.writestr(name,data)
            rows.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    with zipfile.ZipFile(archive)as z:
        for q in rows:assert hashlib.sha256(z.read(q['path'])).hexdigest()==q['sha256']
    assert archive.stat().st_size<100_000
    D.mkdir(parents=True,exist_ok=True);shutil.copyfile(archive,D/'inputs.zip')
    old=R/'docs/qa/checkpoints/2026-11-02/excitebike-source-v1'
    manifest=dict(passed=True,source_only=True,ROM_included=False,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
                  files=rows,source_recipes={n:sha(R/n)for n in source},
                  inherited_compiler_sources=dict(checkpoint=old.relative_to(R).as_posix(),inputs_sha256=sha(old/'inputs.zip')),
                  exact_rebuild='Apply the175 exact offset/old/new byte records in current4-composition.json to authenticatedd8a87050 weapon-tail-candidate.nes. Result must becf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8. Recompile private source using retained v1 exact component/pose/host source plus heat-recovery.s; public addresses stayfixed.',
                  original_phases=['D310..D325 longtimer divider','DD8D..DDCE cooling/lane; HUD tails typedreturn','DCDE..DCF1 post-air throttle gate'],
                  qualification='Actual native5 controls/hardware and heat-native2 overheat→recovery5→0→resumed motion pass. Earlier full11 and too-short heat-native negatives retained. Full1-1/tallpipe/no-helper qualification remains open until full11-v3 returns.')
    (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    stage=source+['docs/qa/excitebike-readiness-1101-v3.md']+[(D/n).relative_to(R).as_posix()for n in ['inputs.zip','manifest.json','commit-files.txt']]
    (D/'commit-files.txt').write_text('\n'.join(stage)+'\n')
    print(json.dumps(dict(passed=True,source_files=len(source),retained_inputs=len(paths),archive_bytes=archive.stat().st_size,checkpoint=D.relative_to(R).as_posix(),stage_list=(D/'commit-files.txt').relative_to(R).as_posix())))


if __name__=='__main__':main()
