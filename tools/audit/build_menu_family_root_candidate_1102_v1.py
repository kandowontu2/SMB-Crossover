"""Independent menu candidate snapshot with ordinary Start/A qualification."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2]
O=R/'build/menu-family-root-candidate-1102-v1'
def main():
    source=R/'tools/audit/prepare_mr_gimmick_family_1102_v18.py'
    text=source.read_text()
    substitutions={
      "O=R/'build/bub-menu-candidate-1102-v2'":"O=R/'build/menu-family-root-candidate-1102-v1'",
      'for key in[16,128,48,160]:':'for key in[16,128]:',
      "O/'combined-event.nes'":"R/'build/bub-menu-candidate-1102-v2/combined-event.nes'",
      "(O/('combined-event'+suffix))":"(R/'build/bub-menu-candidate-1102-v2'/('combined-event'+suffix))",
    }
    for old,new in substitutions.items():
        assert old in text,old;text=text.replace(old,new)
    O.mkdir(exist_ok=True)
    snapshot=O/'producer-snapshot.py';snapshot.write_text(text)
    scope={'__name__':'root_menu_candidate','__file__':str(snapshot)}
    exec(compile(text,str(snapshot),'exec'),scope)
    sys.argv=[str(snapshot),'--emit'];scope['main']()
if __name__=='__main__':main()
