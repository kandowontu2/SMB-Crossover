"""Strict current Bub/Bob natural-route foundation; frozen f88 inputs unchanged."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import inspect
import re
import replay_wwf_natural_stock_7a80_1115 as Current
import replay_bub_combined_route_1113 as Previous
import compose_smb2_postbg_mirror_1113 as Post
import compose_smb2_foreground_current_1113 as Foreground

ROM,PIN,B=Current.ROM,Current.PIN,Previous.B
PINS=((Previous,'5d272ff6fb070527707cd8db601c7489a6499434917ce6c03a7dbb090472646f'),
      (Current,'1b9879d692c3a50de881c605d8f9b0b3e7257761b8b4958affaddde63675a211'),
      (Post,'415ca42d6efe1023a56c147a2d1dc0c8e32c75c98fef31b9f1a54e0fb71b7647'),
      (Foreground,'3cade46f267ab926384de0687d59670b0fc16f5ea27b821aa683a973936d05f2'))


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN
    for module,pin in PINS:assert sha256(Path(module.__file__).read_bytes()).hexdigest()==pin
    post=Current.normalize(raw).postbg
    f88=Foreground.inverse(Post.inverse(post))
    assert sha256(f88).hexdigest()==Previous.PIN
    # Full code, both runtime cookies, art and current UI operands stay owned
    # by the existing Bub recipes. Current shared fixes execute on actual raw.
    spans=[(1048592+p*1024,1024)for p in (*B.PAGES,441)]
    spans.append((16+65*8192+0xfea,16))
    spans.extend((Previous.U.at(pc),len(new))for pc,old,new in Previous.U.changes())
    for at,size in spans:assert raw[at:at+size]==f88[at:at+size],(at,size)
    return f88


@lru_cache(maxsize=4)
def controller(raw,identity=0,mode='mushroom'):
    old=Previous.controller(reference(raw),identity,mode)
    assert old.count(Previous.PIN)==1
    text=old.replace(Previous.PIN,PIN,1)
    # Every ROM callback has an exact runtime preimage check; authenticate it
    # here as well, including the complete IdleLoop and actual stomp entry.
    hooks=re.findall(r'kind="rom",pc=(\d+),offset=(\d+),data="([0-9a-f]+)"',text)
    assert len(hooks)==2
    for pc,offset,data in hooks:
        at=16+int(offset);assert raw[at:at+len(data)//2]==bytes.fromhex(data)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def metadata(raw,identity=0,mode='mushroom'):
    f88=reference(raw);text=controller(raw,identity,mode)
    return dict(ROM_SHA256=PIN,reference_SHA256=sha256(f88).hexdigest(),identity=identity,mode=mode,
        controller_SHA256=sha256(text.encode()).hexdigest(),
        complete_Bub_carrier_art_cookies_UI_exact=True,inputs_equal_frozen_f88=True,
        actual_current_CPU=True,game_changes=False,outputs=0,native=False)


def source_check(raw,identity=0,mode='mushroom',maximum=11000):
    """Exact frozen driver and scheduler, actual current CPU, new strict pin."""
    reference(raw)
    namespace=dict(Previous.__dict__,PIN=PIN,controller=controller)
    source=inspect.getsource(Previous.source_check)
    exec(compile(source,str(Path(__file__))+':current-source-driver','exec'),namespace)
    return namespace['source_check'](raw,identity,mode,maximum)
