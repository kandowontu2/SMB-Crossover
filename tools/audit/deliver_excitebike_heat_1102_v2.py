"""Root-only delivery of original continuation repair and Downloads heat replay."""
from pathlib import Path
import json,re
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_excitebike_dispatch_1101_v1 import O,labels
from nightly_patch_guard_v1 import check
PIN='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
PARENT='d8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05'


def main():
    rom=O/'current4.nes';assert sha(rom)==PIN
    results={}
    for name in ['native5','heat-native2']:
        c=O/name/'capture';result=json.loads((c/'result.json').read_text());b=json.loads((c/'binding.json').read_text())
        assert result['passed']and b['ROM_sha256']==PIN and b['exit_code']==0
        for p,h in json.loads((O/name/'ready.json').read_text())['bindings'].items():assert sha(p)==h,p
        results[name]=result
    h=json.loads((O/'heat-native2/capture/heat.json').read_text())
    assert all(h[n]for n in ['heat_seen','recovery5_seen','returned_recovery0','resumed_motion'])
    assert results['heat-native2']['initial_lives']==results['heat-native2']['final_lives']==2
    for name in ['heat-CPU.json','heat-ISR-CPU.json']:
        q=json.loads((O/name).read_text());assert q['passed']and q['memory_candidate_SHA256']==PIN
    ref=O/'heat-native2/controller.lua';text=ref.read_text();lab=labels(rom.with_suffix('.lbl'))
    names=set(re.findall(r"\br\('([^']+)'",text))|set(re.findall(r"\bL\[['\"]([^'\"]+)['\"]\]",text))|set(re.findall(r'\bL\.(\w+)',text))
    assert names and names<=lab.keys()and not re.search(r'\bB[.\[]',text)
    # Only the final screenshot name changes; heat-only success is not1-2.
    assert text.count("passed and 'active-1-2' or 'route-stop'")==1
    text=text.replace("passed and 'active-1-2' or 'route-stop'","passed and 'cooldown-recovered' or 'route-stop'")
    prefix=['L=L or {};B=B or {}']+[f'L[{json.dumps(n)}]={lab[n]}'for n in sorted(names)]
    destination=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    previous=sha(destination);assert previous in [PARENT,PIN]
    before=check(destination);assert before['passed']
    if previous!=PIN:destination.write_bytes(rom.read_bytes())
    after=check(destination);assert after['passed']and sha(destination)==PIN
    prepare(O/'heat-downloads',rom,'\n'.join(prefix)+'\n'+text,
            [Path(__file__),ref,destination,O/'current4-composition.json',O/'native5/capture/result.json',O/'heat-native2/capture/result.json',O/'heat-native2/capture/heat.json'],
            expected=PIN,timeout=180,allow_interactive=True,
            scope='Actual Downloads same heat-native2 inputs/strong genuine overheat→recovery5→0→resumed source speed/motion/no-life-loss assertions. ExplicitL/B addresses, no Downloads sidecars/backup/emulated writes. Accurate cooldown-recovered PNG name; full1-1 remains separate.')
    path=O/'heat-downloads/ready.json';ready=json.loads(path.read_text());ready['ROM']=str(destination);path.write_text(json.dumps(ready,indent=2)+'\n')
    receipt=dict(installed=True,ROM_sha256=PIN,previous_sha256=previous,destination=str(destination),candidate=rom.relative_to(R).as_posix(),
                 backup_created=False,downloads_launch_verified=False,before=before,after=after,
                 native_controls=dict(passed=True,frames=results['native5']['frames'],original_jump_pixels=61,hardware=True),
                 native_heat=dict(passed=True,frames=results['heat-native2']['frames'],updates=results['heat-native2']['updates'],
                                  initial_lives=2,final_lives=2,heat_seen=h['heat_seen'],recovery5_seen=h['recovery5_seen'],
                                  returned_recovery0=h['returned_recovery0'],resumed_motion=h['resumed_motion'],heat_start_x=h['heat_start_x'],released_x=h['released_x']),
                 scope='Original timer divider, cooling/lane continuation and throttle-inhibit release restored with105B private code. Native controls/61px jump and real overheat recovery/motion pass, installed Arthur row34 retained. Full1-1/every-powerup/audio remains open.',helpers_added=False)
    (O/'heat-delivery.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(installed=True,ROM_sha256=PIN,backup_created=False,Downloads_packet=str(path),explicit_symbols=len(names))))


if __name__=='__main__':main()
