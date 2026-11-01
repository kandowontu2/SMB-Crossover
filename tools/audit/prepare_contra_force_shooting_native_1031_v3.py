"""Prepare, never launch, four exact-source controller-only CF first looks."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools'), str(R / 'tools/audit')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address, location
from observe_chip_committed_write import lua
from prepare_contra_force_p1_coherent_cart_v2 import native_abi

J = R / 'build/contra-force-projectile-contact-1031-v3/joint'
H = R / 'docs/qa/checkpoints/2026-10-31/contra-force-projectile-contact-source-v1/handoff.json'
K = R / 'build/contra-force-projectile-contact-1031-v3/kernel'
OLD = R / 'build/bt-ready-native-1031-v2/rash'
T = R / 'tools/reference/contra_force_shooting_native_1031_v3.lua'
EXPECTED = 'f4767d595a25bf64355b1e2cea86be7a93046f1cf139a4d9b0544e35f9ed4182'
HANDOFF = '78ce571a5670df0d3cf97a20e3b5a27499497fd685eb81fda90eb66c0645d706'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')


def check(doc):
    q = json.loads(doc.read_text())
    for path, digest in q['bindings'].items():
        assert sha(path) == digest, ('Immutable input changed', path)
    return q


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args(); out = a.output.resolve()
    assert out.is_relative_to(R / 'build') and not out.exists()
    assert sha(H) == HANDOFF and sha(J / 'candidate.nes') == EXPECTED
    h = check(H); stage = check(J.parent / 'source-stage.json'); kernel = stage
    b = qualified(J / 'candidate.nes'); imports = native_abi(b)
    raw = b['raw']; chrstart = 16 + 128 * 8192
    # Source carrier really is the qualified A1/C2/A3 image, not a preload.
    images = []
    for i in (1, 2, 3):
        image = bytearray((K / f'ram{i}.bin').read_bytes())
        image.extend(bytes(8192-len(image)))
        if i in (2, 3):
            image[0x1fe0:] = bytes(32)
        images.append(image)
    stream = b''.join(images)
    assert raw[chrstart + 935 * 1024:chrstart + 959 * 1024] == stream
    own = {n: int(v, 16) for v, n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)', (K / 'runtime.lbl').read_text())}
    extra = {n: own[n] for n in ['CfHostConstruct', 'CfHostMovement', 'CfNativeBody', 'CfRenderRecord',
              'CfPointers', 'CfRenderSlot', 'CfRenderRemaining', 'CfRenderXLo', 'CfRenderYLo',
              'CfState', 'CfP1Late', 'CfA2Router','CfShotSlot','CfEnemySlot','CfOrdinaryDefeat','CfSourceImpact','CfContactDone']}
    extra['CfRecordReady'] = own['CfRenderRecord'] + 14
    ptr = own['CfPointers']; p = own['CfRenderRecord'] - 0xa000
    observed = list((K / 'ram3.bin').read_bytes()[p:p+14])
    expected = [0x68, 0xa8, 0x68, 0xaa, 0xa5, ptr, 0x48, 0xa5, ptr+1, 0x48, 0x86, ptr, 0x84, ptr+1]
    assert ptr < 255 and observed == expected, ('Genuine direct-emitter pointer-ready seam', observed)
    guard = address(b, 'CfExternalCookie') - 1
    gp = location(b, 'CfExternalCookie') - 1
    assert raw[gp] == 0x60
    extra['CfGuardReturn'] = guard
    image3=(K/'ram3.bin').read_bytes();ip=own['CfSourceImpact']-0xa000
    impact_code=list(image3[ip:ip+9])
    impact_expected=[0xae,own['CfShotSlot']&255,own['CfShotSlot']>>8,0x20,own['CfNativeShotImpact']&255,own['CfNativeShotImpact']>>8,0x4c,own['CfContactDone']&255,own['CfContactDone']>>8]
    assert impact_code==impact_expected and image3[own['CfContactDone']-0xa000]==0x68
    diagnostic=R/'build/contra-force-projectile-impact-boundary-diagnostic-1031-v1/controls.json'
    diagnosis=check(diagnostic);assert diagnosis['passed']and len(diagnosis['rows'])==4
    for row in diagnosis['rows']:
        assert row['earned']['post_impact']['raw_maps'][1:3]==[3,2]and row['earned']['post_impact']['mapped_kind']==6
        assert row['earned']['native_return']['raw_maps'][2]==0xd0 and row['earned']['native_return']['mapped_kind']==3 and row['earned']['native_return']['physical_C2_kind']==6
    # Main's real final RTS, derived from its genuine emitted source size.
    size = int(b['syms']['GameLoop']['size'])
    main_return = address(b, 'GameLoop') + size - 1
    assert main_return == 0x8355 and raw[location(b, 'GameLoop') + size - 1] == 0x60
    cookie = list(raw[location(b, 'CfExternalCookie'):location(b, 'CfExternalCookie') + 16])
    assert cookie[0] == 0xa7 and cookie[1] == 31
    policy = (OLD / 'controller.lua').read_text()
    start = policy.index('emu.addMemoryCallback(function()\n if active()and bank(L.GameLoop)')
    end = policy.index('emu.addEventCallback(function()\n if done then return end;local b={}', start)
    timing = policy[start:end]
    old = "assert(r('SelectedCharacter')==33 and (r('FmGroups')&32)==P.variant,'Stable selected BT owner')"
    assert timing.count(old) == 1
    timing = timing.replace(old, "assert(r('SelectedCharacter')==31 and class()==P.variant,'Stable selected CF owner')")
    assert timing.count('  main=nil\n') == 1
    timing = timing.replace('  main=nil\n', '  main=nil\n  routeAfterMain()\n')
    template = T.read_text(); assert template.count('@@TIMING@@') == 1
    assert "OUTPUT..name..'.png','wb'" in template
    assert 'emu.write(' not in template and 'emu.write(' not in timing
    template = template.replace('@@TIMING@@', timing)
    # Lua 5.4 syntax only: no emulator/ROM execution or gameplay model here.
    luapath = R / 'build/smb2-final62-observer-lua-deps-v1'
    sys.path.insert(0, str(luapath))
    from lupa.lua54 import LuaRuntime
    rt = LuaRuntime(unpack_returned_tuples=True)
    runner = (OLD / 'run.py').read_text()
    assert 'timeout=q[\'host_timeout_seconds\']' in runner and "'--nes.removeSpriteLimit=false'" in runner
    out.mkdir()
    refs = [Path(__file__), T, H, J.parent / 'source-stage.json', J / 'candidate.nes', J / 'candidate.dbg',
            J / 'candidate.lbl', J.parent / 'source-stage.json', K / 'runtime.lbl', K / 'ram1.bin', K / 'ram2.bin',
            K / 'ram3.bin', OLD / 'controller.lua', OLD / 'run.py', R / 'tools/run_mesen.py',
            R / 'tools/audit/capture_budget.py', R / 'tools/audit/prepare_contra_force_p1_coherent_cart_v2.py',
            Path('C:/mesen2/Mesen.exe'),
            R / 'build/contra-force-firstlooks-native-1031-v1/prepared.json',
            R / 'build/contra-force-firstlooks-native-1031-v1/burns/ready.json',
            R / 'build/contra-force-firstlooks-native-1031-v1/burns/capture/binding.json',
            R / 'build/contra-force-firstlooks-native-1031-v1/burns/capture/body-DMA.csv',
            R / 'build/contra-force-firstlooks-native-1031-v1/burns/capture/trace.csv',
            R / 'build/contra-force-firstlooks-native-1031-v1/burns/capture/candidate-controller.log']
    refs += [diagnostic,R/'tools/audit/contra_force_projectile_impact_boundary_diagnostic_1031_v1.py',R/'tools/reference/contra_force_shooting_native_1031_v1.lua',R/'tools/audit/prepare_contra_force_shooting_native_1031_v1.py',R/'build/contra-force-shooting-native-1031-v1/prepared.json',R/'build/contra-force-shooting-native-1031-v1/burns/ready.json']
    refs += [p for p in (R/'build/contra-force-shooting-native-1031-v1/burns/capture').iterdir()if p.is_file()]
    predicate_audit=R/'build/contra-force-shooting-predicate-audit-1031-v2/diagnosis.json'
    assert check(predicate_audit)['passed']
    refs += [predicate_audit,R/'tools/audit/contra_force_shooting_predicate_audit_1031_v2.py',R/'tools/reference/contra_force_shooting_native_1031_v2.lua',R/'tools/audit/prepare_contra_force_shooting_native_1031_v2.py',R/'build/contra-force-shooting-native-1031-v2/prepared.json',R/'build/contra-force-shooting-native-1031-v2/burns/ready.json']
    refs += [p for p in (R/'build/contra-force-shooting-native-1031-v2/burns/capture').iterdir()if p.is_file()]
    # Retain the actual qualified producer closure, without copying parent archives.
    bindings = dict(h['bindings']); bindings.update(kernel['bindings']);bindings.update(diagnosis['bindings'])
    bindings.update({str(p.resolve()): sha(p) for p in refs})
    packets = []
    oracle = dict(impact_commit=dict(address=own['CfContactDone'],raw_A=3,raw_C=2,source_call_code=impact_code,expected_post_kind=6),source_native_imports=imports, direct_record_ready=dict(address=extra['CfRecordReady'],
                  source_prefix=observed), guard_RTS=guard, main_RTS=main_return, menu=[])
    native_names = set(re.findall(r"r\('([^']+)'\)", template))
    native_names |= {'GameLoop', 'NonMaskableInterrupt', 'IrqScrollSplit', 'AudioUpdate', 'ScrollHandler', 'AreaParserTaskHandler', 'ProcessEnemyData', 'Block_Buffer_1', 'NativeGoombaRender','ShellOrBlockDefeat','SetupFloateyNumber'}
    # Wrapper generates the two RTI convenience symbols from actual DBG sizes.
    native_names -= set(extra)
    prefix = ''.join(f'L[{json.dumps(n)}]={address(b, n)}\n' for n in sorted(native_names))
    prefix += ''.join(f'L[{json.dumps(n)}]={v}\n' for n, v in sorted(extra.items()))
    for n in ('GameLoop', 'AudioUpdate', 'CfOrBtCheck', 'ScrollHandler', 'AreaParserTaskHandler', 'ProcessEnemyData', 'NativeGoombaRender','ShellOrBlockDefeat','SetupFloateyNumber'):
        prefix += f'B[{json.dumps(n)}]={(location(b, n)-16)//8192}\n'
    for i, name in enumerate(('burns', 'smith', 'iron', 'beans')):
        folder = out / name; folder.mkdir()
        c = cookie[:]; c[2] = i
        record = address(b, f'FmDrawCfPreview::Cf{i}')
        rp = location(b, f'FmDrawCfPreview::Cf{i}')
        assert raw[rp] == 20
        rows = [list(raw[rp+1+n:rp+5+n]) for n in range(0, 20, 4)]
        np = location(b, 'FmNames') + (26+i)*16
        tiles = list(raw[np:np+16]); assert len(tiles) == 16 and 0x2a not in tiles
        goomba_records={address(b,n):True for n in ['MetaspriteData_GOOMBA_WALKING_1_LEFT','MetaspriteData_GOOMBA_WALKING_1_RIGHT','MetaspriteData_GOOMBA_WALKING_2_LEFT','MetaspriteData_GOOMBA_WALKING_2_RIGHT']}
        native_patterns={tile:list(raw[chrstart+17*1024+((tile&254)*16)%1024:chrstart+17*1024+((tile&254)*16)%1024+32])for tile in (162,164)}
        gp=location(b,'GroundPaletteData');assert list(raw[gp:gp+3])==[63,0,32];native_P3=list(raw[gp+32:gp+35]);assert native_P3==[15,54,23]
        args = dict(raw=31, slot=30, variant=i, selects=i, sha256=EXPECTED, main_return=main_return,native_patterns=native_patterns,goomba_records=goomba_records,native_P3=native_P3,native_defeat_sound=address(b,'Sfx_EnemySmack'),
                    cookie=c, menu=rows, menu_tiles=tiles, menu_palette=[55,18,15,15,55,22,15])
        text = 'COLD_ARGS=' + lua(args) + '\n' + prefix + template
        compiled, error = rt.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
        assert compiled, error
        (folder / 'controller.lua').write_text(text, encoding='utf-8', newline='\n')
        (folder / 'run.py').write_text(runner, encoding='utf-8', newline='\n')
        own_bindings = dict(bindings)
        for p in (folder / 'controller.lua', folder / 'run.py'):
            own_bindings[str(p.resolve())] = sha(p)
        ready = dict(prepared=True, native=False, root_launch_only=True, ROM=str(J / 'candidate.nes'),
            ROM_sha256=EXPECTED, source_handoff=str(H), class_name=name, variant=i,
            host_timeout_seconds=90, runner_kill_allowance_seconds=105,
            run_cap_bytes=536870912, max_files=64, max_PNGs=4, maximum_physical_frames=1800,
            gameplay_physical_frames=1000, normal_eight_sprites=True, power_on='AllZeros',
            emulated_writes=False, movie=False, Lua54_syntax_passed=True,
            scope='Controller-only cold title/menu/lives plus bounded earned-shot smoke. Actual worldX369/camera257 crossing, new native terrain/enemy parser, exact hardware world1..3/nativeGoomba patterns and rendered opaque enemy pixels, original source shot/native defeat/score/SFX/impact; original physical body/DMA/palette/stack/33SMC-ISR guards. Four binary PNGs, no movie/RAM writes. No earned pickup,1-1clear or60Hz claim.',
            bindings=own_bindings)
        save(folder / 'ready.json', ready)
        packets.append(dict(name=name, variant=i, ready=str(folder / 'ready.json'),
                            ready_sha256=sha(folder / 'ready.json'), runner=str(folder / 'run.py')))
        oracle['menu'].append(dict(variant=i, descriptor=record, rows=rows, name_tiles=tiles))
    save(out / 'source-observer-binding.json', oracle)
    prepared = dict(prepared=True, native=False, source_candidate=EXPECTED, source_handoff_sha256=HANDOFF,
                    packets=packets, bounds=dict(physical_frames=1800, gameplay_frames=1000, PNGs=4,
                    files=64, bytes=536870912, emulator_timeout_seconds=90, process_timeout_seconds=105),
                    existing_Mesen_process_guard=True, no_launch_performed=True,
                    observer_binding_sha256=sha(out / 'source-observer-binding.json'),
                    bindings={str(p.resolve()):sha(p) for p in refs})
    save(out / 'prepared.json', prepared)
    print(json.dumps(dict(prepared=True, native=False, path=str(out / 'prepared.json'),
                         sha256=sha(out / 'prepared.json'), packets=packets)))


if __name__ == '__main__':
    main()
