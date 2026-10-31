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

J = R / 'build/bt-cf-coherent-source-1031-v1/joint'
H = R / 'docs/qa/checkpoints/2026-10-31/bt-cf-coherent-source-v1/handoff.json'
K = R / 'build/contra-force-p1-kernel-v1'
OLD = R / 'build/bt-ready-native-1031-v2/rash'
T = R / 'tools/reference/contra_force_firstlook_native_1031_v2.lua'
EXPECTED = 'e538d2b809b1dac9b70a0a1b23a1b33b3d361297b25fac0b556d8eae5c7721ed'
HANDOFF = 'e1f30c16f7f49426690c6a3e4ad7f42fa572d297128ed44bcc9625a51490c214'
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
    h = check(H); stage = check(J.parent / 'source-stage.json'); kernel = check(K / 'build-proof.json')
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
              'CfState', 'CfP1Late', 'CfA2Router']}
    extra['CfRecordReady'] = own['CfRenderRecord'] + 14
    ptr = own['CfPointers']; p = own['CfRenderRecord'] - 0xa000
    observed = list((K / 'ram3.bin').read_bytes()[p:p+14])
    expected = [0x68, 0xa8, 0x68, 0xaa, 0xa5, ptr, 0x48, 0xa5, ptr+1, 0x48, 0x86, ptr, 0x84, ptr+1]
    assert ptr < 255 and observed == expected, ('Genuine direct-emitter pointer-ready seam', observed)
    guard = address(b, 'CfExternalCookie') - 1
    gp = location(b, 'CfExternalCookie') - 1
    assert raw[gp] == 0x60
    extra['CfGuardReturn'] = guard
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
    template = T.read_text(); assert template.count('@@TIMING@@') == 1
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
            J / 'candidate.lbl', K / 'build-proof.json', K / 'runtime.lbl', K / 'ram1.bin', K / 'ram2.bin',
            K / 'ram3.bin', OLD / 'controller.lua', OLD / 'run.py', R / 'tools/run_mesen.py',
            R / 'tools/audit/capture_budget.py', R / 'tools/audit/prepare_contra_force_p1_coherent_cart_v2.py',
            Path('C:/mesen2/Mesen.exe')]
    # Retain the actual qualified producer closure, without copying parent archives.
    bindings = dict(h['bindings']); bindings.update(kernel['bindings'])
    bindings.update({str(p.resolve()): sha(p) for p in refs})
    packets = []
    oracle = dict(source_native_imports=imports, direct_record_ready=dict(address=extra['CfRecordReady'],
                  source_prefix=observed), guard_RTS=guard, main_RTS=main_return, menu=[])
    native_names = set(re.findall(r"r\('([^']+)'\)", template))
    native_names |= {'GameLoop', 'NonMaskableInterrupt', 'IrqScrollSplit', 'AudioUpdate'}
    # Wrapper generates the two RTI convenience symbols from actual DBG sizes.
    native_names -= set(extra)
    prefix = ''.join(f'L[{json.dumps(n)}]={address(b, n)}\n' for n in sorted(native_names))
    prefix += ''.join(f'L[{json.dumps(n)}]={v}\n' for n, v in sorted(extra.items()))
    for n in ('GameLoop', 'AudioUpdate', 'CfOrBtCheck'):
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
        args = dict(raw=31, slot=30, variant=i, selects=i, sha256=EXPECTED, main_return=main_return,
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
            run_cap_bytes=536870912, max_files=64, max_PNGs=4, maximum_physical_frames=1200,
            gameplay_physical_frames=360, normal_eight_sprites=True, power_on='AllZeros',
            emulated_writes=False, movie=False, Lua54_syntax_passed=True,
            scope='Controller-only title/menu/lives/360 gameplay frames; authentic source five-part menu and real mapped direct body emitter; original P0/P2, fair complete P1 owner epochs, walk/jump/land and ground/air original B projectiles. Hardware winner pixels only. No 1-1 clear, every powerup, 60Hz or repaired crowding claim.',
            bindings=own_bindings)
        save(folder / 'ready.json', ready)
        packets.append(dict(name=name, variant=i, ready=str(folder / 'ready.json'),
                            ready_sha256=sha(folder / 'ready.json'), runner=str(folder / 'run.py')))
        oracle['menu'].append(dict(variant=i, descriptor=record, rows=rows, name_tiles=tiles))
    save(out / 'source-observer-binding.json', oracle)
    prepared = dict(prepared=True, native=False, source_candidate=EXPECTED, source_handoff_sha256=HANDOFF,
                    packets=packets, bounds=dict(physical_frames=1200, gameplay_frames=360, PNGs=4,
                    files=64, bytes=536870912, emulator_timeout_seconds=90, process_timeout_seconds=105),
                    existing_Mesen_process_guard=True, no_launch_performed=True,
                    observer_binding_sha256=sha(out / 'source-observer-binding.json'),
                    bindings={str(p.resolve()):sha(p) for p in refs})
    save(out / 'prepared.json', prepared)
    print(json.dumps(dict(prepared=True, native=False, path=str(out / 'prepared.json'),
                         sha256=sha(out / 'prepared.json'), packets=packets)))


if __name__ == '__main__':
    main()
