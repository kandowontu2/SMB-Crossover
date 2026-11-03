"""Exact no-request hook ABI and source-declared same-bank funding closure."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import check_prince_player_pipeline_1102_v67 as C
from check_tmnt_render_oa import address,location
N,O=C.N,C.O
SOURCE=R/'build/karnov-host-resource-base-1101-v1/new_roster_dispatch.s'
sha=lambda b:hashlib.sha256(b).hexdigest()


def reachable(raw,start,stop):
 mem=[0]*65536;mem[0xa000:0xc000]=raw[16+124*8192:16+125*8192];todo=[start];seen=set();branches=[]
 while todo:
  pc=todo.pop()
  if pc in seen or not start<=pc<stop:continue
  seen.add(pc);op=mem[pc];mn,mode=N.NesMPU.disassemble[op];size=1 if mode in ['imp','acc']else 2 if mode in ['imm','zpg','zpx','zpy','inx','iny','rel']else 3
  assert mn not in ['BRK','???'],(hex(pc),mn)
  if mode=='rel':
   v=mem[pc+1];target=pc+2+(v if v<128 else v-256);branches.append([pc,target]);todo.extend([target,pc+2])
  elif mn=='JMP':
   assert mode=='abs';target=mem[pc+1]|mem[pc+2]<<8;branches.append([pc,target]);todo.append(target)
  elif mn not in ['RTS','RTI']:todo.append(pc+size)
 return sorted(seen),branches


def main():
 _,b,_,_=C.M.bundle();raw=b['raw'];mem=[0]*65536
 first=(O/'post-return-v78.bin').read_bytes();second=(O/'post-return-second-v78.bin').read_bytes();mem[0xa760:0xa760+len(first)]=first;mem[0xa795:0xa795+len(second)]=second
 flags=[0x20|v for v in range(256)if not v&0x30 and not v&0x0c];counts={};foreign=owned=0
 for selected,a,p in itertools.product(range(256),range(256),flags):
  mem[0x6002]=selected;mem[0x16a]=a^255;c=N.NesMPU(memory=mem,pc=0xa760);c.a=a;c.x=(a*73+selected)&255;c.y=(a*29+selected)&255;c.p=p;c.sp=224;c.stPushWord(0x5aff);x,y=c.x,c.y
  for _ in range(30):
   if c.pc in [0x5b00,0x97d6]:break
   c.step()
  else:raise AssertionError(('Post-return hook bound',selected,a,p))
  queued=selected==38 and bool(p&1)
  if not queued:
   assert c.pc==0x5b00 and(c.a,c.x,c.y,c.p&0xef,c.sp)==(a,x,y,p&0xef,224),(selected,a,p,c.a,c.x,c.y,c.p,c.sp)
   foreign+=1
  else:assert c.pc==0x97d6 and(c.x,c.y,c.sp)==(x,y,222);owned+=1
  assert mem[0x16a]==a
 text=SOURCE.read_text();pads=[]
 for name,entry,end in [('NrRise',0xa760,0xa76f),('NrPrivate',0xa795,0xa7a4)]:
  start=text.index('.proc '+name+'\n');capsule=text[start:text.index('.endproc',start)]
  target='GmRiseGate'if name=='NrRise'else'GmPrivateGate'
  assert capsule.count(' jmp '+target+'\n .res 15,$ea\nNative:')==1
  assert address(b,name+'::Native')==end;at=16+124*8192+entry-0xa000
  assert raw[at:at+15]==bytes([0xea])*15 and raw[at-3]==0x4c
  pcs,edges=reachable(raw,address(b,name),end+5);assert not any(entry<=pc<end for pc in pcs)
  assert not any(entry<=target<end for _,target in edges)
  symbols={n for n,s in b['syms'].items()if s.get('seg')and entry<=int(s['val'],0)<end and(16+124*8192<=location(b,n)<16+125*8192)};assert not symbols,symbols
  pads.append(dict(owner=name,half_open=[entry,end],file_offset=at,source_explicit_bytes=15,preimage_hex=raw[at:at+15].hex(),predecessor_hex=raw[at-3:at].hex(),preimage_SHA256=sha(raw[at:at+15]),native_source_CFG_instructions=len(pcs),native_source_edges=edges,no_exported_or_internal_symbol_in_pad=True,no_indirect_control_in_capsule=True))
 installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes();regions=[(p['file_offset'],15)for p in pads]+[(16+124*8192+0xd75,3)]
 assert all(installed[at:at+n]==raw[at:at+n]for at,n in regions),'Current installed hook preimages drifted'
 at=16+124*8192+0xd75;assert raw[at:at+3]==bytes.fromhex('8d6a01')and raw[at-3:at]==bytes.fromhex('205a01')
 q=dict(passed=True,CPU_only=True,ROM_written=False,shared_grant=False,no_queued_request_AXYP_SP_exact_cases=foreign,queued_owned_tail_to_genuine_Kill_cases=owned,raw_IDs=256,all_A_values=256,physical_flag_states=len(flags),flags_mask_ignored_only_nonphysical_B=0x10,source_pad_candidates=pads,post_callback_entry=dict(CPU=0xad75,file_offset=at,old_hex='8d6a01',new_hex='2060a7',immediately_preceding_actual_farcall_return='JSR FarCallCommon atAD72, returnsAD75 with native A-window124 restored'),current_installed_SHA256=sha(installed),all_current_hook_preimages_exact=True,indirect_consumer_closure='Both are explicit source-declared unlabelled15EA tails after unconditional legacy JMP. Native own branches target the unchanged Native label AFTER each tail. Finite source capsule CFGs have no indirect jumps and reach neither tail. Original exported/internal symbols contain no entry into either tail; native dispatch source publishes named capsule entries/Native labels and explicit TargetLo/Hi/Bank arrays, never these unlabelled retired tails. This is the same retired-farcall source funding mechanism granted for v64 NrPickupCollision; it is a new ungranted proposal for these two distinct spans.',required='Root full reader/allocation review; actual same-bank return and IRQ in wholeGameCore; changed-image cold/auth/retire/respawn/tag0179 lifetime before native admission.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),SOURCE,O/'post-return-v78.s',O/'post-return-v78.bin',O/'post-return-second-v78.bin',O/'post-return-measurement-v78.json',O/'deferred-death-CPU-v79.json',R/'docs/qa/allocations/prince-native-rare-gate-1102-v64.json']})
 (O/'post-return-foreign-CPU-v81.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','source_pad_candidates','indirect_consumer_closure']}))


if __name__=='__main__':main()
