"""Reject overlap between current Metal, Tank and Shinobi integration grants."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];D=R/'docs/qa/checkpoints/2026-11-01'
sys.path.insert(0,str(R/'tools'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/pending-roster-allocations-1101-v1'

def verify_tank_tail_baseline(grant):
    """Check reviewed predecessor bytes, not a partially patched successor."""
    path=R/'build/karnov-native-platform-1101-v1/candidate.nes'
    b=scoped_load(path);raw=b['raw']
    assert hashlib.sha256(raw).hexdigest()==grant['baseline_ROM_sha256']
    checked=[]
    for row in grant['intervals']:
        bank=row['physical_PRG_bank'];start,end=row['physical_offsets_half_open']
        image=raw[16+bank*8192:16+(bank+1)*8192]
        assert hashlib.sha256(image).hexdigest()==row['bank_sha256'],('Changed predecessor bank',bank)
        assert image[start:end]==bytes([255])*(end-start),('Occupied allocation',bank)
        name=row['old_end_symbol'];symbol=b['syms'][name]
        typed_sizes={'CfLoaderExpectedCookie':16,'MaaNeckOdd':3,'GmStage0Palette':16,'X5MusicBank0F':405}
        if name=='SsNativeChunk':
            size=1+raw[location(b,name)]
            assert size==5
        elif name in typed_sizes:size=typed_sizes[name]
        else:size=int(symbol['size'],0)
        assert address(b,name)+size==row['old_end_PC'],('Producer endpoint changed',name)
        assert location(b,name)+size==16+bank*8192+start,('Producer not adjacent',name)
        checked.append(dict(bank=bank,old_end=row['old_end_PC'],bytes=end-start))
    return checked
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
    tails=read('mario-tank-code-tail-grant.json')
    verified_tails=verify_tank_tail_baseline(tails)
    for q in tails['intervals']:
        start,end=q['physical_offsets_half_open'];prg.append(('Tank',q['physical_PRG_bank'],start,end-start))
    art=read('mario-tank-art-tail-grant.json')
    verified_tails.extend(verify_tank_tail_baseline(art))
    for q in art['intervals']:
        start,end=q['physical_offsets_half_open'];prg.append(('Tank',q['physical_PRG_bank'],start,end-start))
    music=read('mario-tank-music-tail-grant.json')
    verified_tails.extend(verify_tank_tail_baseline(music))
    for q in music['intervals']:
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
         'Shinobi':shinobi['RAM_intervals_physical_bank_offset_size'],
         'Tank':read('mario-tank-ram-grant.json')['RAM_intervals_physical_bank_offset_size']}
    ram['Metal'][0][2]=bridge['extended_actor_offsets_half_open'][1]
    for owner,spans in ram.items():
        for i,(bank,start,size) in enumerate(spans):
            assert bank in [2,3] and 0<=start<start+size<=8192
            for bank2,start2,size2 in spans[i+1:]:
                assert bank!=bank2 or start+size<=start2 or start2+size2<=start,(owner,bank)
    result=dict(passed=True,PRG_intervals=len(prg),CHR_pages={k:sorted(v)for k,v in chrsets.items()},
        conditional_RAM=ram,verified_Tank_predecessor_tails=verified_tails,bindings=bindings,
        scope='Allocation conflict check only. Cross-character RAM overlap requires the granted exclusive-identity retirement protocol; runtime correctness remains unproven.')
    O.mkdir(exist_ok=True);(O/'allocation-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,PRG_intervals=len(prg),CHR_pages=len(seen),RAM_owners=list(ram))))
if __name__=='__main__':main()
