"""Return native terrain query results instead of the generic rejected service."""
import json
import prepare_shinobi_body_1101_v15 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import prepare
R=P.R; BASE=P.O; O=R/'build/shinobi-probes-1101-v16'

def main():
 O.mkdir(exist_ok=True)
 assert P.S.sha(BASE/'candidate.nes')=='73fab8d7e73b82139cd0fbba55eeac63737c742cb2d7218f5a7f2c87f7ccc203'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 labels=P.S.labels(P.BASE/'resident.lbl');patches=[]
 for row,name in [(10,'BlockBufferColli_Head'),(14,'BlockBufferColli_Side')]:
  target=address(b,name);assert 0x8000<=target<0xa000
  at=16+65*8192+labels['ShServiceVeneers']-0xa000+3*row
  old=bytes([76,labels['ShDispatch']&255,labels['ShDispatch']>>8])
  assert raw[at:at+3]==old
  new=bytes([76,target&255,target>>8]);raw[at:at+3]=new
  patches.append(dict(row=row,target=name,offset=at,old=old.hex(),new=new.hex()))
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 receipt=dict(ROM_sha256=P.S.sha(O/'candidate.nes'),patches=patches,installed=False)
 (O/'assembly.json').write_text(json.dumps(receipt,indent=2)+'\n')
 prepare(O/'native-smoke',O/'candidate.nes',(BASE/'native-smoke/controller.lua').read_text(),[__import__('pathlib').Path(__file__)],expected=receipt['ROM_sha256'],timeout=90,scope='Cold title to Shinobi, idle and walking after native terrain-query fix. Three screenshots; no state writes.')
 print(json.dumps(receipt))

if __name__=='__main__':main()
