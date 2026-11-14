"""Typed421 adapter and disjoint actualDK source composition, memory only."""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import current_smb2_hidden_input_1114 as T

DK_SOURCE='c5885ac48e48ae21f50fefd7be595fa456b6644ff145b012ef121b2562290f6b'
DK_WITH_FA66='a5942300cd677a9c62b1f3ff312552216766de8fcca8d93f8939143f3f650625'


def run(*,dk_component=False):
    # Root owns this already tested exact421 candidate. This checker never
    # writes it and does not race the current Downloads replacement.
    source=T.Response.R/'build/smb2-flag-native-1113/candidate.nes'
    raw=source.read_bytes();assert T.digest(raw)==T.HIDDEN
    nightly=T.Response.Cache.Parent.Owner.D.C.Owner.NIGHTLY.resolve()
    read=Path.read_bytes;nightly_reads=0
    def guarded(path):
        nonlocal nightly_reads
        if path.resolve()==nightly:
            nightly_reads+=1;raise AssertionError('Typed421 source adapter must not read mutable Downloads')
        return read(path)
    def forbid(*args,**kwargs):raise AssertionError('Source adapter check attempted a file write')
    rejects=[]
    def reject(name,fn):
        try:fn()
        except (AssertionError,KeyError,TypeError):rejects.append(name)
        else:raise AssertionError(('Unknown, dirty, overlapping or untyped input accepted',name))
    with patch.object(Path,'read_bytes',guarded),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),\
         patch.object(T.Response.Cache,'parent_image',side_effect=AssertionError('Mutable parent lookup forbidden')):
        T.Response.bindings.cache_clear();T.Response.Cache.bindings.cache_clear();T.Response.Cache.public_image.cache_clear()
        typed=T.normalize(raw,kind='hidden-421')
        assert typed.kind=='hidden-421'and T.digest(typed.fa66)==T.CHEAT and T.digest(typed.postbg)==T.POSTBG
        assert len(typed.inverse_steps)==3
        assert T.Response.proposal(typed.fa66)[0]==raw and T.Response.inverse(raw)==typed.fa66
        same,identity=typed.preserve(typed.postbg,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=())
        assert same==raw and identity['current_fix_changed_bytes_preserved']==176
        assert identity['hidden_response_changed_bytes_preserved']==110 and identity['fa66_changed_bytes_preserved']==66
        # Existing exactfa66 and explicitpostbg APIs stay independently strict.
        previous=T.Previous.normalize(typed.fa66,kind='cheat-fa66')
        assert previous.postbg==typed.postbg
        old=T.Previous.normalize(typed.postbg,kind='postbg12397')
        assert old.preserve(old.postbg,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=())[0]==old.postbg
        fixture=bytearray(typed.postbg);fixture[16]^=1;fixture=bytes(fixture)
        combined,unit=typed.preserve(fixture,legacy_result_SHA256=T.digest(fixture),allowed_component_offsets={16})
        assert unit['component_changed_bytes']==1 and combined[16]==fixture[16]
        assert combined[:16]+combined[17:]==raw[:16]+raw[17:]
        for name,parent,at in(('dirty_hidden',raw,971064),('dirty_unowned',raw,16),
                               ('dirty_cheat',raw,T.Previous.C.EDITS[0][0])):
            dirty=bytearray(parent);dirty[at]^=1
            reject(name,lambda dirty=bytes(dirty):T.normalize(dirty,kind='hidden-421'))
        reject('fa66_mislabeled421',lambda:T.normalize(typed.fa66,kind='hidden-421'))
        reject('postbg_mislabeled421',lambda:T.normalize(typed.postbg,kind='hidden-421'))
        reject('unknown_kind',lambda:T.normalize(raw,kind='auto'))
        reject('missing_explicit_kind',lambda:T.normalize(raw))
        reject('old_fa66_api_rejects421',lambda:T.Previous.normalize(raw,kind='cheat-fa66'))
        reject('wrong_legacy_hash',lambda:typed.preserve(fixture,legacy_result_SHA256=T.POSTBG,allowed_component_offsets={16}))
        reject('component_change_unowned',lambda:typed.preserve(fixture,legacy_result_SHA256=T.digest(fixture),allowed_component_offsets=()))
        reject('wrong_legacy_size',lambda:typed.preserve(fixture[:-1],legacy_result_SHA256=T.digest(fixture[:-1]),allowed_component_offsets=()))
        reject('forged_inverse_provenance',lambda:replace(typed,inverse_steps=()).preserve(typed.postbg,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=()))
        reject('forged_legacy_view',lambda:replace(typed,previous=replace(typed.previous,postbg=raw)).preserve(typed.postbg,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=()))
        for index in(-1,len(raw),'16',True):
            reject('invalid_offset_'+str(index),lambda index=index:typed.preserve(typed.postbg,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=(index,)))
        hidden={i for at,size in T.hidden_envelopes()for i in range(at,at+size)}
        cheat={i for at,size in T.Previous.protected_envelopes()for i in range(at,at+size)}
        assert len(hidden)==201 and len(cheat)==252 and not hidden&cheat
        for at in sorted(hidden|cheat):
            reject('complete_envelope_overlap_'+str(at),lambda at=at:typed.preserve(typed.postbg,
                legacy_result_SHA256=T.POSTBG,allowed_component_offsets=(at,)))
        for at,size in T.protected_envelopes():
            dirty=bytearray(typed.postbg);dirty[at]^=1;dirty=bytes(dirty)
            reject('dirty_legacy_protected_'+str(at),lambda dirty=dirty:typed.preserve(dirty,
                legacy_result_SHA256=T.digest(dirty),allowed_component_offsets={16}))
        print(json.dumps(dict(progress='typed421 identity/strictness complete',rejections=len(rejects),
            hidden_envelope_bytes=len(hidden),cheat_envelope_bytes=len(cheat))),flush=True)
        actual_dk=None
        if dk_component:
            import compose_dkjr_direct_postbg_current_1113 as DK
            assert sha256(Path(DK.__file__).read_bytes()).hexdigest()==DK_SOURCE
            legacy,dk_info=DK.proposal(typed.postbg)
            assert T.digest(legacy)==DK.PIN and DK.inverse(legacy)==typed.postbg
            allowed={i for at,size in DK.Old.dk_envelopes()for i in range(at,at+size)}
            assert len(allowed)==11433 and not allowed&(hidden|cheat)
            previous_dk,previous_info=previous.preserve(legacy,legacy_result_SHA256=DK.PIN,allowed_component_offsets=allowed)
            assert T.digest(previous_dk)==DK_WITH_FA66 and previous_info['component_changed_bytes']==846
            image,actual_dk=typed.preserve(legacy,legacy_result_SHA256=DK.PIN,allowed_component_offsets=allowed)
            changed={i for i,(a,b)in enumerate(zip(typed.postbg,legacy,strict=True))if a!=b}
            assert len(changed)==846 and changed<=allowed
            independent=bytearray(raw)
            for i in changed:independent[i]=legacy[i]
            assert bytes(independent)==image
            independent=bytearray(previous_dk)
            for at,size in T.hidden_envelopes():independent[at:at+size]=raw[at:at+size]
            assert bytes(independent)==image
            stripped=bytearray(image)
            for i in changed:stripped[i]=raw[i]
            assert bytes(stripped)==raw
            current={i for i,(a,b)in enumerate(zip(typed.postbg,raw,strict=True))if a!=b}
            stripped=bytearray(image)
            for i in current:stripped[i]=typed.postbg[i]
            assert len(current)==176 and bytes(stripped)==legacy
            assert all(image[at:at+size]==raw[at:at+size]for at,size in T.protected_envelopes())
            actual_dk.update(legacy_DK_SHA256=DK.PIN,prior_fa66_DK_SHA256=DK_WITH_FA66,
                complete_DK_envelope_bytes=len(allowed),DK_changed_bytes=len(changed),
                exact_component_and_current_inverses=True,independent_composition_orders_equal=True,
                source_only=True,native_qualified=False,installed=False)
        assert nightly_reads==0
    assert source.read_bytes()==raw
    return dict(passed=True,adapter_source_SHA256=T.digest(Path(T.__file__).read_bytes()),
        typed_current_SHA256=T.HIDDEN,normalized_fa66_SHA256=T.CHEAT,normalized_postbg_SHA256=T.POSTBG,
        inverse_steps=list(typed.inverse_steps),identity_roundtrip=True,
        complete_hidden_envelope_bytes=201,complete_cheat_envelope_bytes=252,
        hidden_changed_bytes_retained=110,fa66_changed_bytes_retained=66,current_changed_bytes_retained=176,
        complete_protected_byte_overlap_rejections=453,strict_rejections=len(rejects),
        rejected_case_digest=T.digest(json.dumps(rejects,separators=(',',':')).encode()),
        actual_frozen_DK_merge=actual_dk,synthetic_ownership_unit=unit,
        live_Downloads_reads=nightly_reads,retained421_candidate_unchanged=True,
        outputs=0,Mesen_run=False,installed=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dk-component',action='store_true');args=p.parse_args()
    print(json.dumps(run(dk_component=args.dk_component),separators=(',',':')),flush=True)
