"""Strict571 FF stock source facade; frozen Nov10 modules remain unchanged."""
from hashlib import sha256
from pathlib import Path
from types import FunctionType,SimpleNamespace

import compose_native_floatey_score_1114 as Score
import check_ff_white_mushroom_current_1110 as White
import check_ff_all_mushrooms_current_1110 as All
import check_ff_flowers_current_1110 as Flower
import check_ff_star_life_current_1110 as Stock

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN=Score.CANDIDATE
KIND='score571-ff-stock'
PINS={White:'c6c3a7dca9cea3bf4577d5038f74a22261be8989edc1ad87ddd8590d0e581de0',
      All:'e122dc0dc793eeb7aa002389ea1112302f3cc008b19b77d38d75f695cdcc5f7e',
      Flower:'e990661e7b9fe754dede187b39dd0dfda6367f051cdd701b01ddc9b03aad50ec',
      Stock:'19650c8f19ad03c8eecf4652a91b6ecd33ce9676c5544206cbe4e4ce23d72ee2'}


class MemoryImage:
    def __init__(self,raw):self.raw=raw
    def read_bytes(self):return self.raw


def clone(module,**bindings):
    """Independent function globals, never patch a frozen module's globals."""
    space=dict(vars(module));space.update(bindings)
    for name,fn in tuple(space.items()):
        if isinstance(fn,FunctionType)and fn.__globals__ is vars(module):
            copy=FunctionType(fn.__code__,space,fn.__name__,fn.__defaults__,fn.__closure__)
            copy.__kwdefaults__=fn.__kwdefaults__;space[name]=copy
    return SimpleNamespace(**space)


def bind(raw,*,kind):
    assert kind==KIND and isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    original=Score.inverse(raw);assert sha256(original).hexdigest()==Score.PIN and Score.proposal(original)[0]==raw
    for module,pin in PINS.items():assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    # Current FF owner is its CHR893..900 worker, not Kirby PRG74.
    at=1048592+893*1024;kernel=raw[at:at+8192];cookie=raw[511774:511790]
    assert len(kernel)==8192 and kernel[0x1fe0:0x1ff0]==bytes((255,))*16
    assert cookie[:4]==bytes((0xa7,22,0,12))and cookie[4:]==sha256(kernel).digest()[:12]
    w=clone(White,ROM=MemoryImage(raw),PIN=PIN)
    a=clone(All,W=w);f=clone(Flower,A=a,W=w);s=clone(Stock,F=f,A=a,W=w)
    info=dict(actual_input_SHA256=PIN,explicit_kind=KIND,source_only_score_inverse_F11=sha256(original).hexdigest(),
        actual_runtime_bytes_SHA256=sha256(raw).hexdigest(),FF_CHR_half_open=[893,901],
        FF_worker_SHA256=sha256(kernel).hexdigest(),FF_cookie=cookie.hex(),
        frozen_modules_SHA256={Path(m.__file__).name:p for m,p in PINS.items()},
        frozen_APIs_and_globals_unchanged=True,legacy_ROM_reads=0,ROM_changes=0,outputs=0)
    return s,info
