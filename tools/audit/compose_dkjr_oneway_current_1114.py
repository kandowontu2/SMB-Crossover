"""Explicit421-preserving source merge of granted DK one-way code; no files."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_oneway_support_1114 as S
import compose_dkjr_direct_postbg_current_1113 as Old
import current_smb2_hidden_input_1114 as Current
from check_ff_stdout_controller_source_1110 import LuaRuntime

PARENT=Current.HIDDEN
LEGACY_PIN='e6c7c82744276690d0e5e6765f9165f8e9d636307fa1cc25556f51c03258fc57'
OLD_CURRENT_PIN='df130d5dba8d21e74f5bc2899aad4d77b681381c8f8dfa34b72b392131eedada'
PIN='e98df463b9376105af9fa699e7e34b1d93fe95b4550e35a1558afdaa9f17cd47'


def ownership():
    own=frozenset(i for at,size in Old.Old.dk_envelopes()for i in range(at,at+size))
    protected=frozenset(i for at,size in Current.protected_envelopes()for i in range(at,at+size))
    assert not own&protected
    return own


@lru_cache(maxsize=1)
def proposal(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PARENT
    typed=Current.normalize(raw,kind='hidden-421');own=ownership()
    legacy_old,prior=Old.proposal(typed.postbg)
    private_old=Old.private_image(legacy_old)
    assert sha256(private_old).hexdigest()==S.PARENT
    private_new,private_info=S.proposal(private_old)
    legacy_new,spans,changes=S.replace_owned(legacy_old)
    for at,size in Old.Old.dk_envelopes():assert legacy_new[at:at+size]==private_new[at:at+size]
    legacy_pin=sha256(legacy_new).hexdigest()
    if LEGACY_PIN is not None:assert legacy_pin==LEGACY_PIN
    previous,previous_info=typed.preserve(legacy_old,legacy_result_SHA256=Old.PIN,allowed_component_offsets=own)
    old_current_pin=sha256(previous).hexdigest()
    if OLD_CURRENT_PIN is not None:assert old_current_pin==OLD_CURRENT_PIN
    image,info=typed.preserve(legacy_new,legacy_result_SHA256=legacy_pin,allowed_component_offsets=own)
    digest=sha256(image).hexdigest()
    if PIN is not None:assert digest==PIN
    assert S.replace_owned(previous)[0]==image
    assert all(image[at:at+size]==raw[at:at+size]for at,size in Current.protected_envelopes())
    return image,dict(info,parent_SHA256=PARENT,candidate_SHA256=digest,
        canonical_private_SHA256=S.PIN,legacy_postbg_merge_SHA256=legacy_pin,
        previous_current_DK_merge_SHA256=old_current_pin,previous_DK_merge=prior,
        one_way=private_info,old_and_new_composition_orders_equal=True,
        complete_current_hidden_and_cheat_envelopes_exact=True,
        logical_grant_SHA256=S.GRANT_SHA,outputs_written=0,installed=False,native_qualified=False)


@lru_cache(maxsize=1)
def inverse(raw):
    """Recover pure421 entirely from owning source, not a mutable nightly.

    Frozen typed wrappers accept only pure421. This separately pinned merge
    first removes its own component, then reconstructs source preimages in
    the protected foreign envelopes and rebuilds the strict typed parent.
    """
    assert PIN is not None and isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    previous,_,_=S.replace_owned(raw,reverse=True)
    assert sha256(previous).hexdigest()==OLD_CURRENT_PIN
    Current.dependencies();Response=Current.Response;Cheat=Current.Previous.C
    resource=Response.Cache.GRANT.read_bytes()
    assert sha256(resource).hexdigest()==Response.Cache.GRANT_SHA
    g=json.loads(resource)
    _,owned,_=Response.Cache.Measure.Route.Current.Flag.source_recipe(previous)
    probe=owned['probe']
    assert len(probe)==174 and sha256(probe).hexdigest()==g['spans'][0]['preimage_SHA256']
    out=bytearray(previous)
    for index,row in enumerate(g['spans']):
        at,end=row['file_half_open'];before=probe if index==0 else bytes.fromhex(row['preimage_hex'])
        assert len(before)==end-at==row['bytes'];out[at:end]=before
    for at,before,after in Cheat.EDITS:
        assert out[at]==after;out[at]=before
    for at,before,after in Cheat.Owner.SPANS:
        assert out[at:at+len(after)]==after;out[at:at+len(before)]=before
    legacy=bytes(out);assert sha256(legacy).hexdigest()==Old.PIN
    postbg=Old.inverse(legacy);assert sha256(postbg).hexdigest()==Current.POSTBG
    e8,_=Cheat.Owner.proposal(postbg);fa66,_=Cheat.proposal(e8);parent,_=Response.proposal(fa66)
    assert sha256(parent).hexdigest()==PARENT
    typed=Current.normalize(parent,kind='hidden-421')
    own=ownership()
    rebuilt,_=typed.preserve(legacy,legacy_result_SHA256=Old.PIN,allowed_component_offsets=own)
    assert rebuilt==previous
    assert all(raw[at:at+size]==parent[at:at+size]for at,size in Current.protected_envelopes())
    assert proposal(parent)[0]==raw
    return parent


@lru_cache(maxsize=1)
def private_image(raw):
    pure=inverse(raw);typed=Current.normalize(pure,kind='hidden-421')
    legacy,_=Old.proposal(typed.postbg);parent=Old.private_image(legacy)
    assert sha256(parent).hexdigest()==S.PARENT
    result,_=S.proposal(parent);assert sha256(result).hexdigest()==S.PIN
    for at,size in Old.Old.dk_envelopes():assert raw[at:at+size]==result[at:at+size]
    return result


def controller(raw,*,diagnostic=False):
    private=private_image(raw);text=S.controller(private,diagnostic=diagnostic)
    assert text.count(S.PIN)==1
    text=text.replace(S.PIN,PIN,1);LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    image,info=proposal(current)
    if PIN is not None:
        assert inverse(image)==current
        info['strict_source_inverse_roundtrip']=True
        info['controller_Lua_SHA256']=sha256(controller(image).encode()).hexdigest()
    print('DKJR_ONEWAY_CURRENT '+json.dumps(info,separators=(',',':')),flush=True)
