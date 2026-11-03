"""Replace nightly without backups and bind a real Downloads menu launch."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check
P=R/'build/menu-family-root-candidate-1102-v1'
O=R/'build/menu-family-delivery-1102-v1'
PIN='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'
def main():
    rom=P/'mr-gimmick-family.nes';assert sha(rom)==PIN
    for name in ['native-browse','native-bub','native-bob','native-mr-gimmick']:
        directory=P/name;q=json.loads((directory/'ready.json').read_text());result=json.loads((directory/'capture/result.json').read_text());binding=json.loads((directory/'capture/binding.json').read_text())
        assert result['passed'] and binding['exit_code']==0 and binding['ROM_sha256']==PIN
        assert binding['ready_sha256']==sha(directory/'ready.json')
        for path,digest in q['bindings'].items():assert sha(path)==digest,path
    d=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    before=check(d);assert before['passed']
    assert sha(d)=='d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d'
    d.write_bytes(rom.read_bytes());after=check(d);assert after['passed']and sha(d)==PIN
    O.mkdir(exist_ok=True);source=P/'native-bob/controller.lua';packet=O/'downloads-smoke'
    prepare(packet,rom,source.read_text(),[Path(__file__),source,d],expected=PIN,timeout=240,scope='Actual Downloads full menu navigation to Bob and A launch; exact names, Battletoads silhouette, native raw39/Bob Fresh identity and active gameplay. No fullstage claim.',allow_interactive=True)
    f=packet/'ready.json';q=json.loads(f.read_text());q['ROM']=str(d);f.write_text(json.dumps(q,indent=2)+'\n')
    (O/'delivery.json').write_text(json.dumps(dict(installed=True,ROM_sha256=PIN,destination=str(d),backup_created=False,before=before,after=after,downloads_launch_verified=False),indent=2)+'\n')
if __name__=='__main__':main()
