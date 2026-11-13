"""All101 actual menu rows and rendered bytes, exact7ef versus privatee73."""
from hashlib import sha256
import json

import check_menu_facing_1112 as Menu
import compose_dkjr_helper_retire_1113 as P

AUDITOR_SHA='4e886d4259f4ba308c91d9779e052c3756a878bdfdc074551ed82494a576c671'
ROWS_SHA='f58ec905102307ca87d9c302248fa7da9c44cd5550df154323e67024da245db7'


def main():
    assert sha256((P.B.R/'tools/audit/check_menu_facing_1112.py').read_bytes()).hexdigest()==AUDITOR_SHA
    parent=P.B.C.ROM.read_bytes()
    assert sha256(parent).hexdigest()==P.PRINCE_CURRENT
    from compose_dkjr_platform_contact_1113 import load_parent
    candidate=load_parent()
    assert sha256(candidate).hexdigest()==P.PRINCE_PROPOSAL
    assert P.inverse_current(candidate)==parent
    compared=[]
    for name,raw in(('parent7ef',parent),('privatee73',candidate)):
        rows,images=Menu.audit(raw,include_images=True)
        assert len(rows)==len(images)==101
        compared.append((rows,images))
        print('DKJR_MENU_PROGRESS '+json.dumps(dict(input=name,ROM_SHA256=sha256(raw).hexdigest(),
            actual_rows=len(rows),images=sum(len(pair)for pair in images),outputs_written=0),separators=(',',':')),flush=True)
    (before,old_images),(after,new_images)=compared
    assert before==after
    row_digest=sha256(json.dumps(after,sort_keys=True).encode()).hexdigest()
    assert row_digest==ROWS_SHA,row_digest
    pixel_bytes=0;images_checked=0
    for old_pair,new_pair in zip(old_images,new_images,strict=True):
        for old,new in zip(old_pair,new_pair,strict=True):
            assert old.mode==new.mode=='RGBA' and old.size==new.size
            assert old.tobytes()==new.tobytes()
            pixel_bytes+=len(new.tobytes());images_checked+=1
    assert images_checked==202 and pixel_bytes==350404
    result=dict(passed=True,parent_SHA256=P.PRINCE_CURRENT,candidate_SHA256=P.PRINCE_PROPOSAL,
        exact_DK_inverse_to_parent=True,source_auditor_SHA256=AUDITOR_SHA,
        actual_menu_rows=101,row_digest_default_sorted_JSON=row_digest,
        exact_identity_facing_sprite_count_portrait_silhouette_rows=True,
        exact_RGBA_images=images_checked,exact_RGBA_bytes=pixel_bytes,
        outputs_written=0,emulator_launched=False,
        scope='Actual menu input/Select/native renderer/NMI in CPU peripheral model. No new native raster or inherent-art orientation claim.')
    receipt=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('DKJR_MENU_PARITY '+json.dumps(dict(result,receipt_SHA256=receipt),separators=(',',':')),flush=True)


if __name__=='__main__':main()
