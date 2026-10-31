"""Finite controls on the genuinely linked current CF P1 successor.

No instruction fetch overlays, mapper redirects, native emulator or readiness
edits. Existing finite group/queue/lifecycle suites are rebound only after all
their historical helper imports have completed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/audit'))
import contra_force_p1_stale_palette_ppu_v2 as F
import contra_force_p1_group_ppu_controls_v2 as G
import contra_force_p1_queue_order_controls_v1 as QO
import contra_force_p1_acquire_retire_controls_v1 as LR
V, Q, T, C, U = F.V, F.Q, F.T, F.C, F.U
K = R / 'build/contra-force-p1-kernel-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def bind(parent):
    for module in [V, Q, Q.V, V.J, C, T, V.D]:
        module.P = parent
    Q.K = Q.V.K = K
    T.B = T.qualified(parent / 'joint/candidate.nes')
    U.B = T.B
    T.PAYLOAD = (parent / 'joint/cf-stream.bin').read_bytes()
    T.COOKIE = (parent / 'joint/cf-cookie.bin').read_bytes()
    Q.L = Q.V.L = {n: int(v, 16) for v, n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',
                                                       (K / 'runtime.lbl').read_text())}


def raw_global(memory):
    return [list.__getitem__(memory, i) for i in range(32768)]


def worker_start(memory, flags=0x30):
    return C.start(memory, T.address(T.B, 'CfP1NativeRestore'), 91 | 128, p=flags)


def endpoints():
    rows = []
    for variant in range(4):
        for state in [0, 1]:
            m = V.scene(variant)
            T.put(m, SmFreezeRenderState=state)
            d = V.draw(m)
            assert d['hits'] == ['nativeDraw', 'earlyCF', 'lateCF'], d
            assert d['source_phase'] == 0 and d['Last'] == 193 and d['Pending'] == 128
            n = F.normal(m)
            assert n['paletteP1'] == [32, 56, 22]
            # Injury/status6 with no early token remains the original no-op.
            saved = raw_global(m), [bytes(bank) for bank in m.ram]
            six = Q.public(m, 6, p=0x79)
            assert six['AXYP'] == [87, 2, 3, 0x78]
            # The genuine generic router always records its target and A/P
            # arguments, even when the selected status worker is a no-op.
            # Preserve every source/state/code byte outside those five aliases.
            scratch = {Q.L['CfTarget'] & 8191, (Q.L['CfTarget'] + 1) & 8191,
                       Q.L['CfTargetBank'] & 8191, Q.L['CfArgA'] & 8191, Q.L['CfArgP'] & 8191}
            changes = [(bank, at, saved[1][bank][at], m.ram[bank][at])
                       for bank in range(4) for at in range(8192) if saved[1][bank][at] != m.ram[bank][at]]
            assert all(bank == 2 and at in scratch for bank, at, old, new in changes), changes
            assert [m.ram[2][at] for at in sorted(scratch)] == [17, 190, 3, 87, 120]
            assert bytes(m[512:768]) == bytes(saved[0][512:768])
            rows.append(dict(variant=variant, native_state=state, hits=d['hits'], nativeP1=n['paletteP1'],
                             drawCPU=d['result']['CPU'], ordinary6AXYP=six['AXYP'], declared_router_scratch=changes))
    stale = []
    base = V.scene()
    V.draw(base)
    F.normal(base)
    assert T.get(base, 'SmFreezeLastBlue') == 193 and list(base.vram[0x3f15:0x3f18]) == [32, 56, 22]
    for byte in range(16):
        m = C.clone(base)
        m.ram[2][0x1fe0 + byte] ^= 1
        m.executed_guest.clear()
        d = V.draw(m)
        assert d['hits'] == ['nativeDraw'] and not m.executed_guest, ('Rejected cookie executed guest', byte, d)
        assert d['Last'] == 192 and d['Pending'] == 192 and d['Turn'] == 1
        n = F.normal(m)
        assert n['paletteP1'] == [26, 48, 39]
        assert any(m[512 + off] < 240 and m[514 + off] & 3 == 1 for off in range(0, 256, 4))
        stale.append(dict(poisoned_byte=byte, no_guest_opcode=True, native_draws=1,
                          visible_nativeP1=True, hardwareP1=n['paletteP1'], normalNMI_CPU=n['CPU']))
    return dict(all4classes_2native_states=rows, all16_poisoned_C1_actual_normalNMI_restore=stale)


def api_vectors():
    base = V.scene()
    rows = []
    protocol = set(range(0x7e0, 0x7e7)) | {0x7ea, 0x7ffa}
    for marker in [0, 1, 128, 192, 193]:
        for flags in [v for v in range(256) if v & 48 == 48]:
            before = C.clone(base)
            T.put(before, SmFreezeLastBlue=marker, SmFreezePalettePending=19, SmFreezeTurn=1)
            before[T.address(T.B, 'SmFreezePalettePacket'):T.address(T.B, 'SmFreezePalettePacket') + 7] = [173] * 7
            expected_m = C.clone(before)
            expected = Q.public(expected_m, 6, p=flags)
            m = C.clone(before)
            actual = T.finish(m, worker_start(m, flags))
            assert actual['AXYP'] == expected['AXYP'] and m.rawtags == expected_m.rawtags
            assert T.smc(m) == T.smc(expected_m) and [bytes(x) for x in m.ram] == [bytes(x) for x in expected_m.ram]
            differences = [at for at in range(32768) if list.__getitem__(m, at) != list.__getitem__(expected_m, at)]
            assert all(0x100 <= at <= 0x1e0 or at in protocol for at in differences), ('Unexpected worker application write', marker, flags, differences)
            if marker in [192, 193]:
                assert [T.get(m, n) for n in ['SmFreezeLastBlue', 'SmFreezePalettePending', 'SmFreezeTurn']] == [192, 192, 1]
                assert list(m[T.address(T.B, 'SmFreezePalettePacket'):T.address(T.B, 'SmFreezePalettePacket') + 7]) == [63, 21, 3, 26, 48, 39, 0]
            else:
                assert not any(at in protocol for at in differences)
            rows.append(dict(marker=marker, P=flags, AXYP=actual['AXYP'], minimum_SP=actual['minimum_SP']))

    # Genuine linked shared59 -> A91 -> B020 -> guard -> actual worker frame.
    # Cuts cover all instructions in the newly placed67B plus shared entry,
    # native-tail return and B0206/guard/firstA2/lateA3 seams on that live frame.
    b = V.scene()
    T.put(b, NmiDisable=255, ReloadCHRBank=0, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0,
          Sprite0HitDetectFlag=0, SavedJoypadBits=0)
    b[T.address(T.B, 'VRAM_Buffer1')] = 0
    b[0x5224] = 128
    m = C.clone(b)
    c = T.cpu(m, 'FwNativeDrawAll', public=True, p=0x30)
    reference = C.clone(b)
    rc = T.cpu(reference, 'FwNativeDrawAll', public=True, p=0x30)
    expected = T.finish(reference, rc)
    native_pc = T.address(T.B, 'DrawAllMetasprites')
    points = {(190, T.address(T.B, 'FwNativeDrawAll')),
              (190, T.address(T.B, 'FfMuxNativeTail')),
              (215, T.address(T.B, 'BtServiceVeneers') + 18),
              (197, T.address(T.B, 'CfOrBtCheck')),
              (2, Q.L['CfServiceVeneers'] + 18),
              (3, Q.L['CfP1LateEntry'])}
    seen = set()
    cuts = []
    native_calls = 0
    while c.pc != 32767:
        raw = m.rawtags[(c.pc - 32768) // 8192] if c.pc >= 32768 else -1
        if c.pc == native_pc and raw == 132:
            native_calls += 1
        own = raw == 219 and 0xae97 <= c.pc < 0xaeda
        key = (raw, c.pc)
        if (own or key in points) and key not in seen:
            seen.add(key)
            for kind in ['NMI', 'IRQ']:
                if kind == 'IRQ' and c.p & 4:
                    continue
                z, d = U.clone(m, c)
                before_isr = raw_global(z)
                writes = len(z.writes)
                proof = U.interrupt(z, d, kind, keep_ppu=False)
                after_isr = raw_global(z)
                event = z.writes[writes:]
                readonly = protocol | {0x7ff7, 0x7ff8, 0x7ff9, T.address(T.B, 'AreaType')}
                assert not any(at in readonly for at, value in event), ('Busy ISR touched protocol inputs', key, kind, event)
                effects = [at for at, (a, v) in enumerate(zip(before_isr, after_isr)) if a != v]
                wanted = raw_global(reference)
                for at in effects:
                    wanted[at] = after_isr[at]
                actual = T.finish(z, d)
                assert actual['AXYP'] == expected['AXYP'] and z.rawtags == reference.rawtags and T.smc(z) == T.smc(reference)
                assert [bytes(x) for x in z.ram] == [bytes(x) for x in reference.ram]
                mismatch = [at for at in range(32768) if not 0x100 <= at <= 0x1e0 and list.__getitem__(z, at) != wanted[at]]
                assert not mismatch, ('Linked ISR continuation differs beyond measured native event', key, kind, mismatch)
                cuts.append(dict(raw=raw, PC=c.pc, entry_SP=c.sp, measured_native_ISR_changed_addresses=effects, **proof))
        c.step()
    assert native_calls == 1 and any(raw == 219 for raw, pc in seen)
    assert all(key in seen for key in points), ('Missing linked seam', points - seen)
    return dict(actual_A91_5markers_64flags=rows, actual_live_shared_to_late_vectors=cuts,
                linked_instruction_seams=len(seen), actual_vector_cases=len(cuts), genuine_native_DrawAll_once=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cart-root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--suite', choices=['endpoints', 'groups', 'queue', 'lifecycle', 'api-vectors'], required=True)
    args = parser.parse_args()
    parent = args.cart_root.resolve()
    out = args.output_root.resolve()
    assert not out.exists()
    bind(parent)
    for name, digest in json.loads((parent / 'source-stage.json').read_text())['bindings'].items():
        assert sha(name) == digest, name
    if args.suite in ['groups', 'queue', 'lifecycle']:
        module = {'groups': G, 'queue': QO, 'lifecycle': LR}[args.suite]
        module.O = out
        module.main()
        return
    out.mkdir(parents=True)
    result = dict(passed=False, source=True, native=False, ready=False, admitted=False,
                  actual_linked_cartridge=True, synthetic_fetch_overlay=False, checks={})
    result['retained_v1_fixture_negative'] = dict(
        path=str(R / 'build/contra-force-p1-coherent-endpoints-v1/controls.json'),
        sha256=sha(R / 'build/contra-force-p1-coherent-endpoints-v1/controls.json'),
        correction='V1 demanded every RAM byte remain equal across ordinary public6. Actual original router updates only existing C2 CfTarget[2], CfTargetBank, CfArgA/P before the phase-rejected late worker returns. V2 asserts these exact five declared writes and every other bank/state byte unchanged; no ROM or original source contract changed.')
    try:
        result['checks'] = endpoints() if args.suite == 'endpoints' else api_vectors()
        result['passed'] = True
    except Exception as error:
        result.update(error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        files = [Path(__file__), Path(V.__file__), Path(F.__file__), Path(U.__file__),
                 parent / 'source-stage.json', parent / 'joint/candidate.nes', parent / 'joint/candidate.dbg',
                 parent / 'joint/cf-stream.bin', parent / 'joint/cf-cookie.bin', K / 'build-proof.json',
                 R / 'build/contra-force-p1-coherent-endpoints-v1/controls.json']
        result['bindings'] = {str(p.resolve()): sha(p) for p in files}
        p = out / 'controls.json'
        p.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(dict(path=str(p), sha256=sha(p), passed=result['passed'], error=result.get('error'))), flush=True)


if __name__ == '__main__':
    main()
