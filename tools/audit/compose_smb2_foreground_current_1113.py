"""Source-bound SMB2 repairs over the delivered Bub/Bob nightly, in memory."""
from hashlib import sha256
import json

import compose_smb2_pipe_foreground_1113 as Foreground

Flag=Foreground.Check.Priority.Mirror.Flag
Mirror=Foreground.Check.Priority.Mirror
Priority=Foreground.Check.Priority
PIN='f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
CANDIDATE='3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'


def edits(raw):
    """Rebuild every exact envelope from its owning source and grants."""
    old,new,_=Flag.source_recipe(raw)
    _,world,_=Foreground.recipe(raw)
    patches=[(Flag.PROBE_AT,old['probe'],new['probe']),
             (Flag.WORLD_AT,old['world'],world)]
    canonical,_=Mirror.code()
    patches.extend((16+bank*8192+(Mirror.START&8191),Mirror.OLD,canonical)
                   for bank in Mirror.MIRRORS)
    patches.extend(Priority.inputs(raw,inverse=True)[0])
    owned=set()
    for at,before,after in patches:
        assert len(before)==len(after)
        span=set(range(at,at+len(before)))
        assert not owned&span
        owned.update(span)
    assert len(patches)==10
    return patches


def proposal(raw):
    assert sha256(raw).hexdigest()==PIN
    out=bytearray(raw)
    patches=edits(raw)
    for at,before,after in patches:
        assert raw[at:at+len(before)]==before
        out[at:at+len(after)]=after
    image=bytes(out)
    digest=sha256(image).hexdigest()
    if CANDIDATE is not None:assert digest==CANDIDATE
    return image,dict(parent_SHA256=PIN,ROM_SHA256=digest,
        exact_envelopes=[[at,len(before)]for at,before,after in patches],
        changed_bytes=sum(a!=b for a,b in zip(raw,image,strict=True)),
        all_unowned_bytes_exact=True,new_RAM_bytes=0,new_ROM_bytes=0,
        new_CHR_bytes=0,installed=False,native_qualified=False)


def inverse(raw):
    assert CANDIDATE is not None and sha256(raw).hexdigest()==CANDIDATE
    out=bytearray(raw)
    for at,before,after in edits(raw):
        assert raw[at:at+len(after)]==after
        out[at:at+len(before)]=before
    parent=bytes(out)
    assert sha256(parent).hexdigest()==PIN and proposal(parent)[0]==raw
    return parent


def independently_compare(public):
    """Reproduce the frozen private chain and prove disjoint commutation."""
    import bub_native_noops_1113 as Bub
    base=Bub.combined_reverse(public)
    flagged=Flag.proposal(base)[0]
    mirrored=Mirror.all_mirrors_proposal(flagged)[0]
    priority=Priority.proposal(mirrored)[0]
    private=Foreground.proposal(priority)[0]
    assert sha256(private).hexdigest()==Foreground.CANDIDATE
    bub={i for i,(a,b)in enumerate(zip(base,public,strict=True))if a!=b}
    smb2={i for i,(a,b)in enumerate(zip(base,private,strict=True))if a!=b}
    assert not bub&smb2
    merged,q=proposal(public)
    other=bytearray(private)
    for i in bub:
        assert other[i]==base[i]
        other[i]=public[i]
    assert merged==other
    if CANDIDATE is not None:assert inverse(merged)==public
    return dict(**q,private_parent_SHA256=Foreground.CANDIDATE,
        Bub_changed_bytes=len(bub),SMB2_changed_bytes=len(smb2),
        exact_disjoint_commutation=True,outputs_written=0)


if __name__=='__main__':
    from pathlib import Path
    public=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    print(json.dumps(independently_compare(public),separators=(',',':')),flush=True)
