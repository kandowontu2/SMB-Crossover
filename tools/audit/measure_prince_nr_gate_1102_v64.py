"""Source-funded Prince-only native rare ingress proposal and binary parity."""
from collections import Counter
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_collision_manifest_1102_v59 as M
import check_hogan_current_bounded_v1 as N
O=M.O;A=M.A
SOURCE=R/'build/karnov-host-resource-base-1101-v1/new_roster_dispatch.s'
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
 base,prior,_,details=M.bundle();raw=prior['raw'];source=SOURCE.read_text();start=source.index('.proc NrPickupCollision\n');end=source.index('.endproc',start);capsule=source[start:end]
 assert capsule.count(' jmp GmMatureGate\n .res 15,$ea\nOwn:')==1
 assert '::GmOnlyHigh:'in source and '::GmOnlyLegacy:'in source and '::HuOnlyRare:'in source
 # The current exact gate is the source range check after selected-character
 # classification. It preserves downstream PCs; all actual native callbacks
 # enter GmOnlyCommon which reloads SelectedCharacter. Quick's one alternate
 # path supplies32. Other earlier paths can enter the rare target directly.
 def off(pc):return 16+124*8192+pc-0xa000
 assert raw[off(0xa22a):off(0xa22a)+6]==bytes.fromhex('ad02604c90a1')
 assert raw[off(0xa2be):off(0xa2be)+7]==bytes.fromhex('c925b08c4c79a1')
 assert raw[off(0xa7c7):off(0xa7d9)]==bytes.fromhex('4c5aa4')+bytes([0xea])*15
 text='''.setcpu "6502"
.segment "VENEER"
.export PrNrRare,PrNrRareEnd
PrNrRare:
 cmp #38
 beq Own
 cmp #37
 bcs Legacy
Own:jmp $a2c2
Legacy:jmp $a24e
PrNrRareEnd:
'''
 veneer,labels=A.assemble('native-nr-gate-v64',text,'MEMORY{M:start=$a7ca,size=$f,file=%O;}SEGMENTS{VENEER:load=M,type=ro;}');assert len(veneer)==14 and labels['PrNrRareEnd']==0xa7d8
 changes=[(0xa2be,bytes.fromhex('4ccaa7ea'),'Replace existing4B comparison/branch with fixed JMP, keep A2C2 and all downstream PCs.'),(0xa7ca,veneer,'Original source-declared15B farcall retirement tail; use14B, preserve final1B NOP.')]
 post=bytearray(raw);patches=[]
 for pc,blob,why in changes:
  at=off(pc);pre=raw[at:at+len(blob)];post[at:at+len(blob)]=blob;patches.append(dict(physical_PRG=124,CPU_half_open=[pc,pc+len(blob)],file_offset=at,bytes=len(blob),old_hex=pre.hex(),new_hex=blob.hex(),old_SHA256=sha(pre),new_SHA256=sha(blob),role=why))
 # Run original and proposed actual native instructions from genuine common
 # ingress. Stop at the unchanged rare/legacy/table targets before any owner
 # worker runs. Incoming arbitraryA is overwritten by the actual LDASelected.
 memories=[]
 for image in [raw,bytes(post)]:
  mem=[0]*65536;mem[0xa000:0xc000]=image[16+124*8192:16+125*8192];memories.append(mem)
 counts=Counter();highA=set();routes=Counter();foreign=0
 for selected,alt,subtype,y,initialA,flags in itertools.product(range(256),[0,32,64,68],[0,1],range(16),[0,255],[0x20,0xe1]):
  results=[]
  for image,mem in enumerate(memories):
   mem[0x6002]=selected;mem[0x5fe5]=alt;mem[0x5fee]=subtype;c=N.NesMPU(memory=mem,pc=0xa22a);c.a,c.x,c.y,c.p,c.sp=initialA,197,y,flags,224
   for _ in range(60):
    if c.pc in [0xa179,0xa24e,0xa252]:break
    if c.pc==0xa2be:highA.add((selected,c.a));assert c.a==selected or selected==9 and c.a==32
    assert mem[c.pc]!=0,('Native rare gate BRK',selected,image,hex(c.pc));c.step()
   else:raise AssertionError(('Native rare gate bound',selected,image,hex(c.pc)))
   results.append((c.pc,c.a,c.x,c.y,c.p,c.sp))
  if selected!=38:assert results[0]==results[1],(selected,alt,subtype,y,initialA,flags,results);foreign+=1
  else:assert results[0][0]==0xa24e and results[1][0]==0xa179
  counts['original_native_common_ingress']+=1;routes[results[1][0]]+=1
 changed={i for i,(a,z)in enumerate(zip(raw,post))if a!=z};assert len(changed)==18
 # No Sunny/Bub/menu or already proposed Prince payload byte is borrowed.
 writes={i for p in patches for i in range(p['file_offset'],p['file_offset']+p['bytes'])}
 for row in details['sunny_five_exact_extents']:
  at=row['file_offset'];assert not writes&set(range(at,at+row['bytes']))
 for at,length in details['all55_Bub_event_spans_retained']:assert bytes(post[at:at+length])==raw[at:at+length]
 q=dict(passed=True,source_funding_proposal_only=True,shared_span_granted=False,ROM_written=False,base_SHA256=M.PIN,prior_memory_SHA256=sha(raw),expected_memory_only_SHA256=sha(post),patches=patches,source_declared_padding_half_open=[0xa7ca,0xa7d9],source_padding_bytes=15,used_veneer_bytes=14,remaining_padding=1,foreign_original_binary_parity_cases=foreign,all_native_common_ingress_cases=counts['original_native_common_ingress'],finite_GmOnlyHigh_actual_A=sorted(highA),new_routes={hex(k):v for k,v in routes.items()},foreign_AXYP_SP_and_route_exact=True,all_fixed_downstream_CPU_addresses_preserved=True,source_reader_closure='NrPickupCollision source ends foreign path with unconditional JMP GmMatureGate followed by explicit .res15EA and Own label. Earlier own branches targetA7D9 afterpadding; no fallthrough intoA7CA. It is executable source padding, not a zero/FF scan. Native rare targets are source-defined finite dispatch capsules, original fixed public entrypoints and table rows, never this unexported tail. Current actual fixed gate entryA22A reloads Selected before GmOnlyHigh; finite binary differentials cover all256 raw IDs,4FmAlts states,2Peachsubtypes,16typed Y rows,2initialA and2physicalflag sets. The sole altered identity38 now enters existing HuOnlyRare; every other real ingress ends at the exact old route with exact AXYP/SP.',scope='Measured memory-only proposal uses new physicalPRG124 shared spans requiring root grant. No shared ROM mutation or native-ready claim. Actual complete PowerUpObjHandler/body/head/side ingress must be rerun with the two reviewed patches; both prior missing-callback negative and Sunny native fixes retained.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),SOURCE,R/'tools/audit/prepare_thomas_private_ingress_1031_v5.py',R/'tools/audit/prepare_functional_roster_smb2_v1.py',O/'native-nr-gate-v64.s',O/'native-nr-gate-v64.bin',O/'collision-manifest-v59.json',O/'collision-lifetime-proposal-v62.json',O/'current-ingress-negative-v61.json',R/'docs/qa/allocations/prince-collision-lifetime-1102-v62.json']})
 (O/'native-nr-gate-proposal-v64.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings','finite_GmOnlyHigh_actual_A','source_reader_closure']}))


if __name__=='__main__':main()
