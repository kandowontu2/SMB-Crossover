"""Strict source-only DK769 merge over exact delivered3684, with inverse."""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_direct_platform_1113 as DK
import compose_smb2_foreground_current_1113 as SMB2
import bub_native_noops_1113 as Bub
import bub_empty_loops_1113 as Empty

P=DK.P
PARENT=SMB2.CANDIDATE
PIN='86238670d642b49c905207d4bad3eb84a7d43b41e25760a2cdf3c2e40aaacb35'
BUB_ORIGINAL_IMAGE_SHA='1eecc22950713c0d19cb4fbccdbc517b848e39c5afc4bd1d1a553f44cbc509d0'


def spans(raw):
    """Exact independent owner envelopes, with source-qualified Bub originals."""
    source=SMB2.edits(raw)
    source.extend((Bub.at(pc),before,after)for pc,before,after in Bub.changes())
    old=(P.B.R/'build/bub-initial-tier-1103-v87/private-image.bin').read_bytes()
    assert sha256(old).hexdigest()==BUB_ORIGINAL_IMAGE_SHA
    assert len(old)==1024*len(Empty.B.PAGES)
    for i,page in enumerate(Empty.B.PAGES):
        at=1048592+1024*page
        source.append((at,old[i*1024:(i+1)*1024],raw[at:at+1024]))
    source.append((Empty.COOKIE,Empty.OLD_COOKIE,raw[Empty.COOKIE:Empty.COOKIE+16]))
    return source


@lru_cache(maxsize=1)
def canonical(base):
    assert sha256(base).hexdigest()==P.PRINCE_CURRENT
    e73,_=P.proposal_current(base)
    old14,_=DK.Old.transform(e73)
    private,_=DK.transform(old14)
    assert sha256(private).hexdigest()==DK.PIN
    return private


def dk_envelopes():
    rows=[(P.B.CHR+page*1024,1024)for page in P.B.PAGES]
    rows.append((P.B.COOKIE_AT,16))
    rows.extend((at,len(before))for at,before,after in DK.parts()[1])
    return rows


def proposal(raw):
    assert sha256(raw).hexdigest()==PARENT
    assert PARENT=='3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'
    base=DK.Old.Old.normalize_public(raw);private=canonical(base)
    own={i for at,size in dk_envelopes()for i in range(at,at+size)}
    others=spans(raw)
    foreign={i for at,before,after in others for i in range(at,at+len(before))}
    assert not own&foreign,'Complete DK and Bub/SMB2 owner envelopes must be disjoint'
    changed={i for i,(a,b)in enumerate(zip(base,private,strict=True))if a!=b}
    assert changed<=own
    assert all(raw[i]==base[i]for i in own),'Exact current DK-owned source preimages'
    out=bytearray(raw)
    for i in changed:out[i]=private[i]
    out=bytes(out);digest=sha256(out).hexdigest()
    if PIN is not None:assert digest==PIN
    assert all(out[i]==raw[i]for i in range(len(raw))if i not in changed)
    assert all(out[i]==raw[i]for i in foreign)
    independent=bytearray(private)
    for at,before,after in others:
        assert private[at:at+len(before)]==before
        assert raw[at:at+len(after)]==after
        independent[at:at+len(after)]=after
    assert bytes(independent)==out
    return out,dict(parent_SHA256=PARENT,canonical_DK_SHA256=DK.PIN,candidate_SHA256=digest,
        DK_changed_bytes=len(changed),complete_DK_envelope_bytes=len(own),
        complete_Bub_SMB2_envelope_bytes=len(foreign),complete_envelopes_disjoint=True,
        independent_source_envelope_commutation=True,
        all_Bub_SMB2_and_other_unowned_bytes_exact=True,new_RAM_bytes=0,new_CHR_bytes=0,
        new_native_capacity_bytes=0,native_ready=False,outputs_written=0)


def private_image(raw):
    assert PIN is not None and sha256(raw).hexdigest()==PIN
    # Independently restore the other owners from their source recipes and
    # retained exact original Bub image, never from an installed parent ROM.
    out=bytearray(raw)
    for at,before,after in spans(raw):
        assert raw[at:at+len(after)]==after
        out[at:at+len(before)]=before
    private=bytes(out)
    assert sha256(private).hexdigest()==DK.PIN
    return private


def inverse(raw):
    private=private_image(raw)
    old14=DK.reverse(private);e73=DK.Old.reverse(old14)
    base=P.inverse_current(e73)
    assert sha256(base).hexdigest()==P.PRINCE_CURRENT
    bub,_=Bub.combined_proposal(base)
    assert sha256(bub).hexdigest()==SMB2.PIN
    parent,_=SMB2.proposal(bub)
    assert sha256(parent).hexdigest()==PARENT and proposal(parent)[0]==raw
    return parent


def controller(raw,*,full=False,departure_enemy_guard=False,approach_enemy_guard=False):
    assert PIN is not None and sha256(raw).hexdigest()==PIN
    private=private_image(raw)
    text=DK.controller(private,full=full,departure_enemy_guard=departure_enemy_guard,
        approach_enemy_guard=approach_enemy_guard)
    assert text.count(DK.PIN)==1
    text=text.replace(DK.PIN,PIN,1)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    image,info=proposal(current)
    if PIN is not None:assert inverse(image)==current
    print('DKJR_DIRECT_CURRENT '+json.dumps(info,separators=(',',':')),flush=True)
