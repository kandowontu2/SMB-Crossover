"""Positive current-owner parity for the ungranted DK Jr bbox port proposal."""
import itertools
import json
from pathlib import Path
import check_dkjr_native_bbox_1102_v66 as B
import check_prince_strike_cold_1103_v131 as C

A, R, O, W, N = B.A, B.R, B.O, B.W, B.N


def main():
    base, manifest = C.image()
    assert manifest['parent_memory_SHA256'] == 'cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
    assert A.sha(base['raw']) == 'cba497aabf91ccb357a9392a4407f261c8fd33a66032ae9d7b2e1ba790ef490d'
    prior = json.loads((C.O / 'current-shared-cold-CPU-v131.json').read_text())
    assert prior['passed'] and prior['memory_only_SHA256'] == A.sha(base['raw'])
    proposal = json.loads((O / 'native-bbox-v65-layout.json').read_text())['ungranted_shared_gate_proposal']
    raw = bytearray(base['raw'])
    at, old, new = proposal['file_offset'], bytes.fromhex(proposal['old_hex']), bytes.fromhex(proposal['new_hex'])
    assert raw[at:at + len(old)] == old and raw[at + 37] == 0x60
    raw[at:at + len(new)] = new
    changed = dict(base, raw=bytes(raw))
    seeds, cold = {}, []
    # Current ShCheckCode/ShRetire/ShLoad instructions retain their exact
    # source-assembled bytes. Its independently updated cookie follows them.
    sh_source = R / 'build/shinobi-bbox-design-1101-v29/resident-design.bin'
    sh = sh_source.read_bytes()
    sh_at = 16 + 65 * 8192 + 0x800
    assert base['raw'][sh_at:sh_at + 0x278] == sh[:0x278]
    for owner in [36, 37, 38, 39]:
        if owner == 36:
            N.Bus = C.C.C.C.V.ControllerBus
            m = N.fresh(base)
            for bank in [2, 3]:
                m.ram[bank][:] = bytes([0x9d]) * 8192
                m.ram[bank][0x1fe0:0x1ff0] = bytes(16)
            C.fields(m, owner)
            z = C.I.invoke(m, 193, 0xa87f, (83, 71, 109, 0x21))
            assert z['regs'][3] & 1, ('current ShLoad', z['regs'])
            C.clear(m)
        else:
            m, z = C.cold(base, owner)
        headers = [bytes(m.ram[k][0x1fe0:0x1ff0]) for k in [2, 3]]
        assert headers[0] == headers[1] and headers[0][0] == 0xa7
        N.put(m, NmiDisable=255, DisableScreenFlag=0, Mirror_PPUMASK=30,
            TimerControl=0, AreaType=1, FrameCounter=0, VRAM_Buffer1_Offset=0)
        fresh = N.invoke(m, 'HuFresh', a=85, x=0, y=0, p=0x31)
        assert fresh['P'] & 1, ('current actual Fresh', owner, fresh)
        if owner in [36, 39]:
            full = N.invoke(m, 'HuFullBox', a=85, x=0, y=0, p=0x31)
            assert full['P'] & 1, ('authenticated current FullBox', owner, full)
        seeds[owner] = N.fork(m)
        cold.append(dict(owner=owner, actual_cold_CPU=z['CPU'],
            header=headers[0].hex(), actual_Fresh_handled=True,
            authenticated_FullBox_handled=owner in [36, 39]))
    cases = []
    anchors = [(8, 0, 32), (120, 0, 176), (255, 135, 208), (256, 16, 144), (700, 660, 176), (1024, 912, 208)]
    for owner, (world, camera, y), mode, flags in itertools.product(
            [36, 37, 38, 39], anchors, [0, 1], [0x30, 0x71, 0xf1]):
        pair = []
        for bundle in [base, changed]:
            m = N.fork(seeds[owner])
            m.bundle = bundle
            N.put(m, SelectedCharacter=owner, Player_X_Position=world & 255,
                Player_PageLoc=world >> 8, Player_Y_Position=y, Player_Y_HighPos=1,
                ScreenLeft_X_Pos=camera & 255, ScreenLeft_PageLoc=camera >> 8,
                Player_Rel_XPos=(world - camera) & 255, Player_Rel_YPos=y,
                CrossoverBehaviorVersion=mode)
            z = N.invoke(m, 'LmBoundingBoxGate', a=165, x=0, y=0, p=flags)
            pair.append((m, z))
        a, az = pair[0]
        b, bz = pair[1]
        assert [az[k] for k in ['A', 'X', 'Y', 'P']] == [bz[k] for k in ['A', 'X', 'Y', 'P']], ('AXYP', owner, world, camera, mode, flags)
        assert a.rawtags == b.rawtags and a.ram == b.ram, ('private/maps', owner, world, mode, flags)
        assert not B.P.differences(B.P.native(a), B.P.native(b)), ('native', owner, world, mode, flags)
        assert bytes(a[0x15a:0x17b]) == bytes(b[0x15a:0x17b]), ('liveSMC', owner)
        assert bytes(a[0x1e0:0x200]) == bytes(b[0x1e0:0x200]), ('liveStack', owner)
        cases.append(dict(owner=owner, world=world, camera=camera, anchorY=y, mode=mode, flags=flags))
    out = dict(passed=True, qualified=False, ROM_written=False, shared_grant=False,
        native_owner_admitted=False, parent_ROM_SHA256=manifest['parent_memory_SHA256'],
        positive_current_owner_memory_SHA256=A.sha(base['raw']),
        memory_only_with_bbox_proposal_SHA256=A.sha(changed['raw']),
        cold=cold, positive_foreign_fullstate_cases=len(cases),
        positive_owners=[36, 37, 38, 39], proposal=proposal,
        scope='Actual current cf7 plus exact Prince130 payload/manager, not a historical cookie or seeded source actor. Real source-bound ShLoad and complete shared Ex/Prince/Bub cold, both full headers, real HuFresh; current Sh/Bub HuFullBox explicitly return handled.144 native-port comparisons preserve complete architecturalAXYP/native application/liveSMC/live stack/private RAM/maps. No DK40 cold/payload/cookie or shared mutation/admission is established.',
        bindings={p.relative_to(R).as_posix(): A.sha(p.read_bytes()) for p in [
            Path(__file__), Path(C.__file__), C.O / 'strike-manifest-v130.json',
            C.O / 'current-shared-cold-CPU-v131.json', sh_source,
            R / 'build/shinobi-bbox-design-1101-v29/resident-design.lbl',
            O / 'native-bbox-v65-layout.json', O / 'native-bbox-gate-v65.bin']})
    (O / 'native-bbox-current-foreign-v72.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ['passed', 'positive_current_owner_memory_SHA256', 'positive_foreign_fullstate_cases', 'cold']}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        (O / 'native-bbox-current-foreign-v72-negative.json').write_text(json.dumps(dict(passed=False, exception=repr(error), ROM_written=False, shared_grant=False), indent=2) + '\n')
        raise
