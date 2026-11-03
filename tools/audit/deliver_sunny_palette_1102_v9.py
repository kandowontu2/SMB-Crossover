"""Install qualified Sunny fix and prepare the actual Downloads full route."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check
PIN='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
O=R/'build/sunny-delivery-1102-v9'

def main():
    rom=R/'build/sunny-growth-prelude-1102-v9/candidate.nes';p=R/'build/sunny-growth-native-1102-v9/native'
    assert sha(rom)==PIN
    ready=json.loads((p/'ready.json').read_text());binding=json.loads((p/'capture/binding.json').read_text());result=json.loads((p/'capture/result.json').read_text())
    assert result['passed'] and result['full_stage'] and result['final_lives']==result['initial_lives']==2 and binding['exit_code']==0
    assert result['ROM_sha256']==binding['ROM_sha256']==PIN and binding['ready_sha256']==sha(p/'ready.json')
    for name,h in ready['bindings'].items():assert sha(name)==h,name
    for name in ['build/sunny-palette-qualification-1102-v6/CPU.json','build/sunny-growth-prelude-1102-v9/candidate.json']:assert json.loads((R/name).read_text())['passed']
    d=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');before=check(d);assert before['passed']
    assert sha(d)in ['22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19',PIN]
    d.write_bytes(rom.read_bytes());after=check(d);assert after['passed'] and sha(d)==PIN
    O.mkdir(exist_ok=True);source=p/'controller.lua';packet=O/'downloads-smoke'
    prepare(packet,rom,source.read_text(),[Path(__file__),source,d,*map(Path,ready['bindings'])],expected=PIN,timeout=240,scope='Actual Downloads launch context: Sunny cold Hard full non-shortcut1-1 controller-only mushroom and damage transforms into active1-2, unchanged hardware deadline/DMA/CHR/IRQ assertions. Other roster/bothmode/allpowerup qualification remains incomplete.',allow_interactive=True)
    f=packet/'ready.json';q=json.loads(f.read_text());q['ROM']=str(d);f.write_text(json.dumps(q,indent=2)+'\n')
    (O/'delivery.json').write_text(json.dumps(dict(installed=True,ROM_sha256=PIN,destination=str(d),backup_created=False,before=before,after=after,downloads_launch_verified=False,candidate_full11=result),indent=2)+'\n')
if __name__=='__main__':main()
