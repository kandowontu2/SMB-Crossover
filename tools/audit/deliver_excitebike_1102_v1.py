"""Root-only direct nightly delivery and actual Downloads controller packet."""
from pathlib import Path
import json,re
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_excitebike_dispatch_1101_v1 import labels
from nightly_patch_guard_v1 import check

O=R/'build/excitebike-pose-1101-v3'
PIN='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
PARENT='b9e685ffd0620a213a2fc05219e2bae415ee81aa07ab0e994db79455792ef6c4'


def main():
    rom=O/'current3.nes';assert sha(rom)==PIN
    results={}
    for name in ['native4','arthur-flower']:
        c=O/name/'capture';q=json.loads((c/'result.json').read_text());b=json.loads((c/'binding.json').read_text())
        assert q['passed'] and b['exit_code']==0 and b['ROM_sha256']==PIN
        ready=json.loads((O/name/'ready.json').read_text())
        for path,digest in ready['bindings'].items():assert sha(path)==digest,path
        results[name]=q
    diagnosis=json.loads((O/'native4/capture/diagnosis.json').read_text())
    assert diagnosis['hardware_checks']>1000 and diagnosis['hardware_failures']==0 and diagnosis['source_color_calls']>0
    jump=next(q for q in results['native4']['phases']if q['phase']=='jump')
    assert jump['first_y']-jump['minimum_y']==61
    assert results['native4']['initial_lives']==results['native4']['final_lives']==2
    assert results['arthur-flower']['lives_start']==results['arthur-flower']['lives_end']==2
    ref=O/'native4/controller.lua';text=ref.read_text();lab=labels(rom.with_suffix('.lbl'))
    names=set(re.findall(r"\br\('([^']+)'",text))|set(re.findall(r"\bL\[['\"]([^'\"]+)['\"]\]",text))|set(re.findall(r'\bL\.(\w+)',text))
    assert names and names<=lab.keys()
    assert not re.search(r'\bB[.\[]',text)
    prefix=['L=L or {};B=B or {}']+[f'L[{json.dumps(n)}]={lab[n]}'for n in sorted(names)]
    destination=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    previous=sha(destination);assert previous in [PARENT,PIN]
    before=check(destination);assert before['passed']
    if previous!=PIN:destination.write_bytes(rom.read_bytes())
    after=check(destination);assert after['passed'] and sha(destination)==PIN
    prepare(O/'downloads',rom,'\n'.join(prefix)+'\n'+text,
            [Path(__file__),ref,destination,O/'current3-composition.json',O/'native4/capture/result.json',
             O/'native4/capture/diagnosis.json',O/'arthur-flower/capture/result.json'],
            expected=PIN,timeout=150,allow_interactive=True,
            scope='Actual Downloads exact native4 cold Excitebike menu/idle/throttle/coast/reverse/original turbo-backlean61px jump/landing with native CHR/palette/HUD/alignedOAM checks. Explicit L/B prefix; no Downloads debug sidecars, backup or emulated writes. Full1-1 remains open.')
    path=O/'downloads/ready.json';ready=json.loads(path.read_text());ready['ROM']=str(destination)
    path.write_text(json.dumps(ready,indent=2)+'\n')
    receipt=dict(installed=True,ROM_sha256=PIN,previous_sha256=previous,destination=str(destination),
                 candidate=rom.relative_to(R).as_posix(),backup_created=False,downloads_launch_verified=False,
                 before=before,after=after,native_controls=results['native4'],hardware=diagnosis,
                 Arthur_flower=results['arthur-flower'],helpers_added=False,
                 scope='Source-backed original Excitebike motor/air/pose/recovery with deliberate SMB controls and32px native terrain profile. Native61px jump and actual Arthur flower/torch regression pass. Full1-1 and complete ability/powerup/audio review remain open.')
    (O/'delivery.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(installed=True,ROM_sha256=PIN,backup_created=False,Downloads_packet=str(path),explicit_symbols=len(names))))


if __name__=='__main__':main()
