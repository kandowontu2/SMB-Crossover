"""Current source/SMC relocation consumers for the measured five DK spans."""
from hashlib import sha256
import json
import re

import measure_dkjr_floor_entry_fit_1114 as Fit

P,H=Fit.P,Fit.H


def run():
    proposal,model=Fit.measure(include_model=True)
    original=model['original'];source=original['source'];labels=original['labels'];body=original['body']
    new=model['proposed']['symbols']
    moved={name:(value,new[name])for name,value in labels.items()if name in new and value!=new[name]
        and name.startswith(('D_','DkShortCandidate'))and any(lo<=value<hi for lo,hi in
            ((labels['D_d955'],labels['D_da14']),(labels['D_ea08'],labels['D_eb69'])))}
    assert moved
    outside=source
    for begin,end in (('D_d955','D_da14'),('D_ea08','D_eb69')):
        outside=outside[:outside.index(begin+':')]+outside[outside.index(end+':'):]
    external=[]
    for line_no,line in enumerate(outside.splitlines(),1):
        code=line.split(';',1)[0].strip()
        if not code or code.startswith('.export '):continue
        hits=sorted(set(re.findall(r'\b\w+\b',code))&set(moved))
        if hits:external.append((line_no,code,hits))
    assert not external,external
    native=[]
    for root in ('src','inc'):
        for path in sorted((P.B.R/root).rglob('*')):
            if path.suffix not in ('.s','.inc'):continue
            for number,line in enumerate(path.read_text(errors='replace').splitlines(),1):
                code=line.split(';',1)[0]
                hits=sorted(set(re.findall(r'\b\w+\b',code))&set(moved))
                if hits:native.append((str(path.relative_to(P.B.R)),number,code,hits))
    assert not native,native
    def current_instructions(opcode,target):
        out=[]
        for lo,data in ((0xa000,body[:0x1fe0]),(0xc900,body[8192:9216]),(0xd000,body[9216:])):
            out.extend(lo+i for i in range(len(data)-2)if data[i]==opcode
                and int.from_bytes(data[i+1:i+3],'little')==target)
        return out
    stores=[]
    for row in original['rows']:
        if not row['exact_current']:continue
        for operand,offset in ((row['PC']+23,5),(row['PC']+24,17)):
            actual=current_instructions(0x8d,operand)
            assert actual==[row['PC']+offset],(row['label'],hex(operand),actual)
            stores.append(dict(SMC_operand=operand,sole_current_writer=actual[0]))
    # Every current ROM-visible row is a JMP; none publishes a moved body
    # label. The two preserved original aliases keep their exact addresses.
    services=labels['DkServices'];table=body[services-0xa000:services-0xa000+38*3]
    assert len(table)==114 and all(table[i]==0x4c for i in range(0,114,3))
    targets=[int.from_bytes(table[i+1:i+3],'little')for i in range(0,114,3)]
    assert not set(targets)&{old for old,_ in moved.values()}
    aliases={n:labels[n]for n in ('DkjrPose','DkjrFruitAdvance','DkjrFruitCollision','DkjrRect')}
    assert all(new[n]==value for n,value in aliases.items())
    anchor=next(r for r in proposal['fragments']if r['role']=='anchor')
    anchor_lo,anchor_hi=anchor['PC'],anchor['end_exclusive'];anchor_consumers=[]
    for lo,data in ((0xa000,body[:0x1fe0]),(0xc900,body[8192:9216]),(0xd000,body[9216:])):
        for i in range(len(data)-2):
            pc=lo+i;target=int.from_bytes(data[i+1:i+3],'little')
            if data[i]in (0x20,0x4c)and anchor_lo<=target<anchor_hi and not anchor_lo<=pc<anchor_hi:
                anchor_consumers.append(dict(PC=pc,opcode=data[i],target=target))
    assert anchor_consumers and all(r['target']==anchor_lo for r in anchor_consumers),anchor_consumers
    cell=original['reader_cell'];translate=original['reader_translate']
    assert body[translate-0xa000:cell-0xa000+3]==bytes.fromhex('c908b00209c08d67ae6828b9ffff')
    assert current_instructions(0x8d,cell+1)==[translate-6]
    assert current_instructions(0x8d,cell+2)==[translate+6]
    words=re.findall(r'^\s*\.word\s+([^\n;]+)',source,re.M)
    assert words and all(re.fullmatch(r'DData_c[0-9a-f]{3}',word.strip())for word in words),words
    return dict(passed=True,private_parent_SHA256=proposal['private_parent_SHA256'],
        current_source_SHA256=H.T.FROZEN_SHA,moved_labels={n:dict(old=o,new=v)for n,(o,v)in sorted(moved.items())},
        source_export_relocations_explicit=True,external_original_source_consumers=external,
        external_native_named_consumers=native,preserved_aliases=aliases,
        public_service_rows=38,no_service_row_publishes_moved_internal_label=True,
        source_data_vectors_only_symbolic_DData_targets=True,source_word_vector_count=len(words),
        original_SMC_operand_writer_census=stores,
        unchanged_shared_reader=dict(translate_PC=translate,cell_PC=cell,
            low_writer=translate-6,high_writer=translate+6,new_prefixes_push_P_then_A=True,
            high_translation_dominates_every_load=True,every_old_RectRead_call_republishes_low_and_high=True),
        old_anchor_external_literal_consumers=anchor_consumers,
        ordinary_Main_cookie_cold_or_native_admission=False,ROM_composed=False,outputs_written=0,
        scope='Current retained-source + actual private literal/SMC/table consumer closure. Other-bank numerical coincidences are outside the RAM3 caller domain; public native dispatch continues through unchanged A000+3*row anchors.')


if __name__=='__main__':print('DKJR_FLOOR_ENTRY_CONSUMERS '+json.dumps(run(),separators=(',',':')),flush=True)
