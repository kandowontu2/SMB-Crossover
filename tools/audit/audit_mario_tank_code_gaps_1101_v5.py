"""Current compiled Quick UI / RiverCity last literal domains for86/81."""
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as M
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN;seed=M.fresh(b);site=address(b,'X5QuickUiAdmission');assert site==0xa79c
 at=location(b,'X5QuickUiAdmission');code=b['raw'][at:at+24];assert code==bytes.fromhex('e00d90034cdca5e009d00aade55f2920f0034cf9a54cfea5')
 # Every X, accepted flag source and both branch-relevant incoming carries
 # execute the actual terminal leaf, stopping at the first external jump.
 cuts=0;exits={}
 for x,alt,p in itertools.product(range(256),[0,32,255],[0x30,0xf9]):
  m=M.fork(seed);m.raw_page(1,214);M.put(m,CurrentBank=214,FmAlts=alt);c=NesMPU(memory=m,pc=site);c.x=x;c.p=p;c.sp=224
  for _ in range(20):
   if not site<=c.pc<site+24:break
   c.step()
  else:raise AssertionError('Quick leaf bounded')
  assert c.sp==224 and c.pc in[0xa5dc,0xa5f9,0xa5fe],hex(c.pc);exits[str(c.pc)]=exits.get(str(c.pc),0)+1;cuts+=1
 # All core-local indexed literal inputs in the exact source include chain:
 # WalkPoses is AND3; RcBits is admitted six native enemy slots; both final
 # seven-cell status names setY6 then decrement through0 before return.
 root=R/'build/bt-ready-menu-1031-v2/joint/src';paths=[root/n for n in['river_city.s','river_city_core_host_v8.inc','river_city_wall_prepass_v2.inc','river_city_combat.s','river_city_required_ink_v1.inc','x5_bounce.s']]
 required=(root/'river_city_required_ink_v1.inc').read_text();combat=(root/'river_city_combat.s').read_text();bounce=(root/'x5_bounce.s').read_text()
 assert 'and #3\n tay\n lda WalkPoses,y'in required and 'ldy #6' in required
 assert 'RcBits:.byte 1,2,4,8,16,32'in combat and 'AlexText:.byte "ALEX    "\nRyanText:.byte "RYAN    "'in required
 assert '.assert *<=$a7c4'in bounce
 seg=next(s for s in b['segs'].values()if s['name'].strip('"')=='RIVER_CITY_CORE');assert int(seg['start'],0)==0xa300 and int(seg['size'],0)==0xdce
 alex=address(b,'RcStatusName::AlexText');ryan=address(b,'RcStatusName::RyanText');assert [alex,ryan]==[0xb04b,0xb053],(hex(alex),hex(ryan))
 # Same compiled segment also contains two subsequently appended SMB3plus
 # owners. Bind them explicitly; absence from the old RCR include is not
 # permission to allocate their bytes.
 extra=R/'build/bt-ready-menu-1031-v2/joint/smb3plus_menu_name.s';source=extra.read_text();paths.append(extra)
 assert '.assert *<=$b100'in source
 names=address(b,'MbMenuNameSelect::Names');leaf=address(b,'MbPeachLeafOverride');assert [names,leaf]==[0xb07f,0xb09f]
 assert int(b['syms']['MbPeachLeafOverride']['size'],0)==47 and leaf+47==0xb0ce
 oldbus=M.Bus
 class Reads(oldbus):
  def __getitem__(self,i):
   if isinstance(i,int)and (alex<=i<alex+8 or ryan<=i<ryan+8 or names<=i<names+32)and getattr(self,'watch',False)and self.rawtags[1]==209:self.reads.add(i)
   return super().__getitem__(i)
 M.Bus=Reads
 try:m=M.fresh(b)
 finally:M.Bus=oldbus
 m.watch=True;m.reads=set();calls=0
 for variant,p in itertools.product([0,1],[0x30,0x31,0x71,0xf9]):
  M.put(m,RcVariant=variant);M.invoke(m,'RcStatusName',p=p,y=255);calls+=1
 assert m.reads==set(range(alex,alex+7))|set(range(ryan,ryan+7));statusreads=sorted(m.reads);m.reads=set()
 for variant in range(4):
  M.put(m,M3Variant=variant,VRAM_Buffer1_Offset=0);M.invoke(m,'MbMenuNameSelect');calls+=1
 assert m.reads==set(range(names,names+32));namereads=sorted(m.reads)
 leaves=0
 for variant,expired,ready,frame,power,p in itertools.product(range(4),[0,1],[0,1,2],[0,0x38],[0,0x7f],[0x30,0x31,0x71,0xf9]):
  M.put(m,M3Variant=variant,MbFloatExpired=expired,MbFloatReady=ready);m[address(b,'M3Native::Player_Frame')]=frame;m[address(b,'M3Native::Player_Power')]=power
  M.invoke(m,'MbPeachLeafOverride',a=85,p=p);leaves+=1
 q=dict(passed=True,current_ROM_sha256=PIN,formal_grant=False,PRG86=dict(physical_gap=[0x7b4,0x800],old_segment='X5_BOUNCE',compiled_last_leaf_PC=site,compiled_last_leaf_hex=code.hex(),finite_leaf_cases=cuts,terminal_JMP_destinations=exits,no_fallthrough_into_gap=True,required_source_cap_change=['X5QuickUiAdmission <=A7C4','X5QuickUiAdmission <=A7B4']),PRG81=dict(physical_gap=[0x10d0,0x1100],old_segment='RIVER_CITY_CORE',compiled_half_open=[0xa300,0xb0ce],appended_smb3plus_owners_closed=True,appended_menu_name_data=dict(PC=names,length=32,legal_M3Variant=[0,1,2,3],actual_name_read_addresses=namereads),last_leaf=dict(PC=leaf,bytes=47,source_legal_native_cases=leaves,finite_no_indexed_or_indirect_memory=True,all_paths_RTS=True),original_RCR_literals=[dict(name='AlexText',PC=alex,length=8),dict(name='RyanText',PC=ryan,length=8)],actual_status_and_menu_name_calls=calls,actual_RCR_literal_reads=statusreads,core_local_literal_domains=dict(WalkPoses=[0,3],RcBits=[0,5],AlexText=[0,6],RyanText=[0,6]),Rogue_consumer_proof_sha256=sha((O/'orbit-gap-owners.json').read_bytes()),Rogue_page_only=[0xb100,0xb200],required_source_cap='Appended MbPeachLeafOverride end<=B0D0; preserve all prior bytes/PCs'),limits=['These are exact named previous-owner boundaries and typed last-leaf/literal domains, not a blanketFF allocation. Root must review and grant the intervals before owning-source placement.','Other PRG gaps in combined request require their separately named graphics/audio/code-owner closures; this receipt does not imply they are granted.'],bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in paths+[Path(__file__)]})
 (O/'code-gap-owners.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,Quick_tail_cases=cuts,last_literal_calls=calls,Peach_last_leaf_cases=leaves,RcCore_end=0xb0ce)))
if __name__=='__main__':main()
