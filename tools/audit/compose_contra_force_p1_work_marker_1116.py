"""Leased strict6a3 CF work-marker composition and portable inverse, memory only."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import base64,json,zlib
import plan_contra_force_p1_work_marker_1116 as Plan

C=Plan.C
R,ROM,H=C.R,C.ROM,C.H
PIN=Plan.Audit.Current.CANDIDATE
CANDIDATE='ffbb98f80038a51747f36339c6420c5446a4b3da1a7b0d2b3114146a6674b53d'
GRANT=R/'docs/qa/allocations/contra-force-p1-work-marker-source-1116.json'
GRANT_SHA='8d7c98581a68451920e3f0088d0deef8ee3cd33af5ca0a1f5aebe4ab3800c2c3'
PLAN_SHA='e8747d78a3d307449d2c3458869df880f361b5e4efb868fd37f36347ee50ccd3'
CODE_SPANS=((2027356,668),(2030094,85),(2030179,172),(2030420,17),(2024616,68))
COOKIE_SITES=(573373,642966)
OLD_COOKIE=bytes.fromhex('a71f00053a7d2d9a77d5accd30e79766')
NEW_COOKIE=bytes.fromhex('a71f000544ac85adda900991a69dad5d')
OLD_B85='c-mD{O>7fK6rS1LcsC{>bD>LA+7(=45Qu{hE{6*BP%Wv|o_g!Sy{(nxz=0Eopoj!1)l}wI30Xu|Q+eG?a1<=DRW@0@&A}UxSRqb`{DAlgk%Be}#3q*NzFC7RMjFk$_r7`Wn{VE5H6I?~x70}GM@X86QZ}#WjfJJHE&Cx$4A~P*9m*Ta^Txlf@#{QaOJwuL!~*a4O`gH&5|dw60~+??Rxc3d5}UA$KRf5S-aPB~4RY5)r-eQX%{amFAFkXsa`QzQgZz{i^c9sieYKWeNU}DR`zFoVHW*j$zHI|<LvXCvV~c=QT?t>r=dr>%upK}Kk(^ts&-VKpUQz7a?^l9OD0Wr1e4p)t`|ShMeS$M_UoR{%ZD@*=W#hssze2LxU#n~n_%CGpgv#Cl-vhm%p{FRnMN3>K#ohz|lN3ny4Q2a~BlX{RU?W)*1vZX#D~|bbJvZYAU&d?}`hD-WIOf=Ye`Hf}?#x7rt%Xv|-O0=#H|I1rooQ~m#2*|SOn+5zf;wjK>rSJNeB2*>B;#5>lE72@U^mM0R07Fc6{|Weo70LpAzxQe5`APBS?BK6gVlJMT}$vo!%<>VAJK-ZQ{qVuU`}RDXy_yFfqekpgp^`;1fP+82vz<8f(S4EKWq<J>oeFph(w$pKzI`2B_hqqB`P)M<iqPwlB5Q2K}nW2apeB0HyRIiA)J_;K^{tWTN`F;32R)j#^v}4Eelm4gpv-yK`HG}VbD&eBV1j7`3v_(Psv%`AkjDOvqY2$Zr09MH1A?9X-ggnRhvYzb7lz%4<J(nr{#+C)8g4CL>gMXsnU&}mDE3c9eS^!?0G6Fnr5PTUa<!BZXa0#nmK9yVPY|7HO4oMYl}i+YakyBS0*lzf~a=fm87&DXpt7A!aiF<Rp{XZK!mt+_yoaiAx|JjTAD^jZ5k$dYxELLQ`Q<4txY~<ID{FFVsnRTloU&k-9kM@^ff9Or+b|Hc?mOasqA31d%WvdhiZxVC9=F3HrYjwedn>4z+M4+4Qvxw2kdifY#D#dm~T_|Xqi0+{9~el*T8sM$>#q9W5)n4'


@lru_cache(maxsize=1)
def lease():
    assert H(GRANT.read_bytes())==GRANT_SHA and H(Path(Plan.__file__).read_bytes())==PLAN_SHA
    q=json.loads(GRANT.read_text());assert q['owning_parent_SHA256']==PIN
    assert(q['owned_bytes'],q['changed_bytes'])==(1042,714)
    assert q['source_in_memory_composition_and_mounts_authorized']
    assert not any(q[k]for k in('physical_ROM_file_writes_authorized','native_Mesen_authorized','Downloads_delivery_authorized'))
    assert q['RAM3_code_file_spans']==[list(p)for p in CODE_SPANS]
    assert q['cookie_views']['files']==list(COOKIE_SITES)
    assert q['cookie_views']['old_hex']==OLD_COOKIE.hex()and q['cookie_views']['new_hex']==NEW_COOKIE.hex()
    return q


@lru_cache(maxsize=1)
def preimages():
    lease();data=zlib.decompress(base64.b85decode(OLD_B85));assert len(data)==1010
    assert H(data)=='014487f4e9b92c8bb3e17eeb6eb2c8c5a295fa6d5d5454970219cfb494143b45'
    rows=[];offset=0
    for at,count in CODE_SPANS:rows.append((at,data[offset:offset+count]));offset+=count
    return tuple(rows)+tuple((at,OLD_COOKIE)for at in COOKIE_SITES)


@lru_cache(maxsize=1)
def proposal(parent):
    q=lease();assert isinstance(parent,bytes)and H(parent)==PIN,'Exact owning6a3 parent required'
    d=Plan.descriptor(parent)
    assert d['owned_bytes']==1042 and d['changed_bytes']==714
    old=preimages();new=tuple((f['file'],bytes.fromhex(f['new_hex']))for f in d['fragments'])+tuple((at,NEW_COOKIE)for at in COOKIE_SITES)
    out=bytearray(parent);owned=set()
    for(at,before),(site,after)in zip(old,new,strict=True):
        assert at==site and len(before)==len(after)and parent[at:at+len(before)]==before
        addresses=set(range(at,at+len(before)));assert not owned&addresses;owned|=addresses;out[at:at+len(after)]=after
    out=bytes(out);changed={i for i,(x,y)in enumerate(zip(parent,out,strict=True))if x!=y}
    assert len(owned)==1042 and len(changed)==714 and changed<=owned
    for at,before,after in Plan.Audit.Current.spans():assert out[at:at+len(after)]==after
    payload=out[Plan.Audit.P.CHR+935*1024:Plan.Audit.P.CHR+959*1024]
    assert H(payload)==q['payload']['new_SHA256']==d['detached_new_payload_SHA256']
    if CANDIDATE is not None:assert H(out)==CANDIDATE
    return out,dict(parent_SHA256=PIN,candidate_SHA256=H(out),grant_SHA256=GRANT_SHA,plan_SHA256=PLAN_SHA,
        owned_bytes=1042,changed_bytes=714,payload_SHA256=H(payload),new_cookie=NEW_COOKIE.hex(),
        all_unowned_bytes_and_all_Bowser72_exact=True,existing_router291_packet124_all14services_fullchecks_exact=True,
        portable_preimages_bytes=1010,source_CPU_qualification_pending=True,
        native_physical_file_delivery_authorized=False,outputs=0)


def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and H(raw)==CANDIDATE,'Exact frozen work-marker candidate required'
    parent=bytearray(raw)
    for at,before in preimages():parent[at:at+len(before)]=before
    parent=bytes(parent);assert H(parent)==PIN
    assert proposal(parent)[0]==raw
    return parent


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)==PIN,'Only exact current6a3 can be loaded; candidate must be supplied explicitly'
    return raw


if __name__=='__main__':
    raw=load_current_image();reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=ROM.resolve(),'Portable composition/inverse attempted mutable Nightly reread'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('In-memory marker composer attempted files/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        new,q=proposal(raw)
        if CANDIDATE is not None:assert inverse(new)==raw
        rejected=0
        for data in(raw[:100]+bytes((raw[100]^1,))+raw[101:],raw[:2027356]+bytes((raw[2027356]^1,))+raw[2027357:],bytes(2097168)):
            try:proposal(data)
            except AssertionError:rejected+=1
            else:raise AssertionError('Unknown/dirty parent accepted')
        inverse_rejected=0
        for data in(raw,new[:100]+bytes((new[100]^1,))+new[101:],new[:2027356]+bytes((new[2027356]^1,))+new[2027357:]):
            try:inverse(data)
            except AssertionError:inverse_rejected+=1
            else:raise AssertionError('Unknown/dirty candidate accepted')
        q.update(unknown_dirty_parents_rejected=rejected,unknown_dirty_candidates_rejected=inverse_rejected,
            portable_inverse_and_roundtrip_exact=True,mutable_Downloads_read_forbidden_after_capture=True)
    q['source_receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
