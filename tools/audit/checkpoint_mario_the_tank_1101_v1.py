"""Keep a compact reproducible WIP receipt without ROM or debug copies."""
from pathlib import Path
import json,zipfile
from deliver_mario_the_tank_1101_v1 import R,O,DEST,PIN,BASE,sha
from nightly_patch_guard_v1 import check
def main():
    assert check(DEST)['ROM_sha256']==PIN
    run=O/'downloads-smoke'
    assert json.loads((run/'capture/result.json').read_text())['passed']
    b=json.loads((run/'capture/binding.json').read_text())
    assert b['exit_code']==0 and b['ROM_sha256']==PIN
    d=R/'docs/qa/checkpoints/2026-11-01/mario-the-tank-nightly-v1';d.mkdir(parents=True,exist_ok=True)
    files=set()
    for folder in [R/'tools/audit',R/'tools/reference']:
        for pattern in ['*mario_tank*1101_v5*','*mario_the_tank*1101_v1*','mario_tank_shared_gates_1101_v3.inc','mario_tank_loader_1101_v4.inc']:
            files.update(folder.glob(pattern))
    for pattern in ['*.json','*.s','*.cfg','*.lbl']:
        files.update(p for p in O.glob(pattern) if p.name!='candidate.lbl')
    for n in ['native-final-smoke','native-powered-final','downloads-smoke']:
        p=O/n
        files.update([p/'controller.lua',p/'ready.json',p/'capture/result.json',p/'capture/binding.json'])
    files.update((R/'docs/qa/checkpoints/2026-11-01').glob('mario-tank-*-grant.json'))
    packet=d/'source-and-proof.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    assert packet.stat().st_size<2_000_000
    receipt=dict(passed=True,installed=True,complete=False,backup_created=False,ROM_sha256=PIN,
        replaced_sha256=BASE,destination=str(DEST),checkpoint=str(d.relative_to(R)),
        source_packet_sha256=sha(packet),source_packet_bytes=packet.stat().st_size,
        build_method='Source-assembled fragments and exact fixed-size host substitutions; not a full repository relink.',
        character='Mario the Tank',selection='Mario slot, Select seven times, Start',
        allocation='All 18 ROM regions granted; conditional RAM grant checked.',
        verification=['Native cold menu, entry and movement on candidate and actual Downloads path.',
          'Powered boots native fixture; explicitly writes PlayerStatus=2 and PlayerSize=0.',
          'CPU menu, rendering, loader faults and actual Main interrupt-return checks.'],
        limits=['Full 1-1 and natural powerup progression not yet verified.',
          'Metal Storm, Shinobi and full roster qualification remain incomplete.'])
    (d/'handoff.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (d/'README.md').write_text('Mario the Tank WIP nightly\n\nSelect Mario, press Select seven times, then Start. Uses the source game movement and powered boots; native fireballs remain at full power.\n\nCold menu and movement passed on the actual Downloads ROM. Powered graphics passed an explicit status fixture, not natural pickup progression. Full-stage qualification remains outstanding. This source-fragment integration preserves the preceding Karnov and Kirby repairs.\n')
    p=R/'docs/qa/continuation-current.json';q=json.loads(p.read_text())
    q['installed_nightly']=receipt
    q['current_owning_candidate']=str(O/'candidate.nes')
    q['current_owning_build_recipe']='tools/audit/prepare_mario_tank_candidate_1101_v5.py'
    q['current_priority']='Mario the Tank WIP delivered and actual Downloads cold selection/Start/walking passed. Continue natural powerup and full-stage testing, Metal Storm and Shinobi integration. Preserve current Kirby/Karnov repairs. Full goal incomplete.'
    q['november_1_allocation_followup']['remaining_Tank_banks']=[]
    q['november_1_allocation_followup']['Tank_followup']='All18 ROM grants checked. PowerUpType+5 renderer fix tested. Native smoke and powered fixture passed; natural progression outstanding.'
    q['november_1_allocation_followup']['scope']='Supersedes older allocation and worker interruption notes for Mario the Tank; now delivered as WIP.'
    q['source_override_required']='Compose the current58 Karnov/Kirby baseline with prepare_mario_tank_visible_1101_v5.py, prepare_mario_tank_graft_1101_v5.py and prepare_mario_tank_candidate_1101_v5.py. All formal grants/preimages must pass. Do not replace with an older kernel.'
    p.write_text(json.dumps(q,indent=2)+'\n')
    (O/'source-stage.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
if __name__=='__main__':main()
