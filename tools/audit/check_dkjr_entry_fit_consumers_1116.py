"""Detached entry-only current consumer closure; no executable overlay."""
from hashlib import sha256
import json
import re

import measure_dkjr_forced_entry_fit_1116 as Fit

C,Plan=Fit.C,Fit.Plan.Plan
H=lambda value:sha256(value).hexdigest()


def check(parent):
    proposal=Fit.measure(parent);raw,_=C.proposal(parent);body=C.Camera.payload(raw)
    source,labels=Plan.source_inputs()
    moved={row['label']:(row['old_PC'],row['new_PC'])for row in proposal['moved_labels']}
    assert moved
    outside=source
    for first,last in(('D_d955','D_da14'),('D_ea08','D_eb69')):
        outside=outside[:outside.index(first+':')]+outside[outside.index(last+':'):]
    source_hits=[]
    for number,line in enumerate(outside.splitlines(),1):
        code=line.split(';',1)[0].strip()
        if not code or code.startswith('.export '):continue
        hits=sorted(set(re.findall(r'\b\w+\b',code))&set(moved))
        if hits:source_hits.append((number,code,hits))
    assert not source_hits,source_hits
    native_hits=[]
    for folder in('src','inc'):
        for path in sorted((C.R/folder).rglob('*')):
            if path.suffix not in('.s','.inc'):continue
            for number,line in enumerate(path.read_text(errors='replace').splitlines(),1):
                hits=sorted(set(re.findall(r'\b\w+\b',line.split(';',1)[0]))&set(moved))
                if hits:native_hits.append((str(path.relative_to(C.R)),number,hits))
    assert not native_hits,native_hits
    carriers=((0xa000,body[:0x1fe0]),(0xc900,body[8192:9216]),(0xd000,body[9216:]))
    def absolute(opcode,target):
        return [base+i for base,data in carriers for i in range(len(data)-2)
            if data[i]==opcode and int.from_bytes(data[i+1:i+3],'little')==target]
    smc=[]
    for row in proposal['exact_funding_templates']:
        pc=row['old_PC']
        for operand,writer in((row['old_cell_PC']+1,pc+5),(row['old_cell_PC']+2,pc+17)):
            assert absolute(0x8d,operand)==[writer],(row,operand,absolute(0x8d,operand))
            smc.append(dict(old_field=operand,sole_old_writer=writer,role=row['role'],operation=row['operation']))
    services=body[:38*3]
    assert all(services[i]==0x4c for i in range(0,114,3))
    targets=[int.from_bytes(services[i+1:i+3],'little')for i in range(0,114,3)]
    assert not set(targets)&{old for old,_ in moved.values()}
    words=re.findall(r'^\s*\.word\s+([^\n;]+)',source,re.M)
    assert words and all(re.fullmatch(r'DData_c[0-9a-f]{3}',word.strip())for word in words)
    entries=[]
    spans=[(row['PC'],row['end_exclusive'])for row in proposal['fragments']if row['role']in('fruit','draw','anchor')]
    for base,data in carriers:
        for i in range(len(data)-2):
            pc=base+i;target=int.from_bytes(data[i+1:i+3],'little')
            if data[i]not in(0x20,0x4c,0x6c)or not any(lo<=target<hi for lo,hi in spans):continue
            if any(lo<=pc<hi for lo,hi in spans):continue
            entries.append(dict(PC=pc,opcode=data[i],target=target))
    coincidence=dict(PC=labels['DData_c312'],opcode=0x20,target=0xac50)
    assert coincidence in entries
    at=coincidence['PC']-0xa000
    assert body[at:at+3]==bytes.fromhex('2050ac')
    live=[row for row in entries if row!=coincidence]
    assert len(live)==6 and all(row['target']in{lo for lo,_ in spans}for row in live),live
    return dict(passed=True,detached_only=True,actual_source_parent_a3fb=H(raw),
        measured_fit_receipt_SHA256=H(json.dumps(proposal,sort_keys=True,separators=(',',':')).encode()),
        semantic_moved_labels=len(moved),moved_label_map={n:dict(old=a,new=b)for n,(a,b)in sorted(moved.items())},
        external_source_named_consumers=source_hits,external_native_named_consumers=native_hits,
        sole_old_SMC_field_writers=smc,public_rows=38,public_row_interiors_unpublished=True,
        immutable_source_word_vectors=len(words),source_vectors_are_DData_only=True,
        conservative_external_literal_candidates=entries,live_external_entries_preserved=live,
        immutable_data_coincidence=dict(**coincidence,source_label='DData_c312',bytes_hex='2050ac',
            classification='Three original pose-data bytes, not a source instruction or dispatch pointer; unchanged.'),
        native_RAM3_domain='Existing authenticated Selected40 service dispatch A000+3*row; no direct external named interior draw/fruit consumer.',
        current_heads_and_runtime_cells_unborrowed=True,
        CPU_executed=False,source_overlay=False,ROM_composed=False,outputs=0,
        scope='Source named/word/SMC and three actual DK carrier literal census. The sole extra raw candidate is authenticated original pose data. Other-bank numeric coincidences do not bypass the authenticated RAM3 service domain. ABI/IRQ and legal entry lifecycle remain post-lease work.')


if __name__=='__main__':
    report=check(C.BT.ROM.read_bytes())
    text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_FIT_CONSUMERS '+text,flush=True)
    print('DKJR_ENTRY_FIT_CONSUMERS_SHA256 '+H(text.encode()),flush=True)
