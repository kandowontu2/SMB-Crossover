"""Strict current590 three-span Prince composition; memory only."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,struct,zlib
import plan_prince_transition_590_1115 as Plan

R,Packet=Plan.R,Plan.Packet
PIN=Plan.PIN
CANDIDATE='16a385654e80105f83470e14cd328d8bbceaa659730f4a81a2f36ca039cfbcfb'
ORIGINAL_ZLIB_HEX='''78da2d514b4c1351146d3b2d20d13a900ab32876141676832cbbc3b576a31b131393ba310ec29615a2063f40fa4a81026df906a8c9243c5233990589a927111f96a4664c4cc0cda4db2e6866c712ef2bcc62927bee39f79efbceded7c38ecc3ad21bc8eb4f7e9a3e96066360199801b6053e81da148652ce28d74455f182d5a0f3827f466d01d9b0f3947f426d1ed9a017283f32fd242240336ec63d360762193e966d51079d4e3ed7a20e7877690711e721390b204672bc42a5660c332228cd0598176c052c0fbe8b444363af2d5e42c3c7462dbdb84b843468185b04cf82e5c073ad15114f493ef8ce175b5bdabd50f6aa94ea1ca456b5b2cf0820734b52c496c197e1f4f32554ef64a389869fa8a6ef8a799de04443256ad2ad10af9647b6d389105a5b415976c922e1e4b2c970b92aee69864abeca4a72a7d2cc81febfb7e045b861c986615163b2d21cb1e8cf33f0429cc1e9e669784133e2f4ca2a68fabc30a7e357c1f3606ba057dd045f057b0bbe06f64e26c2de637f1d7b1bb8c73791d22f0ef5ee1f66df7e8fa82b5e473de805eb6127600eb029f02e91389b423960fa1eb63e894d4062ac806d1f2f40f51f678ad86e0b173058c4b173ce3f401b2bc874280eb60bfe1163451913a3b04a72a43636d332382b035e93ee5a8255e950522f21432184d2a2ea0d551addcf27a562c44af12f882bd5004536edea7f2cf3153b7529f413773b64ab55bf73dfeeadb697e3762cae3bfdfacbbf55c589da256af4e833ae7eb0530ef35ed44edd721b093327eeb1fa6bffc41d1a99bdf6ae16155e7cebc6c13fb71015d3ea39412c2a328f91518f6845f71145dc75c45c412feb081a675734e3168b09bb645c305d24784c9cd17d31c17571360b824cdfb7e110fcf4a617ac5feaea224553ea8206a7ec71cde8607dc27e4ea7dd16a9ff2e71caaa'''
ORIGINAL_SHA='a731ed311b6d2c90cfd88de19f623f39219dc2d8294e4f85d0e0a7dfa8c17442'
GRANT=R/'docs/qa/allocations/prince-body-transition-compose-1115.json'
GRANT_SHA='5cf227ac25e6a0cbf78901dad685a6c271133087a76a6c32c86665459b5d4b43'


def digest(data):return sha256(data).hexdigest()


@lru_cache(maxsize=1)
def allocation():
    data=GRANT.read_bytes();assert digest(data)==GRANT_SHA;q=json.loads(data)
    assert q['eligible_input_SHA256']==PIN and q['in_memory_ROM_composition_authorized']
    assert digest((R/q['plan_source']).read_bytes())==q['plan_source_SHA256']
    for path,pin in Plan.SOURCE_GATES.items():assert digest((R/path).read_bytes())==pin,path
    Plan.Body.allocation()
    return q


def replacement_arrays(parent):
    current=Plan.Current.normalize(parent,kind='prince-graphics-590')
    typed=Plan.Body.normalize_parent(current.reference1daca,kind='dk-window7-1daca')
    fitted=Plan.Body.Funding.plan(typed.reference421)
    transition=Plan.Transition.importer_plan(current.referenceAE)
    return(fitted['world']+b'\xea'*3,fitted['prepare']+fitted['helper'],transition['new'])


@lru_cache(maxsize=1)
def proposal(parent):
    assert isinstance(parent,bytes)and digest(parent)==PIN,'Expected exact installed590 parent'
    grant=allocation();head,before,old_sizes=Packet.extract(parent);new=replacement_arrays(parent)
    originals=[]
    def change(*parts):
        for row,replacement in zip(grant['decoded_spans'],new,strict=True):
            stream=row['stream'];lo,hi=row['decoded_half_open'];old=bytes(parts[stream][lo:hi])
            assert len(replacement)==hi-lo==row['bytes']
            assert digest(old)==row['preimage_SHA256']and digest(replacement)==row['proposed_SHA256']
            originals.append(old);parts[stream][lo:hi]=replacement
        return parts
    raw,codec=Packet.rebuild(parent,change);after=Packet.extract(raw)
    assert after[2]==tuple(grant['new_packed_stream_bytes'])and codec['spare']==grant['carrier_spare_bytes']
    assert raw[Packet.COOKIE:Packet.COOKIE+16].hex()==grant['planned_cookie']
    assert after[2][0]<=6528 and 0xe100-after[2][1]>=0xc900 and after[2][2]<=1280
    changed_decoded=0
    for stream,(a,b)in enumerate(zip(before,after[1],strict=True)):
        owned={at for row in grant['decoded_spans']if row['stream']==stream for at in range(*row['decoded_half_open'])}
        assert len(a)==len(b)and all(x==y for at,(x,y)in enumerate(zip(a,b,strict=True))if at not in owned)
        changed_decoded+=sum(x!=y for x,y in zip(a,b,strict=True))
    assert changed_decoded==698
    for row in Plan.Current.Graphics.allocation()['decoded_envelopes']:
        stream=row['stream'];lo=row['offset'];hi=lo+row['bytes'];assert before[stream][lo:hi]==after[1][stream][lo:hi]
    config=len(head)-54;words=struct.unpack_from('<12H',head,config);newwords=struct.unpack_from('<12H',after[0],config)
    edits=[dict(index=i,old=a,new=b)for i,(a,b)in enumerate(zip(words,newwords,strict=True))if a!=b]
    assert edits==grant['header_word_edits']
    allowed_head={config+2*row['index']+byte for row in edits for byte in(0,1)}
    assert len(head)==len(after[0])==grant['head_bytes']
    assert all(a==b for at,(a,b)in enumerate(zip(head,after[0],strict=True))if at not in allowed_head)
    assert head[:31072]==after[0][:31072]and head[-30:]==after[0][-30:]
    allowed={*range(Packet.COOKIE,Packet.COOKIE+16),*(at for page in Packet.PAGES for at in range(Packet.CHR+page*1024,Packet.CHR+(page+1)*1024))}
    changed={at for at,(a,b)in enumerate(zip(parent,raw,strict=True))if a!=b};assert changed<=allowed
    if CANDIDATE is not None:assert digest(raw)==CANDIDATE
    if ORIGINAL_ZLIB_HEX is not None:assert b''.join(originals)==zlib.decompress(bytes.fromhex(ORIGINAL_ZLIB_HEX))
    return raw,dict(parent_SHA256=PIN,candidate_SHA256=digest(raw),grant_SHA256=GRANT_SHA,
        exact_decoded_spans=grant['decoded_spans'],changed_decoded_bytes=changed_decoded,changed_physical_bytes=len(changed),
        old_packed_stream_bytes=old_sizes,new_packed_stream_bytes=after[2],cookie=codec['cookie'],carrier_spare_bytes=codec['spare'],
        exact_four_config_word_edits=edits,all_other_decoded_and_physical_bytes_exact=True,
        qualified590_graphics_exact=True,immutable_head_art_decoder_loader_and_page_tables_exact=True,
        BT160_score10_Gimmick192_DK_and_all_older_fixes_preserved=True,
        compact_original_preimage_bytes=sum(map(len,originals)),
        compact_original_preimages_zlib_hex=zlib.compress(b''.join(originals),9).hex()if ORIGINAL_ZLIB_HEX is None else None,
        original_preimage_SHA256=digest(b''.join(originals)),portable_inverse_no_mutable_Downloads=True,
        equal_facing_F090_exit_open=True,full_route4874_negative_retained=True,
        source_qualification_complete=False,native_qualified=False,installed=False,outputs=0,Mesen=False)


@lru_cache(maxsize=1)
def inverse(raw):
    assert CANDIDATE is not None and isinstance(raw,bytes)and digest(raw)==CANDIDATE,'Expected exact new Prince candidate'
    grant=allocation();assert ORIGINAL_ZLIB_HEX is not None
    old=zlib.decompress(bytes.fromhex(ORIGINAL_ZLIB_HEX));assert len(old)==848 and digest(old)==ORIGINAL_SHA
    def restore(*parts):
        cursor=0
        for row in grant['decoded_spans']:
            stream=row['stream'];lo,hi=row['decoded_half_open'];size=hi-lo
            assert digest(parts[stream][lo:hi])==row['proposed_SHA256']
            prior=old[cursor:cursor+size];assert digest(prior)==row['preimage_SHA256']
            parts[stream][lo:hi]=prior;cursor+=size
        assert cursor==len(old);return parts
    parent,_=Packet.rebuild(raw,restore);assert digest(parent)==PIN
    return parent


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Memory-only composition attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,info=proposal(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(info,separators=(',',':')),flush=True)
