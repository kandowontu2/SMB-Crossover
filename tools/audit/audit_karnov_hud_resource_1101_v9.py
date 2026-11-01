"""Independent current-image Karnov HUD cache/font and lifecycle audit."""
from pathlib import Path
import collections,hashlib,io,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from py65.devices.mpu6502 import MPU
from private_build_outputs_v1 import validate
import check_hogan_current_bounded_v1 as M
P=R/'build/karnov-host-resource-base-1101-v1'
O=R/'build/karnov-hud-resource-1101-v9'
PIN='1c073196b51b6aaaaac90d1bea925b68807fcaa3055665cf6dd0cc8f7858fe33'
sha=lambda b:hashlib.sha256(b).hexdigest()
save=lambda n,q:(O/n).write_text(json.dumps(q,indent=2)+'\n')

def pin():
 raw=(P/'candidate.nes').read_bytes();debug=(P/'candidate.dbg').read_text()
 assert sha(raw)==PIN
 b=scoped_load(P/'candidate.nes');assert b['raw']==raw
 images={}
 for g in b['segs'].values():
  if 'ooffs'not in g:continue
  path=Path(g['oname'].strip('"'))
  if path not in images:images[path]=raw if path==P/'candidate.nes'else path.read_bytes()
 path=R/'docs/qa/checkpoints/2026-11-01/karnov-options-nightly-v8/source.zip'
 packed=path.read_bytes();assert sha(packed)=='dedeb87c123ce5b575bcf16f0eb84bd52bffd6a1808174cfd4f25fe5856514ea'
 with zipfile.ZipFile(io.BytesIO(packed))as z:snapshot={n:z.read(n)for n in z.namelist()}
 gpath=R/'build/karnov-carrier-extension-1101-v7/carrier-grant.json'
 grant=json.loads(gpath.read_text());assert sha(gpath.read_bytes())=='0d43f5788bc22a1bcee80a91a123e4a1d29f7da22c4fabac116517ba322507aa'and grant['carrier_granted']
 compiled=json.loads((R/'build/karnov-carrier-final-1101-v6/compiled-writers.json').read_text())
 integrated=json.loads((R/'build/karnov-options-native-1101-v8/options-integrated.json').read_text());assert integrated['passed']and integrated['ROM_sha256']==PIN and integrated['owners']['unchanged_other_owners']
 # All later native/peripheral tests use raw and side images already in RAM.
 # Read-only old-owner source witnesses are independent of root's O build.
 sources={n:snapshot[n].decode()for n in snapshot if n.startswith(('host/kr-','host/karnov-options-','original-source/'))and n.endswith(('.inc','.s'))}
 for n in ['mmc5_expanded.s','mmc5.s','reset.s','remaining_audio.s','inventory.s','parodius_hud_queue.s']:
  path=R/'build/bt-ready-menu-1031-v2/joint/src'/n;sources['native/'+n]=path.read_text()
 command=json.loads((P/'terrain-kernel-build.json').read_text())['command'][:]
 command[command.index('-o')+1]=str(O/'kernel.o');command[1:1]=['-l',str(O/'kernel.lst')]
 guard=validate(command,O,cwd=R);done=subprocess.run(command,cwd=R,capture_output=True,text=True)
 assert done.returncode==0,done.stderr
 old=(P/'kr-kernel.o').read_bytes();new=(O/'kernel.o').read_bytes()
 assert old[:100]==new[:100]and old[105:]==new[105:]and len(old)==len(new),'Exact kernel object differs beyond OPT_DATETIME'
 save('kernel-assembly.json',dict(passed=True,command=command,guard=guard,returncode=done.returncode,object_exact_except_OPT_DATETIME=True,datetime_field=[100,105],original_object_sha256=sha(old),reproduced_object_sha256=sha(new)))
 pins=dict(ROM_sha256=PIN,debug_sha256=sha(debug.encode()),checkpoint_sha256=sha(packed),carrier_grant_sha256=sha(gpath.read_bytes()),images={str(p):sha(v)for p,v in images.items()},source_bindings={n:sha(v.encode())for n,v in sources.items()})
 save('pinned.json',pins)
 print(json.dumps(dict(pinned=True,ROM_sha256=PIN,no_further_live_O_reads=True)),flush=True)
 return b,debug,images,snapshot,grant,compiled,integrated,sources,pins

