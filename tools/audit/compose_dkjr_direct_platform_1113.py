"""Strict private direct-foreign successor; compose/invert in memory only."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_dkjr_descending_platform_1113 as Old
import check_dkjr_direct_foreign_funding_1113 as Fit

P,H=Old.P,Old.H
PARENT=Old.PIN
ENTRY=0xb97f
PIN='769afe8d7fcdb58bed5f9f43109d7aabab3d93b1a7afb0535926e51cffce94ff'
GRANT=P.B.R/'docs/qa/allocations/dkjr-direct-foreign-1113.json'
SOURCE=Fit.SOURCE
LAYOUT=Fit.LAYOUT


def parts():
    grant=json.loads(GRANT.read_text())
    assert grant['frozen_private_parent_SHA256']==PARENT
    assert grant['original_private_parent_SHA256']==Old.PARENT
    assert sha256(SOURCE.read_bytes()).hexdigest()==grant['proposal_source_SHA256']
    linked=H.T.assemble(SOURCE.read_text(),LAYOUT)
    assert linked['used']==dict(RYU=28,NATIVE=58,POLICY=9,WORKER_A=26,WORKER_B=25)
    prior=Old.parts()[1]
    before_by_at={at:after for at,before,after in prior}
    images={6515:linked['images']['RYU']+linked['images']['NATIVE'].ljust(59,b'\xea'),
        5199:bytes.fromhex('207fb9'),5911:linked['images']['POLICY'].ljust(11,b'\xea'),
        482667:linked['images']['WORKER_A'],482789:linked['images']['WORKER_B'].ljust(26,b'\xea')}
    rows=[]
    for row in grant['resources']:
        at=row['file_offset'];before=before_by_at[at];after=images[at]
        assert at==16+row['physical_PRG']*8192+(int(row['CPU_start'],16)&8191)
        assert len(before)==len(after)==row['bytes']
        assert sha256(before).hexdigest()==row['preimage_SHA256']
        assert sha256(after).hexdigest()==row['proposed_SHA256']
        rows.append((at,before,after))
    assert len(rows)==5 and grant['new_RAM_bytes']==grant['new_CHR_bytes']==grant['new_native_capacity_bytes']==0
    return linked,rows


def transform(raw):
    assert sha256(raw).hexdigest()==PARENT
    linked,rows=parts();out=bytearray(raw);allowed=set()
    for at,before,after in rows:
        assert raw[at:at+len(before)]==before
        out[at:at+len(after)]=after;allowed.update(range(at,at+len(after)))
    out=bytes(out);pin=sha256(out).hexdigest()
    if PIN is not None:assert pin==PIN
    delta={i for i,(a,b)in enumerate(zip(raw,out))if a!=b}
    assert delta<=allowed and len(raw)==len(out)
    return out,dict(parent_SHA256=PARENT,candidate_SHA256=pin,changed_bytes=len(delta),
        entry=ENTRY,used=linked['used'],all_unowned_bytes_exact=True,
        new_RAM_bytes=0,new_CHR_bytes=0,new_native_capacity_bytes=0,
        source_motor_body_helpers_cache_head_hooks_unchanged=True,
        native_ready=False,outputs_written=0)


def reverse(raw):
    assert PIN is not None and sha256(raw).hexdigest()==PIN
    out=bytearray(raw)
    for at,before,after in parts()[1]:
        assert raw[at:at+len(after)]==after
        out[at:at+len(before)]=before
    out=bytes(out)
    assert sha256(out).hexdigest()==PARENT and transform(out)[0]==raw
    return out


def load_parent():
    public=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    Old.Old.normalize_public(public)
    raw=(P.B.R/'build/metal-flower-native-1112/candidate.nes').read_bytes()
    digest=sha256(raw).hexdigest()
    if digest==PIN:return reverse(raw)
    assert digest==PARENT,digest
    assert Old.transform(Old.reverse(raw))[0]==raw
    return raw


def load_inputs():
    raw=load_parent();return raw,transform(raw)[0]


def controller(raw,*,full=False,departure_enemy_guard=False,approach_enemy_guard=False):
    assert not approach_enemy_guard or(full and departure_enemy_guard)
    parent=reverse(raw)
    if full:
        import replay_dkjr_descending_platform_1113 as R
        # A checker may separately bind the reusable finite D.T to this
        # successor. The frozen14 control factory must still use its own ABI.
        with patch.object(R,'T',Old):
            text=R.controller(parent,descending_roof=(2,3),observe_prior=True,early_ledge=True,
                native_gap_observer=True,departure_enemy_guard=departure_enemy_guard,
                approach_enemy_guard=approach_enemy_guard)
        expected='36307f8ca293bf558377591a05939ed74d4b5a8cc42152a38cdce1c998cf0fbc'if approach_enemy_guard else'acf454572d604b049deebbb82300a07c6852c9712065d6d32f44932c6e38442f'if departure_enemy_guard else'122f4984fcf4310ce19fb26e4a7a121c83c0fff08b62dbc85af6d95adfffee66'
        assert sha256(text.encode()).hexdigest()==expected
        text=P.once(text,"mapped(0xb98a,'nesPrgRom',0x198a)","mapped(0xb97f,'nesPrgRom',0x197f)")
        text=P.once(text,'end),emu.callbackType.exec,0xb98a)','end),emu.callbackType.exec,0xb97f)')
    else:
        text=Old.controller(parent)
        assert sha256(text.encode()).hexdigest()=='b784ed4ed57a051231424e1f603dda8b160a34b749d23138649ae7d463fe4a47'
    assert text.count(PARENT)==1
    return text.replace(PARENT,PIN,1)


if __name__=='__main__':
    parent=load_parent();candidate,info=transform(parent)
    if PIN is not None:assert reverse(candidate)==parent
    print('DKJR_DIRECT_PLATFORM_COMPOSE '+json.dumps(info,separators=(',',':')),flush=True)
