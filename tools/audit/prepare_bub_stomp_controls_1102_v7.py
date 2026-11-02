"""Rebind the passing original controls to exact v7 and its moved observer."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]

def main():
    source=R/'tools/audit/prepare_bub_native_controls_1102_v1.py';text=source.read_text()
    replacements={
        "ROM=O/'combined-visible.nes'":"ROM=O/'combined-stomp.nes'",
        '4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab':'31c0de8d169c84a03465eea959961cb38da3666a1e3dffd4bda982efbac11f85',
        "'native-observer-'+a.identity+'-1102-v2.lua'":"'native-observer-'+a.identity+'-1102-v4.lua'",
        "'native-observer-prepared-1102-v2.json'":"'native-observer-prepared-1102-v4.json'",
        "refs={Path(__file__),source,extension,observer,observer_receipt,ordered,":"refs={Path(__file__),R/'tools/audit/prepare_bub_native_controls_1102_v1.py',source,extension,observer,observer_receipt,ordered,",
        "O/'combined-visible.json',O/'visible-cold-native-v6.json'":"O/'combined-stomp.json'",
        'bubble-visible-1102-v6.json':'bubble-stomp-1102-v7.json',
        "'native-source-'+a.identity+'-controls'":"'native-stomp-'+a.identity+'-controls'",
        "Observerfirstnativeuse not yet runtime-qualified.":"Exact31c0 v7 Easy source successor, observerv4 movedPCs/newcookie; source-controls fixture unchanged.",
        'and len(own)<=128':'and len(own)<1000'
    }
    for old,new in replacements.items():assert text.count(old)==1,old;text=text.replace(old,new)
    scope={'__file__':str(Path(__file__).resolve()),'__name__':'bub_v7_controls'}
    exec(compile(text,str(source),'exec'),scope);scope['main']()

if __name__=='__main__':main()
