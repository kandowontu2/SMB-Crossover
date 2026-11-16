"""Read-only local WfOneLifeStatus consumer/funding census on exact91dc."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json,re
import profile_contra_force_service_layers_1116 as S

C=S.C
K=C.R/'build/wwf-roster-native-1101-v1'
PINS={'runtime.s':'758271c1a91286e4217b346138a3aa7cbe1ef5180b5c4994c09bb53c3ddcb2ed',
      'runtime.lst':'8bd3a47dcc794ee04ceb532dbf11f575b65a0242904f58a289cb0077b31d0cd1',
      'candidate.dbg':'582ed31688b4f0aefa685872274741f46106f68af030540922b4fdd96af8537f'}
AT=16+96*8192+0x1796


def run(raw):
    assert C.H(raw)==C.PIN
    data={n:(K/n).read_bytes()for n in PINS}
    for n,pin in PINS.items():assert C.H(data[n])==pin,n
    source=data['runtime.s'].decode();listing=data['runtime.lst'].decode();debug=data['candidate.dbg'].decode()
    mentions=[dict(line=i,text=t.strip())for i,t in enumerate(source.splitlines(),1)if'WfOneLifeStatus'in t]
    assert len(mentions)==2 and'WfOneLifeStatus:lda #0'in mentions[0]['text']and'Target WfOneLifeStatus'==mentions[1]['text']
    exports=[t for t in source.splitlines()if t.startswith('.export')];assert not any('WfOneLifeStatus'in t for t in exports)
    sym=next(t for t in debug.splitlines()if t.startswith('sym\t')and'name="WfOneLifeStatus"'in t)
    assert'val=0xB796,'in sym and'ref=316187+316187+316187,'in sym
    assert'0004D7r 1  A9 00        WfOneLifeStatus:lda #0'in listing
    assert'0004D9r 1  60            rts'in listing and'00052Fr 1  rr rr rr      Target WfOneLifeStatus'in listing
    assert raw[AT:AT+3]==bytes.fromhex('a90060')and raw[AT-1]==0x60
    table=raw[792489+67:792489+175];targets=[(table[i+2],table[i]+256*table[i+1])for i in range(0,108,3)]
    assert(224,0xb796)not in targets and targets[6]==(134,0xa6db)
    word_counts=Counter();same=[];direct=[];standard=[]
    for bank in range(128):
        page=raw[16+bank*8192:16+(bank+1)*8192];cursor=0
        while(cursor:=page.find(bytes.fromhex('96b7'),cursor))>=0:
            word_counts[bank]+=1
            row=dict(bank=bank,offset=cursor,file=16+bank*8192+cursor,preceding=page[cursor-1]if cursor else None)
            if bank in(96,126,127):same.append(row)
            if row['preceding']in(0x20,0x4c,0x6c):direct.append(row)
            cursor+=1
        for pattern in('a9968d6c01a9b78d6d01a9e0','96b7e0'):
            cursor=0
            while(cursor:=page.find(bytes.fromhex(pattern),cursor))>=0:
                standard.append(dict(bank=bank,file=16+bank*8192+cursor,pattern=pattern));cursor+=1
    assert not same and not standard
    assert all(r['bank']not in(96,126,127)for r in direct)
    # Decode every actual same-source relative branch into the three bytes.
    branches=[]
    for line in listing.splitlines():
        match=re.match(r'^([0-9A-F]{6})r\s+\d+\s+((?:[0-9A-F]{2} ){1,3})\s+',line)
        if not match:continue
        offset=int(match[1],16);pc=0xb2bf+offset
        if not 0xa000<=pc<0xc000:continue
        at=16+96*8192+(pc&8191);op=raw[at]
        if op not in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):continue
        delta=raw[at+1];target=pc+2+(delta if delta<128 else delta-256)
        if 0xb796<=target<0xb799:branches.append(dict(PC=pc,target=target,line=line))
    assert not branches
    # Current Hu descriptor planes are the published computed target domain.
    page=raw[16+79*8192:16+80*8192];hu=[]
    for i in range(144):
        low=page[0x18e5+i];pair=page[0x1975+i]
        hi,bank=page[0x1a05+pair],page[0x1a33+pair]
        if(bank,low+256*hi)==(224,0xb796):hu.append(i)
    assert not hu
    return dict(reference6a3_SHA256=C.H(raw),retained_source_PINS=PINS,
        compiled_local_symbol=sym,sole_source_consumer=mentions,
        local_not_exported=True,current_threebytes_A90060_and_preceding_RTS=True,
        old_sole_descriptor_slot6_replaced_by_current_P1Late=dict(bank=targets[6][0],PC=targets[6][1]),
        all36_Wf_and144_Hu_published_targets_exclude_old_status=True,
        current_same_or_fixed_PRG_word_candidates=same,
        all_PRG_word_counts=[dict(bank=b,count=n)for b,n in sorted(word_counts.items())],
        other_bank_direct_word_leads=direct,standard_E0_farcall_and_triple_candidates=standard,
        source_relative_branch_inbound=branches,
        candidate_funding=dict(bytes=3,CPU_half_open=[0xb796,0xb799],file_half_open=[AT,AT+3],
            intended_use='Move helper entry back2 and grow by2, keep tableB7DC/endB848 fixed; do not drop live X high-byte input'),
        limits=['This is producer/source and explicit current target-domain closure, not arbitrary numeric/computed-address impossibility',
                'Other-bank literal near calls retain their own bank; root review may require actual decode/owner classification',
                'No new Wf array, CPU execution, source overlay, allocation or candidate created'],outputs=0)


if __name__=='__main__':
    raw,pin=S.load_reference()
    def deny(*a,**kw):raise AssertionError('Status funding audit attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    q['actual_input_SHA256']=pin;q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
