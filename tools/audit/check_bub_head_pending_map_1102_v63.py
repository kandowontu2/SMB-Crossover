"""Source-bound pending C-bank publication in the old SpecialDrawShots macro."""
from collections import Counter
import json
from pathlib import Path
import check_bub_head_nmi_i1_1102_v60 as H
O,N,R,sha=H.O,H.N,H.R,H.sha
PENDING=Counter()

def resume_pending(c,m,maps):
    # Macro source: BankPRGC #.bank(SsArt0Right), expanded as two immediate
    # loads around the cache store. Only this actual reached native site is
    # admitted; every other discrepancy retains the original strict check.
    if c.pc!=0xb771 or m.rawtags[1]!=188:return False
    assert bytes(m[0xb76c:0xb776])==bytes.fromhex('a98d8da17da98d8d1651')
    at=16+60*8192+0x176c
    assert m.bundle['raw'][at:at+10]==bytes.fromhex('a98d8da17da98d8d1651')
    assert N.get(m,'CurrentBankC')==141 and m.rawtags[2]==141
    assert all(maps[k]==m.rawtags[k]for k in[0,1,3])
    before=(c.a,c.x,c.y,c.p,c.sp)
    # Both next instructions are fetched from unchanged A-bank188. LDA#8D
    # has no memory read; STA5116 is the sole C-window bus consumer. There is
    # no C-window data access/fetch, branch, stack write or call beforehand.
    assert bytes(m[c.pc:c.pc+2])==bytes.fromhex('a98d');c.step()
    assert c.pc==0xb773 and bytes(m[c.pc:c.pc+3])==bytes.fromhex('8d1651');c.step()
    assert c.pc==0xb776 and m.rawtags==[maps[0],maps[1],141,maps[3]]
    expected_p=(before[3]&~0x82)|0x80
    assert(c.a,c.x,c.y,c.p,c.sp)==(141,before[1],before[2],expected_p,before[4])
    PENDING['60:B771 actual LDA8D/STA5116 after cache141 publication']+=1
    return True

def patched_run():
    text=H.text.replace('if active or bank==3 and newlo<=c.pc<newhi:','if active or headreturn is not None or bank==3 and newlo<=c.pc<newhi:')
    before="""            if maps!=m.rawtags:
                ins=bytes(m[c.pc:c.pc+3]);assert ins in[bytes.fromhex(x)for x in['8d1551','8d1651','8e1651']]
                window=1 if ins[1]==0x15 else 2
                assert m.rawtags[window]==N.get(m,'CurrentBank'if window==1 else'CurrentBankC')
                assert all(maps[k]==m.rawtags[k]for k in range(4)if k!=window)"""
    after="""            if maps!=m.rawtags:
                if not resume_pending(c,m,maps):
                    ins=bytes(m[c.pc:c.pc+3]);assert ins in[bytes.fromhex(x)for x in['8d1551','8d1651','8e1651']],('Unexpected mapper-return window',interrupt,maps,m.rawtags,hex(c.pc),ins.hex())
                    window=1 if ins[1]==0x15 else 2
                    assert m.rawtags[window]==N.get(m,'CurrentBank'if window==1 else'CurrentBankC')
                    assert all(maps[k]==m.rawtags[k]for k in range(4)if k!=window)"""
    assert text.count(before)==1;text=text.replace(before,after)
    env=dict(H.env,resume_pending=resume_pending);exec(compile(text,str(Path(__file__)),'exec'),env)
    return env['run'],env

def main():
    _,b,route,q,p,_=H.P.H.bundle();run,env=patched_run();rows=[]
    for identity in[0,1]:
        m,_=H.seeds(b,route)[identity];z=N.fork(m);ref=run(z,p,q);want=H.state(z)
        # Only the exact retained macro negative is replayed here; the full
        # expanded domain belongs to nested qualification, not this oracle.
        count=0
        focused=[cut for cut in ref['cuts']if cut[0]==0xb771];assert len(focused)==1
        for cut in focused:
            z=N.fork(m);out=run(z,p,q,('lagNMI',cut))
            assert out['regs']==ref['regs']and H.state(z)==want,(identity,cut)
            count+=1
        rows.append(dict(identity=identity,source_macro_FF_contexts=count,expanded_foreground_contexts=len(ref['cuts'])))
    out=dict(passed=True,CPU_only=True,ROM_written=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],scenarios=rows,source_bound_pending_bus_writes=dict(PENDING),
        scope='Retained62 mapper oracle negative is an actual current BankPRGC immediate macro: cache141 is stored before a second LDA8D/STA5116. NMI restores cached141 early. Exact10B preimage at physical60:B76C, same unchanged A-window fetches, exact two instructions, no affected-C read/fetch before bus consume, same AXYP effect as uninterrupted prefix; every other window/state remains strict. No mapper state normalization or ROM change.',
        bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(H.__file__),O/'head-projection-v62-map-negative.json',R/'src/mmc5.s',R/'src/special_weapons.s',O/'head-projection-v55.json']})
    (O/'head-projection-v63-pending-map.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':main()
