"""Read current linked gaps and duplicates; no memory or storage allocation."""
from pathlib import Path
import collections,hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
J=R/'build/doki-current-component-1101-v1';O=R/'build/karnov-current-resource-audit-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);b=scoped_load(J/'candidate.nes');segments=list(b['segs'].values());raw=b['raw'];gaps=[]
    for bank in range(128):
        base=16+bank*8192;mask=bytearray(8192)
        for s in segments:
            lo=int(s.get('ooffs','0'),0);n=int(s['size'],0);a,z=max(base,lo),min(base+8192,lo+n)
            if a<z:mask[a-base:z-base]=bytes([1])*(z-a)
        at=0
        while at<8192:
            if mask[at]:at+=1;continue
            end=at+1
            while end<8192 and not mask[end]:end+=1
            if end-at>=32:gaps.append(dict(bank=bank,start=at,end=end,bytes=end-at,all_ff=set(raw[base+at:base+end])=={255},preimage_sha256=hashlib.sha256(raw[base+at:base+end]).hexdigest()))
            at=end
    pages=[];dup=collections.defaultdict(list)
    for p in range(1024):
        base=1048592+p*1024;data=raw[base:base+1024];owners=[]
        for s in segments:
            a=int(s.get('ooffs','0'),0);z=a+int(s['size'],0)
            if a<base+1024 and base<z:owners.append(s['name'].strip('"'))
        item=dict(page=p,zero=not any(data),sha256=hashlib.sha256(data).hexdigest(),owners=owners);pages.append(item);dup[item['sha256']].append(p)
    q=dict(passed=True,read_only=True,no_allocation=True,candidate=sha(J/'candidate.nes'),PRG_unemitted_intervals=gaps,CHR_unemitted_pages=[p['page']for p in pages if not p['owners']],CHR_zero_pages=[p['page']for p in pages if p['zero']],CHR_duplicate_groups=[v for v in dup.values()if len(v)>1],pages=pages,scope='Linked emission coverage only. Zero, duplicate, or unemitted bytes are not free until actual source consumers and owner storage contracts are checked.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'candidate.cfg',J/'source-stage.json']})
    (O/'inventory.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(PRG_largest=sorted(gaps,key=lambda q:q['bytes'],reverse=True)[:16],CHR_unemitted=q['CHR_unemitted_pages'],CHR_zero_count=len(q['CHR_zero_pages']),high_pages=pages[1016:])))


if __name__=='__main__':main()
