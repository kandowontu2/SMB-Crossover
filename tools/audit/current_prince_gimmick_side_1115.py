"""Explicit7a80 input boundary preserving the complete qualified16a Prince."""
from dataclasses import dataclass
from functools import cached_property,lru_cache
from hashlib import sha256
from pathlib import Path
import compose_gimmick_empty_side_1115 as Gimmick
import current_prince_body_transition_1115 as Previous

PIN='7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79'
PARENT='16a385654e80105f83470e14cd328d8bbceaa659730f4a81a2f36ca039cfbcfb'
COMPOSER_SHA='a9eaabb0dc63a8c457b35bc908da5e887460a7f70dc8f57a29c88a7a9a85b02c'


@dataclass(frozen=True)
class Input:
    original:bytes
    reference16a:bytes

    @cached_property
    def previous(self):return Previous.normalize(self.reference16a,kind='prince-body-transition-16a')

    def metadata(self):return dict(kind='prince-current-gimmick-7a80',actual_owning_ROM_SHA256=PIN,
        exact_inverse_parent16a_SHA256=PARENT,typed_inverse='compose_gimmick_empty_side_1115.current_inverse',
        all_Prince_packet_cookies_and_4027_static_bytes_unchanged=True,
        all_changes_inside191_Gimmick_owned_bytes=True,changed_bytes=160,
        source_only=True,outputs=0,Mesen=False)


@lru_cache(maxsize=1)
def normalize(raw,*,kind):
    assert kind=='prince-current-gimmick-7a80'and isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    assert sha256(Path(Gimmick.__file__).read_bytes()).hexdigest()==COMPOSER_SHA
    parent=Gimmick.current_inverse(raw);assert sha256(parent).hexdigest()==PARENT
    assert Gimmick.current_proposal(parent)[0]==raw
    allowed=set(range(*Gimmick.SPAN))|set(range(*Gimmick.SCREEN))|{203358,203359,203560,203561}
    changed={i for i,(a,b)in enumerate(zip(raw,parent))if a!=b}
    assert len(raw)==len(parent)==2097168 and len(allowed)==191 and len(changed)==160 and changed<=allowed
    Packet=Previous.C.Packet
    assert Packet.extract(raw)==Packet.extract(parent)
    at=Packet.COOKIE;assert raw[at:at+16]==parent[at:at+16]
    return Input(raw,parent)
