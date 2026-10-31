"""Reserve67 source-qualified M3 table bytes for the CF ROM palette repair."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load


def main():
    qpath = R/'build/smb3plus-low-table-factor-host-1031-v4/cf-67-byte-proposal.json'
    hpath = R/'docs/qa/checkpoints/2026-10-31/smb3plus-low-table-factor-v1/handoff.json'
    ppath = R/'build/contra-force-p1-native-restore-proposal-v1/proposal.json'
    assert B.sha(qpath) == '3deb9a9e72f874f83924bfc2a82e101c2040fe33c555d675c61a79f49b255137'
    assert B.sha(hpath) == 'fea3b4521242846abe7b38053f2bb0283d261c626cd351c1ba48f3d405fdb260'
    assert B.sha(ppath) == 'af8ae0fe63d7a69609f1b0d08c37b8a25ed450aa3054f59770eb217c796dd4e5'
    q, h, p = [json.loads(B.read(v)) for v in [qpath, hpath, ppath]]
    for value in [q, h, p]:
        B.bound(value)
    assert q['physical_bank'] == 91 and q['A_begin'] == 0xae97 and q['A_end'] == 0xaeda and q['bytes'] == 67
    assert p['measured']['any_A_ROM']['bytes'] == 67
    folder = R/'build/smb3plus-low-table-factor-host-1031-v4'
    controls = []
    for n in ['refs-consumer', 'regressions-factor', 'helper-factor', 'pixels-factor',
              'vectors-factor', 'vectors-consumer', 'foreign-factor', 'menu-factor', 'whole-factor']:
        path = folder/(n+'-controls-v1.json')
        d = json.loads(B.read(path)); B.bound(d)
        assert d['passed'] and d['candidate'] == q['candidate']
        controls.append(path)
    b = scoped_load(folder/'joint/candidate.nes')
    lo = q['file_begin']; hi = lo+67
    assert lo == 16+91*8192+0xe97
    assert b['raw'][lo-7:lo] == bytes([0,4,4,244,0,248,252])
    assert b['raw'][lo:hi] == bytes([0xea])*67
    assert hashlib.sha256(b['raw'][lo:hi]).hexdigest() == q['preimage_sha256']
    # The alternate93 proposal is not padding: preserve the actual bbox owner.
    current = scoped_load(R/'build/smb3plus-current66-source-1031-v2/joint/candidate.nes')
    bbox = 16+93*8192+0xfa7
    assert current['raw'][bbox:bbox+4] == bytes.fromhex('0848ad02')
    assert any(s.get('name') == '"HOST_BBOX_LOCAL"' and int(s['ooffs'],0) == bbox
               and int(s['size'],0) == 79 for s in current['segs'].values() if 'ooffs' in s)
    out = R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/native-restore-factor-grant-v1.json'
    assert not out.exists()
    d = dict(status='PRIVATE_SOURCE_CF_RESTORE67_GRANT_WITH_FACTOR_PREREQUISITE',
        source=True, native=False, installed=False, ready=False, admission=False,
        prerequisite_candidate=q['candidate'], installed68_modified=False,
        physical_bank=91, A_start='AE97', A_end_exclusive='AEDA',
        C_start='CE97', C_end_exclusive='CEDA', file_begin=lo, bytes=67,
        preimage_sha256=q['preimage_sha256'], former_owner='Now-dead low-table suffix after MbChrOffsets seven bytes',
        remaining_reclaimed_M3_bytes=331, new_RAM_CHR_OAM_bytes=0,
        rejected_alternative=dict(bank=93, A_start='AFA7', reason='Live79B HuPlayerSubsAdapter/HOST_BBOX_LOCAL, not free; preserve exact.'),
        constraints=[
            'Compose the genuine qualified e54b91fa M3 factoring source FIRST. Installed01a4 and older CF parents still have live table data here and must not be overwritten.',
            'Use the measured67B any-A-ROM worker with real A-view labels/imports, not C-view PCs. Emit through actual source assembly/link recipes; no post-link ROM patch.',
            'Preserve all other M3/foreign bytes, MbChrOffsets7, complete caller ABI/pointers and remaining331B. New exact compiled source must establish all size/PC assertions.',
            'Keep FwMuxNativeSelect as a zero-byte entry after genuine spriteclear. Repair only CF LastC0/C1; Pending invalidated first, complete nativeC0 packet last; preserve Turn, State, Control, OAM and FF ACK.',
            'Restore callerAXYP before real guarded B020 service6. No firstA2 on invalid/stale/corrupt cookie, no duplicate native draw. Keep all prior4dc4/5e70 constraints.',
            'Qualify actual paired OAM/nativePPU with valid/invalid cache, fullqueue/late native writers/pause/lag/retirement. Preserve genuine common cold/warm/menu sources and current68 M3 before eventual native checks.',
            'Source experiment only; root owns final join, native launch, readiness and Downloads installation.'
        ],
        bindings={str(v.resolve()): B.sha(v) for v in [Path(__file__), qpath, hpath, ppath, *controls,
            folder/'joint/candidate.nes', folder/'joint/candidate.dbg', folder/'joint/src/smb3_mario_art.inc',
            R/'build/smb3plus-current66-source-1031-v2/joint/candidate.nes',
            R/'build/smb3plus-current66-source-1031-v2/joint/candidate.dbg']})
    B.write(out, json.dumps(d, indent=2)+'\n')
    print(json.dumps(dict(grant=str(out), sha256=B.sha(out), bytes=67, prerequisite=q['candidate'])))


if __name__ == '__main__':
    main()
