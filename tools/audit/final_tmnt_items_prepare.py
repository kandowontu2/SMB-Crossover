"""Prepare eight source-only, exact-ROM turtle physical-item lifecycle profiles.

This tool never launches Mesen. Generated scripts remain unqualified until a
native worker is granted and the scripts actually finish on their bound ROM.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load

ROOT = Path(__file__).resolve().parents[2]
TARGET = '52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
NAMES = ['Leonardo', 'Raphael', 'Michelangelo', 'Donatello']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def lua(value):
    # Python bool subclasses int; emit Lua literals before numeric fallback.
    if isinstance(value,bool):return 'true' if value else 'false'
    if isinstance(value,str):return json.dumps(value)
    if isinstance(value,list):return '{'+','.join(lua(x) for x in value)+'}'
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in value.items())+'}'
    if value is None:return 'nil'
    assert isinstance(value,(int,float)),type(value)
    return str(value)


def plan():
    steps = []
    def add(action, name, **values):
        steps.append(dict(action=action, name=name, **values))
    add('block', 'mushroom-full-health-cap', type=0, hp=128, food=1)
    add('block', 'full-health-flower-kiai-frozen-after-real-injury', type=1,
        gear=4, hp=112, food=1, injure_after_rise=True)
    add('use', 'kiai-real-hit-cleanup', gear=4, projectiles=1)
    add('block', 'hurt-flower64-cap128', type=1, hp=128, food=0)
    add('damage', 'three-actual-contacts-to80', contacts=3, hp=80)
    add('block', 'mushroom32-restores80-to112', type=0, hp=112, food=1)
    add('damage', 'four-actual-contacts-to48', contacts=4, hp=48)
    add('block', 'hurt-flower64-restores48-to112', type=1, hp=112, food=0)
    add('block', 'mushroom32-cap112-to128', type=0, hp=128, food=1)
    for i in range(5):
        add('block', f'kiai-same-kind-refill-{i+1}', type=1, gear=4, hp=128, food=1)
    for gear in [1, 2, 3]:
        add('drop', f'gear{gear}-native25-defeats-replacement', gear=gear)
        add('use', f'gear{gear}-real-hit-cleanup', gear=gear, projectiles=3 if gear==2 else 1)
        for i in range(5):
            add('drop', f'gear{gear}-native25-defeats-same-kind-refill-{i+1}', gear=gear)
    add('drop', 'boomerang-refill-actor-earned-before-three-throws', gear=3, hold=True)
    add('boom_overcap', 'physical99-refill-with-three-live-returning-boomerangs', gear=3)
    assert len(steps) == 37
    return steps


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expected-sha256', default=TARGET)
    p.add_argument('--source', type=Path, default=ROOT/'src')
    a = p.parse_args()
    assert sha(a.rom) == a.expected_sha256
    a.output.mkdir(parents=True, exist_ok=False)
    frozen = a.output/'frozen-current'
    frozen.mkdir()
    shutil.copytree(a.source, frozen/'src')
    ledger = {str(f.relative_to(frozen)).replace('\\', '/'):sha(f)
              for f in sorted((frozen/'src').rglob('*')) if f.is_file()}
    (frozen/'source-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
    for ext in ['.nes', '.dbg', '.lbl', '.map']:
        shutil.copy2(a.rom.with_suffix(ext), frozen/('candidate'+ext))
    b = scoped_load(frozen/'candidate.nes')
    fixture = ROOT/'tools/audit/final_tmnt_items_native.lua'
    shutil.copy2(fixture, frozen/fixture.name)
    shutil.copy2(Path(__file__), frozen/Path(__file__).name)
    names = ['GameLoop', 'NonMaskableInterrupt', 'IrqScrollSplit', 'RosterOamReady',
             'TnPreparePickupDispatch', 'TnRisePickupDispatch', 'TnCollectEquipment',
             'TnHeal', 'TnGiveEquipment', 'TnInjuryStart', 'TnWeaponPosition',
             'TnEnemyDropDispatch', 'TnTrySecondary', 'TnRestoreBoomerang',
             'TnDropOverlap', 'ShellOrBlockDefeat']
    names += ['PlayerEnemyCollision','EColl','HandlePECollisions','GuestBodyContactBridge',
              'InjurePlayer','ForceInjury','TnInjuryStatus']
    hooks = {n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,
                     bytes=list(b['raw'][location(b,n):location(b,n)+3])) for n in names}
    for key, name in [('finish','GameLoop'), ('NmiReturn','NonMaskableInterrupt')]:
        delta = int(b['syms'][name]['size'],0)-1
        pos = location(b,name)+delta
        assert b['raw'][pos] in [0x60,0x40]
        hooks[key] = dict(address=address(b,name)+delta,physical_bank=(pos-16)//8192,
                          bytes=[b['raw'][pos]])
    pos,size = location(b,'IrqScrollSplit'),int(b['syms']['IrqScrollSplit']['size'],0)
    irq = [address(b,'IrqScrollSplit')+i for i in range(size-2)
           if b['raw'][pos+i:pos+i+3] == b'\x8d\x05\x20']
    assert irq
    used = set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",fixture.read_text()))
    common = dict(hooks=hooks,irq_scroll_stores=irq,plan=plan(),ROM_sha256=a.expected_sha256,
                  ram={n:address(b,n) for n in used if n in b['syms']},
                  powerup_sfx=address(b,'Sfx_PowerUpGrab'),
                  art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)
                       for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},
                  smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC',
                    'SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    direct = set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",fixture.read_text()))
    assert not direct-set(common['ram']),direct-set(common['ram'])
    profiles = []
    for variant,name in enumerate(NAMES):
        for hard in [False,True]:
            mode = 'hard' if hard else 'easy'
            folder = a.output/f'{name.lower()}-{mode}-prepared-v1'
            folder.mkdir()
            config = dict(common,variant=variant,name=name,hard=hard,mode_value=int(hard))
            script = folder/'run.lua'
            rendered=lua(config)
            assert '["hard"]='+('true' if hard else 'false') in rendered
            assert '["injure_after_rise"]=true' in rendered and '["hold"]=true' in rendered
            script.write_text('FINAL_TMNT_ITEMS='+rendered+'\n'+fixture.read_text(),encoding='utf-8')
            (folder/'config.json').write_text(json.dumps(config,indent=2)+'\n')
            profiles.append(dict(identity=name,variant=variant,mode=mode,
                                 script=str(script),script_sha256=sha(script),steps=len(config['plan']),
                                 native_status='prepared_not_run',passed=False))
    manifest = dict(ROM_sha256=a.expected_sha256,status='prepared_not_native_run',
                    native_passed=False,goal_complete=False,profiles=profiles,
                    expected_per_profile=dict(physical_collections=30,food_collections=5,
                        gear_collections=25,drop_actor_generations=19,eligible_native_defeats=475,
                        actual_injuries=8,source_plan_steps=37),
                    fixture_sha256=sha(fixture),preparer_sha256=sha(Path(__file__)),
                    source_ledger_sha256=sha(frozen/'source-ledger.json'),
                    forbidden_fixture_writes=['TnHealth','TnFood','TnEquipment','TnAmmo',
                        'TnGearSelected','TnDropCounter','TnDropKind','TnDropReceipt','PseudoRandomBitReg',
                        'PlayerStatus','TnVariant','SelectedCharacter','PowerUpType','InvPickup'],
                    scope='Eight cold-selection plans; actual head/reveal/rise, disclosed post-rise contact placement, actual source injuries and eligible defeats, native PRNG timing gate rather than RNG/counter writes. Source/CPU preparation only; script timing and expectations require native validation.')
    (a.output/'preparation.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(status=manifest['status'],profiles=8,ROM_sha256=a.expected_sha256,
                          preparation_sha256=sha(a.output/'preparation.json'))))


if __name__ == '__main__':
    main()
