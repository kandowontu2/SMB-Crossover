"""Reject overlap between current Metal, Tank and Shinobi integration grants."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];D=R/'docs/qa/checkpoints/2026-11-01'
O=R/'build/pending-roster-allocations-1101-v1'
def main():
    bindings={}
    def read(name):
        p=D/name;data=p.read_bytes();bindings[str(p)]=hashlib.sha256(data).hexdigest();return json.loads(data)
    metal=read('metal-storm-owning-resource-grant.json')
    prg=[('Metal',*v) for v in metal['PRG_intervals_bank_offset_size']]
    for owner,name in [('Metal','metal-storm-prg94-grant.json'),('Tank','mario-tank-prg31-grant.json')]:
        q=read(name);start,end=q['physical_offsets_half_open'];prg.append((owner,q['physical_PRG_bank'],start,end-start))
    for q in read('mario-tank-prg32-33-grant.json')['intervals']:
        start,end=q['physical_offsets_half_open'];prg.append(('Tank',q['physical_PRG_bank'],start,end-start))
    for q in read('mario-tank-prg35-81-86-grant.json')['intervals']:
        start,end=q['physical_offsets_half_open'];prg.append(('Tank',q['physical_PRG_bank'],start,end-start))
    for i,(owner,bank,start,size) in enumerate(prg):
        assert 0<=start<start+size<=8192 and bank!=125
        for other,bank2,start2,size2 in prg[i+1:]:
            assert bank!=bank2 or start+size<=start2 or start2+size2<=start,(owner,other,bank)
    chrq=read('metal-storm-chr-resources-v10/resource-grant.json')
    chrsets={'Metal':set(chrq['Metal_pages']),'Tank':set(chrq['Tank_pages']),
        'Shinobi':set(read('shinobi-chr-resource-grant.json')['physical_CHR_1KB_pages'])}
    seen=set()
    for owner,pages in chrsets.items():
        assert not pages&seen and not pages&{511,512,514,1023},owner
        seen|=pages
    shinobi=read('shinobi-identity-ram-grant.json')
    bridge=read('metal-storm-a3-bridge-grant.json')
    ram={'Metal':[list(v) for v in metal['RAM_intervals_physical_bank_offset_size']],
         'Shinobi':shinobi['RAM_intervals_physical_bank_offset_size']}
    ram['Metal'][0][2]=bridge['extended_actor_offsets_half_open'][1]
    for owner,spans in ram.items():
        for i,(bank,start,size) in enumerate(spans):
            assert bank in [2,3] and 0<=start<start+size<=8192
            for bank2,start2,size2 in spans[i+1:]:
                assert bank!=bank2 or start+size<=start2 or start2+size2<=start,(owner,bank)
    result=dict(passed=True,PRG_intervals=len(prg),CHR_pages={k:sorted(v)for k,v in chrsets.items()},
        conditional_RAM=ram,bindings=bindings,
        scope='Allocation conflict check only. Cross-character RAM overlap requires the granted exclusive-identity retirement protocol; runtime correctness remains unproven.')
    O.mkdir(exist_ok=True);(O/'allocation-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,PRG_intervals=len(prg),CHR_pages=len(seen),RAM_owners=list(ram))))
if __name__=='__main__':main()
