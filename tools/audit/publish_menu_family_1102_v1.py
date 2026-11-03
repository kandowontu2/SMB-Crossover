"""Generate and round-trip the exact Downloads menu nightly IPS."""
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def main():
    source=R/'tools/audit/publish_thomas_lifts_1102_v3.py'
    text=source.read_text()
    text=text.replace('build/thomas-delivery-1102-v3','build/menu-family-delivery-1102-v1')
    text=text.replace('d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d','22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19')
    text=text.replace('Exact candidate Thomas full1-1, six native helper crossings, no life loss; actual Downloads cold menu/lives/first assisted crossing and IRQ/NMI pass. Other characters/all powerups/both modes remain incomplete.','All32 roster slots/all Select cycles and separate Mr Gimmick/Bub/Bob launches pass. Actual Downloads Bob launch and silhouette/name checks pass. This is menu qualification, not new fullstage/powerup proof.')
    old='Thomas now clears non-shortcut1-1 into1-2 without life loss, using native helper lifts at leftX400/560/688/864/2560/2816, initialY192 (width32; centers+16). Both late crossings verified. Actual Downloads cold launch and first helper crossing verified. Existing Bub/Bob and prior roster retained. Full roster/all powerups qualification remains ongoing.'
    assert old in text
    text=text.replace(old,'Mr. Gimmick now cycles to Bub and Bob with Select; their standalone slot is removed. Bub/Bob previews face right. Battletoads now has a roster silhouette. Nine stale coming-soon indicators removed from playable characters; Prince remains locked. Full32slot/alternate browse and allthree family launches tested, including actual Downloads launch. Gameplay/full roster/powerup qualification remains ongoing.')
    scope={'__name__':'menu_publish','__file__':str(source)}
    exec(compile(text,str(source),'exec'),scope);scope['main']()
if __name__=='__main__':main()
