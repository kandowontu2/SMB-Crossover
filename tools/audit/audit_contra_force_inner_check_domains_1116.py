"""Read-only current CF validation/entry domains; no replacement byte arrays."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json,re
import contra_force_checked_resolver_model_1116 as M

C,W=M.C,M.W
K=C.R/'build/contra-force-projectile-contact-1031-v3/kernel'
ROUTER=C.R/'build/contra-force-p1-kernel-v1/a2-router.s'
ROUTER_SHA='410d81b56f20bbff77c1732164a9879395aef8ce3d2ee6daf6c9c7be76ce56c2'
CFG=K/'runtime.cfg'
CFG_SHA='87cde222a35c4dede2a11d0202b16c3b87be9c1acd327ac79d4f4343616bc55d'


def run(raw):
    assert C.H(raw)==C.PIN,'Exact current91dc owning input required'
    b=M.symbols(raw);reference=C.reference(raw);z,labels=C.Plan.Rejected.Source.C.Plan.inputs(reference)
    assert C.H(ROUTER.read_bytes())==ROUTER_SHA
    assert C.H(CFG.read_bytes())==CFG_SHA
    cfg=CFG.read_text()
    assert 'C2TAIL:start=$de00,size=$1e0'in cfg and'CF_A2_ROUTER:load=C2TAIL,run=A2ALIAS,type=ro'in cfg
    source=ROUTER.read_text();carrier=raw[2006032:2030608]
    assert C.H(carrier)=='3a7d2d9a77d5accd30e7976645856118f8734fca5a84f7df7bff8946ec989f84'
    assert(labels['CfA2Router'],labels['CfA2RouterEnd'],labels['CfOwnLo'],labels['CfOwnHi'])==(0xbe6e,0xbf91,0xbf49,0xbf6d)
    own=carrier[8192+0x1e00:8192+0x1f91]
    assert all(own[3*i:3*i+3]==bytes.fromhex('4c6ebe')for i in range(36))
    assert own[108:110]==bytes.fromhex('1860')
    outer=raw[573373:573389];inner_at=W.location(b,'CfLoaderExpectedCookie');inner=raw[inner_at:inner_at+16]
    assert outer==inner and inner_at==642966,(inner_at,outer.hex(),inner.hex())
    assert'cpx #2\n beq CfCookieNext'in source and'cmp CfLoaderExpectedCookie,x'in source
    assert'cmp $bfe2'in source and'lda FmGroups\n lsr\n lsr\n lsr\n and #3'in source
    lo=carrier[8192+(labels['CfOwnLo']&8191):8192+(labels['CfOwnLo']&8191)+36]
    hi=carrier[8192+(labels['CfOwnHi']&8191):8192+(labels['CfOwnHi']&8191)+36]
    targetrows=[]
    for i in range(36):
        pc=lo[i]+256*hi[i];names=sorted(n for n,v in labels.items()if v==pc and n.startswith('Cf'))
        targetrows.append(dict(service=i,PC=pc,tag=3,names=names))
    # RAM3 workers may legitimately share the BE/BF CPU address range.
    # Actual router LDA#3/STA CfTargetBank binds this table to RAM3, not A2.
    assert'lda #3\n sta CfTargetBank-$2000'in source
    # These are producer leads, not arbitrary-word execution claims.
    standard=[];triples=[];map2=[];header=[];near_private=[];C2_alias_leads=[];bank_writers=[]
    containers=[]
    def scan(name,data,base_file=None,private_tag=None):
        sf=[];tw=[]
        for i in range(len(data)-2):
            if i+12<=len(data):
                p=data[i:i+12]
                if p[0]==0xa9 and p[2:6]==bytes.fromhex('8d6c01a9')and p[7:]==bytes.fromhex('8d6d01a902'):
                    pc=p[1]+256*p[6]
                    if 0xbe00<=pc<0xbf91:sf.append(dict(offset=i,target=pc))
            if data[i+2]==2 and 0xbe00<=int.from_bytes(data[i:i+2],'little')<0xbf91:tw.append(i)
            if private_tag is not None and data[i]in(0x20,0x4c,0x6c)and 0xbe00<=int.from_bytes(data[i+1:i+3],'little')<0xbf91:
                near_private.append(dict(container=name,tag=private_tag,offset=i,target=int.from_bytes(data[i+1:i+3],'little'),opcode=data[i]))
            if private_tag is not None and data[i]in(0x20,0x4c,0x6c)and 0xde00<=int.from_bytes(data[i+1:i+3],'little')<0xdf91:
                C2_alias_leads.append(dict(tag=private_tag,offset=i,target=int.from_bytes(data[i+1:i+3],'little'),opcode=data[i]))
            if private_tag is not None and data[i]==0x8d and int.from_bytes(data[i+1:i+3],'little')in(0xa2ee,0xc2ee):
                bank_writers.append(dict(tag=private_tag,offset=i,operand=int.from_bytes(data[i+1:i+3],'little'),
                    previous_bytes=data[max(0,i-2):i].hex(),immediate_bank=data[i-1]if i>=2 and data[i-2]==0xa9 else None))
        containers.append(dict(name=name,bytes=len(data),SHA256=C.H(data),standard_bank2_farcall_setups=sf,
            bank2_target_word_tuple_leads=tw))
    for bank in range(128):
        page=raw[16+bank*8192:16+(bank+1)*8192]
        for i in range(8190):
            pc=0xa000+i;op=page[i];arg=int.from_bytes(page[i+1:i+3],'little')
            if op in(0x8d,0x8e,0x8c)and arg in tuple(range(0xbfe0,0xbff0))+tuple(range(0xdfe0,0xdff0)):
                header.append(dict(bank=bank,PC=pc,file=16+bank*8192+i,opcode=op,address=arg))
            if op in(0x99,0x9d)and any(base-255<=arg<base+16 for base in(0xbfe0,0xdfe0)):
                header.append(dict(bank=bank,PC=pc,file=16+bank*8192+i,opcode=op,address=arg,index_bound_needed=True))
            if page[i:i+8]==bytes.fromhex('a9028d45018d1551'):map2.append(dict(bank=bank,PC=pc,file=16+bank*8192+i))
        # Whole PRG standard target setups use physical bank+offset for review.
        for match in re.finditer(bytes.fromhex('a9')+b'.'+bytes.fromhex('8d6c01a9')+b'.'+bytes.fromhex('8d6d01a902'),page,re.S):
            p=match.group();target=p[1]+256*p[6]
            if 0xbe00<=target<0xbf91:standard.append(dict(bank=bank,PC=0xa000+match.start(),target=target))
        for i in range(8190):
            if page[i+2]==2 and 0xbe00<=int.from_bytes(page[i:i+2],'little')<0xbf91:triples.append(dict(bank=bank,offset=i,target=int.from_bytes(page[i:i+2],'little')))
    for tag in(1,2,3):scan('CF_RAM'+str(tag),carrier[(tag-1)*8192:tag*8192],private_tag=tag)
    import prince_cold_packet_1111 as Prince
    _,streams,_=Prince.extract(raw)
    for name,data in zip(('Prince_runtime','Prince_metadata','Prince_staged_state'),streams,strict=True):scan(name,data)
    pages={37:(728,729,730,731,732,733),38:(),39:(301,305,337,362,363,440,819,666),40:(),41:(),42:(991,992),43:()}
    for owner,indices in pages.items():scan('common_code_rows_'+str(owner),b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in indices))
    seen=set()
    for seg in b['segs'].values():
        if seg['name'].strip('"')not in('FF_STREAM','BW_STREAM','BT_STREAM','QW_STREAM','KR_KERNEL_IMAGE','ARTHUR_CACHE_EXEC','WF_TEMPLATE_CHR'):continue
        at,n=int(seg['ooffs'],0),int(seg['size'],0)
        if(at,n)in seen:continue
        seen.add((at,n));scan(seg['name'],raw[at:at+n])
    tables=[]
    def table(name,rows):
        hits=[r for r in rows if r['bank']==2 and 0xbe00<=r['CPU']<0xbf91]
        tables.append(dict(name=name,rows=len(rows),A2_hits=hits))
    planes=[]
    for at in(653484,653490,653494,653500):
        assert raw[at]==0xb9;pc=int.from_bytes(raw[at+1:at+3],'little');planes.append(16+79*8192+(pc&8191))
    hu_lo,hu_ix,hu_hi,hu_bank=planes
    table('Hu144',[dict(CPU=raw[hu_lo+i]+256*raw[hu_hi+raw[hu_ix+i]],bank=raw[hu_bank+raw[hu_ix+i]])for i in range(144)])
    wf=raw[792556:792664]
    table('Wf36',[dict(slot=i,CPU=wf[3*i]+256*wf[3*i+1],bank=wf[3*i+2])for i in range(36)])
    blo,bhi,bba=[W.location(b,n)for n in('BwColdLo','BwColdHi','BwColdBank')]
    table('Bw8',[dict(CPU=raw[blo+i]+256*raw[bhi+i],bank=raw[bba+i])for i in range(8)])
    nr=raw[16+124*8192:16+125*8192];nr_count=0
    for i in range(len(nr)-42):
        code=nr[i:i+27]
        if code[:9]!=bytes.fromhex('8d6a0108984820cca1'):continue
        if not(code[9]==code[15]==code[21]==0xb9 and code[12:15]==bytes.fromhex('8d6c01')and code[18:21]==bytes.fromhex('8d6d01')and code[24:27]==bytes.fromhex('4c0da6')):continue
        p=[int.from_bytes(code[j:j+2],'little')&8191 for j in(10,16,22)]
        table('Nr5@'+hex(0xa000+i),[dict(CPU=nr[p[0]+j]+256*nr[p[1]+j],bank=nr[p[2]+j])for j in range(5)]);nr_count+=1
    assert nr_count==13
    symbols=[]
    for name,sym in b['syms'].items():
        if'seg'not in sym or'val'not in sym:continue
        seg=b['segs'][sym['seg']]
        if'ooffs'not in seg or not int(seg.get('size','0'),0):continue
        at=int(seg['ooffs'],0)+int(sym['val'],0)-int(seg['start'],0)
        if 16<=at<1048592:symbols.append((at,name,int(sym['val'],0),seg['name']))
    for lead in header+map2:
        at=lead['file'];owners=[dict(name=name,file=start,PC=pc,delta=at-start,segment=seg)
            for start,name,pc,seg in symbols if 0<=at-start<128 and(start-16)//8192==lead['bank']]
        lead['nearest_compiled_metadata_symbols']=sorted(owners,key=lambda r:r['delta'])[:3]
        lead['current_bytes']=raw[at:at+12].hex()
    # Header matches are deliberately kept as unclassified leads until exact
    # compiled/source ownership and actual mapped memory writes are established.
    bybank=Counter(r['bank']for r in header)
    result=dict(actual_current_SHA256=C.PIN,CF_full_payload_SHA256=C.H(carrier),
        source_route_SHA256=ROUTER_SHA,source_route_precondition=source.splitlines()[:3],
        outer_cookie_file=573373,inner_expected_cookie_file=inner_at,all16_expected_bytes_equal=True,
        full16_semantics='Fifteen exact cookie comparisons skip byte2; dynamic class at byte2 is compared separately by both loops',
        private_A2_domain=dict(veneers=[0xbe00,0xbe6c],unavailable=[0xbe6c,0xbe6e],router_and_tables=[0xbe6e,0xbf91],
            whole401_SHA256=C.H(own),code219_SHA256=C.H(own[110:329]),targets36=targetrows),
        source_capacity_lead=dict(cfg_SHA256=CFG_SHA,declared_C2TAIL=[0xde00,0xdfe0],actual_segment_end=0xdf91,
            tail_bytes=79,tail_SHA256=C.H(carrier[8192+0x1f91:8192+0x1fe0]),
            no_resource_grant_or_reader_closure_inferred=True),
        PRG_standard_bank2_farcall_setups=standard,PRG_bank2_target_tuple_leads=triples,
        PRG_direct_map_A2_leads=map2,current_private_near_control_leads=near_private,
        current_private_C2_alias_control_leads=C2_alias_leads,
        private_CfTargetBank_direct_store_leads=bank_writers,
        actual_shared_target_planes=tables,
        decoded_and_immutable_container_census=containers,
        conservative_PRG_RAM2_header_store_leads=header,header_store_lead_counts_by_bank=dict(bybank),
        completion=False,remaining=[
            'Classify all standard/structured/computed A2 entry producers and legal caller-return contracts',
            'Classify direct-map and near-control leads by actual mapped owner; words alone are not ingress',
            'Bind every live direct/indexed/indirect RAM2 header writer and its legal lifecycle range',
            'Prove no header writer between external full validation and the private check, including actual IRQ/busyNMI',
            'RAM3 validation is different and must remain; public/private malformed-entry contracts need explicit root review'],
        no_new_arrays_no_CPU_no_overlay_no_lease_or_auth_change=True,outputs=0)
    result['receipt_SHA256']=C.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    raw=C.load_current_image();assert C.H(raw)==C.PIN
    def deny(*a,**kw):raise AssertionError('Read-only check-domain census attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
