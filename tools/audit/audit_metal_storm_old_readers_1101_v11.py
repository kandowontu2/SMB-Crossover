"""Small typed old-reader caps for the nine private linker partitions."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_owning_graft_1101_v11 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=P.O;sha=P.sha

def main():
 stage=json.loads((O/'owning-link.json').read_text());b=scoped_load(O/'candidate.nes');assert sha(O/'candidate.nes')==stage['ROM_sha256']
 raw=b['raw'];owned=json.loads((O/'ownership.json').read_text())['holes'];rows=[];sources=[]
 # Code-only terminal owners are not raw-bank art streams. Bind the real last
 # instruction and its named source; do not classify every FF byte as free.
 for role,name,file in[
  ('GATE','CdNewGameProfiles',R/'src/chip_hud_queue.s'),
  ('WORK','RyuPrimaryBlocked',R/'src/ryu_primary_gate.s'),
  ('AUTH','GuestVictoryGuestControl',R/'src/guest_victory_control.s'),
  ('ZERO','PnHudCancelWork',R/'src/parodius_hud_queue.s'),
  ('COPY','DkHostWeaponTail',R/'tools/reference/donkey_kong_host_v1.s')]:
  s=b['syms'][name];n=int(s['size'],0);at=location(b,name);body=raw[at:at+n];h=next(h for h in owned if h['role']==role)
  assert at+n==h['file_interval'][0],(role,name,at+n,h['file_interval'][0])
  terminal=body[-1]==0x60 or body[-3]==0x4c;assert terminal,(role,body[-6:].hex())
  text=file.read_text();assert '.proc '+name in text and '.endproc'in text
  rows.append(dict(role=role,last_owner=name,exact_owner_end=at+n,body_bytes=n,terminal_hex=body[-3:].hex(),terminal='RTS'if body[-1]==0x60 else'absolute JMP',compiled_owner_sha256=hashlib.sha256(body).hexdigest(),code_owner_no_fallthrough=True,raw_bank_stream=False,scope='This terminal function has no inline ROM table or raw-bank-copy consumer. Other earlier owner tables remain governed by their existing valid-state typed contracts.'))
  sources.append(file)
 # Exact terminal tables: each legitimate index is finite in its real source.
 for role,name,count,file,clauses in[
  ('ENTRY','MacRosterStatusName::Names',21,R/'build/bt-ready-menu-1031-v2/joint/src/mac_roster_adapter.s',['cpy #7','Offsets:.byte 0,7,14']),
  ('MAP','SsBassBanks',104,R/'src/bass_special_poses.inc',['SsBassBanks:', 'SsBassRightHi:']),
  ('FINISH','SoundTestSfxHi',37,R/'src/sound_test_tables.inc',['SoundTestHeroCount=37','SoundTestSfxHi: .byte'])]:
  at=location(b,name);data=raw[at:at+count];h=next(h for h in owned if h['role']==role);text=file.read_text()
  assert all(c in text for c in clauses),(name,clauses)
  # Bass has the one-byte QW_EMPTY34 zero-length descriptor after its104-entry
  # bank table. The native descriptor reader consumes only that zero header.
  assert at+count==h['file_interval'][0]-(1 if role=='MAP'else 0),(name,at,count,h['file_interval'])
  if role=='MAP':assert raw[at+count]==0 and address(b,'QwEmpty34')==0xdd9d
  rows.append(dict(role=role,last_table=name,valid_byte_index_range=[0,count-1],table_bytes=count,file_interval=[at,at+count],compiled_sha256=hashlib.sha256(data).hexdigest(),native_next_padding_reads=0,source_clauses=clauses))
  sources.append(file)
 # Check all generated descriptors in both gfx owners, including static attack
 # and low-pressure overrides. Native records use one length +4bytes/cell;
 # aliases refer to those same records. No sourcelegal descriptor reaches the
 # following Bill stream or the bank34 ending audio Bits table.
 descriptors=[]
 for fname in['simon_metasprites.inc','bass_metasprites.inc','bass_special_poses.inc','ordinary_body_layout_art.inc','remaining_art.inc']:
  file=R/'build/bt-ready-menu-1031-v2/joint/src'/fname;text=file.read_text();sources.append(file);segment=None
  for line in text.splitlines():
   m=re.search(r'\.segment "([^"]+)"',line)
   if m:segment=m[1]
   m=re.match(r'^(\w+):\s*$',line)
   if not m or segment not in['SIMON_GFX','XG_BASS_GFX']:continue
   name=m[1];tail=text[text.index(line)+len(line):];head=re.match(r'\s*\.byte (\d+)\s*\n',tail)
   if not head:continue
   assert name in b['syms'],name
   count=int(head[1]);assert count%4==0 and count<256
   at=location(b,name);s=b['segs'][b['syms'][name]['seg']];a=int(s['ooffs'],0);z=a+int(s['size'],0)
   assert s['name'].strip('"')==segment and a<=at<at+count+1<=z
   assert raw[at]==count,(name,count,raw[at]);descriptors.append(dict(name=name,segment=segment,record_bytes=count+1,file_interval=[at,at+count+1]))
 assert len(descriptors)>100,len(descriptors)
 bill=R/'build/mario-tank-loader-1101-v4/Bill-tail-readers.json';report=json.loads(bill.read_text());assert report['passed']and report['current_ROM_sha256']==P.PIN
 b21=next(v for v in report['physical_banks']if v['bank']==21);assert b21['actual_reads_inside_proposal']==0 and b21['unique_read_addresses']==4096 and b21['actual_read_bounds']==[0xcf8a,0xdf8a]
 # Source selector bounds behind the two compact terminal tables are included,
 # not merely their table declarations.
 mac=R/'build/bt-ready-menu-1031-v2/joint/src/mac_roster.s';m=mac.read_text();assert 'cmp #MAC_ROSTER_VARIANTS\n bcc Done\n lda #MAC_ROSTER_MAC'in m;sources.append(mac)
 sound=R/'src/sound_test.s';s=sound.read_text();assert 'cpx #SoundTestHeroCount\n bcc HeroReady\n ldx #0'in s and 'ldx SoundTestHero\n' in s;sources.append(sound)
 special=R/'src/special_weapons.s';poseids=R/'src/expanded_poses.inc';armids=R/'src/bass_special_pose_ids.inc'
 assert 'XG_POSE_COUNT=84'in poseids.read_text()and'SS_BASS_ARM_CARRY_JUMP=102'in armids.read_text()
 sp=special.read_text();assert 'ldx #SS_BASS_ARM_CARRY_JUMP'in sp and 'inx                            ; Each special-arm pose has a Pharaoh pair.'in sp and 'lda SsBassBanks,x'in sp
 sources.extend([special,poseids,armids])
 q=dict(passed=True,ROM_sha256=stage['ROM_sha256'],inherited_native_ROM=P.PIN,code_and_terminal_table_caps=rows,generated_descriptor_count=len(descriptors),generated_descriptor_maxima={seg:max(v['file_interval'][1]for v in descriptors if v['segment']==seg)for seg in['SIMON_GFX','XG_BASS_GFX']},descriptor_aggregate_sha256=hashlib.sha256(json.dumps(descriptors,sort_keys=True).encode()).hexdigest(),Bill4_finite_CPU_cases=report['native_BillFlareLoadLate_cases'],Bill4_actual_C_window_bounds=b21['actual_read_bounds'],Bill4_witness_sha256=sha(bill),no_actual_copy_domain_intersects_proposed_PRG=True,PRG_granted=False,RAM_granted=False,native=False,installed=False,
  scope='Named terminal-owner code and finite inline data/descriptor caps, plus exact inherited7424-case Bill stream CPU witness. Bass valid ordinary poses0..83 and explicit arm pairs84..103; typed source-state contracts required. This is not an arbitrary corrupted-index or everyinstruction control-flow proof.',
  remaining_specific_gates=['Root must accept/grant the nine exact linker partitions; onlyCHR has a resource grant.','Install an identity/scene retirement hook which invalidates both Metal headers before a different selected-owner overlay can modify C2/C3. Both authentic headers are necessary but not a universal cross-owner mutation fence.','Actual Main constructor/update/camera/pickup/injury/death/scene/audio hooks and full12-byte Main stack/ISR/SMC boundary proof are still absent.','Original source8874/FF39 ports are not native implementations; GravityFire82 and original health/death/scene/audio/native combat remain excluded.'],bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'owning-link.json',O/'ownership.json',O/'candidate.nes',O/'candidate.dbg',bill]+sources})
 (O/'old-reader-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','code_and_terminal_table_caps']}))
if __name__=='__main__':main()