def compiled_font(b,images,compiled):
 segs={g['name'].strip('"'):g for g in b['segs'].values()};same=[];owned=[]
 for w in compiled['writers']:
  g=segs[w['segment']];at=int(g['ooffs'],0)+w['offset'];actual=images[Path(g['oname'].strip('"'))][at:at+len(bytes.fromhex(w['bytes']))]
  old=w['witnesses'][0]['path']
  if '/karnov-host-resource-base-'in old and Path(old).name.startswith('kr-'):owned.append(w['PC']);continue
  assert int(g['start'],0)+w['offset']==w['PC']and actual.hex()==w['bytes'],('Other font writer changed',w,actual.hex())
  same.append(dict(segment=w['segment'],PC=w['PC'],bytes=w['bytes']))
 assert len(same)==821 and len(owned)==24
 save('compiled-font-witness.json',dict(passed=True,ROM_sha256=PIN,unchanged_old_owner_writer_spans=same,Karnov_owned_spans=owned,indirect_domains_inherited=123,CF_indirect_domains_inherited=1,prior_maximum_named_page=1018,proposed_page=1023))
 return dict(passed=True,unchanged_old_owner_writers=821,Karnov_owned_writers=24,old_owner_grant_inherited=True,proposed_font=1023)

def cache_census(b,debug,images,sources):
 # The delivered debug intentionally omits full span/line tables. A private
 # exact-object reproduction provides source instruction offsets without a
 # second whole-cartridge relink/debug copy.
 listing=(O/'kernel.lst').read_text().splitlines();segs={g['name'].strip('"'):g for g in b['segs'].values()}
 segment=None;stack=[]
 bounded={0xc844:(0,7,'KC_SAVE+4,x; LDX7/DEX/BPL'),0xc859:(0,6,'KC_PLAYER,x; seven native proxy fields'),0xc869:(0,16,'KC_PARK,y; LDY0/CPY17')}
 memory_ops={'ADC','AND','ASL','BIT','CMP','CPX','CPY','DEC','EOR','INC','LDA','LDX','LDY','LSR','ORA','ROL','ROR','SBC','STA','STX','STY'}
 allmem=[];near=[];indirect=[];unclassified=[]
 for line_number,line in enumerate(listing,1):
  if len(line)<24 or not re.match(r'^[0-9A-F]{6}r ',line):continue
  text=line[24:].split(';',1)[0].strip()
  if text=='.pushseg':stack.append(segment);continue
  if text=='.popseg':segment=stack.pop();continue
  match=re.match(r'\.segment "([^"]+)"',text)
  if match:segment=match[1];continue
  prefix=line[:24].split();tokens=prefix[2:]
  if len(tokens)not in[2,3]or not re.fullmatch('[0-9A-F]{2}',tokens[0])or not all(re.fullmatch('[0-9A-F]{2}|rr',q)for q in tokens):continue
  size=len(tokens);op,mode=MPU.disassemble[int(tokens[0],16)]
  if op not in memory_ops or not re.match(r'(?:(?:[\w@]+|::[\w@]+)?:\s*)?'+op+r'\b',text,re.I):continue
  offset=int(prefix[0][:-1],16);g=segs[segment];at=int(g['ooffs'],0)+offset
  actual=images[Path(g['oname'].strip('"'))][at:at+size]
  assert all(t=='rr'or int(t,16)==v for t,v in zip(tokens,actual)),('Listing/current instruction mismatch',segment,offset,line,actual.hex())
  code=actual
  row=dict(segment=segment,PC=int(g['start'],0)+offset,bytes=code.hex(),operation=op,mode=mode,witnesses=[dict(path='kernel.lst',line=line_number,text=text,clause='\n'.join(listing[max(0,line_number-8):line_number+5]))])
  if mode in['inx','iny','izx','izy']:
   row['pointer']=code[1];indirect.append(row);continue
  if mode not in['abs','abx','aby']or size!=3:continue
  target=code[1]+256*code[2];indexed=mode in['abx','aby'];row['base']=target
  if 0xc000<=target<0xe000:allmem.append(row)
  if target<=0xc87f and target+(255 if indexed else 0)>=0xc87a:
   if indexed and target in bounded:
    lo,hi,why=bounded[target];row.update(index=[lo,hi],exact_extent=[target+lo,target+hi],proof=why)
    assert target+hi<0xc87a
   else:unclassified.append(row)
   near.append(row)
 assert not unclassified,unclassified
 assert any(q['base']==0xc869 for q in near),'Park loop must be covered'
 # Original state code never targets beyond C7FF. The four explicit indirect
 # producers are original inline dispatch (code pointer), metadata copy,
 # new-life C000..C7FF clear and cold whole-C2 clear before authentication.
 save('cache-compiled-consumers.json',dict(passed=True,ROM_sha256=PIN,proposed_interval=[0xc87a,0xc880],actual_direct_C2_memory_sites=len(allmem),indexed_near_consumers=near,indirect_sites=indirect,unclassified=[],scope='Compiled instruction spans witnessed by exact current Karnov source leaves; source rows and static domains supplement aggregate actual-Main sentinel checks.'))
 return dict(passed=True,direct_C2_memory_sites=len(allmem),bounded_near_consumers=len(near),indirect_sites=len(indirect),unclassified=[])

