"""Read-only current13x5 caller-plane funding census, no proposed code."""
from hashlib import sha256
from pathlib import Path
from collections import Counter
import json

PIN='91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc'
H=lambda b:sha256(b).hexdigest()


def run(raw):
    assert H(raw)==PIN
    page=raw[16+124*8192:16+125*8192];rows=[];sharing=Counter()
    for i in range(len(page)-42):
        c=page[i:i+27]
        if c[:9]!=bytes.fromhex('8d6a0108984820cca1'):continue
        if not(c[9]==c[15]==c[21]==0xb9 and c[12:15]==bytes.fromhex('8d6c01')and c[18:21]==bytes.fromhex('8d6d01')and c[24:27]==bytes.fromhex('4c0da6')):continue
        planes=[int.from_bytes(c[j:j+2],'little')for j in(10,16,22)]
        data=[page[p&8191:(p&8191)+5]for p in planes]
        sharing[data[2].hex()]+=1
        rows.append(dict(PC=0xa000+i,file=16+124*8192+i,code27_SHA256=H(c),code27_hex=c.hex(),
            plane_CPU=planes,Lo_hex=data[0].hex(),Hi_hex=data[1].hex(),Bank_hex=data[2].hex(),
            targets=[dict(row=j,PC=data[0][j]+256*data[1][j],bank=data[2][j])for j in range(5)]))
    assert len(rows)==13
    current_planes={r['plane_CPU'][2]for r in rows}
    current_bytes=set().union(*(set(range(p,p+5))for p in current_planes))
    q=dict(parent_SHA256=PIN,fronts13=rows,identical_bank_plane_groups=dict(sharing),
        gross_bank_plane_traversal_bytes=65,current_unique_bank_plane_CPU=sorted(current_planes),
        actual_current_unique_bank_plane_bytes=len(current_bytes),ideal_shared_bank_plane_bytes=5*len(sharing),
        theoretical_bytes_from_bank_dedup=len(current_bytes)-5*len(sharing),
        funding_not_qualified=True,unresolved=['All external plane readers and source-owned containing extents',
            'Actual raw31 classifier/command meaning and all13 public old row contracts',
            'Any new row/index admission must preserve all old/unknown selector paths'],
        no_new_arrays_no_CPU_no_overlay=True,outputs=0)
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    print('RESULT '+json.dumps(run(raw),separators=(',',':')),flush=True)
