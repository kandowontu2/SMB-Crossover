"""Preserve passing menu evidence and the failing native gameplay reproduction."""
from pathlib import Path
import json,zipfile
import prepare_metal_storm_menu_1101_v15 as P
def main():
    s=json.loads((P.O/'menu-assembly.json').read_text());cpu=json.loads((P.O/'menu-CPU.json').read_text())
    n=P.O/'native-smoke';result=json.loads((n/'capture/result.json').read_text());binding=json.loads((n/'capture/binding.json').read_text())
    assert cpu['passed'] and cpu['ROM_sha256']==s['ROM_sha256']==binding['ROM_sha256']
    assert not result['passed'] and result['selected']==35 and result['world_x']==0 and binding['exit_code']==1
    d=P.R/'docs/qa/checkpoints/2026-11-01/metal-storm-menu-v15';d.mkdir(exist_ok=True)
    files=[P.O/x for x in ['menu.s','menu.cfg','menu.lbl','menu-assembly.json','menu-CPU.json']]
    files += [n/'controller.lua',n/'ready.json',n/'capture/result.json',n/'capture/binding.json',n/'capture/walking.png',n/'capture/selected.png']
    packet=d/'source-and-native-failure.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,f.relative_to(P.R).as_posix())
    q=dict(complete=False,installed=False,menu_CPU_passed=True,native_gameplay_passed=False,ROM_sha256=s['ROM_sha256'],
        packet_sha256=P.sha(packet),packet_bytes=packet.stat().st_size,menu_CPU=cpu,native=result,
        finding='Controller-only cold selection and Start reach gameplay with raw35, but no visible player and worldX stays0 after36 right+B frames. Native smoke exits1. Do not publish this candidate.',
        next='Trace real cold scene load, authenticated cache headers, constructor timing, movement and draw dispatch. Existing component fixtures began with initialized native coordinates and do not prove real spawn behavior.')
    (d/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    grant=dict(grant=True,owner='Metal Storm menu resolve/retirement and Start flags',baseline_ROM_sha256=s['base_ROM_sha256'],
        physical_PRG_bank=29,physical_offsets_half_open=s['allocation']['ranges'],
        evidence='Pinned megaman_physics.s explicit .res $72/$1f around B400 37-row veneers; native MarioWaterCoast ProductHi relocated to BB8E and all256 table bytes checked.',
        conditions=['Keep B400..B46F veneers and relocated256-byte water table byte-exact.','Keep public KrStartFlags address; maintain fixed-size source wrapper and assertions.','This is allocation only, not native gameplay approval.'])
    (d/'allocation.json').write_text(json.dumps(grant,indent=2)+'\n')
    path=P.R/'docs/qa/continuation-current.json';c=json.loads(path.read_text())
    c['previous_goal_turn_classification']='progress'
    c['metal_storm_menu_followup']=dict(checkpoint=str(d.relative_to(P.R)),candidate=str(P.O/'candidate.nes'),installed=False,native_gameplay_passed=False,next=q['next'])
    c['current_priority']='Fix Metal Storm native spawn failure: selected35 starts but invisible/worldX0. CPU menu/Start/retirement pass; candidate9af4 must not be delivered. Public7ec9 unchanged. Remaining roster/health/combat/audio/full-stage work incomplete.'
    path.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
