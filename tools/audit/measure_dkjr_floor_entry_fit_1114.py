"""Exact existing-span DK endpoint funding proposal; no ROM composition."""
from hashlib import sha256
import json
import re

import measure_dkjr_indirect_funding_1114 as Indirect
import measure_dkjr_compact_floor_entry_1114 as Endpoint

P,H=Indirect.P,Indirect.H


def measure(*,include_model=False):
    inventory,m=Indirect.inventory(include_model=True)
    source,labels,body=m['source'],m['labels'],m['body']
    defs,endpoint=Endpoint.sources()
    fruit_begin,fruit_end=labels['D_d955'],labels['D_da14']
    fruit=source[source.index('D_d955:'):source.index('D_da14:')]
    fruit_defined=set(re.findall(r'^(\w+):',fruit,re.M))
    original_defs=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in fruit_defined)
    original=H.T.assemble(original_defs+'.segment "FRUIT"\n'+fruit,
        dict(FRUIT=(fruit_begin,fruit_end-fruit_begin)))
    assert original['used']['FRUIT']==fruit_end-fruit_begin
    assert original['images']['FRUIT']==body[fruit_begin-0xa000:fruit_end-0xa000]
    for row in m['rows']:
        if not(row['exact_current']and fruit_begin<=row['PC']<fruit_end):continue
        assert row['operation']=='lda'and row['pointer']==0xc091
        suffix=row['label'][2:]
        match=re.search(r'^DIndirect_'+suffix+r': lda \$ffff,y$',fruit,re.M)
        start=fruit.index(row['label']+':');stop=match.end()
        fruit=fruit[:start]+row['label']+':\n jsr ReadPointer91\n'+fruit[stop:]
    draw_begin,draw_end=labels['D_ea08'],labels['D_eb69']
    helpers=m['helpers'].split('.segment "HELPERS"',1)[1]
    read4=helpers[:helpers.index('ReadPointer91:')]
    read91=helpers[helpers.index('ReadPointer91:'):helpers.index('StorePointer04:')]
    store4=helpers[helpers.index('StorePointer04:'):]
    parts={name:chunk for name,chunk in re.findall(r'\.segment "(\w+)"\n(.*?)(?=\.segment|\Z)',endpoint,re.S)}
    assert set(parts)=={'ENTRY','PREDICATE','VISIBLE','FLOOR','STATIC','CONTEXT'}
    fruit_compact_size=fruit_end-fruit_begin-88
    layout=dict(FRUIT=(fruit_begin,fruit_compact_size),
        READ91=(fruit_begin+fruit_compact_size,14),
        ENTRY=(fruit_begin+fruit_compact_size+14,56),
        DRAW=(draw_begin,428),READ4=(draw_begin+428,14),STORE4=(draw_begin+442,26),
        STATIC=(draw_begin+468,100),FLOOR=(draw_begin+568,60),
        CONTEXT=(draw_begin+628,52),VISIBLE=(draw_begin+680,17),
        ANCHOR=(0xbfc1,3),PREDICATE=(0xbfc4,22),BODY_GUARD=(0xbc8c,10),SERVICE34=(0xa066,3))
    sections={'FRUIT':fruit,'DRAW':m['draw_source'],'READ4':read4,'READ91':read91,
        'STORE4':store4,**parts,
        'ANCHOR':' jmp MeasuredAnchorReady\n',
        'BODY_GUARD':' jsr MeasuredDrawAdmission\n bcs FittedBodyYes\n jmp $bd24\nFittedBodyYes:\n nop\n nop\n',
        'SERVICE34':' jmp MeasuredAfterEffects\n'}
    all_source=''.join(f'.segment "{name}"\n{sections[name]}\n'for name in layout)
    defined=set(re.findall(r'^(\w+):',all_source,re.M))
    defs+=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined and not re.search(r'^'+re.escape(n)+r'=',defs,re.M))
    proposed=H.T.assemble(defs+all_source,layout)
    assert all(proposed['used'][name]==size for name,(_,size)in layout.items())
    spans=[('fruit',fruit_begin,fruit_end),('draw',draw_begin,draw_end),
        ('anchor',0xbfc1,0xbfe0),('body_guard',0xbc8c,0xbc96),('service34',0xa066,0xa069)]
    rows=[]
    for role,lo,hi in spans:
        before=body[lo-0xa000:hi-0xa000];after=bytearray(b'\xea'*(hi-lo))
        members=[]
        for name,(pc,size)in layout.items():
            if lo<=pc<hi:
                assert pc+size<=hi
                after[pc-lo:pc-lo+size]=proposed['images'][name]
                members.append(dict(name=name,PC=pc,bytes=size))
        rows.append(dict(role=role,PC=lo,end_exclusive=hi,bytes=hi-lo,
            payload_offset=lo-0xa000,preimage_hex=before.hex(),proposed_hex=after.hex(),
            preimage_SHA256=sha256(before).hexdigest(),proposed_SHA256=sha256(after).hexdigest(),members=members))
    callers=[]
    for base,data in ((0xa000,body[:0x1fe0]),(0xc900,body[8192:9216]),(0xd000,body[9216:])):
        for i in range(len(data)-2):
            target=int.from_bytes(data[i+1:i+3],'little');pc=base+i
            if data[i]in (0x20,0x4c)and fruit_begin<=target<fruit_end and not fruit_begin<=pc<fruit_end:
                callers.append(dict(PC=pc,opcode=data[i],target=target))
    result=dict(measurement_only=True,ROM_composed=False,allocation_granted=False,
        private_parent_SHA256=inventory['actual_private_SHA256'],fragments=rows,
        logical_envelope_bytes=sum(r['bytes']for r in rows),
        endpoint_bytes=sum(proposed['used'][n]for n in parts),generic_helper_bytes=54,
        remaining_source_spare=dict(fruit_tail=18,draw_tail=17,anchor_tail=6),
        new_CHR_pages=0,new_RAM_bytes=0,new_native_PRG_bytes=0,cold_copier_changed=False,
        head_bridge_bytes_changed=False,all_source_pointer_high_values_still_supported=True,
        old_fruit_external_literal_consumers=callers,
        old_draw_external_literal_consumers=inventory['draw_fragment']['external_executable_literal_consumers'],
        old_draw_data_coincidence=inventory['draw_fragment']['conservative_byte_census_data_coincidences'],
        moved_source_exports=inventory['draw_fragment']['explicit_source_exports_inside'],
        outputs_written=0,complete_consumer_ABI_IRQ_and_finite_semantics_closure=False,
        scope='Measured exact preimages and five-fragment proposal only; no ROM/capsule re-encoding, executable RAM placement, candidate, native or resource grant.')
    if include_model:return result,dict(proposed=proposed,sections=sections,layout=layout,original=m)
    return result


if __name__=='__main__':
    print('DKJR_FLOOR_ENTRY_FIT '+json.dumps(measure(),separators=(',',':')),flush=True)
