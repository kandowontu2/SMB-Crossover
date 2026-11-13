"""Typed current-Doki pipe priority successor; source-owned exact envelopes."""
from hashlib import sha256
import json

import check_smb2_pipe_priority_1113 as Check
import compose_smb2_foot_mirror_1113 as Mirror

PIN=Mirror.ALL_IMAGES[Mirror.PARENTS[1]]
CANDIDATE='dadb9d80702148fe40b1a64d1cfff7ff2df65248b9c72e7c167d32e3589670be'
CALLS=((974799,'S2Graphics::DokiMeta','G_Meta'),(974826,'S2Graphics::SetBody','G_SetBody'))


def inputs(raw,*,inverse=False):
    if not inverse:
        assert sha256(raw).hexdigest()==PIN
        flag=Mirror.all_mirrors_inverse(raw);parent=Mirror.Flag.inverse(flag)
    else:parent=raw
    q,old,new,labels,constants,b=Check.measure(parent,components=True,_original=not inverse)
    grant=json.loads((Check.R/'docs/qa/allocations/smb2-pipe-priority-1113.json').read_text())
    assert q['source_SHA256']==grant['fresh_source_SHA256']
    assert q['exact_Ready85_member_SHA256']==grant['exact_Ready85_render_member_SHA256']
    assert q['exact_Doki_member_SHA256']==grant['exact_Ready85_Doki_member_SHA256']
    patches=[]
    for name,segment in(('graphics','S2_PRIORITY_GRAPHICS'),('palette','S2_PRIORITY_PALETTE')):
        row=q['original_complete_source'][name]
        patches.append((row['file'],old[name],new[segment]))
    body_at,size,old_body=q['body_site'];assert size==6
    patches.append((body_at,bytes.fromhex(old_body),new['S2_PRIORITY_BODY']))
    for at,old_name,new_name in CALLS:
        oldpc=Check.F.W.address(b,old_name);newpc=labels[new_name]
        patches.append((at,b'\x4c'+oldpc.to_bytes(2,'little'),b'\x4c'+newpc.to_bytes(2,'little')))
    if not inverse:assert all(raw[at:at+len(before)]==before for at,before,after in patches)
    assert all(len(before)==len(after)for at,before,after in patches)
    assert len(patches)==5
    assert [[at,len(before)]for at,before,after in patches]==[
        [item['file_offset'],item['bytes']]for item in grant['resources']]
    q.update(grant='docs/qa/allocations/smb2-pipe-priority-1113.json',grant_status=grant['status'])
    return patches,q


def proposal(raw):
    patches,q=inputs(raw);out=bytearray(raw)
    for at,before,after in patches:out[at:at+len(after)]=after
    image=bytes(out)
    q.update(parent_SHA256=PIN,ROM_SHA256=sha256(image).hexdigest(),candidate_prepared=True,
        exact_envelopes=[[at,len(before)]for at,before,after in patches],
        changed_bytes=sum(a!=b for a,b in zip(raw,image,strict=True)))
    assert q['ROM_SHA256']==CANDIDATE
    return image,q


def inverse(raw):
    # Only exact new scoped bytes are reversed. The full reconstructed parent
    # hash then authenticates every unrelated byte; no installed-ROM dependency.
    assert sha256(raw).hexdigest()==CANDIDATE
    patches,_=inputs(raw,inverse=True);out=bytearray(raw)
    for at,before,after in patches:
        assert raw[at:at+len(after)]==after
        out[at:at+len(before)]=before
    original=bytes(out);assert sha256(original).hexdigest()==PIN
    assert proposal(original)[0]==raw
    return original


if __name__=='__main__':
    parent7=Check.F.load_input();parent=Mirror.all_mirrors_proposal(Mirror.Flag.proposal(parent7)[0])[0]
    image,q=proposal(parent);assert inverse(image)==parent
    print(json.dumps(q,separators=(',',':')),flush=True)
