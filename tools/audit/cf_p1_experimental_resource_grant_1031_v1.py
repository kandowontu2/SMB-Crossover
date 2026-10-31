"""Reserve exact private P1 experiment resources, requiring executed closure."""
from pathlib import Path
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location


def main():
    proposal=R/'build/contra-force-p1-shared-factor-proposal-v3/proposal.json'
    controls=R/'build/contra-force-p1-classifier-controls-v1/controls.json'
    assert B.sha(proposal)=='789fe2855d8e8355eac784e904158da3c544aae4deb2a0294df047cf823b19da'
    assert B.sha(controls)=='87d80212d8fd2e062812121848d091941d47b6b2350991973ec1e69e67db6800'
    p,c=[json.loads(B.read(x)) for x in [proposal,controls]]
    B.bound(p);B.bound(c)
    assert p['measured_source_size']==57 and p['current_bridge']['span']==59
    assert c['passed'] and c['all256raw_64flags_4states_3incomingA_classifier_cases']==196608
    assert c['actual_old_vs_near_tail_source_setup_pairs']==16384
    j=R/'build/cf-cold-warm-palette-source-v1/joint';b=scoped_load(j/'candidate.nes')
    assert B.sha(j/'candidate.nes')=='ef2f11e232ec878c277245c3802bcf8a415415e38507c26feefaef3744c1bee1'
    mailbox={n:address(b,n) for n in ['SmFreezePalettePacket','SmFreezePalettePending','SmFreezeLastBlue','SmFreezeTurn']}
    protected={n:address(b,n) for n in ['SmFreezeRenderState','SmFreezePaletteControl']}
    leased=set(range(mailbox['SmFreezePalettePacket'],mailbox['SmFreezePalettePacket']+7))
    leased.update(mailbox[n] for n in mailbox if n!='SmFreezePalettePacket')
    assert len(leased)==10 and not leased.intersection(protected.values())
    native_tail=p['source_factoring']['existing_tail'];tail=16+62*8192+native_tail-0xa000
    assert b['raw'][tail:tail+18].hex()==p['source_factoring']['existing_tail_bytes']
    api=R/'build/contra-force-palette-names-qualified-v1/api-and-scope.json'
    # C2 belongs to the selected31 overlay. Its active last-life byte is
    # excluded; this grant does not introduce any new globally resident RAM.
    own=json.loads(B.read(api));kernel=Path(own['kernel'])
    runtime=kernel/'runtime.dbg';labels=kernel/'runtime.lbl';ram2=kernel/'ram2.bin'
    names={int(m[1],16) for m in re.finditer(r'^al ([0-9A-Fa-f]+) \.CfHostLastLife$',B.read(labels),re.M)}
    assert names=={0xddb8}
    for line in B.read(runtime).splitlines():
        if line.startswith('seg\t'):
            seg=dict(x.split('=',1) for x in line[4:].split(',') if '=' in x)
            at=int(seg.get('start','0'),0);size=int(seg.get('size','0'),0)
            assert not(size and at<0xddd2 and at+size>0xddb9),seg
    assert ram2.read_bytes()[0x1db9:0x1dd2]==bytes([255])*25
    out=R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/root-review-and-reservations.json'
    assert not out.exists();out.parent.mkdir(parents=True)
    receipt=dict(status='PRIVATE_EXPERIMENT_ONLY_CF_PAIRED_OAM_PALETTE_RESOURCE_GRANT',source=True,native=False,
        installed=False,ready=False,admission=False,parent=B.sha(j/'candidate.nes'),
        shared_source=dict(physical_ROM=62,first=p['current_bridge']['PC'],bytes=59,
            allowed='Exact57B measured selector plus2EA inside the original59B span. Zero-byte label at the actual18B FfMuxRomNative tail. No new code span.'),
        own_C2=dict(raw_RAM=2,first=0xddb9,end_exclusive=0xddd2,bytes=25,
            protected_last_life=0xddb8,scope='24 original native actor attributes and one completed native C result; selected31 temporal overlay only.'),
        temporal_global_aliases=dict(addresses=mailbox,bytes=10,exclusive_owner='Authenticated selected31 epoch, with retirement before foreign publication'),
        protected_globals=protected,
        required_before_any_admission=[
            'Preserve original foreign A/P/X/Y/live stack/33SMC/raw maps; prove actual emitted shared selector, not only abstract model. Classify31 before stale Samus state without writing protected State/Control or FF body ACK.',
            'Authenticate complete16 cookie/class in ROM before every first A2; invalid/abandoned paths run genuine native DrawAll exactly once and leave no CF producer.',
            'Save/restore all24 real native attributes. Tag and filter complete native/P1-shot groups, then strip ignored marker bits. Body remains native-authentic P0. Do not add OAM or change CHR.',
            'Complete paired palette packet and OAM before LastBlue C0/C1 and publish Pending LAST. Actual pre/post flush, full queue, noFX, sprite pressure, lag, paused/skipped draw and normalNMI/IRQ cuts must keep palette paired with rendered OAM.',
            'Execute acquisition/retirement before every foreign Selected/OAM/WRAM writer and warm/death/player/area transition. Reuse existing proven retirement only if actual execution establishes it. Additional shared code/state requires another concrete review.',
            'Run exact current66 foreign/UI/audio/control regressions and own CF native source pixels/PPU/group closure before proposing readiness. Root owns Mesen and final installation.'
        ],
        limits='Permission to construct a reviewable private source successor. No readiness, native gameplay, perfect emulation, installation or goal completion is inferred.',
        bindings={str(x):B.sha(x) for x in [Path(__file__),proposal,controls,api,runtime,labels,ram2,j/'candidate.nes',j/'candidate.dbg',j/'private.cfg']})
    B.write(out,json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(grant=str(out),sha256=B.sha(out),shared_new_bytes=0,own_C2_bytes=25,temporal_alias_bytes=10)))


if __name__=='__main__':main()
