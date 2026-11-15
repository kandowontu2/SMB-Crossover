"""Strict590 pure three-span encoding plan; never rebuild a combined ROM."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,struct
import current_prince_transition_590_1115 as Current
import compose_prince_body_world_1114 as Body
import research_prince_opponent_absence_1114 as Transition

R,Packet=Body.R,Current.Graphics.Packet
PIN=Current.Graphics.CANDIDATE
SOURCE_GATES={
    'tools/audit/check_prince_transition_free_idle_1115.py':'39a65a2a97d2c17d56e09161f0c9c0f1e513420051d1f9d86c400e8702df1e14',
    'tools/audit/check_prince_transition_interrupt_pairs_1115.py':'3ce63530ea873a399c14cdc2cef887580086b68601f689e5bc1111ec6b1d979a',
    'tools/audit/research_prince_opponent_absence_1114.py':'7cc6c6f773effad8a6de3c21046d8b8c21f5cc79f45e4e336b6586950d2045d2',
}


def digest(data):return sha256(data).hexdigest()


def plan(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact verified590'
    for name,pin in SOURCE_GATES.items():assert digest((R/name).read_bytes())==pin,name
    current=Current.normalize(raw,kind='prince-graphics-590');header,before,old_sizes=Packet.extract(raw)
    # Reuse the exact source assembler and its typed original reference, not
    # a restored historical candidate or any mutable nightly baseline.
    original_reference=Body.normalize_parent(current.reference1daca,kind='dk-window7-1daca')
    fitted=Body.Funding.plan(original_reference.reference421)
    replacements=(fitted['world']+bytes([234])*3,fitted['prepare']+fitted['helper'])
    spans=[];after=list(map(bytearray,before))
    for row,new in zip(Body.allocation()['decoded_spans'],replacements,strict=True):
        stream=row['decoded_stream'];lo,hi=row['decoded_half_open'];old=before[stream][lo:hi]
        assert digest(old)==row['preimage_SHA256']and digest(new)==row['proposed_SHA256']and len(new)==hi-lo
        after[stream][lo:hi]=new
        spans.append(dict(name=row['name'],stream=stream,decoded_half_open=[lo,hi],live_CPU_half_open=row['live_CPU_half_open'],
            bytes=hi-lo,preimage_SHA256=digest(old),proposed_SHA256=digest(new)))
    transition=Transition.importer_plan(current.referenceAE);lo,hi=Transition.START-0xc800,Transition.END-0xc800
    old=before[1][lo:hi];new=transition['new'];assert old==transition['old']and len(new)==219
    after[1][lo:hi]=new
    spans.append(dict(name='Opponent-loss transition importer',stream=1,decoded_half_open=[lo,hi],
        live_CPU_half_open=[Transition.START,Transition.END],bytes=219,preimage_SHA256=digest(old),proposed_SHA256=digest(new)))
    changed=[]
    for stream,(a,b)in enumerate(zip(before,after,strict=True)):
        allowed={at for row in spans if row['stream']==stream for at in range(*row['decoded_half_open'])}
        assert len(a)==len(b)and all(x==y for at,(x,y)in enumerate(zip(a,b,strict=True))if at not in allowed)
        changed.extend((stream,at)for at,(x,y)in enumerate(zip(a,b,strict=True))if x!=y)
    for row in Current.Graphics.allocation()['decoded_envelopes']:
        stream=row['stream'];lo=row['offset'];hi=lo+row['bytes'];assert bytes(after[stream][lo:hi])==before[stream][lo:hi]
    parts=tuple(map(bytes,after));packed=tuple(map(Packet.encode,parts));sizes=tuple(map(len,packed))
    config=len(header)-54;words=struct.unpack_from('<12H',header,config)
    newwords=(0xc500,0xa000,sizes[0],len(parts[0]),0xe100-sizes[1],0xc800,sizes[1],len(parts[1]),0xc300,0xc100,sizes[2],len(parts[2]))
    planned_header=bytearray(header);struct.pack_into('<12H',planned_header,config,*newwords)
    edits=[dict(word_index=i,head_half_open=[config+2*i,config+2*i+2],old=a,new=b)
        for i,(a,b)in enumerate(zip(words,newwords,strict=True))if a!=b]
    allowed_header={at for row in edits for at in range(*row['head_half_open'])}
    assert all(a==b for at,(a,b)in enumerate(zip(header,planned_header,strict=True))if at not in allowed_header)
    assert {row['word_index']for row in edits}<={2,4,6,10}
    assert bytes(planned_header[:31072])==header[:31072]and bytes(planned_header[-30:])==header[-30:]
    capacity=len(Packet.PAGES)*1024;used=len(planned_header)+sum(sizes)
    assert len(Packet.PAGES)==45 and used<=capacity and sizes[0]<=6528 and 0xe100-sizes[1]>=0xc900 and sizes[2]<=1280
    payload=bytes(planned_header)+b''.join(packed)
    q=dict(passed=True,kind='Pure proposed encoding plan; no combined ROM constructed',parent_SHA256=PIN,
        exact_decoded_spans=spans,owned_decoded_bytes=sum(row['bytes']for row in spans),actual_changed_decoded_bytes=len(changed),
        old_packed_stream_bytes=old_sizes,new_packed_stream_bytes=sizes,
        planned_decoded_SHA256=list(map(digest,parts)),planned_packed_SHA256=list(map(digest,packed)),
        head_bytes=len(header),existing_config_word_edits=edits,head_art31072_decoder_loader_instructions_and_page_tables_exact=True,
        all_other_decoded_bytes_and_all_current_graphics_extents_exact=True,
        planned_cookie=Packet.cookie(parts,payload).hex(),cookie_file_half_open=[Packet.COOKIE,Packet.COOKIE+16],
        carrier_CHR_pages=list(Packet.PAGES),carrier_capacity_bytes=capacity,planned_used_bytes=used,carrier_spare_bytes=capacity-used,
        future_physical_write_domain='Only existing45 carrier pages and existing16B cookie; no native instruction or other art writes',
        physical_unowned_BT160_score10_Gimmick192_and_older_fixes_preservation_required=True,
        primitive_free_control_receipt='4e6b85569ac554a93a76fe438ecfa2fd3d75533c3e3f88c0d53c38bb7fab0f75',
        paired_IRQ_receipt='bb7eac550efbcd1ac9308c30f1d19d388ceba26654d9b39f724219c0cd168716',
        narrow_genuine_loss_scope='Opposed-facing Sword2 loss requests1, sheaths to1, movement resumes and re-admission clears request',
        open_equal_facing_F090_exit=True,full_route4874_original_injury_negative_retained=True,
        candidate_ROM_SHA256=None,ROM_composition_authorized=False,ROM_constructed=False,Mesen=False,outputs=0)
    q['plan_receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Pure encoding plan attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=plan(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
