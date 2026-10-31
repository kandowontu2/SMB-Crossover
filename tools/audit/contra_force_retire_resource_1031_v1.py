"""Allocate the measured ROM retirement worker beside the external guard."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-retire-proposal-v2/proposal.json'
Q=R/'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json'
G=R/'docs/qa/checkpoints/2026-10-31/contra-force-rom-guard-resources/root-review-and-reservations.json'
D=R/'docs/qa/checkpoints/2026-10-31/contra-force-retire-resources'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    assert sha(P)=='69d141b06c6770492b91c5b3ca741c4ddbec5f04aae91d71c899eaa919a71546'
    p=json.loads(P.read_text())
    for f,h in p['bindings'].items():assert sha(f)==h,f
    assert p['proposed']['bytes']==36 and not p['allocated']
    assert dict(bank=69,start=0x1f47,end=0x2000) in json.loads(Q.read_text())['Quick_Man']['PRG']
    assert json.loads(G.read_text())['ROM']['end_offset_exclusive']==0x1fbd
    reviewed=[];files=[Path(__file__),P,Q,G,R/'tools/reference/contra_force_retire_proposal_v2.s']
    for folder in ['peach-palette-fix-1030-v1','bowser-playable-jump-v1','contra-force-guarded-cart-v2']:
        j=R/'build'/folder/'joint';raw=(j/'candidate.nes').read_bytes()
        lo=16+69*8192+0x1fbd;hi=lo+36
        assert raw[lo:hi]==b'\xff'*36
        segs,syms={},[]
        for line in (j/'candidate.dbg').read_text().splitlines():
            if line.startswith(('seg\t','sym\t')):
                q=dict(x.split('=',1) for x in line[4:].split(',') if '=' in x)
                if line.startswith('seg\t'):segs[q['id']]=q
                elif 'val' in q:syms.append(q)
        assert not [q for q in segs.values() if 'ooffs' in q and int(q['ooffs'],0)<hi and int(q['ooffs'],0)+int(q['size'],0)>lo]
        aliases=[]
        for q in syms:
            v=int(q['val'],0)
            if 'seg' in q and 'ooffs' in segs[q['seg']]:
                s=segs[q['seg']];pos=int(s['ooffs'],0)+v-int(s['start'],0)
                # The external guard's end label may sit on this next span.
                if lo<=pos<hi:
                    assert folder=='contra-force-guarded-cart-v2' and pos==lo and q['name']=='"CfExternalGuardEnd"',q
            elif 'seg' not in q and any(base+0x1fbd<=v<base+0x1fe1 for base in [0xa000,0xc000]):
                assert q['name']=='"AR_CACHE_VALID"' and v==0xdfe0,q
                aliases.append(dict(name='AR_CACHE_VALID',value=v,owner='rawRAM2 C data; never ROM69'))
        reviewed.append(dict(joint=str(j),ROM_sha256=sha(j/'candidate.nes'),
            emitted_conflicts=0,classified_temporal_aliases=aliases,
            preimage_sha256=hashlib.sha256(raw[lo:hi]).hexdigest()))
        files += [j/'candidate.nes',j/'candidate.dbg',j/'private.cfg']
    # Bind the declaration establishing the temporal C2 alias, not just FF.
    files += [R/'build/bowser-playable-jump-v1/joint/arthur/cache-wrapper.s']
    assert all(f.is_file() for f in files)
    d=dict(status='PRIVATE_EXACT_CF_RETIRE_ROM_SOURCE_GRANT',native=False,installed=False,
        lifecycle_hooks_granted=False,
        ROM=dict(physical_bank=69,first_offset=0x1fbd,end_offset_exclusive=0x1fe1,
            bytes=36,execution_view='A',CPU_start=0xbfbd),
        authority='36B subset of prior Quick lease, immediately after the separately allocated118B guard',
        reviewed=reviewed,constraints=[
            'Only source-built successors. Preserve all public entries and adjacent bytes; remaining31B is ungranted.',
            'Full caller AXYP/SP/live stack and all33SMC unchanged; restore origin rawC; no guest opcode.',
            'Clear only C2 DFE0 if family byte DFE1 equals31, including malformed/stale CF; foreign families untouched.',
            'Common owner separately composes every required Menu/Start/scene/player/lifecycle and foreign RAM3 replacement path before its first destructive write.',
            'Run actual full-flag/all-cookie/foreign-state and real normal/lag/paused-NMI/IRQ controls before adopting.',
            'No new global/ZP/RAM/CHR lease; no readiness, native, complete lifecycle coverage or installation claim.'
        ],bindings={str(f):sha(f) for f in files})
    D.mkdir(parents=True);out=D/'root-review-and-reservations.json'
    out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(grant=str(out),sha256=sha(out),bytes=36)))


if __name__=='__main__':main()
