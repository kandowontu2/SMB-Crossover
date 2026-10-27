"""One unlaunched ce635 MegaHard6 profile; change only the qualified identity."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import sys
from final_item_abilities_run import lua
from final_item_abilities_current731_prepare_v1 import protocol
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from mm_proto_weapon_boundary_prepare_v6 import component_cpu
from parodius_visibility_hud_static_startup_v1 import MOCK

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D / 'root-render-audio-palette-hud-union-v2'
PROTO = D / 'robot-color-rotation-combined-ready-v1'
OLD_MEGA = D / 'mm-proto-weapon-boundary0a-v1/mega-hard-ready-v2'
SHA = 'ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(B / 'candidate.nes') == SHA
    assert sha(PROTO / 'readiness.json') == '69dcccf56ce2d22a2862bc48a19cea703888f12a7623a74be91b674586f1d69e'
    assert json.loads((PROTO / 'launch-outcome-v1.json').read_text())['strict_profile_pass']
    bindings = json.loads((PROTO / 'bindings.json').read_text())
    for f, h in bindings.items():
        assert sha(f) == h, f
    b = scoped_load(B / 'candidate.nes')
    source = json.loads((B / 'source-manifest.json').read_text())
    assert len(source) == 871
    for rel, h in source.items():
        f = B / 'source' / rel
        assert sha(f) == h, rel
        bindings[str(f.resolve())] = h
    old = json.loads((PROTO / 'native/config.json').read_text())
    cfg = json.loads(json.dumps(old))
    assert old['identity']['owner'] == 1 and old['identity']['variant'] == 1
    cfg['identity']['variant'] = 0
    restore = json.loads(json.dumps(cfg))
    restore['identity']['variant'] = 1
    assert restore == old
    assert cfg['ROM_sha256'] == SHA and cfg['mode_value'] == 1 and cfg['hard']
    assert cfg['identity']['variant_ram'] == 'ProtoVariant'
    assert cfg['character'] == cfg['identity']['owner'] == address(b,'CHARACTER_MEGAMAN') == 1
    assert b['raw'][location(b,'X5MenuCharacters')+cfg['slot']] == 1
    assert cfg['identity']['ammo_indices'] == list(b['raw'][location(b,'InvAmmoIndex')+16:location(b,'InvAmmoIndex')+25])
    assert cfg['dma_protocol'] == protocol(b)
    original = (PROTO / 'native/run.lua').read_text()
    prefix = 'FINAL_ITEM_PROGRESSIVE=' + lua(old) + '\n'
    assert original.startswith(prefix)
    body = original[len(prefix):]
    script = 'FINAL_ITEM_PROGRESSIVE=' + lua(cfg) + '\n' + body
    assert script.split('\n',1)[1] == original.split('\n',1)[1]
    # This exact corrected diagnostic was already native-qualified on Proto.
    # Prove the sole executable-body difference from the old Mega0a profile;
    # do not falsely call the entire old and new observer byte-identical.
    om = json.loads((OLD_MEGA / 'native/config.json').read_text())
    oldmega = (OLD_MEGA / 'native/run.lua').read_text()
    oprefix = 'FINAL_ITEM_PROGRESSIVE=' + lua(om) + '\n'
    assert oldmega.startswith(oprefix)
    oldbody = oldmega[len(oprefix):]
    correction_old = "local f=emu.getState()['ppu.frameCount'];return entered and f>=dCfg.first_frame and f<=dCfg.last_frame"
    correction_new = "local f=emu.getState()['ppu.frameCount'];return f>=dCfg.first_frame and f<=dCfg.last_frame"
    assert oldbody.count(correction_old) == 1 and body.count(correction_new) == 1
    assert oldbody.replace(correction_old, correction_new, 1) == body
    for name in ['cases','charge','rush','primary','effect_records','drop_arrays','smc_fields','irq_scroll_stores','identity']:
        assert cfg[name] == om[name], name
    hook_checks = []
    for group in [cfg['hooks'],cfg['diagnostic']['hooks']]:
        for name,h in group.items():
            off = 16 + h['physical_bank']*8192 + h['address']%8192
            assert list(b['raw'][off:off+len(h['bytes'])]) == h['bytes'], name
            hook_checks.append(dict(name=name, **h))
    for name,v in cfg['ram'].items():
        assert address(b,name) == v,name
    rows = component_cpu(b)
    own = [x for x in rows if x['variant'] == 0]
    assert len(rows) == 24 and len(own) == 12
    put(a.output / 'fresh-assembled-controls.json', dict(passed=True,native_run=False,ROM_sha256=SHA,
        executed_source_calls_all_variants=rows,actual_variant0_control_rows=own,
        source_scope='Actual compiled button-hold/release, summon gate, direct bounce consumer, Balancer source-choice and selectable-cycle controls. Configured actors/resources; no actual controller/PPU/contact/acquisition credit.'))
    native = a.output / 'native'
    native.mkdir()
    put(native / 'config.json',cfg)
    (native / 'run.lua').write_text(script)
    direct = set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",script))
    assert not direct-set(cfg['ram'])
    sys.path.insert(0,str(D / 'final-tmnt-items-v1/lua-parser-deps-v1'))
    from luaparser import ast as last
    last.parse(script)
    sys.path.insert(0,str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    rt = LuaRuntime(unpack_returned_tuples=True)
    mock = MOCK + '\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Unexpected startup write")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'
    rt.execute(mock+script)
    n=rt.eval('#callbacks')
    assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
    rt.execute('emu.addMemoryCallback=function()error("Runtime host registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
    for frame in [1,2,3]:
        rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
    assert rt.eval('#callbacks')==n
    command=json.loads((PROTO / 'command.json').read_text())
    for i,value in enumerate(command):
        if i and command[i-1]=='--output':
            command[i]=str(native)
        elif Path(value).resolve()==(PROTO / 'native/run.lua').resolve():
            command[i]=str(native / 'run.lua')
    assert str(native / 'run.lua') in command and str(B / 'candidate.nes') in command
    put(a.output / 'command.json',command)
    put(a.output / 'exact-profile-delta.json',dict(prepared=True,native_run=False,
        vs_qualified_ce635_Proto=dict(only_config_delta={'identity.variant':[1,0]},entire_executable_Lua_body_byte_exact=True,
            actual_menu_selection='Same owner1/slot1; configuration requests compiled ProtoVariant0. Existing real Select/menu readback code retained; no raw variant/selection memory write.'),
        vs_qualified_0a_Mega=dict(ROM_hash=[om['ROM_sha256'],SHA],same_six_mechanic_case_definitions=True,
            source_actual_hook_and_code_alias_refresh='Already qualified combined Proto metadata, all actual opcode/RAM addresses rebound above.',
            only_executable_body_delta={'old':correction_old,'new':correction_new},
            diagnostic_only_context='Inherited earlier read-only pre-entry dFocus correction, ProtoVariant state binding and990..996 focus; no controller/seeds/mechanics/guards/staticcallback/cap/threshold changes.'),
        actual_hook_opcode_bindings=hook_checks,mode_numeric=1,variant=0,stock_and_charge_caps_unchanged=True,
        original_ce635_script_sha256=sha(PROTO / 'native/run.lua'),original_0a_Mega_script_sha256=sha(OLD_MEGA / 'native/run.lua'),
        new_script_sha256=sha(native / 'run.lua'),full_RAM_and_code_alias_metadata_exact=True,
        fresh24source_controls_and3frame_static_startup_mock=True))
    # The isolated executable/settings used by the already-qualified Proto
    # command are retained literally, not replaced with another portable copy.
    emulator=Path(command[command.index('--emulator')+1])
    environment=dict(emulator=str(emulator),emulator_sha256=sha(emulator),
        core=str(emulator.parent / 'MesenCore.dll'),core_sha256=sha(emulator.parent / 'MesenCore.dll'),
        worker_settings=str(emulator.parent / 'settings.json'),worker_settings_sha256=sha(emulator.parent / 'settings.json'),
        runtime_database=str(emulator.parent / 'MesenNesDB.txt'),runtime_database_sha256=sha(emulator.parent / 'MesenNesDB.txt'),
        Python=sys.version,script_emulated_wall_bound=4000,host_seconds=1200,
        effective_cli='doNotSaveSettings,8sprites,AllZeros RAM,fixedCPU/PPU and mapper startup')
    put(a.output / 'environment.json',environment)
    extras=[Path(__file__),Path(sys.executable),emulator,emulator.parent / 'MesenCore.dll',emulator.parent / 'settings.json',
        PROTO / 'readiness.json',PROTO / 'bindings.json',PROTO / 'ROOT-grant.json',PROTO / 'launch-binding-v1.json',PROTO / 'launch-outcome-v1.json',
        D / 'robot-color-rotation-native-review-v1/proof.json',OLD_MEGA / 'readiness.json',OLD_MEGA / 'native/config.json',OLD_MEGA / 'native/run.lua',
        B / 'candidate.nes',B / 'candidate.dbg',B / 'candidate.lbl',B / 'candidate.map',B / 'source-manifest.json',B / 'proof.json',
        emulator.parent / 'MesenNesDB.txt',*emulator.parent.glob('*.dll')]
    pending=[Path(__file__),R / 'tools/audit/mm_proto_cold_palette_diagnostic_run_v1.py']
    seen=set()
    while pending:
        f=pending.pop()
        if f in seen:continue
        seen.add(f);extras.append(f)
        for node in ast.walk(ast.parse(f.read_text())):
            names=[node.module]if isinstance(node,ast.ImportFrom)else[x.name for x in node.names]if isinstance(node,ast.Import)else[]
            for name in names:
                if name:
                    dep=R / 'tools/audit' / (name.split('.')[0]+'.py')
                    if dep.is_file():pending.append(dep)
    extras += list(a.output.rglob('*'))
    for f in extras:
        if f.is_file():bindings[str(f.resolve())]=sha(f)
    put(a.output / 'bindings.json',dict(sorted(bindings.items())))
    put(a.output / 'readiness.json',dict(prepared=True,native_run=False,native_granted=False,
        candidate_ROM_sha256=SHA,identity=dict(owner=1,slot=1,variant_ram='ProtoVariant',variant=0),mode_numeric=1,
        profile='MegaHard primary-support-passive six components',cases=[x['name']for x in cfg['cases']],
        source_files=871,source_manifest_sha256=sha(B / 'source-manifest.json'),maximum_native_launches=1,maximum_workers=1,
        wall_bound=4000,host_seconds=1200,no_retry=True,entire_qualified_ce635_controller_guard_body_byte_exact=True,
        only_Proto_config_delta='identity.variant1->0',oldMega_readonly_diagnostic_difference_explicit=True,
        exact_profile_delta_sha256=sha(a.output / 'exact-profile-delta.json'),fresh_assembled_controls_sha256=sha(a.output / 'fresh-assembled-controls.json'),
        environment_sha256=sha(a.output / 'environment.json'),command_sha256=sha(a.output / 'command.json'),script_sha256=sha(native / 'run.lua'),
        bindings=len(bindings),bindings_sha256=sha(a.output / 'bindings.json'),tool_sha256=sha(__file__),
        needed_native_checks=['Actual owner1/ProtoVariant0/Hard1 cold menu readback',
            'All six actual source-return outcomes, charge56/87, Rush12debit and stock3refusal, Balancer8credit',
            'Unchanged full256physicalDMA/CHR/IRQ/SMC/stack/input/strictdeadline guards',
            'Actual whole PPU/charged/Rush/HUD review with retained8sprite omission limits'],
        limits='Prepared only, one fresh ROOT grant required. No copied Proto or oldMega native credit. Same B-only tier/resource/contact staging, not natural acquisition. No source/game/default/settings changes, full-roster/allweapon/FPS/perfectfairness/adoption claim.'))
    print(json.dumps(dict(readiness=str(a.output / 'readiness.json'),sha256=sha(a.output / 'readiness.json'),bindings=len(bindings)),indent=2))


if __name__=='__main__':
    main()
