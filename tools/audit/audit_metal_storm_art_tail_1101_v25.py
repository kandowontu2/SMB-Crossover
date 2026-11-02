"""Prove a private art-page tail is not indexed by current Metal graphics."""
import json,re,hashlib
import prepare_metal_storm_hurt_host_1101_v24 as P
O=P.P.R/'build/metal-storm-art-tail-1101-v25'
sha=P.P.sha

def main():
 O.mkdir(exist_ok=True);stage=json.loads((P.O/'assembly.json').read_text())
 for p,h in stage['bindings'].items():assert sha(p)==h,p
 raw=(P.O/'candidate.nes').read_bytes();render=(P.O/'native-render.bin').read_bytes()
 labels={m[2]:int(m[1],16) for line in (P.O/'component.lbl').read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
 def part(name,size):
  at=labels[name]-0xcd00;return render[at:at+size]
 body=part('MsBodyMap',1002);shot=part('MsShotMeta',38)
 lo=part('MsBodyPhysicalLo',5);hi=part('MsBodyPhysicalHi',5)
 assert [lo[i]+256*hi[i] for i in range(5)]==list(range(495,500))
 body_indices=[]
 for group in body[:64]:
  if group==255:continue
  assert group<33
  offset=body[64+group]*4+130;count=body[97+group];assert count in [6,8]
  for i in range(count):body_indices.append(body[offset+i*4+2])
 assert max(body_indices)==143
 shot_indices=[]
 for offset in part('MsShotOffsets',6):
  count=shot[offset]//4
  for i in range(count):shot_indices.append(shot[offset+1+i*4])
 assert max(shot_indices)==4
 source=(P.O/'component.s').read_text()
 assert 'MsShotPhysical=499' in source.replace(' ','')
 # Existing shot renderer applies pair bias16 in physical page499.
 assert 'MsShotCell:\n ldy MsPacketAt\n lda MsPacket,y\n asl a\n ora #$a1' in source
 occupied=set()
 for index in body_indices:
  if index//32==4:occupied.update(range((index%32)*32,(index%32+1)*32))
 for index in shot_indices:occupied.update(range((index+16)*32,(index+17)*32))
 assert max(occupied)==671 and all(n<672 for n in occupied)
 page=raw[16+1048576+499*1024:16+1048576+500*1024]
 original=P.P.R/'build/metal-storm-coexistence-1101-v9/red-white-black.chr'
 assert page==original.read_bytes()[4096:5120] and page[672:]==bytes(352)
 grant=json.loads((P.P.R/'docs/qa/checkpoints/2026-11-01/metal-storm-chr-resources-v10/resource-grant.json').read_text())
 assert 499 in grant['Metal_pages']
 q=dict(passed=True,baseline_ROM_sha256=stage['ROM_sha256'],granted=True,CHR=dict(page=499,byte_half_open=[672,1024],bytes=352,already_exclusive_Metal_page=True),conditional_RAM=dict(bank=2,copy_half_open=[0xd900,0xdd00],code_half_open=[0xdba0,0xdd00],exclusive_selected_owner=35),body_pattern_max=max(body_indices),shot_pattern_max=max(shot_indices),highest_displayed_byte=671,
  conditions=['Extend existing buffered-copy/readback loop from11 to12 rows, mapping499 toD900. No new physical CHR page is allocated.', 'Regenerate both complete owner fingerprints with the extra code image; retain cold forced-blank and full owner retirement.', 'Keep displayed art bytes0..671 exact. Future armor/weapon artwork or metadata changes must re-audit this shared page tail.', 'Copying art bytes intoD900..DBA0 is harmless private data, not executable entrypoints. Only DBA0..DD00 may hold new helpers.', 'This is a source-domain/storage grant, not a native loader or gameplay test.'],
  bindings={str(p):sha(p) for p in [__file__,P.O/'candidate.nes',P.O/'component.s',P.O/'component.lbl',P.O/'native-render.bin',original]})
 (O/'resource-grant.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))
if __name__=='__main__':main()
