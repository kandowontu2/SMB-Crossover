"""Exact renderer dependency rebind and populated foreign retirement parity."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as C
import check_prince_current_foreign_1102_v103 as F
N,O,I=C.N,C.O,C.I


def main():
 b,manifest=C.image();old,_=C.M.parent();before=(O/'native-runtime-v49.bin').read_bytes();after=(O/'native-runtime-v78.bin').read_bytes();meta0=(O/'native-metadata-v49.bin').read_bytes();meta1=(O/'native-metadata-v78.bin').read_bytes()
 render=json.loads((O/'native-render-CPU-v68.json').read_text());assert render['passed']
 lo,hi=render['code_half_open'];changes=[(0xa000+i,x,z)for i,(x,z)in enumerate(zip(before,after))if lo<=0xa000+i<hi and x!=z];assert changes==[(0xbd30,0xe8,0xe0)] # Existing granted source-dead contact span, outside renderer instruction/data closure.
 # Immutable source pose/grid tables and the exact executable grid helper.
 assert meta0[:0x1163]==meta1[:0x1163]
 origin=(R/'build/sunny-growth-prelude-1102-v9/candidate.nes').read_bytes();native_banks=[]
 for name in ['X5SetPhysicalChr','MetaspriteRenderLoop']:
  physical=(I.location(b,name)-16)//8192;at=16+8192*physical
  assert origin[at:at+8192]==b['raw'][at:at+8192];native_banks.append(dict(name=name,physical_PRG=physical,bank_SHA256=C.M.sha(b['raw'][at:at+8192])))
 art=(O/'prince-body-8x16.chr').read_bytes();assert len(art)==31072
 payload=bytearray()
 for page in C.M.POOL[:31]:payload.extend(b['raw'][16+128*8192+page*1024:16+128*8192+(page+1)*1024])
 assert payload[:len(art)]==art # Final art carrier tail is already typed code backing, not zero padding.
 a,_=C.cold(old,39);z,_=C.cold(b,39);assert F.view(a)==F.view(z)
 fields=['Enemy_Flag','Enemy_State','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer'];count=0
 for selected in [0,37,38,39,255]:
  for cwindow in [2,201]:
   for shape in ['valid','flag-mismatch','id-mismatch','already-defeated']:
    pair=[N.fork(a),N.fork(z)];initial=[]
    for m in pair:
     N.put(m,SelectedCharacter=selected)
     for slot in range(6):
      rec=0x320+16*slot;m.ram[2][rec:rec+16]=bytes([1,6,1,0x17,0xcd,4+slot,0x10+slot,0x20+slot,1+slot%2,0x30+slot,0,0,0,0,0,0])
      values=dict(Enemy_Flag=1 if shape=='flag-mismatch'else 128|slot,Enemy_ID=8 if shape=='id-mismatch'else 6,Enemy_State=32 if shape=='already-defeated'else 0,Enemy_X_Speed=0x70,Enemy_Y_Speed=0x71,Enemy_MovingDir=2,EnemyIntervalTimer=0x72)
      for name,value in values.items():m[I.address(b,name)+slot]=value
     initial.append([[m[I.address(b,n)+s]for n in fields]for s in range(6)])
     C.clear(m);m.raw_page(2,cwindow);N.put(m,CurrentBankC=cwindow)
    outputs=[I.invoke(m,193,0xae0b,(83,71,109,0xa1))for m in pair]
    assert outputs[0]['regs']==outputs[1]['regs'] and F.view(pair[0])==F.view(pair[1]),(selected,cwindow,shape)
    for m in pair:
     for slot in range(6):
      got=[m[I.address(b,n)+slot]for n in fields];want=[1,4+slot,0x10+slot,0x20+slot,1+slot%2,0x30+slot]if shape=='valid'else initial[0][slot]
      assert got==want and not m.ram[2][0x320+16*slot],(selected,cwindow,shape,slot,got,want)
     native=bytes(m[0x200:0x800]);I.invoke(m,193,0xae0b,(83,71,109,0xa1));assert native==bytes(m[0x200:0x800]),'Retirement repeated a native actor write'
    count+=1
 q=dict(passed=True,CPU_only=True,ROM_written=False,memory_only_SHA256=manifest['expected_memory_only_SHA256'],renderer_rebind=dict(exact_same_reachable_render_code_and_data=True,container_difference_only_in_granted_dead_contact_span=changes,exact_same_immutable_pose_and_grid_helper_C800_D963=True,native_consumer_full_bank_identities=native_banks,source_art_bytes=len(art),source_art_SHA256=C.M.sha(art),all31physical_carriers_exact=True,reused_all408_source_facing_poses_and280_capacity_edges='native-render-CPU-v68.json',historical_interrupt_scope='v68 positive1 NmiDisable was regularNMI, not lag. Current102/104 carry genuineFF lag/nested coverage; this exact dependency proof does not relabel the old experiment.'),populated_Bub_retirement_pairs=count,actors_per_case=6,selected_characters=[0,37,38,39,255],C_windows=[2,201],shapes=['valid','flag-mismatch','id-mismatch','already-defeated'],valid_original_native_fields_restored=True,invalid_native_actor_fields_untouched=True,repeated_retirement_no_native_effect=True,all_foreign_AXYP_SP_private_native_ZP_SMC_mapper_PPU_exact=True,scope='Exact current97 renderer dependencies equal the already qualified full408pose/280edge renderer, grid metadata/helper,31art pages and full native consumer banks. No repeated emulator or acoustic claim. Actual complete Bub66 cold on parent/successor then every populated six-association retirement shape, current manager/publicCoRetire and idempotent followup execute. No native-play/menu/install claim.',bindings={p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),O/'post-return-manifest-v97.json',O/'native-render-CPU-v68.json',O/'native-runtime-v49.bin',O/'native-runtime-v78.bin',O/'native-metadata-v49.bin',O/'native-metadata-v78.bin',O/'prince-body-8x16.chr',R/'build/bub-upgrades-root-1102-v48/native.s',R/'docs/qa/allocations/prince-battle-lifetime-1102-v46.json']})
 (O/'current-render-retire-CPU-v111.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'current-render-retire-negative-v111.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
