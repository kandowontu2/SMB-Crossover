"""Publish the tested immediate-suction successor, with no nightly backup."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from nightly_patch_guard_v1 import check
from build_storage_guard_v1 import preflight

R=Path(__file__).resolve().parents[2]
O=R/'build/kirby-approach-owner-1101-v3'
N=R/'build/kirby-approach-native-1101-v3'
D=R/'docs/qa/checkpoints/2026-11-01/kirby-approach-nightly-v3'
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='367266d2ec4e62fcefc15fffb3a05095a16060ad52f9d68348f213d94b31268c'
BASE='c864e46a8f333ab7a936c8d8f330944041a3eff12bc6dd4d9ba96892144ff3c7'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    storage=preflight(fresh=True)
    assert sha(O/'candidate.nes')==PIN
    assert check(DEST)['ROM_sha256']==BASE
    cpu=json.loads((O/'Main-CPU.json').read_text())
    assert cpu['passed'] and cpu['ROM_sha256']==PIN
    native=[]
    for name in ['fixed','stationary']:
        p=N/name/'capture/result.json';q=json.loads(p.read_text())
        assert q['passed'] and q['ROM_sha256']==PIN and len(q['cases'])==3
        assert all(c['injuries']==0 and c['captures']==1 for c in q['cases'])
        native.append(dict(name=name,sha256=sha(p),cases=3,updates=q['updates'],frames=q['wall']))
    assert json.loads((N/'baseline/capture/binding.json').read_text())['exit_code']==1
    D.mkdir(parents=True,exist_ok=False)
    files=[O/n for n in ['kirby.s','kirby_core.s','kirby_weapons.s','candidate.cfg','owner-link.json','rollback-witness.json','donor-inhale-witness.json','main-build.json','link.json','Main-CPU.json']]
    files += [R/'tools/audit'/n for n in ['prepare_kirby_approach_owner_1101_v3.py','check_kirby_approach_owner_1101_v3.py','audit_kirby_ordinary_inhale_1101_v3.py','prepare_kirby_approach_native_1101_v3.py','deliver_kirby_approach_1101_v3.py','nightly_patch_guard_v1.py']]
    files += [R/'build/kirby-ordinary-inhale-audit-1101-v3/ordinary-inhale-CPU.json']
    for name in ['baseline','fixed','stationary']:
        files += [p for p in (N/name).rglob('*') if p.is_file() and p.suffix in {'.json','.lua','.log','.csv','.png','.py'}]
    assert len(files)<100 and sum(p.stat().st_size for p in files)<4_000_000
    packet=D/'source-and-native.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    result=dict(passed=True,installed=True,backup_created=False,complete=False,
        ROM_sha256=PIN,output_sha256=PIN,replaced_sha256=BASE,destination=str(DEST),
        selectable_identities=86,total_menu_identities=90,
        checkpoint=D.relative_to(R).as_posix(),owning_candidate=str(O/'candidate.nes'),
        owning_build_recipe='tools/audit/prepare_kirby_approach_owner_1101_v3.py',
        source_packet=dict(path=str(packet.relative_to(R)),sha256=sha(packet),bytes=packet.stat().st_size),
        inherited_source_checkpoint='docs/qa/checkpoints/2026-11-01/kirby-owner-nightly-v2',
        native=native,CPU_passed=True,storage=storage,
        scope='Six bounded Hard native cases: held-direction and stationary inhale plus earned shell attacks; actual Main covers Easy/Hard/front/rear/friction and IRQ/NMI. Not full-stage/all-character qualification.')
    shutil.copyfile(O/'candidate.nes',DEST)
    assert check(DEST)['ROM_sha256']==PIN
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n')
    (D/'README.md').write_text('# Kirby immediate suction nightly\n\n'
        'The original eight-update delay controls the opening pose, not suction. '
        'Suction now starts immediately. Holding inhale applies the original gradual horizontal friction '
        'and retains facing, rather than accelerating through the target.\n\n'
        'The earlier ROM failed the held-direction native case. This exact successor passes six '
        'bounded emulator cases and actual Main/interrupt comparisons; rear contacts remain harmful. '
        'Screenshots were reviewed. Tests disclose flat terrain and NPC placement. '
        'Full stages, every character and every powerup remain incomplete.\n\n'
        'The packet contains changed source, exact build commands, donor evidence, CPU results, '
        'native controllers/results and the original negative. It references the preceding source '
        'checkpoint for unchanged dependencies; it does not duplicate the ROM or debug files.\n')
    p=R/'docs/qa/continuation-current.json';q=json.loads(p.read_text())
    q['installed_nightly']=result
    q['current_owning_candidate']=str(O/'candidate.nes')
    q['current_owning_build_recipe']=result['owning_build_recipe']
    q['current_priority']='Delivered367266 immediate Kirby suction/original friction. Continue Metal Storm/Tank owning integration and remaining roster; preserve both Kirby successor patches.'
    q['kirby_moving_inhale_followup']['status']='FIXED_FOCUSED_TESTS_PASSED'
    q['kirby_moving_inhale_followup']['fixed_nightly_delivered']=True
    q['source_override_required']='Compose current Kirby Core Movement/friction and Weapons Pull immediate-suction changes, plus inherited S2 body boundary/guard and shell repair. Older c864 or Karnov Main alone drops changes.'
    q['previous_goal_turn_classification']='progress'
    p.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':main()
