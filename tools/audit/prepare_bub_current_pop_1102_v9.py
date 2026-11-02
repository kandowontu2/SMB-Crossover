"""Bind the source-proven 24px pop using the current v5 observer."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_bub_current_packets_1102_v8 import pop_extension

def main():
    source=R/'tools/audit/prepare_bub_native_combat_1102_v1.py';text=source.read_text()
    replacements={
        "ROM=O/'combined-visible.nes'":"ROM=O/'combined-cold-fixed.nes'",
        '4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab':'5a8a04c3deabafc2222e594bdcefd4a445afecb5c1ab4c1753e66acc4a883d29',
        "native-observer-bub-1102-v3.lua":"native-observer-bub-1102-v5.lua",
        "native-observer-prepared-1102-v3.json":"native-observer-prepared-1102-v5.json",
        "extension=R/'tools/audit/bub_native_combat_1102_v1.lua'":"extension=R/'tools/audit/bub_native_combat_1102_v1.lua';extension_text=pop_extension(extension.read_text())",
        'extension.read_text()+':'extension_text+',
        "O/('native-earned-bub-'+a.mode)":"O/'native-cold-fixed-bub-pop'",
        "refs={Path(__file__),source,extension,observer,observer_receipt,ordered,":"refs={Path(__file__),R/'tools/audit/prepare_bub_native_combat_1102_v1.py',R/'tools/audit/prepare_bub_current_packets_1102_v8.py',BACK/'original-pop-push-CPU.json',source,extension,observer,observer_receipt,ordered,",
        'combined-visible.json':'combined-cold-fixed.json',
        'bubble-visible-1102-v6.json':'bubble-cold-fixed-1102-v8.json'
    }
    for old,new in replacements.items():assert text.count(old)==1,old;text=text.replace(old,new)
    saved=sys.argv;sys.argv=[str(Path(__file__)),'--mode','pop']
    try:
        scope={'__file__':str(Path(__file__).resolve()),'__name__':'bub_current_pop','pop_extension':pop_extension}
        exec(compile(text,str(source),'exec'),scope);scope['main']()
    finally:sys.argv=saved

if __name__=='__main__':main()
