"""Bind proposed Tank hooks to exact current native compiled call spans."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_host_1101_v2 import P,O,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda b:hashlib.sha256(b).hexdigest()
word=lambda n:bytes([n&255,n>>8])

def far(b,target,bank,tail):
 return b'\x8d'+word(address(b,'SafecallA_SMC')+1)+b'\xa9'+bytes([target&255])+b'\x8d'+word(address(b,'FarcallJmpTarget_SMC')+1)+b'\xa9'+bytes([target>>8])+b'\x8d'+word(address(b,'FarcallJmpTarget_SMC')+2)+b'\xa9'+bytes([bank])+bytes([0x4c if tail else 0x20])+word(address(b,'FarCallCommon'))

def prepare():
 b=scoped_load(P/'candidate.nes');raw=b['raw'];assert sha(raw)==PIN
 labels={q[2][1:]:int(q[1],16)for line in(O/'host.lbl').read_text().splitlines()if len(q:=line.split())==3}
 routes=[('S2BoundaryImmunity','MtHostContact',False,None),('CmHostMarioInjury','MtHostInjury',False,None),('BmMarioMovement','MtHostMovement',True,None),('MarioSourceBeginPowerup','MtHostBeginPowerup',False,'MarioSourcePowerupCollision'),('MarioSourcePowerupUpdate','MtHostGrowthUpdate',False,'PlayerChangeSize'),('MaaHead','MtTerrainHeadProbe',True,None)]
 patches=[];changed=bytearray(raw)
 for old,new,tail,context in routes:
  bank=128|((location(b,old)-16)//8192);pattern=far(b,address(b,old),bank,tail);hits=[];at=raw.find(pattern,16,1048592)
  while at>=0:hits.append(at);at=raw.find(pattern,at+1,1048592)
  if context:
   start=location(b,context);hits=[at for at in hits if start<=at<start+512]
  assert len(hits)==(4 if old=='MaaHead'else 1),(old,hits)
  replacement=far(b,labels[new],2,tail)
  for at in hits:
   changed[at:at+18]=replacement
   patches.append(dict(kind='same18B_farcall_operands',old_owner=old,new_owner=new,context=context,file_offset=at,PRG_bank=(at-16)//8192,within_bank=(at-16)&8191,old_hex=pattern.hex(),fixture_new_hex=replacement.hex(),length=18))
 at=location(b,'MmNativeSideShortcut');length=address(b,'MmSideDispatchTail')-address(b,'MmNativeSideShortcut');assert length==27
 replacement=far(b,labels['MtTerrainSideProbe'],2,True)+bytes([234])*(length-18)
 changed[at:at+length]=replacement
 patches.append(dict(kind='same27B_shortcut_body',old_owner='MmNativeSideShortcut',new_owner='MtTerrainSideProbe',file_offset=at,PRG_bank=(at-16)//8192,within_bank=(at-16)&8191,old_hex=raw[at:at+length].hex(),fixture_new_hex=replacement.hex(),length=length,public_tail_PC=address(b,'MmSideDispatchTail')))
 allowed=set(i for p in patches for i in range(p['file_offset'],p['file_offset']+p['length']))
 differences=[i for i,(x,y)in enumerate(zip(raw,changed))if x!=y];assert set(differences)<=allowed
 after=dict(b);after['raw']=bytes(changed)
 q=dict(passed=True,base_ROM_sha256=PIN,patched_ROM_written=False,fixture_only=True,RAM2_code_must_be_preloaded=True,actual_farcall_A_bank=2,C_window_mapping_unchanged=True,production_source_macro_must_bind_raw_RAM2_bank=True,leases_granted=False,menu_admission=False,patches=patches,changed_bytes=len(differences),all_changes_within_declared_spans=True,
  final_link_conditions=['Rebind against final owning ROM/native symbols; current base e401 predates Karnov and final preservation is conditional.','Fund authenticated CHR carrier/forced-blank loader, complete conditional RAM2 headers and realROM identity/header gates. Shared native foreign callbacks must never jump to unloaded or another character RAM2 payload.','Existing FarCallCommon rawbank2 transports code atA2B600/physicalRAM2offset1600 without remapping C. Native farcall macros normally OR128 for ROM and must use a typed rawRAM2 entry for this worker.','Source edits must regenerate all four existing fixed MaaHead mirror copies; no unrelated fixed bank byte may change.','Use only the MarioSourcePowerupCollision/PlayerChangeSize native public sites. Other internal source-growth callbacks retain their original owners.','Keep MmSideDispatchTail and all original public PCs identical. Existing27B shortcut can hold an18B call and9B padding.'],source_bindings={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes()),'host.bin':sha((O/'host.bin').read_bytes())})
 return b,after,q

def main():
 _,_,q=prepare();(O/'compiled-call-map.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','changed_bytes','patched_ROM_written','leases_granted']}));print('Spans',len(q['patches']))

if __name__=='__main__':main()
