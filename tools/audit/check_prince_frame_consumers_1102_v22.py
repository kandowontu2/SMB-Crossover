"""Finite source/current public-entry and data-reader closure for frame factor."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
import check_hogan_current_bounded_v1 as N
import check_prince_shared_frame_1102_v22 as F
import measure_prince_owner_routes_1102_v23 as A
from check_tmnt_render_oa import address,location
from check_excitebike_router_1101_v1 import endpoint,comparable
from py65.disassembler import Disassembler
O=L.O;B=F.B


def closure(bundle,roots):
 m=N.fresh(bundle);m.raw_page(1,193);c=N.NesMPU(memory=m,pc=0xa740);d=Disassembler(c);todo=list(roots);seen={};edges=[];data=[]
 while todo:
  pc=todo.pop()
  if not 0xa740<=pc<0xb108 or pc in seen:continue
  length,text=d.instruction_at(pc);op,mode=c.disassemble[m[pc]];assert op!='BRK',('Resident closure entered data',hex(pc))
  seen[pc]=(length,text);word=m[pc+1]+256*m[pc+2]if length==3 else None
  if mode in ['abs','abx','aby','ind']and op not in ['JMP','JSR']:data.append((pc,op,mode,word))
  if op in ['JMP','JSR']:
   assert mode=='abs',('Undeclared resident indirect control',hex(pc),text)
   edges.append((pc,word,op));todo.append(word)
   if op=='JMP':continue
  elif mode=='rel':
   delta=m[pc+1];delta-=256 if delta&128 else 0;target=(pc+2+delta)&65535;edges.append((pc,target,op));todo.append(target)
  if op not in ['RTS','RTI']:todo.append(pc+length)
 return seen,edges,data


def main():
 native=F.scoped_load(L.BASE);base=A.BASE.read_bytes();assert hashlib.sha256(base).hexdigest()==A.PIN
 installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes();p65=16+65*8192
 old=dict(native,raw=base);raw=bytearray(base)
 for pc,name in [(0xaaf7,'shared-frame-v22.bin'),(0xa740,'shared-selector-v22.bin'),(0xb031,'shared-foreign-v22.bin')]:
  data=(O/name).read_bytes();at=p65+pc-0xa000;raw[at:at+len(data)]=data
 new=dict(old,raw=bytes(raw))
 for lo,hi in [(0xa740,0xa7f8),(0xaa61,0xaa66),(0xaaf7,0xabd4)]:assert base[p65+lo-0xa000:p65+hi-0xa000]==installed[p65+lo-0xa000:p65+hi-0xa000],'Rebind actual installed transport source before funding'
 assert old['raw'][16+79*8192:16+80*8192]==new['raw'][16+79*8192:16+80*8192]
 # Every actual public Hu0..35 classifier runs, with all raw IDs and both
 # tested status patterns. Scene36 and typed contact37 have separate exact
 # fixed-veneer constructors in the bound source below.
 ss=[N.fresh(b)for b in [old,new]];routes=0;families={};stops={}
 for row in range(36):
  for b in [old,new]:b['syms']['FrameConsumerProbe']=dict(b['syms']['HuMovement'],val=str(0xb600+16*row))
  for char in range(40):
   for flags in [0x30,0xf1]:
    pair=[]
    for seed in ss:
     m=N.fork(seed);N.put(m,SelectedCharacter=char,RdVariant=0,FmAlts=0);pair.append(endpoint(m,'FrameConsumerProbe',p=flags))
    assert comparable(pair[0])==comparable(pair[1]),('Actual public router changed',row,char,flags)
    q=pair[1];routes+=1;stops[str(q['stop_pc'])]=stops.get(str(q['stop_pc']),0)+1
    if char in [36,37,38,39]and q['stop_pc']!=address(new,'HuNativeWorldPalette'):
     origin=0xaa88 if char%2==0 else 0xb08c;assert q['target']==[193,origin+3*row],(row,char,q)
     families[str(char)]=origin
 # Actual fixed veneer machine bytes define every dispatch entry; data/code
 # tails cannot become legal callers through a raw high-byte assumption.
 roots={0xa800,0xa849,0xa87f,0xac1d,0xad88,0xadb6,0xadd8,0xae00,0xae0b,0xaef3,0xb029,0xb100};ven=[]
 for origin in [0xaa88,0xb08c]:
  for row in range(37):
   pc=origin+3*row;at=p65+pc-0xa000;blob=old['raw'][at:at+3];assert blob[0]==76 and new['raw'][at:at+3]==blob
   target=blob[1]+256*blob[2];roots.add(pc);ven.append(dict(veneer=pc,row=row,target=target))
 before,edges,reads=closure(old,roots);after,newedges,newreads=closure(new,roots)
 spans=[(0xa7c7,0xa7f2),(0xab72,0xabd4)]
 for pc in after:assert not any(lo<=pc<hi for lo,hi in spans),('Proposed reclaimed code remains reachable',hex(pc))
 outside=[]
 for pc,target,op in edges:
  if any(lo<=target<hi for lo,hi in spans)and not(0xa740<=pc<0xa7f2 or 0xaaf7<=pc<0xabd4):outside.append((pc,target,op))
 original_reject=int.from_bytes((B/'native-proxy-route-foreign.bin').read_bytes()[45:47],'little')
 assert outside==[(0xb05d,original_reject,'JMP')],outside
 # This exact foreign continuation operand is retargeted to the surviving
 # shared rejection label. Its indexed two-byte UI table is also relocated.
 assert new['raw'][p65+0x105d:p65+0x1060]!=(old['raw'][p65+0x105d:p65+0x1060])
 direct_data=[]
 for pc,op,mode,target in newreads:
  if any(lo<=target<hi for lo,hi in spans):direct_data.append((pc,op,mode,target))
 assert not direct_data,direct_data
 proto=(R/'src/protoman.s').read_text();assert '.res $1108-(*-ProtoArtBegin), $ff'in proto
 art=(R/'src/protoman_art.inc').read_text();rows=[]
 for face in ['Left','Right']:
  lo=location(old,'ProtoPose'+face+'Lo');hi=location(old,'ProtoPose'+face+'Hi')
  names=re.search(r'ProtoPose'+face+r'Lo:\s*\.byte ([^\n]+)',art)[1].split(',');assert len(names)==27
  for i,name in enumerate(names):
   ptr=old['raw'][lo+i]+256*old['raw'][hi+i];at=p65+ptr-0xc000;n=old['raw'][at]
   assert ptr==address(old,name.strip().lstrip('<'))and n%4==0 and 0xc000<=ptr<ptr+n+1<=0xc696;rows.append(ptr+n+1)
 assert address(old,'ProtoArtEnd')==0xc738
 lease=json.loads((R/'build/excitebike-pose-1101-v3/dispatch-lease.json').read_text());assert lease['passed']and lease['source_declared_padding']
 newforeign=(O/'shared-foreign-v22.bin').read_bytes();priorforeign=(B/'native-proxy-route-foreign.bin').read_bytes();delta=[i for i,(a,z)in enumerate(zip(priorforeign,newforeign))if a!=z];assert set(delta)<=set([10,11,45,46])
 table=base[p65+0xa61:p65+0xa66];co=(B/'native-visible-owner.bin').read_bytes()[0x1e6:0x1eb];assert table==co==bytes.fromhex('626a6c6d79')
 q=dict(passed=True,proposal_only=True,ROM_written=False,shared_sources_written=False,grant=False,actual_public_router_ABI_cases=routes,raw36_38_AA_family_and_raw37_39_B0_family=families,fixed_public_veneers=74,original_CFG_instructions=len(before),factored_CFG_instructions=len(after),remaining_external_old_tail_entry=outside,sole_external_entry_retargeted=True,new_reclaimed_code_reachable=False,new_direct_or_indexed_base_reads_inside_reclaimed_spans=False,source_SMC_table_and_common_table_equal=True,Proto_valid_descriptors=len(rows),Proto_last_descriptor_end=max(rows),Proto_art_end=0xc738,source_declared_Proto_padding=True,conditional_free_half_open=spans,conditional_free_bytes=141,base_SHA256=hashlib.sha256(base).hexdigest(),native_symbol_base_SHA256=L.PIN,current_installed_SHA256=hashlib.sha256(installed).hexdigest(),actual_installed_dispatch_and_private_SMC_preimages_exact=True,foreign_UI_relocated_operand_offsets=delta,finite_indirect_reader_domains=[dict(reader='Original Proto pose table selectors',domain='27poses/two faces; descriptor/art reads C000..C738, all before C740 overlay alias.'),dict(reader='Sh/Ex saved SMC offset tables',domain='Five source declared offsets626a6c6d79, no ROM-pointer data.'),dict(reader='CoCheckHeaders (R5),Y',domain='Two current immutable16Bcookies; raw37/39 only, never transport code.'),dict(reader='ExForeignLo-4,X',domain='Exactly X4/5 from bounded5-SMC save; two UI bytes before new A7C7 free tail.'),dict(reader='Common worker/source loader (R0),Y',domain='Mapped private RAM2/3 destinations, no bank65 transport source.'),dict(reader='FarCallCommon service targets',domain='Actual aligned fixed AA88/B08C+3row0..36 or typed B029→virtual37; source scene constructor15/row36 and ROM reset19 explicitly bound.' )],scope='Exact613b installed typed source/actual public router and direct control-flow/data-base closure; supplements full transport ABI proof. No arbitrary corrupt/forged indirect target assumption, grant, ROM or native gameplay.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'tools/audit/check_prince_shared_frame_1102_v22.py',R/'tools/reference/shinobi_resident_dispatch_1101_v1.inc',R/'tools/reference/shinobi_resident_loader_1101_v1.inc',R/'tools/reference/excitebike_resident_dispatch_1101_v1.inc',R/'tools/reference/excitebike_scene_1101_v1.inc',R/'src/protoman.s',R/'src/protoman_art.inc',R/'src/protoman_cold.s',R/'src/protoman_pose_ids.inc',B/'native-proxy-routes.s',B/'native-event-v9-owner.s',O/'shared-frame-v22.bin',O/'shared-selector-v22.bin',O/'shared-foreign-v22.bin',L.BASE,A.BASE]})
 (O/'shared-frame-consumers-v22.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','finite_indirect_reader_domains']}))


if __name__=='__main__':main()
