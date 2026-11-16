"""Current parent-only Wf entry/structured producer census; no new-code CPU."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import inspect,json
import plan_battletoads_flat_resolver_1115 as Prior
import audit_contra_force_wf_status_funding_1116 as Status

S,C,M=Status.S,Status.C,Status.S.M


def run(raw):
    assert C.H(raw)==C.PIN
    source=inspect.getsource(Prior.ingress)
    changes=(('b=Base.symbols(image);','b=M.symbols(image);'),
        ('targets=set(range(0xb799,0xb848))','targets=set(range(0xb796,0xb848))'),
        ("macros[0]['target']==0xb79d","macros[0]['target']==0xb799"),
        ("assert len(wf)==16 and {r['CPU']for r in wf}=={0xb799,0xb79b}","assert not wf,('Current Wf table still publishes old aliases',wf)"),
        ("names=('WfResolve','WfNoop'","names=('WfOneLifeStatus','WfResolve','WfNoop'"))
    for old,new in changes:assert source.count(old)==1,old;source=source.replace(old,new)
    scope=dict(Prior.__dict__,M=M)
    exec(compile(source,str(Path(__file__))+':current-source-domain-rebinding','exec'),scope)
    actual=scope['ingress'](raw,raw);actual['reference_SHA256']=C.H(raw)
    bank_word_rows=[];direct=[];standard_triples=[];push_return=[]
    targets=(0xb796,0xb797,0xb798,0xb799)
    for bank in range(128):
        page=raw[16+bank*8192:16+(bank+1)*8192]
        for target in targets:
            pos=0
            while(pos:=page.find(target.to_bytes(2,'little'),pos))>=0:
                row=dict(bank=bank,file=16+bank*8192+pos,offset=pos,target=target,
                    preceding=page[pos-1]if pos else None)
                if bank in(96,126,127):bank_word_rows.append(row)
                if row['preceding']in(0x20,0x4c,0x6c):
                    assert bank not in(96,126,127),('Unclassified Wf-capable direct control',row)
                    row['classification']='Absolute near control keeps this same non96 bank; opcode itself cannot map96'
                    row['target_physical_file']=16+bank*8192+(target&8191);direct.append(row)
                pos+=1
            for pattern in((target.to_bytes(2,'little')+bytes([224])),
                bytes((0xa9,(target-1)>>8,0x48,0xa9,(target-1)&255,0x48,0x60))):
                pos=0
                while(pos:=page.find(pattern,pos))>=0:
                    row=dict(bank=bank,file=16+bank*8192+pos,target=target,pattern=pattern.hex())
                    (standard_triples if len(pattern)==3 else push_return).append(row);pos+=1
    assert not bank_word_rows and not standard_triples and not push_return
    macro=actual['sole_PRG_bankE0_resolver_farcall'];assert len(macro)==1
    assert macro[0]['offset']+16==716848+0xb0c3-0xb020,macro
    old=dict(Status.run(raw))
    helper=raw[792489:792489+67];return_producers=[]
    for pattern,kind in(('2039b6','Owning group predicate JSR'),('205a01','Owning full-check SFC JSR')):
        needle=bytes.fromhex(pattern);assert helper.count(needle)==1
        pc=0xb799+helper.index(needle);return_producers.append(dict(PC=pc,bytes=pattern,return_PC=pc+3,kind=kind))
    return dict(actual_reference6a3_SHA256=C.H(raw),all_new_arrays_unexecuted=True,
        exact_current_structured_and_container_domains=actual,
        all_same_or_fixed_bank_Wf_status_entry_words=bank_word_rows,
        standard_E0_threebyte_targets=standard_triples,standard_push_RTS_return_producers=push_return,
        other_bank_near_control_candidates=direct,retired_status_source_and_domain_census=old,
        helper_SFC_internal_return_producers=return_producers,
        sole_actual_old_B799_consumer_requires_Router_rebind=True,
        limits=['Typed producer/descriptor and declared executable-container domains; arbitrary computed numeric addresses are not legal roots',
            'Retained compiler reference spans are versioned metadata rebound to exact current bytes, not a rebuilt historical source graph',
            'No CPU, code mount, allocation, ROM file or native run performed'],outputs=0)


if __name__=='__main__':
    raw,pin=S.load_reference()
    def deny(*a,**kw):raise AssertionError('Entry census attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    q['actual_input_SHA256']=pin;q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
