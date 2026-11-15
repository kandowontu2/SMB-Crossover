"""Current executable-container ingress research; no producers or archives restored."""
from collections import Counter
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import check_battletoads_native_service_model_1114 as Model
import prince_cold_packet_1111 as Prince

W,N,R=Model.W,Model.N,Model.R
TARGETS=(0xe4a7,0xbecd,0xbede,0xbee2,0xbeef,0xbef4)


def matches(data,base):
    rows=[]
    for target in TARGETS:
        word=target.to_bytes(2,'little');start=0
        while(start:=data.find(word,start))>=0:
            op=data[start-1]if start else None
            rows.append(dict(target=target,offset=start,CPU=base+start,preceding_byte=op,
                direct_control_opcode=op in(0x20,0x4c,0x6c)))
            start+=1
    return rows


def common_cold(raw,owner,b):
    """Exact live AE00 loader under its documented forced-blank component contract."""
    m=N.fresh(b);m.raw_page(2,2)
    N.put(m,CurrentBank=m.rawtags[1],CurrentBankC=2,SelectedCharacter=owner,
        OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,
        FamilyMainCommit=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0,
        Mirror_PPUCTRL=160,ReloadCHRBank=0)
    m.ppuctrl=160;m[0x2001]=0;before=m.ppu_reads;descriptor=None;minimum=224
    m[0x16a],m[0x16c],m[0x16d]=83,0,0xae
    c=N.NesMPU(memory=m,pc=0x15a);c.a,c.x,c.y,c.p,c.sp=193,71,109,0x21,224;c.stPushWord(0x5aff)
    for _ in range(4_000_000):
        if(c.pc,c.sp)==(0x5b00,224):break
        minimum=min(minimum,c.sp)
        if descriptor is None and m.rawtags[1]==251 and 0xaf40<=c.pc<0xb000 and bytes(m[c.pc:c.pc+2])==b'\xb1\x06':
            ptr=m[6]+256*m[7];rows=m[ptr];assert 1<=rows<=16
            data=bytes(m[ptr:ptr+3+2*rows]);assert data[1]<=rows and data[2]<=32
            descriptor=dict(pointer=ptr,source_tag=m.rawtags[(ptr-0x8000)//8192],hex=data.hex(),
                rows=rows,code_rows=data[1],zero_pages=data[2],
                physical_pages=[int.from_bytes(data[i:i+2],'little')for i in range(3,len(data),2)])
        assert m[c.pc],('Live common loader BRK',owner,hex(c.pc));c.step()
    else:raise AssertionError(('Live common loader bound',owner,hex(c.pc)))
    assert(c.a,c.x,c.y,c.p&0xef,c.sp)==(83,71,109,0x21,224),(owner,c.a,c.x,c.y,c.p,c.sp)
    assert descriptor and all(m.ram[k][0x1fe0]==167 and m.ram[k][0x1fe1]==owner for k in(2,3))
    result=dict(owner=owner,component_loader_contract=True,no_health_actor_terrain_position_seeds=True,
        actual_descriptor=descriptor,PPU_reads=m.ppu_reads-before,minimum_SP=minimum,
        code_SHA256=sha256(m.ram[3][:0x1fe0]).hexdigest(),metadata_SHA256=sha256(m.ram[2][:0x1fe0]).hexdigest(),
        code_target_words=matches(bytes(m.ram[3][:0x1fe0]),0xa000),metadata_target_words=matches(bytes(m.ram[2][:0x1fe0]),0xc000))
    return result


def debug_prefix_refs(raw):
    result=[]
    for name in('kirby-approach-owner-1101-v3/candidate.dbg','bub-menu-candidate-1102-v2/combined-event.dbg','thomas-current-candidate-1102-v3/candidate.dbg'):
        path=R/'build'/name;text=path.read_text();refs=set();defs=[]
        parse=lambda line:dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if'='in x)
        for line in text.splitlines():
            if line.startswith('sym\t')and'name="MmSideDispatchPrefix"'in line:
                row=parse(line)
                if'val'in row:assert int(row['val'],0)==0xe4a7
                refs.update(row.get('ref','').split('+'));defs.append(row)
        refs.discard('');lines=[];wanted=set();segments={}
        for line in text.splitlines():
            if line.startswith('seg\t'):
                row=parse(line);segments[row['id']]=row
            elif line.startswith('line\t'):
                row=parse(line)
                if row['id']in refs:lines.append(row);wanted.update(row.get('span','').split('+'))
        spans=[]
        for line in text.splitlines():
            if not line.startswith('span\t'):continue
            row=parse(line)
            if row['id']not in wanted:continue
            seg=segments[row['seg']]
            if'ooffs'not in seg:continue
            at=int(seg['ooffs'],0)+int(row['start'],0);size=int(row['size'],0)
            spans.append(dict(file=at,CPU=int(seg['start'],0)+int(row['start'],0),size=size,
                type=row.get('type','instruction'),current_hex=raw[at:at+size].hex(),segment=seg['name']))
        result.append(dict(source_debug=name,debug_SHA256=sha256(text.encode()).hexdigest(),symbol_records=defs,
            reference_lines=lines,actual_current_spans=spans))
    return result


