"""Read-only current batch boundary/state leads; no capability allocation."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json,re
import contra_force_c2_direct_model_1116 as M

C,W=M.C,M.W


def run(raw):
    assert C.H(raw)==C.PIN
    b=M.symbols(raw)
    names=('SelectedCharacter','FmGroups','FamilyMainCommit','NmiDisable','CurrentBank','CurrentBankC')
    addresses={n:W.address(b,n)for n in names}
    assert addresses['FamilyMainCommit']==0x5fff
    symbols=[]
    for name,s in b['syms'].items():
        if 'seg'not in s or 'val'not in s:continue
        seg=b['segs'][s['seg']]
        if 'ooffs'not in seg or not int(seg.get('size','0'),0):continue
        at=int(seg['ooffs'],0)+int(s['val'],0)-int(seg['start'],0)
        if 16<=at<1048592:symbols.append((at,name,int(s['val'],0),seg['name']))
    def owners(at):
        q=[dict(name=name,PC=pc,delta=at-start,segment=seg)for start,name,pc,seg in symbols
           if 0<=at-start<96 and(start-16)//8192==(at-16)//8192]
        return sorted(q,key=lambda r:r['delta'])[:2]
    direct=[];indexed=[];headers=[];protocol=[]
    store=(0x8d,0x8e,0x8c,0xee,0xce)
    read=(0xad,0xae,0xac,0xcd,0x2d,0x0d,0x2c)
    # This is a literal lead census. Indexed and indirect ranges still need
    # source ownership, bounds and actual map binding; words are not code.
    for bank in range(128):
        page=raw[16+bank*8192:16+(bank+1)*8192]
        for i in range(8190):
            op=page[i];arg=int.from_bytes(page[i+1:i+3],'little');at=16+bank*8192+i
            kind=('direct'if op in store+read and arg==0x5ffe else
                  'indexed'if op in(0x99,0x9d,0xb9,0xbd)and 0x5eff<=arg<=0x5ffe else
                  'protocol'if op in store+read and arg==0x5fff else
                  'header'if op in store and arg in tuple(range(0xbfe0,0xbff0))+tuple(range(0xdfe0,0xdff0))else None)
            if kind:
                row=dict(bank=bank,PC=0xa000+i,file=at,opcode=op,operand=arg,
                         bytes=page[max(0,i-3):i+9].hex(),symbols=owners(at))
                {'direct':direct,'indexed':indexed,'protocol':protocol,'header':headers}[kind].append(row)
    # The 79B private tail is separately source-owned; a header trailer is
    # NOT inferred free from its current data. Any state requires a lease.
    cf=raw[2006032:2030608]
    cf_state_leads=[]
    for tag in(1,2,3):
        page=cf[(tag-1)*8192:tag*8192]
        for i in range(8190):
            op=page[i];arg=int.from_bytes(page[i+1:i+3],'little')
            if op in store+read and arg==0x5ffe:
                cf_state_leads.append(dict(tag=tag,PC=0xa000+i,opcode=op,operand=arg))
    q=dict(parent_SHA256=C.PIN,actual_parent_only=True,addresses=addresses,
        current_PRG63_protocol_512_SHA256=C.H(raw[16+63*8192+0x1400:16+63*8192+0x1600]),
        actual_Main_gate49_hex=raw[16+63*8192+0x1400:16+63*8192+0x1431].hex(),
        old_global_capacity_lead_5FFE=dict(direct_literal_leads=direct,indexed_leads=indexed,
            CF_private_direct_leads=cf_state_leads,not_allocated=True,
            unresolved='All indexed/indirect writers, decoded containers, later state leases and foreign lifecycle access must close before allocation.'),
        protocol_literal_leads=protocol,protocol_lead_counts=dict(Counter(('store'if r['opcode']in store else'read')for r in protocol)),
        direct_header_store_leads=headers,header_leads_by_bank=dict(Counter(r['bank']for r in headers)),
        current_headers=dict(RAM2=cf[16352:16368].hex(),RAM3=cf[24544:24560].hex(),
            trailer_RAM2=cf[16368:16384].hex(),trailer_RAM3=cf[24560:24576].hex(),trailer_not_allocated=True),
        no_new_arrays_no_CPU_no_overlay_no_flag_allocation=True,outputs=0)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.PIN
    def deny(*a,**kw):raise AssertionError('Batch capacity census attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
