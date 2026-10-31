"""Root reserves the measured17/24B ROM stubs; no readiness is granted."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load

P=R/'build/cf-cold-warm-resource-proposal-v1/proposal.json'
D=R/'docs/qa/checkpoints/2026-10-31/contra-force-cold-warm-resources'


def main():
    assert not D.exists()
    assert B.sha(P)=='7357aa7067966a117fcd63a2cf251ff25df00d59b5ccc1341b900b7c689d1161'
    proposal=json.loads(B.read(P));B.bound(proposal)
    assert proposal['total_new_bytes']==41 and proposal['no_new_RAM_CHR_or_global']
    reviewed=[];files=[Path(__file__),P,R/'tools/reference/cf_cold_warm_resource_proposal_v1.s']
    for folder in ['bowser-playable-jump-v1','cf-owner-retirement-v2','smb3plus-menu-host-1031-v4']:
        j=R/'build'/folder/'joint';b=scoped_load(j/'candidate.nes')
        for request in proposal['requested_new_ROM']:
            bank=request['physical_ROM'];first=int(request['A_start'],16)-0xa000
            end=int(request['A_end_exclusive'],16)-0xa000
            lo=16+bank*8192+first;hi=16+bank*8192+end
            pre=b['raw'][lo:hi];assert pre==bytes([255])*request['bytes']
            assert hashlib.sha256(pre).hexdigest()==request['preimage_SHA256']
            for seg in b['segs'].values():
                if 'ooffs' not in seg:continue
                at=int(seg['ooffs'],0);n=int(seg['size'],0)
                assert not (n and at<hi and at+n>lo),seg
            aliases=set()
            for name,sym in b['syms'].items():
                if 'val' not in sym:continue
                val=int(sym['val'],0)
                if 'seg' in sym and 'ooffs' in b['segs'][sym['seg']]:
                    seg=b['segs'][sym['seg']]
                    at=int(seg['ooffs'],0)+val-int(seg['start'],0)
                    if lo<=at<hi:
                        assert folder=='cf-owner-retirement-v2' and at==lo and name=='CfRetireEnd',name
                elif 'seg' not in sym and any(base+first<=val<base+end for base in [0xa000,0xc000]):
                    assert name in ['AR_CACHE_VALID','AR_CACHE_FAMILY','AR_CACHE_VERSION'],name
                    aliases.add((name,val))
            reviewed.append(dict(joint=str(j),candidate=B.sha(j/'candidate.nes'),bank=bank,
                first=request['A_start'],end_exclusive=request['A_end_exclusive'],
                preimage_sha256=hashlib.sha256(pre).hexdigest(),no_emitted_conflict=True,
                classified_aliases=[dict(name=n,value=v,owner='rawRAM2 C Arthur cache metadata, never this ROM bank') for n,v in sorted(aliases)]))
        files += [j/'candidate.nes',j/'candidate.dbg',j/'private.cfg']
    cache=R/'build/bowser-playable-jump-v1/joint/arthur/cache-wrapper.s'
    assert cache.is_file();files.append(cache)
    d=dict(status='PRIVATE_EXACT_CF_COLD_WARM_STUB_ROM_GRANT',source=True,native=False,installed=False,
        requested_new_ROM=[dict(q,granted=True) for q in proposal['requested_new_ROM']],
        total_bytes=41,no_new_RAM_CHR_or_global=True,reviewed=reviewed,
        constraints=[
            'Only17B ROM69 BFE1..<BFF2 and24B ROM115 BFCB..<BFE3. Other remaining tails are not granted.',
            'Source-built successors only; preserve adjacent public entries/header/CHR and original caller/live stack/33SMC/raw maps.',
            'Scene-only selected31 retirement bypass requires proven invalidation before every foreign C2/A3 writer. Menu retirement stays unconditional before Selected publication.',
            'Warm loading must authenticate full16 cookie/class in ROM before first A2; cold path keeps all original forcedblank, negativeNMI, OperMode, busy-bit and copy/readback conditions.',
            'Invalid15/19 require the genuine native fallback once. Own CF scene ensure/reset must explicitly preserve earned health/gear while handling death/life/class/player changes.',
            'Shared Start/selector source factoring stays inside prior measured owned envelopes. BTrouter owner gate requires its separate owner review.',
            'Actual menu, parser, warm/life/player, all-current66 foreign, fullflag and normal/paused/lagNMI/IRQ tests required before adoption.',
            'No palette/mailbox/NMI/shared-hook/global-state lease, readiness, native-gameplay, admission or installation is granted.'
        ],bindings={str(p):B.sha(p) for p in files})
    D.mkdir(parents=True);p=D/'root-review-and-reservations.json';B.write(p,json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(grant=str(p),sha256=B.sha(p),bytes=41)))


if __name__=='__main__':main()
