"""Explicit owning draw lifecycle-field/fault component fixtures, no gameplay seeds."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import compose_hot_draw_bt_67e_1115 as C
import hot_draw_bt_67e_model_1115 as Model
import check_hot_draw_bt_public_67e_1115 as Public

N,W=Model.N,Model.W


def compact(row):
    q={k:row[k]for k in('PC','A','X','Y','P','SP','CPU','minimum_SP','calls')}
    q['checks']=[]
    for h in row['header_checks']:
        q['checks'].append(dict(tag=h['tag'],PC=h['PC'],SP=h['SP'],return_=h['return'],
            published_target=h['published_target'],accepted=h['accepted'],returned_P=h['returned_P'],
            physical_RAM_header=3,read_indices_in_order=[r['index']for r in h['header_reads']],
            reader_PCs=sorted({r['PC']for r in h['header_reads']}),
            mapped_header_addresses=[r['address']for r in h['header_reads']]))
    return q


def run(parent,image):
    rows=[];cases=0;savings=Counter();checks=Counter()
    for key in('rash','zitz'):
        seed,regs=Public.capture(parent,key)
        vectors=[('header',bad,None)for bad in(-1,0,7,15,16)]
        for field,values in(('OperMode',range(4)),('OperMode_Task',range(5)),('GameEngineSubroutine',range(13)),
            ('GamePauseStatus',range(4)),('Player_State',range(4)),('PlayerStatus',range(3)),
            ('DisableScreenFlag',range(2)),('FmGroups',(0,1,7,32,64,65,71,96,97,103,255))):
            vectors.extend((field,value,None)for value in values)
        for field,value,_ in vectors:
            pair=[Model.reimage(seed,raw)for raw in(parent,image)]
            for m in pair:
                if field=='header':
                    if 0<=value<16:m.ram[3][0x1fe0+value]^=1
                    elif value==16:m.ram[3][0x1fe0]=0
                else:N.put(m,**{field:value})
            out=[Public.execute(m,regs)for m in pair]
            Public.compare(pair,out,(key,field,value))
            assert out[0]['calls'].get('BtCheck',0)==out[1]['calls'].get('BtCheck',0),(key,field,value,out)
            savings[field,out[0]['CPU']-out[1]['CPU']]+=1
            checks[field,out[0]['calls'].get('BtCheck',0)]+=1;cases+=1
            if field=='header':rows.append(dict(identity=key,header_fault=value,returns=[compact(r)for r in out]))
        print('PROGRESS '+json.dumps(dict(identity=key,actual_draw_state_cases=cases)),flush=True)
    return dict(cases=cases,explicit_component_fixtures=True,
        initial_state='Genuine compiled Rash/Zitz cold and reached PRG4:A122 caller; one named input field or cache header byte varies',
        ordinary_gameplay_or_natural_death_not_claimed=True,
        exact_public_return_private_state_OAM_PPU_maps_SMC_live_caller_stack=True,
        savings=[dict(field=f,cycles=d,cases=n)for(f,d),n in sorted(savings.items())],
        check_counts=[dict(field=f,checks=c,cases=n)for(f,c),n in sorted(checks.items())],
        actual_fault_check_entry_return_SP_PC_and_header_reader_examples=rows)


if __name__=='__main__':
    raw=C.load_current_image();parent=Model.F.parent(raw);image,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('State fixture attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(parent,image)
    q.update(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
