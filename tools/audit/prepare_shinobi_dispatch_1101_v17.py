"""Extend the native expanded-only callback range to include Shinobi."""
import json
from pathlib import Path
import prepare_shinobi_probes_1101_v16 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
from prepare_selected_native_packet_v1 import prepare,sha
R=P.R;O=R/'build/shinobi-dispatch-1101-v17'
def main():
 O.mkdir(exist_ok=True);b=scoped_load(P.O/'candidate.nes');raw=bytearray(b['raw'])
 at=location(b,'GmOnlyHigh');assert raw[at:at+2]==bytes([201,36])
 raw[at+1]=37
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
 q=dict(ROM_sha256=sha(O/'candidate.nes'),offset=at+1,old=36,new=37,installed=False)
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n')
 prepare(O/'native-smoke',O/'candidate.nes',(P.O/'native-chr-trace/controller.lua').read_text(),[Path(__file__)],expected=q['ROM_sha256'],timeout=90,scope='Cold controller replay and compact graphics observer after expanded-only callback range admission. Three screenshots; no state writes.')
 print(json.dumps(q))
if __name__=='__main__':main()
