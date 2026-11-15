"""Current590 six-role ordinary M/F controller, shared native/source Lua."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import explore_wwf_natural_flower_590_1115 as Source

R,ROM,PIN,W,N=Source.Images.R,Source.Images.ROM,Source.PIN,Source.W,Source.N
IDENTITIES=Source.IDENTITIES
SOURCE='de035643e747c8bde10c77c28afe12eddbd6e17422c4b793ebcbb01ca21a26e5'
TEMPLATE=R/'tools/playthroughs/wwf_natural_flower_native_1115.lua'

def normalize(raw):
    return Source.Images.WWF.Frozen.normalize(Source.Images.owning(raw)[1])

@lru_cache(maxsize=6)
def bindings(raw,key):
    assert sha256(Path(Source.__file__).read_bytes()).hexdigest()==SOURCE
    q=deepcopy(Source.config(raw,key));q['sha']=PIN;b=dict(W.Symbols.bundle(),raw=raw)
    for n in ('PlayerFacingDir','Player_X_Speed','Player_Y_Speed','A_B_Buttons',
              'PreviousA_B_Buttons','GuestPowerupActive','GuestPowerupAge',
              'TimerControl','Square2SoundQueue','FloateyNum_Control','Player1ScoreDisplay','Block_Buffer_1'):
        q['ram'][n]=W.address(b,n)
    for n in ('WfMovement','HandlePowerUpCollision','GuestPowerupUpdate'):
        at=W.location(b,n);bank=(at-16)//8192
        q['hooks'][n]=dict(pc=W.address(b,n),offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
            bank_SHA256=sha256(raw[16+bank*8192:16+(bank+1)*8192]).hexdigest())
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q

@lru_cache(maxsize=6)
def controller(raw,key):
    q=bindings(raw,key)
    text='local C='+Source.Images.WWF.Previous.Frozen.lua(q)+'\n'+TEMPLATE.read_text(encoding='utf-8')
    Source.Images.WWF.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in ('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(text.encode()).hexdigest(),
        template_SHA256=sha256(TEMPLATE.read_bytes()).hexdigest(),gameplay_seeds=0,outputs=0)
