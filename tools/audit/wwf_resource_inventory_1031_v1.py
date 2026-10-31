"""Read-only current-cart physical inventory; no reclamation or host grant."""
from pathlib import Path
import collections,hashlib,json,re
R=Path(__file__).resolve().parents[2]
J=R/'build/bt-ready-menu-1031-v2/joint';O=R/'build/wwf-resource-inventory-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fields(line):
    return {k:v[1:-1]if v.startswith('"')else int(v,0)if re.fullmatch(r'(?:0x[0-9a-fA-F]+|\d+)',v)else v for k,v in re.findall(r'(\w+)=("[^"\r\n]*"|[^,\r\n]+)',line)}

def main():
    assert not (O/'inventory.json').exists();O.mkdir(exist_ok=True)
    raw=(J/'candidate.nes').read_bytes();assert sha(J/'candidate.nes')=='f0b7b9b80ac59b546cee599b9efcb5337b970b11638a669ace78a67dd024724d'
    assert len(raw)==16+1048576*2
    seg=[fields(s)for s in (J/'candidate.dbg').read_text().splitlines()if s.startswith('seg\t')]
    chrseg=[s for s in seg if s.get('ooffs',0)>=16+1048576 and s['size']]
    chr=raw[16+1048576:];pages=[]
    for p in range(1024):
        blob=chr[p*1024:(p+1)*1024];off=16+1048576+p*1024
        pages.append(dict(page=p,sha256=hashlib.sha256(blob).hexdigest(),zero=not any(blob),owners=[s['name']for s in chrseg if s['ooffs']<off+1024 and off<s['ooffs']+s['size']]))
    groups=collections.defaultdict(list)
    for p in pages:groups[p['sha256']].append(p['page'])
    owners=[]
    for s in chrseg:
        lo=(s['ooffs']-16-1048576)//1024;hi=(s['ooffs']-16-1048576+s['size']+1023)//1024
        owners.append(dict(segment=s['name'],start_page=lo,end_page=hi,bytes=s['size'],unique_page_hashes=len({pages[p]['sha256']for p in range(lo,hi)}),zero_pages=[p for p in range(lo,hi)if pages[p]['zero']]))
    prgseg=[s for s in seg if 16<=s.get('ooffs',0)<16+1048576 and s['size']]
    banks=[]
    for b in range(128):
        lo=16+b*8192;mask=bytearray(8192);names=[]
        for s in prgseg:
            a,z=max(lo,s['ooffs']),min(lo+8192,s['ooffs']+s['size'])
            if a<z:mask[a-lo:z-lo]=b'\1'*(z-a);names.append(s['name'])
        gaps=[];a=0
        while a<8192:
            if mask[a]:a+=1;continue
            z=a+1
            while z<8192 and not mask[z]:z+=1
            data=raw[lo+a:lo+z]
            gaps.append(dict(offset=a,end=z,size=z-a,all_ff=all(v==255 for v in data),sha256=hashlib.sha256(data).hexdigest()))
            a=z
        banks.append(dict(bank=b,emitted_bytes=sum(mask),segments=names,unemitted_intervals=gaps))
    q=dict(read_only=True,no_allocation=True,candidate=sha(J/'candidate.nes'),CHR_bytes=len(chr),CHR_page_count=1024,unique_1KiB_hashes=len(groups),zero_pages=[p['page']for p in pages if p['zero']],emitted_chr_segments=owners,pages=pages,duplicate_groups=[v for v in groups.values()if len(v)>1],PRG_banks=banks,limits=['Repeated/zero/unemitted data are not free resources. Actual source consumers and owner release must be proven separately.','Carrier pages are code/data, never blanket CHR-art dedup candidates.'])
    q['bindings']={str(p):sha(p)for p in [Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'private.cfg',J.parent/'source-stage.json']}
    (O/'inventory.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(unique_1KiB_hashes=len(groups),zero_pages=q['zero_pages'],owners=sorted(owners,key=lambda x:(x['end_page']-x['start_page']-x['unique_page_hashes']),reverse=True)[:15],PRG_unemitted_sum=sum(8192-b['emitted_bytes']for b in banks))))
if __name__=='__main__':main()
