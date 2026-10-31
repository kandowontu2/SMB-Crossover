"""Reserve the measured18B extension while keeping Bowser's ctor intact."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load


def main():
    p=R/'build/cf-cold-warm-resource-proposal-v3/proposal.json'
    prior=R/'docs/qa/checkpoints/2026-10-31/contra-force-cold-warm-resources/root-review-and-reservations.json'
    out=prior.with_name('root-extension-review-v2.json');assert not out.exists()
    assert B.sha(p)=='1da1f01e36a28bc1734b94eca9a228ebab59be0687914accb05af6555306c244'
    d=json.loads(B.read(p));B.bound(d)
    assert d['total_new_bytes']==18 and d['granted_warm24_plus_extension18_total42']
    request=d['additional_requested_ROM'];assert len(request)==1
    q=request[0];assert (q['physical_ROM'],q['A_start'],q['A_end_exclusive'],q['bytes'])==(115,'BFE3','BFF5',18)
    lo=16+115*8192+0x1fe3;hi=lo+18;rows=[];files=[Path(__file__),p,prior]
    for folder in ['bowser-playable-jump-v1','cf-owner-retirement-v2','smb3plus-peach-air-frame-1031-v2']:
        j=R/'build'/folder/'joint';b=scoped_load(j/'candidate.nes')
        before=b['raw'][lo:hi];assert before==bytes([255])*18
        assert hashlib.sha256(before).hexdigest()==q['preimage_SHA256']
        for s in b['segs'].values():
            if 'ooffs' in s:
                at=int(s['ooffs'],0);n=int(s['size'],0)
                assert not(n and at<hi and at+n>lo),s
        rows.append(dict(joint=str(j),candidate=B.sha(j/'candidate.nes'),preimage_sha256=hashlib.sha256(before).hexdigest(),no_emitted_conflict=True))
        files.extend([j/'candidate.nes',j/'candidate.dbg',j/'private.cfg'])
    old=json.loads(B.read(prior));B.bound(old)
    receipt=dict(status='PRIVATE_CF_COLD_WARM_EXTENSION_GRANT',source=True,native=False,installed=False,
        additional_ROM=dict(q,granted=True),additional_bytes=18,combined_loader_helper_bytes=42,
        reviewed=rows,previous_constraints=old['constraints'],
        revised_constructor_contract='Keep Bowser27 original15B direct constructor exact. CF helper authenticates/copies and invokes actual guarded B020 row15, then returns C0 so only the separate Bowser ctor is skipped. All success/error exits preserve the existing outer caller contract.',
        no_new_RAM_CHR_global_palette_mailbox_NMI_or_readiness=True,
        note='The old21B/45B hand-count is not granted. This receipt grants exactly18 additional bytes through BFF5; remaining11B stay ungranted.',
        bindings={str(x):B.sha(x) for x in files})
    B.write(out,json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(grant=str(out),sha256=B.sha(out),additional_bytes=18)))


if __name__=='__main__':main()
