"""Record bounded source experiment approval for the measured BT JMP router."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
P = R/'build/bt-jmp-row-cold-proposal-v1'
S = R/'tools/reference/bt_jmp_row_cold_proposal_v1.s'
O = R/'docs/qa/checkpoints/2026-10-31/battletoads-jmp-router-resources'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    q = json.loads((P/'proposal.json').read_text())
    assert q['passed'] and q['proposal_only'] and q['source_candidate_not_modified']
    for p, digest in q['bindings'].items():
        assert sha(p) == digest, p
    assert sha(S) == '8c31055ea057928e5693666d0064382d5820d9c61dc5bfe851df5385171aa7c3'
    assert q['current211_to_proposed223_of224']
    assert q['public_table_slot36_worker_offsets'] == [0, 108, 110]
    cases = q['actual_old_target_witnesses']
    assert len(cases) == 108
    for c in cases:
        assert int(c['target'], 16) == 0xb020+3*c['service']
        assert c['raw'] in [27, 31, 33]
    src = S.read_text()
    assert src.index('lda FarcallJmpTarget_SMC+1') < src.index('jsr FarCallCommon')
    assert '.assert *-BtServiceVeneers=223' in src
    O.mkdir(parents=True)
    receipt = dict(status='APPROVED_PRIVATE_SOURCE_LINK_EXPERIMENT_ONLY', reviewer='root',
        source=True, native=False, installed=False, ready=False, admission=False,
        candidate_to_modify='New disposable successor only; frozen38a6/8961 leaves and installed68 remain immutable.',
        additional_ROM_RAM_CHR_bytes=0, existing_span='B020..<B100,224B', measured_proposed_bytes=223,
        fixed_public_entries=['B020 service table', 'B08C slot36 rejection', 'B08E router'],
        required=[
            'Actual linked import values and post-disassembly, not unresolved proposal object alone.',
            'All36 public SFC paths for27/31/33 plus privateCfLoad15 preserve real caller continuation after removal of the rowJSR frame.',
            'All flags, foreign rejections and full-cookie states: nativeAXYP, live page1,33SMC, scratch and raw/shadow mapper state. NativeFlags restored before worker, rejectedC only cleared.',
            'Real normal/lag/pausedNMI and legalIRQ at target capture, published-shadow mapper gap, bank changes and returns.',
            'Current-parent Main/menu/Bowser/CF cold-warm regressions. Bind source receipts to exact linked child.',
            'Before admission: actualCfRetire before everyC2 overwrite and genuine row32/native-world behavior; these remain unresolved by the size proposal.',
            'No native launch, unlock, installed ROM change or additional resource use under this experiment approval.'
        ],
        bindings={str(p.resolve()): sha(p) for p in [Path(__file__), P/'proposal.json', S,
            P/'post-source.lst', P/'post.o', P/'pre-disassembly.json', P/'build.json']})
    out = O/'root-review.json'
    out.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(review=str(out), sha256=sha(out), additional_bytes=0)))


if __name__ == '__main__':
    main()
