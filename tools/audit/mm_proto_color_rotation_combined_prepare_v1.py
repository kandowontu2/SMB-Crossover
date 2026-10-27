"""Prepare one unchanged ProtoHard six-case body on ROOT's exact ce635 union."""
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
OLD = D / 'robot-balancer-budget-ready-v1'
COMPONENT = D / 'robot-color-rotation-source-ready-v1'
ROM_SHA = 'ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2) + '\n')


def hook(b, name, old):
    delta = 0
    if name in ['finish', 'NmiReturn', 'IrqReturn']:
        target = {'finish': 'GameLoop', 'NmiReturn': 'NonMaskableInterrupt', 'IrqReturn': 'IrqScrollSplit'}[name]
        delta = int(b['syms'][target]['size'], 0) - 1
    elif name == 'PrimaryArtReady':
        target, delta = 'ProtoLegacyDrawShotsCold::Pointer', 2
    elif name == 'completion':
        target, delta = 'PostDmaMaskEnable', 3
    else:
        target = name
    off = location(b, target) + delta
    result = dict(address=address(b, target) + delta, physical_bank=(off - 16) // 8192,
                  bytes=list(b['raw'][off:off + len(old['bytes'])]))
    return result, dict(real_symbol=target, real_offset=delta, **result)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    assert sha(B / 'candidate.nes') == ROM_SHA
    assert sha(COMPONENT / 'proof.json') == '3c8096400841c336c88d4be33c9951e775324c04b19e3082184d808f6bdc88ed'
    assert sha(OLD / 'readiness.json') == '7a85c202a6304f8689a7069840cf5ba1b517e1fedcbebe2bea30e2c7f94d0786'
    source = json.loads((B / 'source-manifest.json').read_text())
    assert len(source) == 871
    bindings = json.loads((OLD / 'bindings.json').read_text())
    for f, h in bindings.items():
        assert sha(f) == h, f
    for f, h in json.loads((COMPONENT / 'bindings.json').read_text()).items():
        assert sha(f) == h, f
        bindings[f] = h
    for rel, h in source.items():
        f = B / 'source' / rel
        assert sha(f) == h, rel
        bindings[str(f.resolve())] = h
    b = scoped_load(B / 'candidate.nes')
    union = json.loads((B / 'proof.json').read_text())
    assert union['built'] and union['source_composition_exact'] and union['ROM_sha256'] == ROM_SHA
    assert not union['qualified'] and not union['adopted'] and not union['native_run']
    original = json.loads((OLD / 'native/config.json').read_text())
    cfg = json.loads(json.dumps(original))
    cfg['ROM_sha256'] = ROM_SHA
    changes, checks = {}, []
    for group, hooks in [('hooks', cfg['hooks']), ('diagnostic.hooks', cfg['diagnostic']['hooks'])]:
        for name, old in list(hooks.items()):
            new, owner = hook(b, name, old)
            hooks[name] = new
            checks.append(dict(group=group, name=name, **owner))
            if new != old:
                changes[group + '.' + name] = dict(old=old, new=new)
    code_aliases = {}
    for name, old in cfg['ram'].items():
        actual = address(b, name)
        if old < 0x8000:
            assert old == actual, ('actual RAM changed', name, old, actual)
        elif old != actual:
            cfg['ram'][name] = actual
            code_aliases[name] = dict(old=old, actual=actual)
    assert cfg['identity'] == original['identity'] and cfg['mode_value'] == 1
    assert cfg['identity']['owner'] == address(b, 'CHARACTER_MEGAMAN') == 1
    assert cfg['identity']['variant'] == 1 and cfg['identity']['variant_ram'] == 'ProtoVariant'
    assert cfg['identity']['ammo_indices'] == list(b['raw'][location(b, 'InvAmmoIndex')+16:location(b, 'InvAmmoIndex')+25])
    assert cfg['dma_protocol'] == protocol(b)
    # Every actual primary record keeps its source-owner/table contract. The
    # full 0a art-caller proof remains an inherited COMPONENT proof, not a new
    # ce635 test: these complete banks are exactly that donor's originals.
    art_parent = D / 'mm-proto-construction-pivot-candidate-v9'
    ar = (art_parent / 'candidate.nes').read_bytes()
    for bank in [4, 12, 66]:
        lo = 16 + bank * 8192
        assert b['raw'][lo:lo+8192] == ar[lo:lo+8192], bank
    for typ, rows in enumerate(cfg['primary']['records']):
        for frame, faces in enumerate(rows):
            for side, record in zip(['Right', 'Left'], faces):
                index = cfg['primary']['starts'][typ] + frame - address(b, 'METASPRITE_MM_BULLET_1')
                target = f'MmMM_BULLET_{index+1}{side}'
                off = location(b, target)
                assert record == dict(address=address(b, target), bank=(off-16)//8192,
                                      bytes=list(b['raw'][off:off+1+b['raw'][off]]))
    controls = component_cpu(b)
    put(a.output / 'actual-component-CPU.json', dict(passed=True, native_run=False,
        ROM_sha256=ROM_SHA, rows=controls, scope='Fresh configured primary/charge/Rush/Balancer/cycle source calls; not source acquisition/contact/hardware.'))
    restore = json.loads(json.dumps(cfg))
    restore['ROM_sha256'] = original['ROM_sha256']
    restore['hooks'] = original['hooks']
    restore['diagnostic']['hooks'] = original['diagnostic']['hooks']
    restore['ram'] = original['ram']
    assert restore == original
    oldscript = (OLD / 'native/run.lua').read_text()
    oldprefix = 'FINAL_ITEM_PROGRESSIVE=' + lua(original) + '\n'
    assert oldscript.startswith(oldprefix)
    script = 'FINAL_ITEM_PROGRESSIVE=' + lua(cfg) + '\n' + oldscript[len(oldprefix):]
    assert script.split('\n', 1)[1] == oldscript.split('\n', 1)[1]
    direct = set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'", script))
    assert not direct - set(cfg['ram'])
    native = a.output / 'native'
    native.mkdir()
    put(native / 'config.json', cfg)
    (native / 'run.lua').write_text(script)
    sys.path.insert(0, str(D / 'final-tmnt-items-v1/lua-parser-deps-v1'))
    from luaparser import ast as last
    last.parse(script)
    sys.path.insert(0, str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    rt = LuaRuntime(unpack_returned_tuples=True)
    mock = MOCK + '\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Unexpected startup write")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'
    rt.execute(mock + script)
    count = rt.eval('#callbacks')
    assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
    rt.execute('emu.addMemoryCallback=function()error("Runtime host registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
    for frame in [1, 2, 3]:
        rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
    assert rt.eval('#callbacks') == count
    command = json.loads((OLD / 'command.json').read_text())
    for i, value in enumerate(command):
        if i and command[i-1] == '--output':
            command[i] = str(native)
        elif Path(value).resolve() == (OLD / 'native/run.lua').resolve():
            command[i] = str(native / 'run.lua')
        elif Path(value).resolve() == (D / 'robot-base-palette-candidate-v2/candidate.nes').resolve():
            command[i] = str(B / 'candidate.nes')
    assert str(native / 'run.lua') in command and str(B / 'candidate.nes') in command
    put(a.output / 'command.json', command)
    put(a.output / 'metadata-proof.json', dict(prepared=True, native_run=False,
        only_deltas='ROM hash and genuine compiled hook/alias metadata; entire executable observer/controller/6case/assert/guard body byte-exact',
        hook_changes=changes, genuine_code_alias_changes=code_aliases, all_actual_RAM_exact=True,
        complete_hook_bindings=checks, mode=1, variant=1, actual_ammo_indices=cfg['identity']['ammo_indices'],
        diagnostic_focus=[cfg['diagnostic']['first_frame'], cfg['diagnostic']['last_frame']],
        same_thresholds_caps_body_contacts_staging_and_deadlines=True, config_reverse_exact=True,
        static_startup_only_threeframe_mock=True, source_art_whole_banks_4_12_66_exact_0a=True,
        inherited_art_proof_scope='0a donor controls only; exact code/data ownership shown, not retagged as ce635 native.',
        original_script_sha256=sha(OLD / 'native/run.lua'), new_script_sha256=sha(native / 'run.lua')))
    extras = [*B.glob('*.json'), B / 'source.patch', B / 'candidate.nes', B / 'candidate.dbg', B / 'candidate.lbl', B / 'candidate.map',
              COMPONENT / 'proof.json', COMPONENT / 'bindings.json', COMPONENT / 'catalog.json', COMPONENT / 'review-files.json',
              OLD / 'readiness.json', OLD / 'bindings.json', OLD / 'ROOT-grant.json', OLD / 'launch-binding-v1.json', OLD / 'launch-outcome-v1.json',
              D / 'robot-balancer-budget-review-v1/proof.json', Path(sys.executable), Path(__file__)]
    pending, seen = [Path(__file__), R / 'tools/audit/mm_proto_cold_palette_diagnostic_run_v1.py'], set()
    while pending:
        f = pending.pop()
        if f in seen:
            continue
        seen.add(f)
        extras.append(f)
        for node in ast.walk(ast.parse(f.read_text())):
            names = [node.module] if isinstance(node, ast.ImportFrom) else [x.name for x in node.names] if isinstance(node, ast.Import) else []
            for name in names:
                if name:
                    dep = R / 'tools/audit' / (name.split('.')[0] + '.py')
                    if dep.is_file():
                        pending.append(dep)
    extras += list(a.output.rglob('*'))
    for f in extras:
        if f.is_file():
            bindings[str(f.resolve())] = sha(f)
    put(a.output / 'bindings.json', dict(sorted(bindings.items())))
    put(a.output / 'readiness.json', dict(prepared=True, native_run=False, native_granted=False,
        candidate_ROM_sha256=ROM_SHA, combined_source_manifest_sha256=sha(B / 'source-manifest.json'),
        component_source_qualified=True, component_source_ready_sha256=sha(COMPONENT / 'proof.json'),
        combined_source_component_results_not_retagged=True, combined_native_pass_unproved=True,
        unchanged_ProtoHard_sixcase_controller_mechanics_all_guards=True, diagnostic_focus=[990, 996],
        mode_numeric=1, variant=1, maximum_native_launches=1, maximum_workers=1, wall_bound=4000,
        host_seconds=1200, no_retry=True, command_sha256=sha(a.output / 'command.json'),
        script_sha256=sha(native / 'run.lua'), metadata_proof_sha256=sha(a.output / 'metadata-proof.json'),
        bindings=len(bindings), bindings_sha256=sha(a.output / 'bindings.json'), tool_sha256=sha(__file__),
        needed_actual_checks=['Original startup376/378 strict enable boundaries',
            'Six actual primary/charge/Rush/gate/Balancer component returns and full256DMA/CHR guards',
            'Actual993 incoming queue, ColorRotation defer/counter and subsequent eligible retry within unchanged run',
            'Physical PPU/timing/body/shot/HUD review; no automatic all-weapon or fairness verdict'],
        limitations='Prepared only; explicit fresh ROOT grant required. ca9a remains native-unrun. ce635 is a separate combined hash with no current installation/adoption claim. Same original B-only stage setup/contact alignment, not natural acquisition. All earlier FALSEs retained.'))
    print(json.dumps(dict(readiness=str(a.output / 'readiness.json'), sha256=sha(a.output / 'readiness.json'), bindings=len(bindings)), indent=2))


if __name__ == '__main__':
    main()
