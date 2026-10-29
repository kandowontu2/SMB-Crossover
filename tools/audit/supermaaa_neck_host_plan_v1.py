"""Read-only ac126 consumer/lease proposal after original source-ROM proof."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import pit_retold_host_controls_v1 as H
from sunny_integrated_controls_v1 import *
O=R/'build/supermaaa-neck-audit-v1';P=R/'build/pit-retold-host-v3'

def fields(line):return{m[1]:m[2]for m in re.finditer(r'(\w+)=("[^"]*"|[^,\n]+)',line)}

def main():
 assert not(O/'host-plan.json').exists()or'--replace-unbound-draft'in sys.argv
 original=json.loads((O/'proof.json').read_text());assert original['passed']
 b=scoped_load(P/'candidate.nes');assert sha(P/'candidate.nes')=='ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2'
 # Prove the prospective index really is absent from the actual cycle, not
 # merely absent in a mutable source file. Real Select bit is compiled32.
 assert address(b,'Select_Button')==32
 cycle=[]
 for value in range(8):
  q=H.C.setup(b,0);q.put(MarioVariant=value);c,tr,mn=H.C.M.runtrace(q,'KmNextVariant')
  cycle.append([value,c.a,c.processorCycles,mn])
 assert [r[1]for r in cycle]==[1,3,0,4,0,0,0,0]
 q=H.C.setup(b,0);q.put(CrossoverMenuState=2,CrossoverMenuIndex=0,CrossoverMenuButtons=0,MarioVariant=0)
 menu=[]
 for keys in[32,0,32,0,32,0,32]:
  # Both native controller polls are explicit. The CPU bus does not model
  # real controller serial input; no cold/native poll claim is inferred.
  q.put(SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
  c,tr,mn=H.C.M.runtrace(q,'CrossoverMenuInput')
  menu.append([keys,q.get('MarioVariant'),q.get('SelectedCharacter'),q.get('CrossoverMenuIndex')])
  q.put(NmiDisable=0);H.T.nmi(q,c);q.put(NmiDisable=255)
 assert [r[1]for r in menu]==[1,1,3,3,4,4,0]
 q=H.C.setup(b,0);q.put(MarioVariant=2,CrossoverMenuIndex=0);c,tr,mn=H.C.M.runtrace(q,'CmHostResolveCharacter')
 assert q.get('SelectedCharacter')==0
 # Exact emitted3-byte spans, with their actual source-line ownership.
 spans={};lines=[];files={}
 for line in(P/'candidate.dbg').read_text().splitlines():
  if line.startswith('span\t'):
   f=fields(line)
   if f.get('size')=='3'and'type'not in f:spans[f['id']]=f
  elif line.startswith('file\t'):
   f=fields(line);files[f['id']]=Path(f['name'].strip('"'))
  elif line.startswith('line\t'):lines.append(fields(line))
 hits={};ops={0xad,0xae,0xac,0x8d,0x8e,0x8c,0xcd,0xec,0xcc,0xed,0x6d,0x2d,0x0d,0xbd,0xb9,0x9d,0x99}
 for ident,s in spans.items():
  g=b['segs'].get(s['seg'])
  if not g or'ooffs'not in g:continue
  at=int(g['ooffs'],0)+int(s['start'],0);raw=b['raw'][at:at+3]
  if len(raw)==3 and raw[0]in ops and int.from_bytes(raw[1:],'little')==address(b,'MarioVariant'):
   hits[ident]=dict(bank=(at-16)//8192,PC=hex(int(g['start'],0)+int(s['start'],0)),bytes=raw.hex(),sources=[])
 source_bindings={}
 for line in lines:
  for ident in line.get('span','').split('+'):
   if ident not in hits or line.get('file')not in files:continue
   p=files[line['file']];number=int(line.get('line','0'))
   if not p.is_file()or not number:continue
   text=p.read_text().splitlines()
   if number<=len(text)and'MarioVariant'in text[number-1]:
    hits[ident]['sources'].append([str(p),number,text[number-1].strip()]);source_bindings[str(p.resolve())]=sha(p)
 sites={}
 for h in hits.values():
  key=(h['bank'],h['PC'])
  if key not in sites or not sites[key]['sources']:sites[key]=h
 assert sites and all(h['sources']for h in sites.values())
 leases=[]
 for bank,lo,hi,role in[(66,0xb680,0xb9a8,'proposed A-window neck state/terrain/cold hooks,808B cap'),(73,0xd980,0xdd80,'proposed C-window authentic pose constructor/data,1024B cap')]:
  base=0xc000 if bank==73 else 0xa000;at=16+bank*8192+lo-base
  assert b['raw'][at:at+hi-lo]==bytes([255])*(hi-lo)
  owners=[]
  for g in b['segs'].values():
   if'ooffs'not in g or not int(g['size'],0):continue
   off=int(g['ooffs'],0);start=int(g['start'],0);end=start+int(g['size'],0)
   if(off-16)//8192==bank:owners.append([g['name'].strip('"'),hex(start),hex(end)])
   if(off-16)//8192==bank:assert hi<=start or lo>=end
  leases.append(dict(proposed_only=True,bank=bank,start=hex(lo),end_exclusive=hex(hi),bytes=hi-lo,actual_FF_preimage=True,no_compiled_segment_overlap=True,role=role,current_owners=owners))
 #3 pages are a measured simultaneous-body/neck packing, not a disjoint
 # global tile collection. Request next free pages only, never write them.
 first=813;at=1048592+first*1024;assert b['raw'][at:at+3072]==bytes(3072)
 report=R/'docs/qa/supermaaa-neck-source-and-host-plan-2026-10-29.txt'
 text='''SuperMaaa original neck audit and proposed host integration - 2026-10-29

The exact local ROM is 2a415a731495aa6ca3e4e18c9e12abbc382c5dac5daf19f50cfcd0a78d862f27. Author jroweboy's source is https://github.com/jroweboy/smb1base/tree/472735118e2b4fa1b9d3cc36395b947fed466e80 . Six separately assembled sections match the actual ROM bytes exactly, and all 8192 bytes of authored lanky_mario.chr match. A complete source-built ROM match is not claimed. No new art or host implementation has been made.

Actual original sections (physical bank:CPU, including local tables): 7:F5B9 DrawNeck, 150 bytes; 1:AC76 QueueDrawPlayerNeck, 46; 6:8D83 block tables/readers, 186; 6:81C7 RunGameTimer, 97; 1:A48D RenderPlayerSub plus pose/kick tables, 256; 6:946E..94BE neck-side prefix, 80. These total 815 reference bytes, not an exact host implementation size.

Original state is length $07D3, temporary $0100 and queued-draw flag $07D1. Declared X offset $07D2 has no authored consumer. None of these is a host allocation. There is no dedicated neck button. A real game-timer decrement grows length by one pixel, capped at 160. RunGameTimer retains its menu, engine, death, below-screen, pending-timer and time-up guards. A normal tick resets control to 24 and changes 400 to 399 through genuine digit/status writers: 566 CPU cycles below the neck cap, 561 at the cap. Native NMI countdown/pause controls the cadence; this is not growth per host frame.

Regular shell/Goomba stomp at 6:900A halves length. Paratroopa demotion branches directly to bounce, bypassing that instruction. Life loss at 1:A21F clears length. Cold/warm RAM initialization includes it; ordinary game/area clears stop at $076F/$074B, so length survives same-life scene loads. Shrink/grow, Flower, Star and 1-Up do not directly change it. Fireball initialization at 1:A3A6 subtracts length from launch Y and abandons that initialization on underflow; an unconditional projectile offset would change the source behavior.

Bounding-box code at 1:A127 raises upper Y and clamps a subtraction borrow to 1. Feet, width and body anchor remain native. Head block samples subtract length, returning empty above the playfield; feet do not. Each block read clears neck temporary. Bumped-block Y at 6:98BF is also raised. Neck-side code scans X+6/+9 every 16 pixels and collects native coins before continuing to the original body-side checks. Solid-neck impede code is commented out: no neck wall stop, vine/flagpole grab or foot support is supported by the source.

DrawNeck covers 26 authored graphic records, both sizes/faces, crouch, intermediate growth, death and swimming. It lifts the two genuine head sprites, hiding them at $F8 on underflow; body and feet stay fixed. Neck tile $10 inherits head palette, priority and horizontal flip. The first four pose X offsets are right 3/4/3/6 versus left 5/4/5/2; later poses use 4. It attempts floor(length/8)+1 segments, up to 21, with early top-wrap exit. Only hidden native OAM slots 9..63 are used; active world slots are retained. The queue skips zero length.

Measured CPU arenas: 1188 direct DrawNeck cases, 147..1749 cycles and minimum SP 251; 288 queue predicates; 324 actual block-reader cases; 28 timer calls with real digit/status writers; 208 RenderPlayerSub(A=4)-then-neck cases; 15 neck-side prefixes through real native coin writers, stopped before body-side continuation. Body rendering alone takes 567..583 cycles. At length 160, the empty prefix takes 4052 cycles, all-solid 4772, and synthetic all-coin 5021 with three actual grants and 42 queued bytes. The original coin/status writers reuse $00/$01, which are also the neck loop's locals; the observed scan/grant count must not be silently replaced by a tidier algorithm. It is not packet-safety evidence. Every measured arena now rejects unmodeled RAM mirrors, hardware reads/writes and mapper writes, so these static-bank CPU executions do not silently ignore bank changes. The exact omitted AXS $CB,$FC is implemented as the original two-cycle (A&X)-immediate instruction. The earlier incorrect A=0 row-count arena is retained and excluded. No complete Main, NMI, IRQ, native or frame-rate qualification is inferred.

Proposed minimal host integration, pending allocation review:

1. Use exact raw 0/MarioVariant 2. Actual ac126 compiled cycling is 0->1->3->4->0; 2 is unreachable and resolves to raw 0 when inspected. Extending the current 25-byte KmNextVariant at 124:ADCE by seven bytes fits its existing 50-byte capsule without touching Rogue ADA4..<ADCE or AE00. The plan lists 32 genuine emitted named MarioVariant consumer sites, with source ownership. Generic save/lifecycle/sound-test consumers still need explicit integration. Native Mario movement, size, upgrades, injury, fireballs and audio remain the foundation; no added input or physics constant is proposed.

2. Audit and request one active-profile length byte, not the original addresses or a new global draw flag. Do not assume arbitrary $5F storage survives ship clearing. Reset through true cold/new-life ownership; preserve same-life scene and 1-Up progression. Any eliminated queue flag and scratch ownership need actual caller proof, including the native coin writer clobbers.

3. Proposed PRG caps are physical 66:B680..<B9A8 (808 bytes for state, terrain and cold hooks) and 73:D980..<DD80 (1024 bytes for pose construction/data). Both are entirely $FF and outside all compiled ac126 segments. These are proposals, not reservations: ROOT must also check unpublished leases. The reference footprint supports a practical attempt; genuine assembly must establish final size. No extra foreign A-bank trip is proposed. The body C lease must restore real hardware/shadows under interrupts. Report an exact shortfall before growing either cap.

4. Request CHR 813..815, three 1KB pages. A measured simultaneous packing uses 94 authentic 16-high pairs/3008 bytes, with 32/31/31 pairs per page. Every pose's body, head, swim kick and repeated/odd neck pairs share its body window 0; world/effect windows 1..11 remain native. Both faces use original flips. Maximum body count is six, paired neck count eleven. Pixel equality, odd/clipped endings and the optional ink path remain implementation proofs; no CHR asset or page has been written.

5. Reserve/emit the real compact body, then try optional neck in genuinely unused completed OAM slots after world construction. Avoid a permanent 108-byte reservation, full DMA rotation or new NMI work. Vine/no-draw can replace optional neck, while shifted head/body must have no new corruption. Actual DrawAll, ring capacity, clipping, floatey/firebar and all partial writers require executable controls before native admission.

6. Qualify complete Main movement/BG/enemy/stomp/pickup/size/fireball/lifecycle callers, true Select bit 32 and release, names/portrait, scene/1-Up/death ownership, foreign outputs, ordinary hashes, all live AXYP/SP/SMC/bank/IRQ/lag-NMI state, and actual combined coin/palette/scroll parser budget. Long-neck source cost is material; no lag improvement or frame-rate claim is made. Then ROOT can run a bounded cold native test with the normal eight-sprite limit.

The prospective immutable parent is ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2, not a retagged 737d/f56a unit. Existing GB-Pit assets and handoffs are unchanged. This audit made no shared, installed, Downloads or settings changes and launched no native process.
'''
 report.write_text(text)
 proof=dict(passed=True,read_only_plan_only=True,no_host_implementation_or_allocation=True,native_run=False,prospective_parent=sha(P/'candidate.nes'),original_proof=sha(O/'proof.json'),MarioVariant_address=hex(address(b,'MarioVariant')),actual_current_cycle=cycle,actual_MenuInput_with_fresh_both_polls=menu,unreachable_variant2_resolves_raw0=True,emitted_named_MarioVariant_consumer_sites=sorted(sites.values(),key=lambda h:(h['bank'],h['PC'])),cycle_current_bytes=address(b,'KmCycleEnd')-address(b,'KmNextVariant'),cycle_remaining_existing50B_capsule=0xae00-address(b,'KmCycleEnd'),proposed_PRG=leases,proposed_CHR=dict(first=813,last=815,bytes=3072,actual_zero_preimage=True,measured_simultaneous_packing=original['packing_proposal']),bindings={**source_bindings,**{str(p.resolve()):sha(p)for p in[Path(__file__),report,O/'proof.json',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',P/'handoff.json',Path(H.__file__)]}})
 for p in O.iterdir():
  if p.is_file()and p.name!='host-plan.json':proof['bindings'][str(p.resolve())]=sha(p)
 for f in json.loads((R/'build/source-acquisition/super-maaa-author-2026-10-29/acquisition.json').read_text())['files']:proof['bindings'][f['path']]=f['sha256']
 for p,h in proof['bindings'].items():assert sha(Path(p))==h,p
 (O/'host-plan.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,host_plan=sha(O/'host-plan.json'),report=sha(report),bindings=len(proof['bindings']),named_consumers=len(sites),cycle=cycle,lease_proposal=leases)))
if __name__=='__main__':main()
