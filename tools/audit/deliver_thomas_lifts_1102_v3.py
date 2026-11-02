"""Install the six-lift qualified candidate and prepare actual Downloads smoke."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check

def main():
    p=R/'build/thomas-current-candidate-1102-v3';out=R/'build/thomas-delivery-1102-v3'
    rom=p/'candidate.nes';pin=sha(rom);proof=json.loads((p/'native-qualified.json').read_text())
    assert proof['passed'] and proof['ROM_sha256']==pin
    for name,h in proof['bindings'].items():assert sha(name)==h,name
    d=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(d)=='613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'
    before=check(d);d.write_bytes(rom.read_bytes());after=check(d);assert sha(d)==pin
    out.mkdir(exist_ok=True)
    source=p/'native-six-lifts/controller.lua';text=source.read_text()
    old=" if x>=lift+96 then\n"
    assert text.count(old)==1
    text=text.replace(old," if x>=lift+96 then\n  if target==1 then finish(true,'Downloads cold selection and first assisted crossing');return end\n")
    packet=out/'downloads-smoke'
    prepare(packet,rom,text,[Path(__file__),source,p/'native-qualified.json',d],expected=pin,timeout=160,allow_interactive=True,
            scope='Actual Downloads launch: cold menu/lives/game Thomas pixels, first native assisted crossing, genuine IRQ/NMI parity. Separate exact-candidate receipt qualifies all six crossings and full1-1.')
    ready=packet/'ready.json';q=json.loads(ready.read_text());q['ROM']=str(d);ready.write_text(json.dumps(q,indent=2)+'\n')
    report=dict(installed=True,ROM_sha256=pin,previous_SHA256=before['ROM_sha256'],destination=str(d),backup_created=False,before=before,after=after,downloads_launch_verified=False,full11_qualified=True)
    (out/'delivery.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