def static(raw):
    Model.typed(raw);_,lease=Model.recipe(raw);b=Model.Cold.bundle(Model.typed(raw));off=lambda bank,pc:16+bank*8192+(pc&8191)
    registry=[]
    for i in range(7):
        ptr=raw[off(65,0xab91)+i]+256*raw[off(65,0xab98)+i]
        assert ptr not in TARGETS
        registry.append(dict(owner=37+i,descriptor_pointer=ptr,descriptor_is_data_not_control=True))
    assert[el['descriptor_pointer']for el in registry]==[45010,49043,45029,57312,47609,45003,45050]
    readers=[];common=raw[off(65,0xae00):off(65,0xaf90)]
    for ptr in(0xab91,0xab98,0xabaf,0xabb7):
        rows=[]
        for op,index in((0xbd,'X'),(0xb9,'Y')):
            pattern=bytes((op,ptr&255,ptr>>8));at=0
            while(at:=common.find(pattern,at))>=0:rows.append(dict(CPU=0xae00+at,index=index,hex=common[at:at+6].hex()));at+=1
        assert len(rows)==1,(hex(ptr),rows);readers.append(dict(plane=ptr,actual_LDA_indexed_readers=rows))
    nr=[];segment=raw[16+124*8192:16+125*8192]
    for at in range(len(segment)-42):
        code=segment[at:at+27]
        if code[:9]!=bytes.fromhex('8d6a0108984820cca1'):continue
        if not(code[9]==code[15]==code[21]==0xb9 and code[12:15]==bytes.fromhex('8d6c01')and code[18:21]==bytes.fromhex('8d6d01')and code[24:27]==bytes.fromhex('4c0da6')):continue
        planes=[int.from_bytes(code[i:i+2],'little')for i in(10,16,22)];rows=[]
        for i in range(5):
            lo,hi,bank=(segment[(pc&8191)+i]for pc in planes);target=lo+256*hi
            assert not(bank==161 and target in TARGETS),'Indirect Nr target into moved shared-side label'
            assert target!=0xe4a7,'Indirect Nr target into moved fixed prefix'
            rows.append(dict(index=i,raw_bank=bank,CPU=target))
        nr.append(dict(entry=0xa000+at,planes=planes,rows=rows))
    assert nr
    prg=raw[16:1048592]
    macro=bytes.fromhex('a9a28d6c01a9be8d6d01a9a1');starts=[];at=0
    while(at:=prg.find(macro,at))>=0:starts.append(16+at);at+=1
    assert starts==[off(126,0x90ee)],starts
    immediate=[]
    for target in TARGETS:
        pattern=bytes((0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,0x8d,0x6d,1));at=0;hits=[]
        while(at:=prg.find(pattern,at))>=0:hits.append(16+at);at+=1
        assert not hits,(hex(target),hits);immediate.append(dict(target=target,standard_farcall_target_immediates=hits))
    head,streams,packed=Prince.extract(raw);words=matches(streams[0],0xa000)
    assert words==[dict(target=0xbede,offset=7940,CPU=0xbf04,preceding_byte=0x4c,direct_control_opcode=True)]
    assert streams[0][7939:7942]==bytes.fromhex('4cdebe')
    bt=raw[Model.BT.BASE:Model.BT.BASE+8192];btwords=matches(bt,0xa000)
    assert btwords and all(w['preceding_byte']in(0x8d,0xad,0xac,0xae,0x5d,0x9d,0x3d,0xbd)and not w['direct_control_opcode']for w in btwords)
    alias_sites=(978271,986463,1027423,1043807);aliases=[];contexts=[]
    for at in alias_sites:
        assert raw[at:at+3]==bytes.fromhex('4ca7e4')
        context=raw[at-16:at+19];contexts.append(context)
        aliases.append(dict(file=at,PRG=(at-16)//8192,operand=at+1,old='4ca7e4',new='4cabe4',context_hex=context.hex()))
    assert all(context==contexts[0]for context in contexts)
    symbols=debug_prefix_refs(raw);records=[r for row in symbols for r in row['symbol_records']]
    assert len(records)==1 and records[0]['ref']=='52854'and records[0]['val']=='0xE4A7'
    source=R/'tools/audit/chip_hot_control_prepare_v2.py';text=source.read_text()
    assert text.count('   jmp MmSideDispatchPrefix\n')==1
    table_at=W.location(b,'WfPageSourceTable');pages=list(raw[table_at:table_at+24])
    template=next(s for s in b['segs'].values()if s['name']=='"WF_TEMPLATE_CHR"')
    wf_lo=(int(template['ooffs'],0)-1048592)//1024;wf_hi=wf_lo+int(template['size'],0)//1024
    assert all(wf_lo<=512+page<wf_hi for page in pages),(pages,wf_lo,wf_hi)
    return dict(proposal=lease,current_common7_descriptor_pointer_plane_rows=registry,
        current_descriptor_cookie_plane_LDA_readers=readers,actual_Nr_five_entry_split_plane_tables=nr,
        sole_standard_bank33_BE_A2_farcall=starts,no_standard_farcall_to_moved_internal_entries=immediate,
        Prince_decoded_JMP_classification=dict(PC=0xbf03,target=0xbede,instruction='4cdebe',live_CPU_window=[0xa000,0xc000],physical_RAM_bank=3,
            target_same_RAM3_window=True,not_PRG33=True,decoded_runtime_SHA256=sha256(streams[0]).hexdigest()),
        BT_decoded_target_words=len(btwords),BT_target_words_are_private_data_operands=True,
        fixed_prefix_symbol_references=symbols,
        prefix_compiled_reference_cardinality=1,compact_debug_lines_and_spans_not_retained=True,
        retained_sole_JMP_source=dict(file=source.relative_to(R).as_posix(),SHA256=sha256(source.read_bytes()).hexdigest(),
            exact_symbolic_JMP_occurrences=1,source_role='Former solecaller side selector; no historical producer executed'),
        all4_current_runtime_alias_contexts_exact=aliases,
        Wf_template_direct_copy_pages=dict(table_file=table_at,physical_pages=[512+p for p in pages],
            immutable_template_page_domain=[wf_lo,wf_hi],all24_inside_scanned_raw_container=True),
        scope='Current source metadata/decoder and declared target domains; source-model only',
        outputs=0,Mesen_run=False)


def run(raw):
    Model.typed(raw);_,lease=Model.recipe(raw);b=Model.Cold.bundle(Model.typed(raw));b=dict(b,raw=raw)
    rows=[]
    for owner in range(37,44):
        q=common_cold(raw,owner,b);rows.append(q)
        print('PROGRESS '+json.dumps(dict(owner=owner,descriptor=q['actual_descriptor'],code_words=q['code_target_words'],metadata_words=q['metadata_target_words'])),flush=True)
    head,streams,packed=Prince.extract(raw)
    decoded=[dict(role=role,decoded_bytes=len(data),packed_bytes=packed[i],SHA256=sha256(data).hexdigest(),
        target_words=matches(data,base))for i,(role,base,data)in enumerate(zip(('Prince_runtime','Prince_metadata','Prince_staged_state'),(0xa000,0xc800,0xc100),streams,strict=True))]
    groups=[]
    names={'FF_STREAM','BW_STREAM','BT_STREAM','CF_CARRIER','QW_STREAM','KR_KERNEL_IMAGE','ARTHUR_CACHE_EXEC','WF_TEMPLATE_CHR'}
    for seg in b['segs'].values():
        if seg['name'].strip('"')not in names:continue
        at=int(seg['ooffs'],0);size=int(seg['size'],0);data=raw[at:at+size]
        groups.append(dict(role=seg['name'],file=[at,at+size],bytes=size,SHA256=sha256(data).hexdigest(),
            target_words=matches(data,0),raw_container_only=True))
    return dict(proposal=lease,current_common7_actual_loader_results=rows,Prince_authenticated_decoded_streams=decoded,
        Prince_container_bytes=len(head)+sum(packed),other_raw_executable_containers=groups,
        literal_or_word_hits_require_reader_classification=True,indirect_split_plane_and_CFG_closure_pending=True,
        ROM_composed=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--static',action='store_true');args=ap.parse_args()
    raw=Model.Input.ROM.read_bytes();Model.typed(raw)
    def forbid(*a,**k):raise RuntimeError('Ingress research attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Model.Cold.Runner.Native,'run',forbid):q=static(raw)if args.static else run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
