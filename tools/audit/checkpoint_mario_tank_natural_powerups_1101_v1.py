"""Persist bounded natural powerup verification; keep full roster work open."""
from pathlib import Path
import json,zipfile
from prepare_selected_native_packet_v1 import sha
R=Path(__file__).resolve().parents[2]
def main():
    p=R/'build/mario-tank-pickup-1101-v1/natural-powerups'
    result=json.loads((p/'capture/result.json').read_text())
    binding=json.loads((p/'capture/binding.json').read_text())
    ready=json.loads((p/'ready.json').read_text())
    assert result['passed'] and result['natural_boot_collected'] and result['natural_mushroom_collected']
    assert result['controller_only'] and not result['lost_life']
    assert binding['exit_code']==0 and binding['ready_sha256']==sha(p/'ready.json')
    for f,h in ready['bindings'].items():assert sha(Path(f))==h,f
    d=R/'docs/qa/checkpoints/2026-11-01/mario-the-tank-natural-powerups';d.mkdir(exist_ok=True)
    packet=d/'native-proof.zip'
    files=[p/'controller.lua',p/'ready.json',p/'capture/result.json',p/'capture/binding.json',
           p/'capture/route-1430.png',p/'capture/route-1438.png']
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,f.relative_to(p).as_posix())
    assert packet.stat().st_size<100_000
    q=dict(passed=True,complete=False,ROM_sha256=binding['ROM_sha256'],
           verification={k:v for k,v in result.items() if k!='trace'},
           packet_sha256=sha(packet),packet_bytes=packet.stat().st_size,
           scope='Natural first mushroom release, pickup and growth; second block releases visible boot, player jumps onto it and reaches status2. No emulated RAM writes or lost life. Two powered screenshots inspected.',
           limitations='No full-stage clear. Boot combat, terrain destruction and flashing cadence still need native gameplay coverage; screenshots alone do not prove cadence.',
           route_findings='Earlier replay failed to release A between some jumps and launched too early at the second pit. Corrected controller route clears that pit; these are route changes, not ROM fixes.')
    (d/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    path=R/'docs/qa/continuation-current.json';c=json.loads(path.read_text())
    c['previous_goal_turn_classification']='progress'
    c['mario_the_tank_natural_powerups']=str((d/'receipt.json').relative_to(R))
    c['current_priority']='Mario the Tank natural mushroom and boot release/pickup verified on delivered7ec9, no lost life. Full-stage/boot combat/terrain tests remain. Continue Metal Storm and Shinobi integration and full-roster qualification.'
    path.write_text(json.dumps(c,indent=2)+'\n')
    print(json.dumps(q))
if __name__=='__main__':main()
