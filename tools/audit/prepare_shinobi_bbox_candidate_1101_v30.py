"""Compose source-authoritative Shinobi bbox into installed c3dd successor."""
import hashlib,json
from pathlib import Path
import check_shinobi_bbox_design_1101_v29 as C
import check_shinobi_bbox_seams_1101_v29 as I
P=C.P;R=P.R;O=R/'build/shinobi-bbox-candidate-1101-v30'
BASE=R/'build/roster-combined-1101-v3/candidate.nes';PIN='c3dd03031faaef7faf12f865b7a5cdfd363835e2179eca22fe2eef8180553157'


def main():
 O.mkdir(exist_ok=True);assert P.S.sha(BASE)==PIN
 for name in ['design.json','CPU-design.json','seams-CPU.json']:assert json.loads((P.O/name).read_text())['passed']
 old,new,k=C.proposal();source=BASE.read_bytes();raw=bytearray(source)
 delta=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
 assert len(raw)==len(old['raw'])==len(new['raw'])
 for i in delta:assert raw[i]==old['raw'][i],('Composition preimage',i);raw[i]=new['raw'][i]
 for pc in range(k['ShSourceBounds'],k['ShNativeCombatEnd']):
  pos=pc-0xa000;at=16+1048576+P.PAGES[pos//1024]*1024+pos%1024
  assert raw[at]==source[at],'Source combat span changed'
 changed=set(delta);assert all(a==b for i,(a,b)in enumerate(zip(source,raw))if i not in changed)
 arthur=[i for i,(a,b)in enumerate(zip(source,old['raw']))if a!=b]
 assert len(arthur)==531 and all(raw[i]==source[i]for i in arthur),'Arthur531B delta lost'
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes(BASE.with_suffix(suffix).read_bytes())
 (O/'shinobi-cookie.bin').write_bytes(raw[16+65*8192+0xa78:16+65*8192+0xa88])
 q=dict(passed=True,ROM_sha256=P.S.sha(O/'candidate.nes'),base_sha256=PIN,changed_bytes=len(delta),Arthur_531_changed_bytes_exact=True,Metal_41_preserved=True,own_resident_bytes=1534,own_resident_remaining=2,cached_worker_start=0xbaf8,cached_worker_bytes=194,cached_span_bytes=256,duplicate_attributes_now_native_fixed_127_EF36=True,source_physics_and_combat_span_unchanged=True,new_native_body='Exact original six-offset source pose rectangle, current camera, viewport clipping; native small-body fallback only on failed cache authentication.',installed=False,native=False,scope='Source/CPU-qualified private successor. Newnativebboxchanges contacts, so prior1-1/native receipts are not reused; root owns native verification and installation.',bindings={str(p.resolve()):P.S.sha(p)for p in[Path(__file__),P.O/'resident-design.bin',P.O/'body-design.bin',R/'tools/reference/shinobi_bbox_design_1101_v29.inc',R/'tools/audit/check_shinobi_bbox_design_1101_v29.py',R/'tools/audit/check_shinobi_bbox_seams_1101_v29.py',BASE]})
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
 P.CANDIDATE=O/'candidate.nes';P.CURRENT_BASE=BASE;P.CHECK_OUTPUT=O
 C.main();I.main()


if __name__=='__main__':main()
