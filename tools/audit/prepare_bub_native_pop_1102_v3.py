"""Use a closer genuine shot and continue walking toward its trapped victim."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_bub_native_pop_1102_v2 as V2

def transform_extension(text):
    text=V2.transform_extension(text)
    replacements={
        "if combat_part=='fire'then return combat_step<4 and{'b'}or{}end":"if combat_part=='fire'then return combat_step<4 and{'right','b'}or{'right'}end",
        "local _,gap=target();return gap<28 and{'left'}or{}":"local _,gap=target();return gap<18 and{'left'}or{'right'}",
        'if i and gap<=60 then':'if i and gap<=40 then'
    }
    for old,new in replacements.items():assert text.count(old)==1,old;text=text.replace(old,new)
    return text

def main():
    source=R/'tools/audit/prepare_bub_native_combat_1102_v1.py';text=source.read_text()
    replacements={
        "a=ap.parse_args()":"a=ap.parse_args();assert a.mode=='pop'",
        "extension=R/'tools/audit/bub_native_combat_1102_v1.lua'":"extension=R/'tools/audit/bub_native_combat_1102_v1.lua';extension_text=transform_extension(extension.read_text())",
        'extension.read_text()+':'extension_text+',
        'refs={Path(__file__),source,extension,observer,observer_receipt,ordered,':"refs={Path(__file__),R/'tools/audit/prepare_bub_native_combat_1102_v1.py',R/'tools/audit/prepare_bub_native_pop_1102_v2.py',source,extension,observer,observer_receipt,ordered,",
        "O/('native-earned-bub-'+a.mode)":"O/'native-earned-bub-pop3'",
        "Actual Bub cold confirm, naturally parsed positive Goomba, genuine freshB source bubble then earned ":"Original pop3 controls: closer40pxshot, Right duringfire/waitcapture, groundapproach andconditionalfreshAatactualsource |dx|<10; preserves original39update timeout andstrictpopthreshold. Actual Bub cold confirm, naturally parsed positive Goomba, genuine freshB source bubble then earned "
    }
    for old,new in replacements.items():assert text.count(old)==1,old;text=text.replace(old,new)
    scope={'__file__':str(Path(__file__).resolve()),'__name__':'bub_pop_closer','transform_extension':transform_extension}
    exec(compile(text,str(source),'exec'),scope);scope['main']()

if __name__=='__main__':main()
