"""Inventory current DK SMC wrappers for a smaller source funding proposal.

Measurement only. No cartridge or executable RAM is changed or composed.
"""
from collections import Counter
from hashlib import sha256
import json
import re

import compose_dkjr_oneway_support_1114 as S
import check_dkjr_platform_query_lifecycle_1114 as Life

F=S.Replay;G=F.Gate
P,H=G.P,G.H


def inventory(*,include_model=False):
    _,old=F.load_inputs();raw,_=S.proposal(old)
    _,labels=Life.closure(old);source,*_=H.T.old_source();body=P.T.payload(raw)
    rows=[]
    for match in re.finditer(r'^DIndirect_([0-9a-f]+): (lda|sta) \$ffff,y$',source,re.M):
        suffix,op=match.groups();name='D_'+suffix;start=source.index(name+':')
        fragment=source[start:match.end()]+'\n'
        defined=set(re.findall(r'^(\w+):',fragment,re.M))
        defs=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
        linked=H.T.assemble(defs+'.segment "WRAP"\n'+fragment,dict(WRAP=(labels[name],64)))
        data=linked['images']['WRAP'];at=H.T.offset(labels[name]);size=len(data)
        ptr=re.findall(r' lda \$(c[0-9a-f]{3})\n',fragment)
        assert len(ptr)==2 and int(ptr[1],16)==int(ptr[0],16)+1
        rows.append(dict(label=name,operation=op,pointer=int(ptr[0],16),PC=labels[name],
            bytes=size,generated_hex=data.hex(),SHA256=sha256(data).hexdigest(),
            exact_current=body[at:at+size]==data))
    groups=Counter((r['operation'],r['pointer'])for r in rows if r['exact_current'])
    # The already-current head bridge has the same full-domain translator.
    # New read prefixes may enter its existing CMP#8 and retain the exact
    # PHP/PHA/PLA/PLP contract. No head-source byte is changed here.
    rect=H.T.SOURCE.read_text().split('DkRectCompactEnd:')[0]
    reader=H.T.assemble('RectPredicate=$aeef\n'+rect,dict(RECT=(0xadea,261)))
    cell=reader['symbols']['RectReadCell'];read=reader['symbols']['RectRead']
    code=reader['images']['RECT'];assert body[0xdea:0xdea+len(code)]==code
    translate=read+11
    assert body[translate-0xa000:translate-0xa000+4]==bytes.fromhex('c908b002')
    helpers=f'''
.segment "HELPERS"
ReadPointer04:
 php
 pha
 lda $c004
 sta ${cell+1:x}
 lda $c005
 jmp ${translate:x}
ReadPointer91:
 php
 pha
 lda $c091
 sta ${cell+1:x}
 lda $c092
 jmp ${translate:x}
StorePointer04:
 php
 pha
 lda $c004
 sta StoreCell+1
 lda $c005
 cmp #8
 bcs StoreROM
 ora #$c0
StoreROM:
 sta StoreCell+2
 pla
 plp
StoreCell:
 sta $ffff,y
 rts
'''
    measured=H.T.assemble(helpers,dict(HELPERS=(0x9000,128)))
    assert measured['used']['HELPERS']==54
    begin,end=labels['D_ea08'],labels['D_eb69']
    fragment=source[source.index('D_ea08:'):source.index('D_eb69:')]
    defined=set(re.findall(r'^(\w+):',fragment,re.M))
    defs=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
    original=H.T.assemble(defs+'.segment "DRAW"\n'+fragment,dict(DRAW=(begin,end-begin)))
    assert original['used']['DRAW']==end-begin
    assert original['images']['DRAW']==body[begin-0xa000:end-0xa000]
    compact=fragment;compacted=0
    for row in rows:
        if not (row['exact_current']and begin<=row['PC']<end):continue
        suffix=row['label'][2:];match=re.search(r'^DIndirect_'+suffix+r': (lda|sta) \$ffff,y$',compact,re.M)
        start=compact.index(row['label']+':');stop=match.end()
        target='ReadPointer04'if row['operation']=='lda'else'StorePointer04'
        compact=compact[:start]+row['label']+':\n jsr '+target+'\n'+compact[stop:]
        compacted+=1
    assert compacted==13
    newdefs=defs+''.join(f'{n}=${v:x}\n'for n,v in measured['symbols'].items())
    after=H.T.assemble(newdefs+'.segment "DRAW"\n'+compact,dict(DRAW=(begin,end-begin)))
    assert original['used']['DRAW']-after['used']['DRAW']==286
    callers=[]
    for base,data in ((0xa000,body[:0x1fe0]),(0xc900,body[8192:9216]),(0xd000,body[9216:])):
        for i in range(len(data)-2):
            target=int.from_bytes(data[i+1:i+3],'little');pc=base+i
            if data[i]in(0x20,0x4c)and begin<=target<end and not begin<=pc<end:
                callers.append(dict(PC=pc,opcode=data[i],target=target))
    data_coincidence=dict(PC=labels['DData_c312'],opcode=0x20,target=0xac50)
    assert body[labels['DData_c312']-0xa000:labels['DData_c312']-0xa000+3]==bytes.fromhex('2050ac')
    executable=[dict(PC=labels['D_dbe5'],opcode=0x20,target=begin),
        dict(PC=labels['D_e9f8'],opcode=0x20,target=begin),
        dict(PC=labels['D_e9fe'],opcode=0x4c,target=begin),
        dict(PC=labels['D_ea03'],opcode=0x4c,target=begin)]
    assert callers==executable+[data_coincidence],callers
    debug_labels=[n for n,v in P.frozen_labels().items()if begin<=v<end]
    exports=set(re.findall(r'\b\w+\b',' '.join(re.findall(r'^\.export ([^\n;]+)',source,re.M))))
    published=sorted(n for n in exports if n in labels and begin<=labels[n]<end)
    result=dict(measurement_only=True,ROM_composed=False,RAM_changes=0,
        actual_private_SHA256=sha256(raw).hexdigest(),retained_wrappers=len(rows),
        exact_current_wrappers=sum(r['exact_current']for r in rows),
        groups=[dict(operation=op,pointer=ptr,count=count)for(op,ptr),count in sorted(groups.items())],
        rows=rows,outputs_written=0,
        measured_generic_helpers=dict(measurement_origin=0x9000,bytes=54,
            generated_hex=measured['images']['HELPERS'].hex(),
            SHA256=sha256(measured['images']['HELPERS']).hexdigest(),
            existing_current_RectRead=read,existing_translate=translate,existing_read_cell=cell,
            existing_reader_bytes_unchanged=True,pointer_high_restrictions_added=False),
        draw_fragment=dict(PC=begin,end_exclusive=end,current_bytes=end-begin,
            current_SHA256=sha256(original['images']['DRAW']).hexdigest(),
            compact_bytes=after['used']['DRAW'],wrappers_compacted=compacted,
            savings_before_helpers=286,external_executable_literal_consumers=executable,
            conservative_byte_census_data_coincidences=[dict(**data_coincidence,
                source_labels=['DData_c312','DData_c313','DData_c314'],
                source_bytes_hex='2050ac',classification='Three body-pose data bytes, not an instruction boundary. Unchanged.')],
            explicit_source_exports_inside=published,retained_debug_labels_inside=debug_labels,entry_preserved=begin,
            source_relocation_and_indirect_consumer_closure_complete=False),
        aggregate_savings_before_endpoint_and_layout=17*22-54,
        scope='Exact current SMC preimages and virtual fragment fit only; no ABI, whole relocation, interrupt, resource grant or candidate claim.')
    if include_model:
        return result,dict(source=source,labels=labels,body=body,rows=rows,
            helpers=helpers,draw_source=compact,reader_translate=translate,reader_cell=cell)
    return result


if __name__=='__main__':
    print('DKJR_INDIRECT_FUNDING '+json.dumps(inventory(),separators=(',',':')),flush=True)
