"""Prepare one source-backed right-side flower controller; never launch Mesen."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, load, location
from observe_chip_committed_write import lua
from mario_powerups_current3cee_static_v2 import runtime, symbols

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA = '900b669e212b878041c23e438f2fb26e310ce8f929f904681a9c4b17405b6968'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, z):
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')



def controller_controls(folder, module, bundle, rom, output):
    lua_root=D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    sys.path.insert(0,str(lua_root))
    from lupa.lua54 import LuaRuntime
    labels,banks=symbols(bundle,rom)
    cfg=json.loads((folder/'configuration.json').read_text());labels.update(cfg['item']['ram'])
    context='function context()\n'+(folder/'harness.lua').read_text().split('local function context()\n',1)[1].split('\nlocal selectionDone=',1)[0]
    def fresh():
        rt=runtime(LuaRuntime,labels,banks)
        rt.execute('ROSTER_CONFIG='+lua(cfg['roster'])+';MARIO_FLOWER_CONFIG='+lua(cfg['item']))
        rt.execute(module.read_text())
        rt.execute('cfg='+lua(cfg['roster'])+'''
frame=0;poll=0;lastMask=0;stageFrame=0
function r(n,i)return mem[assert(L[n],n)+(i or 0)]or 0 end
function position(lo,hi)return r(lo)+256*r(hi)end
function block()return 0 end
''')
        rt.execute(context)
        rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
        return rt
    def state(rt,*,x=1290,y=176,vx=0,grounded=True,lastA=False,mature=True,enemies=(),flower_slot=5):
        m=rt.globals().mem
        for name,v in dict(Player_X_Position=x%256,Player_PageLoc=x//256,Player_Y_Position=y,
                           Player_Y_HighPos=1,Player_State=0 if grounded else 1,Player_X_Speed=vx).items():m[labels[name]]=v
        rt.globals().lastMask=128 if lastA else 0
        for i in range(6):m[labels['Enemy_Flag']+i]=0
        actors=[dict(slot=flower_slot,id=0x2e,x=1248,y=119,state=128 if mature else 127)]+list(enemies)
        for actor in actors:
            z=dict(slot=0,id=6,flag=1,x=1236,y=120,state=0,high=1)|actor
            for name,v in dict(Enemy_Flag=z['flag'],Enemy_ID=z['id'],Enemy_State=z['state'],
                               Enemy_X_Position=z['x']%256,Enemy_PageLoc=z['x']//256,
                               Enemy_Y_Position=z['y'],Enemy_Y_HighPos=z['high'],PowerUpType=1).items():m[labels[name]+z['slot']]=v
    calls=[]
    def step(rt,name):
        before=rt.eval('#callbacks');buttons=dict(rt.globals().MARIO_FLOWER_RIGHT_CONTROL(rt.globals().context()).items())
        assert all(k in ['a','b','left','right']and type(v)is bool for k,v in buttons.items())
        assert not(buttons.get('left')and buttons.get('right'))and rt.eval('#callbacks')==before
        calls.append(dict(name=name,buttons=buttons));return buttons
    for slot in range(6):
        rt=fresh();state(rt,enemies=[dict(slot=slot,x=1236)],flower_slot=4 if slot==5 else 5)
        assert step(rt,'neutral-source-coast-slot'+str(slot))=={}
        assert step(rt,'actual-clear-live-slot'+str(slot))==dict(a=True,left=True,b=True)
    for name,e in [('inactive',dict(flag=0)),('duplicate',dict(flag=128)),('defeated',dict(state=32)),
                   ('stomped',dict(state=2)),('far-future',dict(x=1600,y=184)),
                   ('other-Y-page',dict(high=2)),('above-corridor',dict(y=20)),
                   ('far-left',dict(x=1198,y=184))]:
        rt=fresh();state(rt,enemies=[dict(x=1250)|e])
        assert step(rt,'ignored-'+name+'-settle')=={}
        assert step(rt,'ignored-'+name+'-launch')==dict(a=True,left=True,b=True)
    for x,vx,ground,expected in [(1249,0,False,dict(right=True,b=True)),
            (1287,0,True,dict(right=True)),(1293,0,True,dict(left=True)),
            (1290,255,True,dict(right=True)),(1290,1,True,dict(left=True))]:
        rt=fresh();state(rt,x=x,vx=vx,grounded=ground)
        assert step(rt,'alignment-'+str(len(calls)))==expected
    rt=fresh();state(rt,mature=False)
    assert step(rt,'physical-flower-still-rising')=={}and step(rt,'no-premature-flower-launch')=={}
    state(rt,mature=True,lastA=True);assert step(rt,'requires-fresh-A')=={}
    state(rt);assert step(rt,'mature-and-fresh')==dict(a=True,left=True,b=True)
    rt=fresh();state(rt,enemies=[dict(x=1285,y=170,state=1)])
    assert step(rt,'actual-body-behind-retreat')==dict(right=True,b=True)
    state(rt,x=1314,enemies=[dict(x=1236)])
    assert step(rt,'bounded-retreat-return')==dict(left=True)
    state(rt,enemies=[dict(x=1236)]);assert step(rt,'return-neutral')=={}
    assert step(rt,'return-live-clear-launch')==dict(a=True,left=True,b=True)
    rt=fresh();state(rt,enemies=[dict(x=1250)])
    for _ in range(360):assert rt.globals().MARIO_FLOWER_RIGHT_CONTROL(rt.globals().context())['a']is None
    try:rt.globals().MARIO_FLOWER_RIGHT_CONTROL(rt.globals().context())
    except Exception as e:assert 'Bounded right-side' in str(e)
    else:raise AssertionError('Relevant blocked gate did not reach its finite bound')
    rt=fresh();state(rt);step(rt,'arc-neutral');assert step(rt,'arc-first-input')==dict(a=True,left=True,b=True)
    for n in range(1,33):
        state(rt,x=1280,y=112,grounded=False)
        b=step(rt,'guided-arc-'+str(n));assert b['a']==(n<32)and b['left']and b['b']
    state(rt,x=1250,y=112);step(rt,'actual-row-ground-not-failed')
    rejected=[]
    for defect in ['slot','coordinate','flag']:
        rt=fresh();state(rt,enemies=[dict(x=1236)])
        rt.execute('testContext=context();local saved=testContext.enemy;testContext.enemy=function()local e=saved();'+
                   dict(slot='e.slot=6',coordinate='e.x=e.x+1',flag='mem[L.Enemy_Flag+e.slot]=128')[defect]+';return e end')
        try:rt.globals().MARIO_FLOWER_RIGHT_CONTROL(rt.globals().testContext)
        except Exception as e:assert 'nearest-enemy' in str(e);rejected.append('invalid-nearest-'+defect)
        else:raise AssertionError('Invalid nearest owner admitted')
    for kind in ['ahead-body','unsafe-ground-landing']:
        rt=fresh();state(rt)
        if kind=='ahead-body':state(rt,enemies=[dict(x=1291,y=170)])
        else:
            step(rt,'negative-arc-settle');step(rt,'negative-arc-launch')
            for n in range(3):state(rt,x=1280,y=112,grounded=False);step(rt,'negative-arc-air-'+str(n))
            state(rt,x=1200,y=176)
        try:rt.globals().MARIO_FLOWER_RIGHT_CONTROL(rt.globals().context())
        except Exception as e:
            assert 'body threat ahead' in str(e)or 'mount fell short' in str(e);rejected.append(kind)
        else:raise AssertionError('Unsafe controller state admitted: '+kind)
    output.mkdir()
    put(output/'proof.json',dict(passed=True,native_executed=False,cases=calls,return_cases=len(calls),
        blocked_live_gate_bound=360,unrelated_future_enemy_does_not_hold_gate=True,
        unsafe_controls_rejected=rejected,all6live_slots_exercised=True,arc_A_updates=32,
        actual_harness_context_sha256=hashlib.sha256(context.encode()).hexdigest(),
        scope='Actual right helper/exact c.enemy Lua under synthetic legal RAM only, no native motion/collision/flower outcome'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    source = D / 'current3cee-postdma-mask-v1/canonical-v2'
    rom = source / 'candidate.nes'
    assert sha(rom) == SHA
    b = load(rom)
    parent = D / 'mario-powerups900-first-v2/mario-easy'
    assert json.loads((parent / 'native-receipt.json').read_text())['passed']
    original = D / 'current3cee-remaining27-routes-v1/native/mario-easy'
    env_path = D / 'parodius-menu3cee-ready-v1/environment.json'
    env = json.loads(env_path.read_text())
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:
        assert sha(env[n]) == env[n + '_sha256'], n
    folder = out / 'mario-easy'
    folder.mkdir()
    (folder / 'frames').mkdir()
    prior = D / 'mario-flower900-first-v1'
    failed = prior / 'failure-freeze-v1/proof.json'
    assert sha(failed) == '592ec9170302df31584ed0f00d66d6a704bda913de830477f5b86159a23aba57'
    failure = json.loads(failed.read_text())
    assert failure['native_passed'] is False and failure['native_worker_released']
    assert all(sha(k) == v for k, v in failure['bindings'].items())
    second = D / 'mario-flower900-corrected-v2/failure-freeze-v1/proof.json'
    assert sha(second) == '5adad47072a91fcca3133b0bb38e4c3eadc72e175ac2e57759de6b35757bd67a'
    second_failure = json.loads(second.read_text())
    assert second_failure['native_passed'] is False and second_failure['native_worker_released']
    assert all(sha(k) == v for k, v in second_failure['bindings'].items())
    model = D / 'mario-flower900-corrected-v2/right-approach-source-v1'
    assert sha(model / 'receipt.json') == '261085e9e910f24295ecffa60f0b37f5a50a6a95faebdae273629085afb2387c'
    model_receipt = json.loads((model / 'receipt.json').read_text())
    assert all(sha(k) == v for k, v in model_receipt['bindings'].items())
    module = ROOT / 'tools/audit/mario_flower900_native_v3.lua'
    text = module.read_text()
    previous_module = ROOT / 'tools/audit/mario_flower900_native_v1.lua'
    old = previous_module.read_text()
    helper = text.split('-- Right-side controller only. Both earlier failed native attempts stay frozen.', 1)[1].split('function MARIO_FLOWER_CONTROL(c,base)', 1)[0]
    stripped = text.replace('-- Right-side controller only. Both earlier failed native attempts stay frozen.' + helper, '', 1)
    new_branch = "   return MARIO_FLOWER_RIGHT_CONTROL(c)"
    old_branch = """   if mount=='back'then
    if c.grounded and c.x>=1204 and c.x<=1212 and c.vx==0 then mount='rise';age=0;return{a=true}end
    return aim(c,1208)
   elseif mount=='rise'then
    if c.y<=108 then mount='onto'end
    return{a=age<32}
   else
    if c.grounded and c.y>128 then mount='back';age=0;return{}end
    local b=aim(c,1248);b.a=age<32;b.b=true;return b
   end"""
    assert stripped.replace(new_branch, old_branch, 1) == old, 'Only the demonstrated controller branch may change'
    (out / 'observer-controller-only.diff').write_text(''.join(difflib.unified_diff(
        old.splitlines(keepends=True), text.splitlines(keepends=True),
        fromfile=previous_module.name, tofile=module.name)), encoding='utf-8', newline='\n')
    v2 = ROOT / 'tools/audit/mario_flower900_native_v2.lua'
    (out / 'observer-v2-to-v3.diff').write_text(''.join(difflib.unified_diff(
        v2.read_text().splitlines(keepends=True), text.splitlines(keepends=True),
        fromfile=v2.name, tofile=module.name)), encoding='utf-8', newline='\n')
    hooks = {n: dict(address=address(b, n), bank=(location(b, n) - 16) // 8192,
                     bytes=list(b['raw'][location(b, n):location(b, n) + 3]))
             for n in ['PwrUpJmp', 'MarioSourcePowerupCollision', 'MarioSourcePowerupUpdate',
                       'MarioSourceFireballBrick', 'HandleEnemyFBallCol']}
    used = set(re.findall(r"\br\('([A-Za-z_][A-Za-z_0-9]*)'", text))
    used |= {'Square2SoundQueue', 'Square1SoundQueue', 'Fireball_State'}
    cfg = dict(json.loads((parent / 'configuration.json').read_text())['roster'])
    cfg.update(out=folder.as_posix() + '/', policy=(folder / 'policy.lua').as_posix(),
               audit=(folder / 'audit.lua').as_posix(), limit=6500, capture=8)
    c = dict(character=0, variant=0, mode=0, ROM_sha256=SHA, blocks=[336, 1248],
             hooks=hooks, ram={n: address(b, n) for n in used},
             sfx={k: address(b, v) for k, v in [('reveal', 'Sfx_GrowPowerUp'),
                    ('pickup', 'Sfx_PowerUpGrab'), ('fire', 'Sfx_Fireball')]})
    put(folder / 'configuration.json', dict(roster=cfg, item=c))
    body = (original / 'policy.lua').read_text().split('\n', 1)[1]
    guard = original.parent / 'native-guard.lua'
    policy = ('dofile(' + lua(guard.as_posix()) + ')\nlocal base=(function()\n' + body +
              '\nend)()\nreturn function(c)return MARIO_FLOWER_CONTROL(c,base)end\n')
    (folder / 'policy.lua').write_text(policy, encoding='utf-8', newline='\n')
    harness = (parent / 'harness.lua').read_text().replace('MARIO_POWERUP_FINISH', 'MARIO_FLOWER_FINISH').replace('MARIO_POWERUP_DONE', 'MARIO_FLOWER_DONE')
    (folder / 'harness.lua').write_text(harness, encoding='utf-8', newline='\n')
    shutil.copyfile(parent / 'audit.lua', folder / 'audit.lua')
    script = ('ROSTER_CONFIG=' + lua(cfg) + '\nMARIO_FLOWER_CONFIG=' + lua(c) +
              '\ndofile(' + lua(module.as_posix()) + ')\ndofile(' +
              lua((folder / 'harness.lua').as_posix()) + ')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n')
    (folder / 'run.lua').write_text(script, encoding='utf-8', newline='\n')
    all_text = text + policy + harness + (folder / 'audit.lua').read_text() + script
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', all_text)
    report = ROOT / 'docs/qa/mario-flower900-right-preparation-2026-10-26.txt'
    assert report.is_file()
    hard_report = ROOT / 'docs/qa/mario-luigi900-hard-pickup-paths-2026-10-26.txt'
    assert hard_report.is_file()
    controls = [
        [sys.executable, '-B', str(ROOT / 'tools/audit/mario_flower900_source_v1.py'),
         '--rom', str(rom), '--output', str(out / 'source-controls-v1')],
        [sys.executable, '-B', str(ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py'),
         '--fixture', str(folder), '--rom', str(rom),
         '--lua-root', str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'),
         '--output', str(out / 'startup-static-v1')]]
    for i, command in enumerate(controls):
        z = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (out / ('control-' + str(i) + '.log')).write_text(z.stdout + z.stderr, encoding='utf-8')
        assert z.returncode == 0, z.stderr
    controller_controls(folder, module, b, rom, out / 'controller-source-controls-v1')
    source_manifest = json.loads((source / 'source-manifest.json').read_text())
    deps = {rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'), source / 'proof.json',
            source / 'source-manifest.json', Path(__file__), module, report, hard_report, env_path, guard,
            previous_module, failed, prior / 'failure-freeze-v1/review-receipt.json',
            second, model / 'receipt.json', v2,
            ROOT / 'tools/audit/mario_flower900_source_v1.py',
            ROOT / 'tools/audit/mario_flower900_run_v1.py',
            ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py',
            ROOT / 'tools/audit/parodius_visibility_hud_static_startup_v1.py',
            ROOT / 'tools/audit/robots_weapon_cpu_v1.py', ROOT / 'tools/audit/verify_native_relocation.py',
            ROOT / 'tools/audit/check_tmnt_render_oa.py', ROOT / 'tools/audit/observe_chip_committed_write.py',
            ROOT / 'tools/audit/run_mesen_isolated.py', ROOT / 'tools/run_mesen.py'}
    for rel, h in source_manifest.items():
        f = source / 'source' / rel
        assert sha(f) == h
        deps.add(f)
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:
        deps.add(Path(env[n]))
    deps |= {parent / n for n in ['native-receipt.json', 'configuration.json', 'harness.lua', 'audit.lua']}
    deps |= {original / n for n in ['policy.lua', 'manifest.json', 'trace.csv']}
    deps |= {f for f in out.rglob('*') if f.is_file()}
    deps |= {Path(path) for path in failure['bindings']}
    deps |= {Path(path) for path in second_failure['bindings']}
    deps |= {Path(path) for path in model_receipt['bindings']}
    lua_deps = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    deps |= {f for f in lua_deps.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'),
               '--output', str(folder), '--emulator', env['emulator'], str(folder / 'run.lua'),
               str(rom), '--timeout', '180']
    command += ['--option=' + v for v in env['deterministic_command_overrides']]
    ready = dict(passed=True, status='PREPARE_DO_NOT_RUN', native_executed=False, native_grant=False,
                 native_workers=1, ROM_sha256=SHA, ordinary_route_parent_SHA256='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99',
                 profiles=[dict(name='mario-easy', mode=0, character=0, variant=0,
                    fixture=str(folder), limit_physical_frames=6500, command=command,
                    endpoint='Real mushroom then later flower while retainingSuper, two native transforms, actual B fireball enemy/brick contact and projectile cleanup')],
                 bindings={str(f): sha(f) for f in sorted(deps, key=str)}, environment=env,
                 no_emulated_state_RNG_resource_or_actor_writes=True,
                 real_second_block_source_coordinate=[1248, 144],
                 original_completed_loop_CHR_raster_mode_death_guards_retained=True,
                 source_CPU_Hard_mismatch_documentation_only=True,
                 original_failure_preserved_sha256=sha(failed),
                 exact_old_assertions_and_native_observer_guards_preserved=True,
                 corrected_failure_preserved_sha256=sha(second),
                 right_source_model_receipt_sha256=sha(model / 'receipt.json'),
                 only_controller_change='Right-side physical alignment/matureflower/live-owner gate/diagonal arc; bounded wait/retreat; no inferred slots or game writes',
                 limits='Controller itinerary is prepared, not native-proven. No flower/use pass, Hard/fullroute/allitems/waveform/entire5SMC-SP claim.')
    put(out / 'readiness.json', ready)
    put(out / 'command.json', dict(not_executed=True, explicit_new_ROOT_native_grant_required=True,
        command=[sys.executable, '-B', str(ROOT / 'tools/audit/mario_flower900_run_v1.py'), '--packet', str(out),
                 '--expected-readiness-sha256', sha(out / 'readiness.json'), '--native-grant']))
    print(json.dumps(dict(passed=True, native_executed=False, profiles=1,
                          bindings=len(ready['bindings']), readiness=str(out / 'readiness.json'),
                          readiness_sha256=sha(out / 'readiness.json')), indent=2))


if __name__ == '__main__':
    main()
