"""Independently replay earned upgrades using the actual Downloads launch."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check

O=R/'build/sunny-upgrades-downloads-1102-v4'
PIN='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'

def main():
    source=R/'build/sunny-upgrades-stairs-1102-v3/native'
    ready=json.loads((source/'ready.json').read_text())
    result=json.loads((source/'capture/result.json').read_text())
    binding=json.loads((source/'capture/binding.json').read_text())
    assert result['passed']and result['full_stage']and result['mushroom_seen']and result['flower_seen']
    assert result['fireball_frames']>0 and result['fireball_cues']>0 and result['initial_lives']==result['final_lives']==2
    assert binding['exit_code']==0 and binding['ready_sha256']==sha(source/'ready.json')
    for p,h in ready['bindings'].items():assert sha(p)==h,p
    downloads=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    guard=check(downloads);assert guard['passed']and sha(downloads)==PIN
    O.mkdir(exist_ok=True)
    packet=O/'native'
    prepare(packet,Path(ready['ROM']),(source/'controller.lua').read_text(),[Path(__file__),source/'ready.json',source/'capture/result.json',source/'capture/binding.json',downloads,*map(Path,ready['bindings'])],expected=PIN,timeout=240,allow_interactive=True,scope='Independent actual Downloads cold Hard1-1 replay with natural mushroom/flower, fireball/use/SFX request, no life loss and unchanged deadline/DMA/CHR/IRQ/stack guards. Identical controller and ROM bytes to successful candidate route. No ROM replacement or backup.')
    p=packet/'ready.json';q=json.loads(p.read_text());q['ROM']=str(downloads);p.write_text(json.dumps(q,indent=2)+'\n')
    (O/'patch-guard-before.json').write_text(json.dumps(guard,indent=2)+'\n')

if __name__=='__main__':main()
