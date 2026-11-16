"""Read-only source capacity/typed consumers for the53B direct resolver lead."""
from pathlib import Path
from unittest.mock import patch
import argparse,ast,json,re
import audit_contra_force_inner_check_domains_1116 as D

C,M,W=D.C,D.M,D.W
DOMAIN_SHA='7c807b063e12c6430100a957965571fee524caa059ce3211970c02017c7de9c0'


def run(raw):
    assert C.H(Path(D.__file__).read_bytes())==DOMAIN_SHA
    q=D.run(raw);b=M.symbols(raw);carrier=raw[2006032:2030608]
    _,labels=C.Plan.Rejected.Source.C.Plan.inputs(C.reference(raw))
    tail=carrier[8192+0x1f91:8192+0x1fe0];assert len(tail)==79 and tail==bytes([255])*79
    def hit(pc):return 0xbf91<=pc<0xbfe0 or 0xdf91<=pc<0xdfe0
    standards=[];tuples=[];private_control=[];common=[]
    def scan(name,data,tag=None):
        for i in range(len(data)-2):
            if data[i+2]==2 and hit(int.from_bytes(data[i:i+2],'little')):tuples.append(dict(container=name,offset=i,word=int.from_bytes(data[i:i+2],'little')))
            if tag==2 and data[i]in(0x20,0x4c,0x6c)and hit(int.from_bytes(data[i+1:i+3],'little')):
                private_control.append(dict(container=name,offset=i,PC=0xa000+i,target=int.from_bytes(data[i+1:i+3],'little')))
            p=data[i:i+12]
            if len(p)==12 and p[0]==0xa9 and p[2:6]==bytes.fromhex('8d6c01a9')and p[7:]==bytes.fromhex('8d6d01a902')and hit(p[1]+256*p[6]):
                standards.append(dict(container=name,offset=i,target=p[1]+256*p[6]))
    scan('all_PRG',raw[16:1048592])
    for tag in(1,2,3):scan('CF_RAM'+str(tag),carrier[(tag-1)*8192:tag*8192],tag)
    import prince_cold_packet_1111 as Prince
    _,streams,_=Prince.extract(raw)
    for name,data in zip(('Prince_runtime','Prince_metadata','Prince_state'),streams,strict=True):scan(name,data)
    for owner,pages in{37:(728,729,730,731,732,733),38:(),39:(301,305,337,362,363,440,819,666),40:(),41:(),42:(991,992),43:()}.items():
        data=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in pages)
        scan('common_code_rows_'+str(owner),data);common.append(dict(owner=owner,pages=list(pages),SHA256=C.H(data)))
    for row in q['decoded_and_immutable_container_census']:
        name=row['name'].strip('"')
        if name.startswith(('CF_','Prince_')):continue
        for seg in b['segs'].values():
            if seg['name'].strip('"')!=name:continue
            at,n=int(seg['ooffs'],0),int(seg['size'],0);scan(name,raw[at:at+n]);break
    assert not standards and not private_control,(standards,private_control)
    table_hits=[];table_counts={}
    def typed(name,rows):
        table_counts[name]=len(rows)
        table_hits.extend(dict(table=name,**r)for r in rows if r['bank']==2 and hit(r['CPU']))
    plane=[]
    for at in(653484,653490,653494,653500):
        assert raw[at]==0xb9;plane.append(16+79*8192+(int.from_bytes(raw[at+1:at+3],'little')&8191))
    lo,ix,hi,bank=plane
    typed('Hu144',[dict(CPU=raw[lo+i]+256*raw[hi+raw[ix+i]],bank=raw[bank+raw[ix+i]])for i in range(144)])
    wf=raw[792556:792664];typed('Wf36',[dict(CPU=wf[3*i]+256*wf[3*i+1],bank=wf[3*i+2])for i in range(36)])
    lo,hi,bank=[W.location(b,n)for n in('BwColdLo','BwColdHi','BwColdBank')]
    typed('Bw8',[dict(CPU=raw[lo+i]+256*raw[hi+i],bank=raw[bank+i])for i in range(8)])
    nr=raw[16+124*8192:16+125*8192]
    for i in range(len(nr)-42):
        p=nr[i:i+27]
        if p[:9]!=bytes.fromhex('8d6a0108984820cca1'):continue
        if not(p[9]==p[15]==p[21]==0xb9 and p[12:15]==bytes.fromhex('8d6c01')and p[18:21]==bytes.fromhex('8d6d01')and p[24:27]==bytes.fromhex('4c0da6')):continue
        lo,hi,bank=[int.from_bytes(p[j:j+2],'little')&8191 for j in(10,16,22)]
        typed('Nr5@'+hex(0xa000+i),[dict(CPU=nr[lo+j]+256*nr[hi+j],bank=nr[bank+j])for j in range(5)])
    assert len(table_counts)==16 and not table_hits,(table_counts,table_hits)
    sources={
        'src/rogue_dawn_audio_upper_raw_v4.s':'0ae0353b517d7e660ad74bc39124f763f2e2f8652d46dff2379e196e2e7ffb89',
        'src/rogue_dawn_audio_reader_native_v6.inc':'a9c0924e4e685f0ccb0d29c13512321d674603da26e8bd75ef8582c267a256de',
        'src/rogue_dawn_audio_reader_v6.s':'b7eeab646450b73afb9ab14de6aa1d99127690fc9e1b75bed849f5f0841ce8ca',
        'audio/expanded/playlist-03.bin':'83ab7abfb17d7f56925f81da24811a7c07b57f4ee22a354b6c5f60ad224e187a',
        'audio/full-roster/full-07.bin':'f293790a3052708305cb4b54b48ff06cb092c7af3865a1a431e37c31e8609a87'}
    inputs={name:(C.R/name).read_bytes()for name in sources}
    for name,pin in sources.items():assert C.H(inputs[name])==pin,name
    def byte_runs(name):
        runs=[];active=[];start=0
        for line,text in enumerate(inputs[name].decode().splitlines(),1):
            code=text.split(';',1)[0].strip()
            if code.startswith('.byte'):
                if not active:start=line
                active.extend(int(v,16)for v in re.findall(r'\$([0-9a-fA-F]{2})(?![0-9a-fA-F])',code))
            elif active:
                if len(active)>=32:runs.append((start,bytes(active)))
                active=[]
        if len(active)>=32:runs.append((start,bytes(active)))
        return runs
    data_runs={name:byte_runs(name)for name in('src/rogue_dawn_audio_upper_raw_v4.s','src/rogue_dawn_audio_reader_native_v6.inc')}
    for row in tuples:
        if row['container']!='all_PRG':continue
        at=16+row['offset'];row['file']=at;row['bank']=row['offset']//8192;row['near_hex']=raw[max(16,at-6):at+8].hex()
        owners=[]
        for name,sym in b['syms'].items():
            if'seg'not in sym or'val'not in sym:continue
            seg=b['segs'][sym['seg']]
            if'ooffs'not in seg or not int(seg.get('size','0'),0):continue
            start=int(seg['ooffs'],0)+int(sym['val'],0)-int(seg['start'],0)
            if 0<=at-start<128 and(start-16)//8192==row['bank']:owners.append(dict(name=name,delta=at-start,segment=seg['name']))
        row['nearest_compiled_metadata_symbols']=sorted(owners,key=lambda r:r['delta'])[:2]
        row['containing_metadata_segments']=[]
        for seg in b['segs'].values():
            if'ooffs'not in seg or not int(seg.get('size','0'),0):continue
            start,n=int(seg['ooffs'],0),int(seg['size'],0)
            if start<=at<start+n:row['containing_metadata_segments'].append(dict(name=seg['name'],start=start,bytes=n,offset=at-start,type=seg['type']))
        row['containing_metadata_segments'].sort(key=lambda x:x['bytes'])
        owner=row['containing_metadata_segments'][0];segment=owner['name'].strip('"')
        current=raw[owner['start']:owner['start']+owner['bytes']]
        if segment in('XG_MUSIC_2A','X5_FULL_MUSIC_07'):
            path='audio/expanded/playlist-03.bin'if segment=='XG_MUSIC_2A'else'audio/full-roster/full-07.bin'
            assert current==inputs[path]
            row['classification']=dict(role='Whole current segment equals declared immutable audio stream incbin; values are decoder data, not host SFC descriptors',source=path,SHA256=sources[path])
        elif segment.startswith('ROGUE_AUDIO_'):
            path='src/rogue_dawn_audio_reader_native_v6.inc'if segment=='ROGUE_AUDIO_DRIVER_C97'else'src/rogue_dawn_audio_upper_raw_v4.s'
            matches=[]
            for line,block in data_runs[path]:
                cursor=0
                while(cursor:=current.find(block,cursor))>=0:
                    if cursor<=owner['offset']and owner['offset']+3<=cursor+len(block):matches.append(dict(line=line,segment_offset=cursor,bytes=len(block),data_SHA256=C.H(block)))
                    cursor+=1
            assert matches,('Unclassified Rogue tail word',row)
            row['classification']=dict(role='Exact current bytes lie inside an explicit source .byte data run, not a decoded host farcall',source=path,SHA256=sources[path],matching_source_data_runs=matches)
    # A positive tag is a virtual ROM view, not a raw RAM selector. Bind the
    # complete actual reader and its BPL target, without executing the older
    # auditor or assuming the pre-virtual v6 source still describes this mux.
    reader_path=C.R/'tools/audit/audit_bub_native_audio_lease_1113.py'
    reader_data=reader_path.read_bytes()
    assert C.H(reader_data)=='0ceaaeb6578a8cf2e98f13aa0c46821b283179b610a8478e79f8ca96bc4a4a4b'
    assignment=next(n for n in ast.parse(reader_data.decode()).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='READER'for t in n.targets))
    authored_reader=bytes.fromhex(ast.literal_eval(assignment.value.args[0]))
    assert len(authored_reader)==119 and raw[795673:795673+119]==authored_reader
    mux=bytes.fromhex('09808d45018d1551a00049dad0062005b74c38c44c00bf')
    assert authored_reader[0xc42c-0xc409:0xc42e-0xc409]==bytes.fromhex('103b')
    assert 0xc42e+0x3b==0xc469 and authored_reader[0xc469-0xc409:]==mux
    raw_banks_at=W.location(b,'RdaUpperRawBankTable');raw_banks=list(raw[raw_banks_at:raw_banks_at+32])
    assert set(raw_banks)=={0x54,0xdb,0xdc,0xe3}
    normalized_banks=sorted({v|128 for v in raw_banks});assert 2 not in normalized_banks
    assert re.findall(r'load=C2TAIL\b',D.CFG.read_text())==['load=C2TAIL']
    # Actual bounded OwnLo/Hi: last Hi byte is BF90, immediately before tail.
    assert(labels['CfOwnLo'],labels['CfOwnHi'])==(0xbf49,0xbf6d)
    own_reader_bound=dict(index_max=35,Lo=[0xbf49,0xbf6d],Hi=[0xbf6d,0xbf91],end_exclusive=0xbf91)
    body=[]
    def read2(pc,n):return carrier[8192+(pc&8191):8192+(pc&8191)+n]
    count=156;lo=read2(labels['CfBodyLo'],count);hi=read2(labels['CfBodyHi'],count);sizes=read2(labels['CfBodyBytes'],count)
    for i,n in enumerate(sizes):
        pc=lo[i]+256*hi[i];assert 0xcd76<=pc and pc+n<=0xdd3a and n and not n%4
        body.append((pc,pc+n))
    assert labels['CfBodyRecords']==0xcd76 and labels['CfBodyRecordsEnd']==0xdd3a
    # This every-byte lead census remains conservative. It is intentionally
    # not used to treat data words as decoded instructions.
    reads=[];ops={0x1d,0x19,0x3d,0x39,0x5d,0x59,0x7d,0x79,0xb9,0xbc,0xbd,0xbe,0xd9,0xdd,0xf9,0xfd}
    for tag in(1,2,3):
        page=carrier[(tag-1)*8192:tag*8192]
        limits=[(0x1e6e,0x1f49)]if tag==2 else[(0,8192)]
        for lo_at,hi_at in limits:
            for i in range(lo_at,min(hi_at,8190)):
                pc=int.from_bytes(page[i+1:i+3],'little')
                if page[i]in ops and((tag==2 and 0xbe92<=pc<0xbfe0)or 0xde92<=pc<0xdfe0):
                    reads.append(dict(tag=tag,offset=i,opcode=page[i],base=pc))
    # Actual offsets are included for independent source review, rather than
    # guessed from the instruction length of a historical router.
    unknown_reads=[r for r in reads if not(r['tag']==2 and r['base']in(0xbf49,0xbf6d))]
    result=dict(parent_SHA256=C.PIN,domain_census_receipt=q['receipt_SHA256'],
        domain_source_SHA256=DOMAIN_SHA,source_capacity=q['source_capacity_lead'],
        source79_fill_and_exclusive_CF_A2_ROUTER_load=True,tail_file_half_open=[2022305,2022384],
        actual_standard_bank2_tail_ingress=standards,actual_CF_RAM2_near_tail_control=private_control,
        common7_published_code_pages=common,
        raw_tail_bank2_word_tuple_leads=tuples,structured_target_reader_counts=table_counts,structured_bank2_tail_targets=table_hits,
        CfTargetBank_all_direct_stores=[r['immediate_bank']for r in q['private_CfTargetBank_direct_store_leads']],
        own_table_reader_bound=own_reader_bound,all156_body_record_extents=[min(p for p,e in body),max(e for p,e in body)],
        body_record_extent_hash=C.H(json.dumps(body,separators=(',',':')).encode()),
        CF_animation_declared_data_extent=[0xc69b,0xca01],CF_state_extent=[0xc000,0xc500],
        conservative_private_tail_indexed_read_leads=reads,unclassified_indexed_read_leads=unknown_reads,
        source_data_and_reader_pins=sources,Rogue_upper_source_reader_bank_tags=sorted(set(raw_banks)),
        actual_Rogue_reader=dict(file_half_open=[795673,795792],SHA256=C.H(authored_reader),
            exact_virtual_mux_hex=mux.hex(),positive_BPL_target=0xc469,
            normalized_physical_ROM_tags=normalized_banks,
            semantics='Bit7-clear54 is OR80 and mapped asD4/ROM84 before JMP BF00; DA uses B705. No raw RAM2 map is admitted.',
            reference_source=str(reader_path.relative_to(C.R)),reference_SHA256=C.H(reader_data),
            PRG84_BF00_head_SHA256=C.H(raw[16+84*8192+0x1f00:16+84*8192+0x1f20])),
        unclassified_tail_tuple_leads=[r for r in tuples if'classification'not in r],
        capacities_are_proposal_only_no_allocation=True,no_new_bytes_CPU_or_mount=True,
        all_RAM2_header_writer_classification_and_ISR_remain_separate=True,outputs=0)
    result['receipt_SHA256']=C.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--reader',action='store_true');args=ap.parse_args()
    raw=C.load_current_image();assert C.H(raw)==C.PIN
    def deny(*a,**kw):raise AssertionError('Tail census attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        if args.reader:
            b=M.symbols(raw);at=W.location(b,'RdaUpperRawBankTable')
            q=dict(diagnostic_only=True,prefix_file=795673,current_prefix=raw[795673:795673+119].hex(),legacy_symbol_file=at,legacy_bytes=raw[at:at+32].hex())
        else:q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
