"""Zero-output typed normalization and current-fix composition checks."""
from dataclasses import replace
from hashlib import sha256
import argparse
import json
from pathlib import Path

import current_smb2_cheat_input_1114 as T


def run(*,input_kind='postbg12397',dk_component=False):
    public=T.normalize(T.C.Owner.D.C.Owner.NIGHTLY.read_bytes(),kind=input_kind).postbg
    assert sha256(public).hexdigest()==T.POSTBG
    raw=T.C.proposal(T.C.Owner.proposal(public)[0])[0]
    q=T.normalize(raw,kind='cheat-fa66')
    assert q.postbg==public and len(q.inverse_steps)==2
    same,info=q.preserve(public,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=())
    assert same==raw and info['current_fix_changed_bytes_preserved']==66
    old=T.normalize(public,kind='postbg12397')
    assert old.preserve(public,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=())[0]==public
    # Ownership unit only: one explicit disposable in-memory difference.
    # This fixture is never a gameplay proposal and is never written out.
    legacy=bytearray(public);legacy[16]^=1;legacy=bytes(legacy)
    legacy_sha=T.digest(legacy);allowed={16}
    combined,merged=q.preserve(legacy,legacy_result_SHA256=legacy_sha,allowed_component_offsets=allowed)
    assert merged['component_changed_bytes']==1
    assert all(combined[i]==raw[i]for i in range(len(raw))if legacy[i]==public[i])
    rejects=[]
    def reject(name,fn):
        try:fn()
        except (AssertionError,KeyError,TypeError):rejects.append(name)
        else:raise AssertionError(('Invalid current input accepted',name))
    corrupt=bytearray(raw);corrupt[16]^=1
    reject('changed_fa66_input',lambda:T.normalize(bytes(corrupt),kind='cheat-fa66'))
    reject('postbg_mislabeled_fa66',lambda:T.normalize(public,kind='cheat-fa66'))
    reject('fa66_mislabeled_postbg',lambda:T.normalize(raw,kind='postbg12397'))
    reject('unknown_kind',lambda:T.normalize(raw,kind='auto'))
    reject('missing_kind',lambda:T.normalize(raw))
    reject('forged_provenance',lambda:replace(q,postbg=raw).preserve(public,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=()))
    reject('wrong_legacy_result_hash',lambda:q.preserve(legacy,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=allowed))
    reject('component_change_unowned',lambda:q.preserve(legacy,legacy_result_SHA256=legacy_sha,allowed_component_offsets=()))
    for name,at in(('owner',T.C.Owner.SPANS[0][0]),('owner_tail',T.C.Owner.SPANS[1][0]),
                   ('gate119',16+119*8192+0x2b),('gate120',16+120*8192+0x2b),
                   ('gate125',16+125*8192+0x2b),('gate127',16+127*8192+0x2b)):
        reject(name+'_envelope_overlap',lambda at=at:q.preserve(public,legacy_result_SHA256=T.POSTBG,allowed_component_offsets=(at,)))
        bad=bytearray(public);bad[at]^=1;bad=bytes(bad)
        reject(name+'_dirty_legacy',lambda bad=bad:q.preserve(bad,legacy_result_SHA256=T.digest(bad),allowed_component_offsets=()))
    actual_dk=None
    if dk_component:
        # Optional actual frozen DK16c composition. No native qualification.
        import compose_dkjr_direct_postbg_current_1113 as DK
        assert sha256(Path(DK.__file__).read_bytes()).hexdigest()=='c5885ac48e48ae21f50fefd7be595fa456b6644ff145b012ef121b2562290f6b'
        legacy,_=DK.proposal(public)
        allowed={i for at,size in DK.Old.dk_envelopes()for i in range(at,at+size)}
        combined,actual_dk=q.preserve(legacy,legacy_result_SHA256=DK.PIN,allowed_component_offsets=allowed)
        assert actual_dk['component_changed_bytes']==846
    return dict(passed=True,typed_current_SHA256=T.CHEAT,normalized_postbg_SHA256=T.POSTBG,
        inverse_steps=list(q.inverse_steps),identity_roundtrip=True,
        current_fa66_changes_preserved=66,synthetic_ownership_unit=merged,
        actual_frozen_DK_merge=actual_dk,actual_frozen_DK_candidate_not_native_qualified=True,strict_rejections=rejects,
        outputs=0,native_run=False,installed=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-kind',choices=('postbg12397','cheat-fa66'),default='postbg12397')
    p.add_argument('--dk-component',action='store_true')
    args=p.parse_args()
    print(json.dumps(run(input_kind=args.input_kind,dk_component=args.dk_component),separators=(',',':')),flush=True)
