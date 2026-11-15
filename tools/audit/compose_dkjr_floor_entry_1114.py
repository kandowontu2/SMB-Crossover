"""Root-granted exact DK Jr floor/entry successor, in memory only."""
from functools import lru_cache
from hashlib import sha256
import json
import re
from unittest.mock import patch

import measure_dkjr_floor_entry_fit_1114 as Measure

S,F,G=Measure.Indirect.S,Measure.Indirect.F,Measure.Indirect.G
P,H=G.P,G.H
PARENT=S.PIN
PIN='60d4bc5c4a0242f45354696d7f56f6df7bd2c44164f45833100b572d58b6eb47'
GRANT=P.B.R/'docs/qa/allocations/dkjr-floor-entry-fit-1114.json'
GRANT_SHA='3ba6f0b10fe1e91265991a9240ee78fd41cef6a04a1c4b596bc6ebd9ddaeaaa7'


def digest(raw):return sha256(raw).hexdigest()


@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA
    q=json.loads(data);assert q['status']=='granted-private-source-proposal-only'
    assert q['frozen_private_parent_SHA256']==PARENT
    assert q['logical_envelope_bytes']==1073 and q['endpoint_bytes']==307
    for name,expected in q['frozen_sources'].items():assert digest((P.B.R/name).read_bytes())==expected
    return q


@lru_cache(maxsize=1)
def original_source():
    """Recover source labels/preimages without any mutable cartridge input."""
    source,*_=H.T.old_source();labels=P.frozen_labels();known=dict(labels)
    aliases=re.findall(r'^(\w+)\s*=\s*(\w+)\s*$',source,re.M)
    for name in set(re.findall(r'\bDData_c[0-9a-f]{3}\b',source)):
        known[name]=labels['DkjrSourceData']+int(name[6:],16)-0xc2cd
    for _ in range(len(aliases)):
        for alias,target in aliases:
            if alias in known and target not in known:known[target]=known[alias]
    pre=''.join(f'{name}=${value:x}\n'for name,value in known.items())
    complete=H.T.assemble(pre+P.expand_branches(source),dict(DKJR=(0xa000,8160),
        DK_MAIN=(0xd65e,73),DK_PAUSE=(0xd540,286),DK_PORTS=(0xd6a7,345)))
    assert all(complete['symbols'][name]==value for name,value in labels.items())
    return source,complete['symbols']


@lru_cache(maxsize=1)
def preimages():
    q=allocation();source,labels=original_source();rows={}
    for role,begin,end in (('fruit','D_d955','D_da14'),('draw','D_ea08','D_eb69'),
        ('anchor','DkNativeAnchorReady','DkjrComponentEnd')):
        fragment=source[source.index(begin+':'):source.index(end+':')]
        defined=set(re.findall(r'^(\w+):',fragment,re.M))
        defs=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
        lo=labels[begin];size=next(r['bytes']for r in q['logical_fragments']if r['role']==role)
        code=H.T.assemble(defs+'.segment "OLD"\n'+P.expand_branches(fragment),dict(OLD=(lo,size)))
        assert code['used']['OLD']==size;rows[role]=code['images']['OLD']
    prior=S.grant();guard=next(r for r in prior['logical_fragments']if r['payload_offset']==0xbc74-0xa000)
    rows['body_guard']=bytes.fromhex(guard['proposed_hex'])[0xbc8c-0xbc74:0xbc96-0xbc74]
    services=source[source.index('DkServices:'):source.index('D_ca82:')]
    jumps=re.findall(r'^ jmp (\w+)$',services,re.M);assert len(jumps)==38 and jumps[34]=='DkNativeHandled'
    rows['service34']=H.T.assemble(f'DkNativeHandled=${labels["DkNativeHandled"]:x}\n.segment "OLD"\n jmp DkNativeHandled\n',
        dict(OLD=(0xa066,3)))['images']['OLD']
    for row in q['logical_fragments']:
        assert len(rows[row['role']])==row['bytes'] and digest(rows[row['role']])==row['preimage_SHA256']
    return rows


def chunks(payload_offset,data):
    """Logical bytes cross discontiguous1KB CHR carrier boundaries."""
    position=0
    while position<len(data):
        page,within=divmod(payload_offset+position,1024)
        size=min(1024-within,len(data)-position)
        yield P.B.CHR+P.B.PAGES[page]*1024+within,data[position:position+size]
        position+=size


