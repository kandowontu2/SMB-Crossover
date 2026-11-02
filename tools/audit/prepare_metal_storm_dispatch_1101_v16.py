"""Admit raw35 to the established expanded-only callbacks instead of legacy tables."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_menu_1101_v15 as P
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import location
O=R/'build/metal-storm-dispatch-1101-v16'
def main():
    O.mkdir(exist_ok=True);b=qualified(P.O/'candidate.nes');raw=bytearray(b['raw'])
    at=location(b,'GmOnlyHigh');assert raw[at:at+2]==bytes([0xc9,35])
    raw[at+1]=36;(O/'candidate.nes').write_bytes(raw)
    for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
    source=(R/'build/karnov-host-resource-base-1101-v1/new_roster_dispatch.s').read_text()
    old='::GmOnlyHigh:\n cmp #35';assert source.count(old)==1
    (O/'new_roster_dispatch.s').write_text(source.replace(old,'::GmOnlyHigh:\n cmp #36'))
    q=dict(passed=True,installed=False,ROM_sha256=P.sha(O/'candidate.nes'),base_ROM_sha256=P.sha(P.O/'candidate.nes'),
           patch=dict(offset=at+1,old=35,new=36),source_change='GmOnlyHigh comparison35→36 admits Metal to HuOnlyRare instead of old legacy callbacks.',
           native_verified=False)
    (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
