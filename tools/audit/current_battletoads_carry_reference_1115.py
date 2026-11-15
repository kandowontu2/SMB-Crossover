"""Explicit174fa/40a to versioned detached references, no owning image join."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import current_battletoads_resolver_research_1115 as Previous

PALETTE_PIN='174fa29cf05ce1d14526ea3778c74b33a3858301c81da49b982e0ca2200ab0b4'
PALETTE_SOURCE='1b3e655bb5d44a0230d690d6dcc7ebd70959e5200fc661ece80f0758f95f58e6'


def load():
    rom=Previous.Frozen.Packet.Frozen.ROM;actual=rom.read_bytes();pin=sha256(actual).hexdigest()
    if pin==PALETTE_PIN:
        import compose_bub_native_palette_current_1115 as Palette
        assert sha256(Path(Palette.__file__).read_bytes()).hexdigest()==PALETTE_SOURCE
        assert Palette.PARENT==Previous.CURRENT and Palette.CANDIDATE==PALETTE_PIN
        parent40a=Palette.inverse(actual);assert sha256(parent40a).hexdigest()==Previous.CURRENT
    else:
        assert pin==Previous.CURRENT,'Expected exact official174fa or versioned40a'
        parent40a=actual
    original=Path.read_bytes;reads=[]
    def read(path):
        if path.resolve()==rom.resolve():reads.append(1);assert len(reads)==1;return parent40a
        return original(path)
    with patch.object(Path,'read_bytes',read):parent,reference,info=Previous.load()
    assert len(reads)==1
    return parent,reference,dict(info,actual_current_input_SHA256=pin,
        explicit_palette174fa_to40a_inverse_for_references_only=pin==PALETTE_PIN,
        reference40a_SHA256=sha256(parent40a).hexdigest(),actual174fa_CPU_or_combined_image_claim=False,
        owning174fa_bytes_not_composed_in_detached_reference=True,physical_mutable_Nightly_reads=1)