@lru_cache(maxsize=1)
def source_spec(parent):
    assert isinstance(parent,bytes)and digest(parent)==PARENT
    legacy=S.inverse(parent);assert digest(legacy)==S.PARENT
    older=F.T.reverse(legacy)
    # A scoped, explicitly typed source resolver supplies the frozen generator
    # its exact769 preimage. No frozen file/API is broadened or read from a
    # mutable emulator slot. This process owns its isolated Python module graph.
    with patch.object(F,'load_inputs',lambda:(older,legacy)):
        measured,model=Measure.measure(include_model=True)
    q=allocation();before=preimages()
    assert measured['private_parent_SHA256']==PARENT
    for actual,expected in zip(measured['fragments'],q['logical_fragments'],strict=True):
        assert actual['role']==expected['role'] and actual['payload_offset']==expected['payload_offset']
        assert all(actual[key]==expected[key]for key in ('bytes','preimage_SHA256','proposed_SHA256'))
        assert bytes.fromhex(actual['preimage_hex'])==before[actual['role']]
    symbols=dict(model['proposed']['symbols'],CurrentRectReadCell=model['original']['reader_cell'],
        CurrentRectReadTranslate=model['original']['reader_translate'])
    return measured,symbols


def replace_component(raw,*,reverse=False,spec=None):
    q=allocation();body=bytearray(P.T.payload(raw));previous=bytes(body);oldsource=preimages()
    cookie=P.B.COOKIE[:3]+sha256(previous).digest()[:13]
    assert raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16]==cookie
    physical=[]
    for row in q['logical_fragments']:
        at,size=row['payload_offset'],row['bytes'];old=oldsource[row['role']]
        if reverse:
            before=bytes(body[at:at+size]);assert digest(before)==row['proposed_SHA256'];after=old
        else:
            assert spec is not None
            source=next(r for r in spec['fragments']if r['role']==row['role'])
            before=old;after=bytes.fromhex(source['proposed_hex'])
        assert body[at:at+size]==before
        body[at:at+size]=after
        for (file,oldchunk),(file2,newchunk)in zip(chunks(at,before),chunks(at,after),strict=True):
            assert file==file2;physical.append((file,oldchunk,newchunk))
    newcookie=P.B.COOKIE[:3]+sha256(body).digest()[:13]
    physical.append((P.B.COOKIE_AT,cookie,newcookie));out=bytearray(raw);owned=set()
    for at,before,after in physical:
        assert out[at:at+len(before)]==before
        out[at:at+len(after)]=after;owned.update(range(at,at+len(after)))
    out=bytes(out);assert P.T.payload(out)==bytes(body)
    changed={i for i,(a,b)in enumerate(zip(raw,out,strict=True))if a!=b}
    assert changed<=owned and len(physical)==8
    return out,physical,changed


@lru_cache(maxsize=1)
def proposal(raw):
    assert isinstance(raw,bytes)and digest(raw)==PARENT
    spec,_=source_spec(raw);out,spans,changed=replace_component(raw,spec=spec)
    if PIN is not None:assert digest(out)==PIN
    return out,dict(parent_SHA256=PARENT,candidate_SHA256=digest(out),allocation_SHA256=GRANT_SHA,
        logical_fragments=5,logical_bytes=1073,serialized_spans=[dict(file=at,bytes=len(old),
            preimage_SHA256=digest(old),proposed_SHA256=digest(new))for at,old,new in spans],
        changed_bytes=len(changed),new_CHR_RAM_PRG_bytes=0,cold_copier_changed=False,
        all_other_bytes_exact=True,outputs_written=0,installed=False,native_qualified=False)


@lru_cache(maxsize=1)
def inverse(raw):
    assert PIN is not None and isinstance(raw,bytes)and digest(raw)==PIN
    parent,_,_=replace_component(raw,reverse=True);assert digest(parent)==PARENT
    assert proposal(parent)[0]==raw
    return parent


if __name__=='__main__':
    _,legacy=F.load_inputs();parent,_=S.proposal(legacy);out,info=proposal(parent)
    if PIN is not None:assert inverse(out)==parent
    print('DKJR_FLOOR_ENTRY_PRIVATE '+json.dumps(info,separators=(',',':')),flush=True)
