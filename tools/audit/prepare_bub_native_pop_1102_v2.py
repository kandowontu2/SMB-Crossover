"""Approach a real trapped circle on foot, then use the original fresh jump."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]

def transform_extension(text):
    replacements={
        'local combat_events,combat_defeats={},0':'local combat_events,combat_defeats={},0\nlocal pop_jump_started=false',
        "if combat_step<32 then keys[#keys+1]='a'end":"if pop_jump_started then keys[#keys+1]='a'end",
        " elseif combat_part=='wait-timeout'or combat_part=='pop-approach'then":""" elseif combat_part=='wait-timeout'or combat_part=='pop-approach'then
  if combat_part=='pop-approach'and not pop_jump_started then
   local dx=((source(0x113+8*combat_target)-source(0x103)+128)&255)-128
   if math.abs(dx)<10 then
    pop_jump_started=true;combat_event('fresh-A-near-trapped-circle',geometry(combat_target))
   end
  end"""
    }
    for old,new in replacements.items():assert text.count(old)==1,old;text=text.replace(old,new)
    return text

def main():
    source=R/'tools/audit/prepare_bub_native_combat_1102_v1.py';text=source.read_text()
    replacements={
        "a=ap.parse_args()":"a=ap.parse_args();assert a.mode=='pop'",
        "extension=R/'tools/audit/bub_native_combat_1102_v1.lua'":"extension=R/'tools/audit/bub_native_combat_1102_v1.lua';extension_text=transform_extension(extension.read_text())",
        'extension.read_text()+':'extension_text+',
        'refs={Path(__file__),source,extension,observer,observer_receipt,ordered,':"refs={Path(__file__),R/'tools/audit/prepare_bub_native_combat_1102_v1.py',source,extension,observer,observer_receipt,ordered,",
        "O/('native-earned-bub-'+a.mode)":"O/'native-earned-bub-pop2'",
        "Actual Bub cold confirm, naturally parsed positive Goomba, genuine freshB source bubble then earned ":"Original pop2 controller: ground approach until actual source |dx|<10, then freshA reduces original vertical separation below10. Actual Bub cold confirm, naturally parsed positive Goomba, genuine freshB source bubble then earned "
    }
    for old,new in replacements.items():assert text.count(old)==1,old;text=text.replace(old,new)
    scope={'__file__':str(Path(__file__).resolve()),'__name__':'bub_pop_successor','transform_extension':transform_extension}
    exec(compile(text,str(source),'exec'),scope);scope['main']()

if __name__=='__main__':main()
