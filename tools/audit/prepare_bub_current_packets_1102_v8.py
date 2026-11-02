"""Bind current v8 controls, native Easy, and the original-proven close pop."""
from pathlib import Path
import argparse,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
OLD='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'
NEW='5a8a04c3deabafc2222e594bdcefd4a445afecb5c1ab4c1753e66acc4a883d29'

def pop_extension(text):
    changes={
        "if combat_part=='fire'then return combat_step<4 and{'b'}or{}end":"if combat_part=='fire'then return combat_step<4 and{'right','b'}or{'right'}end",
        "local _,gap=target();return gap<28 and{'left'}or{}":"return{'right'}",
        "if combat_step<32 then keys[#keys+1]='a'end":"-- Original-proven close ground pop needs no A input.",
        'if i and gap<=60 then':'if i and gap<=24 then',
        "if gap<28 then combat_fail":"if gap<16 then combat_fail",
        " if combat_part=='approach'then\n  local i,gap=target()":""" if q.pops>combat_base.pops then
  assert(q.captures>combat_base.captures and combat_defeats>0,'Committed source capture reaches physical native defeat')
  local slot=nil;local born=nil
  for _,e in ipairs(q.events)do if e.kind=='original-source-trap'then slot=e.detail.slot;born=e.Main end end
  assert(slot~=nil and born~=nil and q.completed_Main-born<40,'Actual earned pop before original timeout')
  combat_target=slot
  assert(ram(L.Enemy_State+slot)&32~=0,'Actual native defeat state32 after original pop')
  combat_event('earned-pop',geometry(slot));local final=BUB_OBSERVER.finish();combat_write(final.passed,'earned-pop',final)
  assert(final.passed,'Actual source/header/hardware earned-pop observer');shot('earned-pop');finish();return
 end
 if combat_part=='approach'then
  local i,gap=target()"""
    }
    for old,new in changes.items():assert text.count(old)==1,old;text=text.replace(old,new)
    return text

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--packet',choices=['bub-controls','bob-controls','easy','pop'],required=True);a=ap.parse_args()
    if a.packet.endswith('controls'):
        source=R/'tools/audit/prepare_bub_native_controls_1102_v1.py'
        args=['--identity',a.packet.split('-')[0]]
        changes={"'native-source-'+a.identity+'-controls'":"'native-cold-fixed-'+a.identity+'-controls'",'and len(own)<=128':'and len(own)<1000'}
    elif a.packet=='easy':
        source=R/'tools/audit/prepare_bub_native_easy_1102_v7.py';args=[]
        changes={"O/'native-stomp-bub-easy'":"O/'native-cold-fixed-bub-easy'"}
    else:
        source=R/'tools/audit/prepare_bub_native_combat_1102_v1.py';args=['--mode','pop']
        changes={"O/('native-earned-bub-'+a.mode)":"O/'native-cold-fixed-bub-pop'",
            "extension=R/'tools/audit/bub_native_combat_1102_v1.lua'":"extension=R/'tools/audit/bub_native_combat_1102_v1.lua';extension_text=pop_extension(extension.read_text())",
            'extension.read_text()+':'extension_text+',
            "refs={Path(__file__),source,extension,observer,observer_receipt,ordered,":"refs={Path(__file__),R/'tools/audit/prepare_bub_native_combat_1102_v1.py',B/'original-pop-push-CPU.json',source,extension,observer,observer_receipt,ordered,"}
    text=source.read_text()
    for old,new in changes.items():assert text.count(old)==1,old;text=text.replace(old,new)
    text=text.replace(OLD,NEW).replace('31c0de8d169c84a03465eea959961cb38da3666a1e3dffd4bda982efbac11f85',NEW)
    text=text.replace("combined-visible.nes","combined-cold-fixed.nes").replace("combined-stomp.nes","combined-cold-fixed.nes")
    text=text.replace("O/'combined-visible.json',O/'visible-cold-native-v6.json'","O/'combined-cold-fixed.json'").replace("combined-visible.json","combined-cold-fixed.json").replace("combined-stomp.json","combined-cold-fixed.json")
    text=text.replace('bubble-visible-1102-v6.json','bubble-cold-fixed-1102-v8.json').replace('bubble-stomp-1102-v7.json','bubble-cold-fixed-1102-v8.json')
    text=text.replace("-1102-v2.lua'","-1102-v5.lua'").replace("-1102-v4.lua'","-1102-v5.lua'")
    text=text.replace("native-observer-prepared-1102-v2.json","native-observer-prepared-1102-v5.json").replace("native-observer-prepared-1102-v4.json","native-observer-prepared-1102-v5.json")
    # Bind the exact source used for this in-memory adaptation as well.
    needle='refs={Path(__file__),';assert text.count(needle)==1
    text=text.replace(needle,"refs={Path(__file__),R/"+repr(source.relative_to(R).as_posix())+",",1)
    saved=sys.argv;sys.argv=[str(Path(__file__)),*args]
    try:
        scope={'__file__':str(Path(__file__).resolve()),'__name__':'bub_current_v8','pop_extension':pop_extension,'B':R/'build/bubble-bobble-source-1101-v1'}
        exec(compile(text,str(source),'exec'),scope);scope['main']()
    finally:sys.argv=saved

if __name__=='__main__':main()
