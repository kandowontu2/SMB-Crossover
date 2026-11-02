"""Rebind the visually qualified cold palette/HUD controls to current v8."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
O=R/'build/bub-menu-candidate-1102-v2';B=R/'build/bubble-bobble-source-1101-v1'
PIN='5a8a04c3deabafc2222e594bdcefd4a445afecb5c1ab4c1753e66acc4a883d29'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');a=ap.parse_args()
    rom=O/'combined-cold-fixed.nes';assert sha(rom)==PIN
    source=O/('native-visible-'+a.identity+'-cold')/'controller.lua'
    controller=source.read_text().replace('4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab',PIN)
    refs={Path(__file__),source,O/'combined-cold-fixed.json',R/'docs/qa/allocations/bubble-cold-fixed-1102-v8.json',
          B/'native-cold-fix-successor-31c0.json',B/'native-cold-fix-qualified-1102-v8.json'}
    prepare(O/('native-cold-fixed-'+a.identity),rom,controller,refs,expected=PIN,timeout=120,
        scope='Exact current v8 +delivered f5 WWF. Unchanged previously visually qualified realcold '+a.identity+' controller asserts simultaneous Select/confirm, actual Fresh identity/ready/active8, blue backdrop/fullHUDattributes/name/WORLD/TIME/sourceRGB. OnePNG, no gameplay/fullstage/install claim.',allow_interactive=True)
    own=[p for p in O.rglob('*')if p.is_file()]
    print(json.dumps(dict(prepared=True,identity=a.identity,ROM_SHA256=PIN,files=len(own),bytes=sum(p.stat().st_size for p in own))))

if __name__=='__main__':main()