class Bus(M.Bus):
 def __init__(self,b):self.cache_reads=[];self.cache_writes=[];self.phase='init';super().__init__(b)
 def __getitem__(self,i):
  if isinstance(i,int)and i>=0x8000 and self.rawtags[(i-0x8000)//8192]==2 and 0x87a<=i&8191<0x880:self.cache_reads.append((self.phase,i))
  return super().__getitem__(i)
 def __setitem__(self,i,v):
  if isinstance(i,int)and i>=0x8000 and self.rawtags[(i-0x8000)//8192]==2 and 0x87a<=i&8191<0x880:self.cache_writes.append((self.phase,i,v&255))
  super().__setitem__(i,v)

def interrupt(m,kind):
 c=NesMPU(memory=m,pc=0x5b00);c.sp=224;c.p=0x30;getattr(c,kind)()
 for _ in range(200000):
  if(c.pc,c.sp)==(0x5b00,224):return
  assert m[c.pc]!=0,(kind,hex(c.pc));c.step()
 raise AssertionError((kind,'bounded return'))

def run_cpu(b):
 M.Bus=Bus
 m=M.fresh(b)
 M.put(m,SelectedCharacter=34,FmAlts=1,OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255,FamilyMainCommit=1)
 m.phase='cold';assert M.invoke(m,'KrLoad')['P']&1
 assert len(m.cache_writes)==6 and len(m.cache_reads)==6
 sentinel=bytes([91,31,222,57,145,204]);m.ram[2][0x87a:0x880]=sentinel;m.cache_reads.clear();m.cache_writes.clear()
 def ram(name):
  m.raw_page(1,3);m.raw_page(2,2);M.put(m,CurrentBank=3,CurrentBankC=2)
  c=NesMPU(memory=m,pc=address(b,name));c.p=0x31;c.sp=224;c.stPushWord(0x5aff)
  for _ in range(100000):
   if c.pc==0x5b00:break
   assert m[c.pc]!=0,(name,hex(c.pc));c.step()
  else:raise AssertionError((name,'bounded'))
  assert c.sp==224
 m.phase='construct';ram('KrConstruct');assert bytes(m.ram[2][0x87a:0x880])==sentinel
 cases=0
 for i in range(64):
  m.phase='Main';keys=[0,1,128,192,64,32,68,12][i%8]
  M.put(m,OperMode=1,OperMode_Task=3,DisableScreenFlag=0,Mirror_PPUMASK=30,GameEngineSubroutine=8,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255,CheatInvincible=1)
  M.invoke(m,'GameLoop');M.consume(m);interrupt(m,'irq');cases+=1
  assert bytes(m.ram[2][0x87a:0x880])==sentinel
 assert not m.cache_reads and not m.cache_writes
 # Positive mapping proof uses only publisher data fields, no executable patch.
 font=[]
 for wide in [0,1]:
  for active in [0,0xe9]:
   m.phase='font'
   M.put(m,DisableScreenFlag=0,NmiDisable=255,InvHudActive=active,InvHudPhysical=255,X5HudChrUpper=3,X5WideChrActive=wide,ReloadCHRBank=1)
   M.invoke(m,'X5PublishChr');published=m.chr_latches[8]
   if active:assert published==(1023 if wide else 255)
   M.invoke(m,'RemainingAudioBegin');audio=m.chr_latches[8]
   if active:assert audio==1023 and m.upper==0
   interrupt(m,'irq');world=m.chr_latches[8]
   assert world!=1023 and m.upper==0
   font.append(dict(wide=wide,active=active,published=published,NMI_audio_restored=audio,IRQ_world_restored=world))
 # Current retirement negative control: it does not clear a newly proposed
 # owner. This is a real integration gate, not an implicit cache-font grant.
 M.put(m,InvHudActive=0xe9,InvHudPhysical=255,X5HudChrUpper=3,X5WideChrActive=1,ReloadCHRBank=0)
 m.phase='retire';M.invoke(m,'KrRetire')
 assert M.get(m,'InvHudActive')==0xe9
 return dict(passed=True,cold_clear_exact6B=True,new_life_construct_sentinel_preserved=True,Main_normal_NMI_IRQ_cases=cases,ungranted_cache_reads=len(m.cache_reads),ungranted_cache_writes=len(m.cache_writes),font_field_fixtures=font,current_retire_leaves_E9=True,no_executable_overlay=True,native_emulator=False)

def main():
 O.mkdir(exist_ok=True)
 b,debug,images,snapshot,grant,compiled,integrated,sources,pins=pin()
 a=compiled_font(b,images,compiled);c=cache_census(b,debug,images,sources);cpu=run_cpu(b)
 resident=address(b,'KrResidentEnd')-address(b,'KrResidentBegin');limit=address(b,'KrResidentLimit')-address(b,'KrResidentBegin')
 assert resident==2430 and limit==2432
 report=dict(passed=True,base_ROM_sha256=PIN,old_owner_font_resource_granted=True,conditional_cache6B_granted=True,full_HUD_lifecycle_granted=False,proposed_font_page=1023,proposed_cache=[0xc87a,0xc880],compiled_font=a,cache=c,CPU=cpu,
  actual_context_end=0xc869+17,cache_condition='Authenticated Karnov C2 only. Cold wholeC2 zero before revised cookies; no global field allocation and no reads after retirement. No foreign conditional C2 owner may retain this HUD.',
  publication_conditions=['Use X5WideChrActive1, InvHudPhysical255, X5HudChrUpper3, publish InvHudActiveE9 last while NmiDisable is negative. Native legacy publisher ignores the upper3 override and maps255; wide mode is mandatory.','Font1023 must preserve every native HUD glyph used outside new icon cells30..3B/plus3C. Native RemainingAudioBegin restores HUD only when screen enabled and active!=0; IRQ31 restores ordinary world font and clears upper latch.','Add ROM-owned E9 cancellation before cache retirement and at every scene/title seam that can retain stale derived HUD state. Do not invoke C2 KrHudCancel after invalidating its cookies.','Revised cookie must bind final HUD code/font data; actual owning Main/pause/death/menu/IRQ cuts and native visuals remain qualification steps.'],
  funding=dict(current_resident_bytes=resident,resident_limit=limit,free_bytes=limit-resident,safe_inline_ROM_E9_cancel_bytes=17,minimum_additional_funding=15,standalone_cancel_with_JSR_bytes=21),
  limits=['Source/compiled/actual CPU peripheral model, no native emulator or installed candidate. Existing1c retirement demonstrably leaves proposed E9 active; do not treat old-owner font grant as final HUD admission.'],pins=pins)
 save('resource-grant.json',report);print(json.dumps({k:v for k,v in report.items()if k in['passed','base_ROM_sha256','old_owner_font_resource_granted','conditional_cache6B_granted','full_HUD_lifecycle_granted','funding']}))

if __name__=='__main__':main()
