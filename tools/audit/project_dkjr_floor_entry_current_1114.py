"""Fast source fixture for the already production-pinned exact CAB image.

This is not the production composer or a new byte owner. The retained769
source input is explicit; the entire result must equal its qualified hash.
"""
from hashlib import sha256

import compose_dkjr_floor_entry_current_1114 as Current


def source_projection(raw,*,kind):
    assert kind==Current.Delivered.KIND and isinstance(raw,bytes)
    assert sha256(raw).hexdigest()==Current.PARENT
    Current.Delivered.delivered_spans()
    Floor=Current.Floor;_,legacy=Floor.F.load_inputs()
    parent=Floor.S.proposal(legacy)[0];private=Floor.proposal(parent)[0]
    assert sha256(private).hexdigest()==Floor.PIN
    image=bytearray(raw)
    for at,size in Current.Previous.Old.Old.dk_envelopes():image[at:at+size]=private[at:at+size]
    image=bytes(image);assert sha256(image).hexdigest()==Current.PIN
    own=Current.Previous.ownership()
    assert all(image[i]==raw[i]for i in range(len(raw))if i not in own)
    for at,size in Current.Previous.Current.protected_envelopes():assert image[at:at+size]==raw[at:at+size]
    for at,_,new in Current.Delivered.delivered_spans():assert image[at:at+len(new)]==raw[at:at+len(new)]
    return image,private,dict(source_projection_only=True,explicit_kind=kind,
        input_SHA256=Current.PARENT,output_SHA256=Current.PIN,private_SHA256=Floor.PIN,
        equals_pinned_production_whole_image=True,all32B_and176_envelopes_preserved=True,
        no_runtime_actor_or_player_state_seed=True,outputs_written=0)
