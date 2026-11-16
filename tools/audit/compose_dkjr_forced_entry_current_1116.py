"""Strict leased a3fb->7c0f entry-only composer and portable inverse; RAM only."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re

import compose_dkjr_footer_bt91dc_current_1116 as Parent
import measure_dkjr_forced_entry_fit_v2_1116 as Plan

R,Camera,BT=Parent.R,Parent.Camera,Parent.BT
PIN=Parent.CANDIDATE
CANDIDATE='7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
GRANT=R/'docs/qa/allocations/dkjr-forced-entry-source-root-1116.json'
GRANT_SHA='4f4e8339c180984857c649287df9071aaf126d5eaa175a36e8cb99563b10db62'
PLAN_SHA='67da40a7d69632b98d1a04070c247cd099e34eac7a43594f53ed5a06936a2745'
H=lambda value:sha256(value).hexdigest()


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA
    assert H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    grant=json.loads(GRANT.read_text())
    assert grant['owning_parent_SHA256']==PIN and grant['proposed_candidate_SHA256']==CANDIDATE
    assert grant['source_in_memory_composition_and_mounts_authorized']
    assert not any(grant[key]for key in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    assert grant['owned_code_bytes']==1070 and grant['owned_with_cookie_bytes']==1086
    return grant


def chunks(payload_offset,data):
    owner=Camera.Plan.Current.F.Prior.Early.Old
    cursor=0
    while cursor<len(data):
        page,within=divmod(payload_offset+cursor,1024)
        size=min(1024-within,len(data)-cursor)
        yield owner.CHR+owner.PAGES[page]*1024+within,data[cursor:cursor+size]
        cursor+=size


@lru_cache(maxsize=1)
def spans(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN
    grant=lease();ancestor=Parent.inverse(parent)
    assert H(ancestor)==Parent.PIN and Parent.proposal(ancestor)[0]==parent
    physical=Plan.physical(ancestor)
    assert physical['predicted_ROM_SHA256']==CANDIDATE
    rows=[]
    for extent,item in zip(grant['physical_spans'],physical['physical'],strict=True):
        lo,hi=item['file_half_open'];old,new=bytes.fromhex(item['old_hex']),bytes.fromhex(item['new_hex'])
        assert extent['file_half_open']==[lo,hi]and extent['bytes']==hi-lo==len(old)==len(new)
        assert H(old)==extent['old_SHA256']and H(new)==extent['new_SHA256']
        assert parent[lo:hi]==old
        rows.append((lo,old,new))
    return tuple(rows)


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and H(parent)==PIN
    grant=lease();out=bytearray(parent);owned=set()
    for at,old,new in spans(parent):
        domain=set(range(at,at+len(old)));assert not owned&domain
        owned|=domain;out[at:at+len(old)]=new
    result=bytes(out)
    changed={i for i,(a,b)in enumerate(zip(parent,result,strict=True))if a!=b}
    assert len(owned)==1086 and changed<=owned and H(result)==CANDIDATE
    body=Camera.payload(result)
    assert H(body)==grant['proposed_packet_SHA256']
    assert result[534485:534501]==bytes.fromhex(grant['proposed_cookie_hex'])
    assert result[534485:534501]==bytes.fromhex('a72801')+sha256(body).digest()[:13]
    protected=[]
    for name,at,size in(('current_BT8192',BT.CACHE,8192),('current_BT487_header_cookie',BT.HEADER,487)):
        assert not owned.intersection(range(at,at+size))and result[at:at+size]==parent[at:at+size]
        protected.append(dict(role=name,offset=at,bytes=size,SHA256=H(parent[at:at+size])))
    return result,dict(parent_a3fb_SHA256=PIN,public_ancestor91dc_SHA256=Parent.PIN,candidate_SHA256=CANDIDATE,
        grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,owned_bytes=len(owned),changed_bytes=len(changed),
        packet_SHA256=H(body),cookie=result[534485:534501].hex(),physical_spans=7,
        all_unowned_a3fb_bytes_exact=True,protected_BT=protected,original_fall_head_world_helpers_unchanged=True,
        source_only=True,CPU_executed=False,ROM_written=False,outputs=0)


@lru_cache(maxsize=1)
def old_logical_preimages():
    """Source-only recovery; does not read a cartridge or invoke a frozen ROM API."""
    source,known=Camera.Plan.source_inputs()
    T=Camera.Plan.Source.T
    assembled=T.assemble(''.join(f'{name}=${value:x}\n'for name,value in known.items())+
        Camera.Plan.Source.expand_branches(source),dict(DKJR=(0xa000,8160),DK_MAIN=(0xd65e,73),
            DK_PAUSE=(0xd540,286),DK_PORTS=(0xd6a7,345)))
    labels=assembled['symbols'];rows=[]
    for first,last in(('D_d955','D_da14'),('D_ea08','D_eb69'),('DkNativeAnchorReady','DkjrComponentEnd')):
        text=source[source.index(first+':'):source.index(last+':')]
        local=set(re.findall(r'^(\w+):',text,re.M))
        definitions=Camera.Plan.numeric(source)+''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in local)
        at,size=labels[first],labels[last]-labels[first]
        part=T.assemble(definitions+'.segment "OLD"\n'+Camera.Plan.Source.expand_branches(text),dict(OLD=(at,size)))
        assert part['used']['OLD']==size
        rows.append((at-0xa000,part['images']['OLD']))
    rows.append((0xbc8c-0xa000,bytes.fromhex('adfec8c902f0034c27bd')))
    return tuple(rows)


def inverse(raw):
    assert isinstance(raw,bytes)and H(raw)==CANDIDATE
    grant=lease();out=bytearray(raw);expected={tuple(row['file_half_open']):row for row in grant['physical_spans']}
    restored=set()
    for at,data in old_logical_preimages():
        for file,old in chunks(at,data):
            key=(file,file+len(old));row=expected[key]
            assert H(old)==row['old_SHA256']and H(raw[key[0]:key[1]])==row['new_SHA256']
            out[key[0]:key[1]]=old;restored.add(key)
    assert len(restored)==6
    old_body=Camera.payload(bytes(out))
    assert H(old_body)=='4f7d5086e85959d041d041de9ae22945edea4f3f942c61424b22f614ee33b1cb'
    old_cookie=bytes.fromhex('a72801')+sha256(old_body).digest()[:13]
    cookie_row=expected[(534485,534501)]
    assert H(old_cookie)==cookie_row['old_SHA256']and H(raw[534485:534501])==cookie_row['new_SHA256']
    out[534485:534501]=old_cookie;parent=bytes(out)
    assert H(parent)==PIN and H(Parent.inverse(parent))==Parent.PIN
    assert proposal(parent)[0]==raw
    return parent


def current_proposal(current):
    """Explicit exact91dc ancestor, preserving all unrelated current bytes."""
    assert isinstance(current,bytes)and H(current)==Parent.PIN
    parent,_=Parent.proposal(current)
    return proposal(parent)


if __name__=='__main__':
    current=BT.ROM.read_bytes();raw,report=current_proposal(current)
    assert inverse(raw)==Parent.proposal(current)[0]and Parent.inverse(inverse(raw))==current
    report=dict(report,portable_strict_inverse_roundtrip=True,composer_source_SHA256=H(Path(__file__).read_bytes()))
    text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FORCED_ENTRY_COMPOSITION '+text,flush=True)
    print('DKJR_FORCED_ENTRY_COMPOSITION_SHA256 '+H(text.encode()),flush=True)
