"""Prepare the unchanged source controls with the corrected pair observer."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]

def main():
    source=R/'tools/audit/prepare_bub_native_controls_1102_v1.py'
    text=source.read_text()
    replacements={
        "'native-observer-'+a.identity+'-1102-v2.lua'":"'native-observer-'+a.identity+'-1102-v3.lua'",
        "'native-observer-prepared-1102-v2.json'":"'native-observer-prepared-1102-v3.json'",
        "refs={Path(__file__),source,extension,observer,observer_receipt,ordered,":"refs={Path(__file__),R/'tools/audit/prepare_bub_native_controls_1102_v1.py',source,extension,observer,observer_receipt,ordered,",
        "'native-source-'+a.identity+'-controls'":"'native-source-'+a.identity+'-controls2'",
        "Observerfirstnativeuse not yet runtime-qualified.":"Pair-observer successor snapshots both actual renderer inputs; preserves original v2 bodytile negative. Observerfirstnativeuse not yet runtime-qualified."
    }
    for old,new in replacements.items():
        assert text.count(old)==1,old
        text=text.replace(old,new)
    scope={'__file__':str(Path(__file__).resolve()),'__name__':'bub_controls_successor'}
    exec(compile(text,str(source),'exec'),scope)
    scope['main']()

if __name__=='__main__':main()
