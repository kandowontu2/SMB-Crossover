"""Explicit current40a to versioned7a80/a90 research boundary; no joined image."""
from hashlib import sha256
from pathlib import Path
import compose_battletoads_idle_funded_1115 as Frozen

PRINCE_SHA='6d2cbeb8bcf6b9a32d85c08ef158bb4dbe67e890831bbdb8dd203359e61b1afc'
CURRENT='40a11ffb8452c3b54caef56ddd5912e2bdda2c276545f20a589baa053de4d20e'


def load():
    actual=Frozen.Packet.Frozen.ROM.read_bytes();pin=sha256(actual).hexdigest()
    if pin==CURRENT:
        path=Frozen.R/'tools/audit/compose_prince_sword_tier2_fresh_1115.py'
        assert sha256(path.read_bytes()).hexdigest()==PRINCE_SHA
        import compose_prince_sword_tier2_fresh_1115 as Prince
        parent=Prince.inverse(actual)
    else:
        assert pin==Frozen.PIN,'Expected exact current40a or versioned7a80'
        parent=actual
    assert sha256(parent).hexdigest()==Frozen.PIN
    image,_=Frozen.proposal(parent);assert Frozen.inverse(image)==parent
    return parent,image,dict(actual_current_input_SHA256=pin,versioned_parent_SHA256=Frozen.PIN,
        executed_research_reference_SHA256=Frozen.CANDIDATE,
        current40a_CPU_or_combined_image_claim=False,current40a_to7a80_inverse_explicit=pin==CURRENT,
        no_frozen_API_changes=True)
