"""Optional two RAM-only shot pictures; exact qualified attack body retained."""
from pathlib import Path
from functools import lru_cache
import replay_rogue_earned_missile54b_1116 as F
import run_rogue_tank_images_root_1116 as Pictures
from check_ff_stdout_controller_source_1110 import LuaRuntime

J,R,ROM,H,N,W,Frames,PIN=F.J,F.R,F.ROM,F.H,F.N,F.W,F.Frames,F.PIN
BASE_SHA='a1f9a70d72e839c4393818a271cd7a6f0be7a78b2c3ea2dae0e90d8937dc3cec'
PICTURES_SHA='7823bb1bc64c7f8c31ef9afa286cbc66f44ccb05587c833dd40a068d9118b694'


def once(t,a,b):assert t.count(a)==1,(a,t.count(a));return t.replace(a,b,1)


@lru_cache(maxsize=1)
def pack(raw):
    assert H(Path(F.__file__).read_bytes())==BASE_SHA and H(Path(Pictures.__file__).read_bytes())==PICTURES_SHA
    base=F.controller(raw);assert H(base.encode())=='ff662f77a42b60e6136b9d1c9b8259c412dbfbaa24e9ad3e4e8e9e553abaaee2'
    edits=(('if finished then return end;finished=true',"if finished then return end;if reason=='earned-missile-motion-expiry-and25workers'then assert(#visual.pictures==2,'Both actual missile pictures')end;finished=true"),
        ('Mesen_images=0}', 'Mesen_images=2,visual=visual}'))
    text=base
    for a,b in edits:text=once(text,a,b)
    restored=text
    for a,b in reversed(edits):restored=once(restored,b,a)
    assert restored==base
    observer=Pictures.OBSERVER
    changes=(('#visual.pictures==0 and mature and not collector', '#visual.pictures==0 and attack.birth and not attack.expiry and attack.moves>=4'),
        ('#visual.pictures==1 and credit', '#visual.pictures==1 and attack.birth and not attack.expiry and attack.moves>=12'),
        ('Mature Rogue energy tank','Genuine earned Rogue missile'),('Earned tank and resumed Rogue','Moving missile and native world'),
        ('state=state(),PNG_bytes=#png','state=state(),shot=shot(attack.slot),moves=attack.moves,PNG_bytes=#png'))
    for a,b in changes:observer=once(observer,a,b)
    source='local visual={pictures={}}\n'+text+'\n'+observer
    LuaRuntime().compile(source)
    assert source.count('emu.takeScreenshot()')==1 and '#visual.pictures>=2'in source and '#png<=65536'in source
    return source,dict(owning_SHA256=PIN,controller_SHA256=H(source.encode()),factory_SHA256=H(Path(__file__).read_bytes()),
        qualified_functional_Lua_SHA256=H(base.encode()),functional_restoration_exact=True,
        picture_tags=['Genuine earned Rogue missile','Moving missile and native world'],
        maximum_RAM_PNGs=2,maximum_PNG_bytes=131072,output_files=0,gameplay_writes=False,native_run=False)


def controller(raw):return pack(raw)[0]
def metadata(raw):return pack(raw)[1]


if __name__=='__main__':
    import json
    print('RESULT '+json.dumps(metadata(J.load_current_image()),separators=(',',':')),flush=True)
