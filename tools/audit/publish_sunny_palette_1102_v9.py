"""Publishable exact IPS after actual Downloads Sunny full-stage validation."""
from pathlib import Path
R=Path(__file__).resolve().parents[2]

def main():
    source=R/'tools/audit/publish_thomas_lifts_1102_v3.py';text=source.read_text()
    text=text.replace('build/thomas-delivery-1102-v3','build/sunny-delivery-1102-v9').replace('d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d','16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b')
    old='Exact candidate Thomas full1-1, six native helper crossings, no life loss; actual Downloads cold menu/lives/first assisted crossing and IRQ/NMI pass. Other characters/all powerups/both modes remain incomplete.'
    assert old in text;text=text.replace(old,'Sunny private candidate and actual Downloads full non-shortcut Hard1-1 into active1-2 without life loss. Original late-render negatives retained; palette cache and typed prelude tests pass, unchanged native deadline/DMA/CHR/IRQ/stack guards pass. Other roster, allpowerups and bothmodes remain incomplete.')
    old='Thomas now clears non-shortcut1-1 into1-2 without life loss, using native helper lifts at leftX400/560/688/864/2560/2816, initialY192 (width32; centers+16). Both late crossings verified. Actual Downloads cold launch and first helper crossing verified. Existing Bub/Bob and prior roster retained. Full roster/all powerups qualification remains ongoing.'
    assert old in text;text=text.replace(old,'Fixed Sunny growth/shrink rendering flicker from repeated palette packets. Sunny cold Hard1-1 into active1-2 passes without life loss on candidate and actual Downloads file, with real rendering deadline and DMA checks. Existing Mr. Gimmick/Bub/Bob menu, Battletoads silhouettes and playable indicators retained. Bub landing repair and new Prince/DK Jr/Sonic integrations remain private work. Full roster/allpowerup qualification remains ongoing.')
    scope={'__name__':'sunny_publish','__file__':str(source)};exec(compile(text,str(source),'exec'),scope);scope['main']()
if __name__=='__main__':main()
