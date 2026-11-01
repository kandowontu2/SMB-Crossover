"""Exact frozen-input CHR ownership audit; no live integration build reads."""
from pathlib import Path
import ast,hashlib,itertools,json,re,sys,zipfile

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as Menu

O=R/'build/karnov-carrier-closure-1101-v4'
F=R/'build/doki-current-component-1101-v1'
PACKET=R/'docs/qa/checkpoints/2026-11-01/karnov-next-integration-v3/carrier-source-and-proof.zip'
ARCHIVE=R/'build/_recovery/legacy-sources-2026-10-31.zip'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

class FrozenSources:
 def __init__(self,inventory):
  self.refs={q['path']:q for q in inventory['source_refs']}
  self.cache={};self.used={};self.z=zipfile.ZipFile(ARCHIVE)
  self.idx={q['path']:q for q in json.loads(self.z.read('index.json'))}
 def read(self,p):
  p=Path(p);key=p.as_posix()
  if key in self.cache:return self.cache[key]
  ref=self.refs.get(key)
  if ref is None:
   # Frozen receipts use Windows absolute paths; normalize their separators.
   ref=next((q for k,q in self.refs.items()if Path(k)==p),None)
  assert ref,('Not an exact declared frozen source',key)
  expected=ref['sha256'];relative=p.relative_to(R/'build').as_posix()if p.is_relative_to(R/'build')else None
  # Never inspect root's active output while it is rebuilding. Its original
  # Karnov allocation is unchanged by this audit and not an other-owner input.
  forbidden=p.is_relative_to(R/'build/karnov-host-resource-base-1101-v1')
  row=self.idx.get(relative)
  if row and row['sha256']==expected:
   data=self.z.read('objects/'+expected);origin='indexed-recovery'
  elif not forbidden and p.is_file():
   data=p.read_bytes();origin='live-hash-verified'
  else:raise AssertionError(('Exact source unavailable without reading active O',key,expected))
  assert hashlib.sha256(data).hexdigest()==expected,(key,'Frozen source hash changed')
  assert len(data)==ref['bytes']
  self.cache[key]=data.decode('utf-8',errors='strict')
  self.used[key]=dict(sha256=expected,bytes=len(data),origin=origin)
  return self.cache[key]
 def build(self,p):return self.read(R/'build'/p)

def invoke(m,name,**kw):return Menu.invoke(m,name,**kw)
def put(m,**kw):Menu.put(m,**kw)

def arthur(b,s):
 loader=s.build('arthur-physical-clock-v1/joint/arthur/cache-loader.s')
 wrap=s.build('arthur-physical-clock-v1/joint/arthur/cache-wrapper.s')
 runtime=s.build('arthur-physical-clock-v1/joint/arthur/cache-runtime.s')
 assert 'cmp #9\n jcs VerifyFail\n clc\n adc #100'in loader
 assert 'CommonOnly:lda #255'in loader
 assert 'cmp #255\n  beq NoBodyPublish'in runtime or 'cmp #255\n beq NoBodyPublish'in runtime
 assert 'ArCacheTablesLow:.byte <$c000,<$c094,<$c128'in runtime
 m=Menu.Bus(b)
 put(m,SelectedCharacter=32,OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,
     Mirror_PPUCTRL=160,NmiDisable=255,ArHostReady=167,ArHostOldPage=0)
 m.ppuctrl=160
 cold=invoke(m,'ArCacheEnsure')
 assert cold['P']&1 and m.ram[2][0x1fe0]==167
 # Enumerate actual original forced-blank output, not a host-generated table.
 views=[];empty=[];pages=set();descriptors=set()
 for mode,key in itertools.product(range(3),range(74)):
  at=mode*148+key*2;p=m.ram[2][at]+256*m.ram[2][at+1]
  if not p:empty.append([mode,key]);continue
  assert 0xc1bc<=p<0xd7f2,(mode,key,hex(p))
  count,page=m.ram[2][p-0xc000:p-0xc000+2]
  assert 1<=count<=11 and page in list(range(100,109))+[255]
  assert p+2+count*4<=0xd7f2
  views.append([mode,key,p,count,page]);descriptors.add(p)
  if page!=255:pages.add(768+page)
 assert len(views)==201 and len(empty)==21
 reads=m.ppu_reads;warm=invoke(m,'ArCacheEnsure')
 assert warm['P']&1 and m.ppu_reads==reads
 # Execute each cached descriptor and both original fast/clipped paths. The
 # common-only records retain whatever previous body page the caller owns.
 pc=address(b,'ArCacheEmit');render_cases=0;physical=set();maxcycles=0
 for mode,key,p,count,page in views:
  for x,y,high,prefix in [(104,200,0,0),(0,0,0,248),(255,239,1,252)]:
   m.raw_page(2,2);put(m,CurrentBankC=2,ArHostOldPage=mode,ArDrawRecord=key,
    ArDrawIndex=0,ArTempHi=high,ArDrawX=x,ArDrawY=y,CurrentOAMOffset=prefix,
    GuestOamRotationActive=0,RgOamRotation=0)
   # A safe known prior body is retained for common-only source descriptors.
   m[address(b,'CurrentCHRBank')]=100;m[address(b,'X5ChrMode')]=131
   c=NesMPU(memory=m,pc=pc);c.sp=224;c.stPushWord(0x5aff)
   for _ in range(5000):
    if c.pc==0x5b00:break
    assert m[c.pc]!=0,('Ar original emitter BRK',hex(c.pc));c.step()
   else:raise AssertionError('Ar original emitter bound')
   assert c.sp==224
   value=m[address(b,'CurrentCHRBank')];modebyte=m[address(b,'X5ChrMode')]
   assert value==(100 if page==255 else page)and modebyte==131
   physical.add(768+value);render_cases+=1;maxcycles=max(maxcycles,c.processorCycles)
 # Original common6/7 selection never comes from a descriptor or scratch.
 assert all(q in wrap for q in ['lda #111','WB6:lda #109','lda #112','WB7:lda #110'])
 physical.update(range(877,881))
 return dict(closed=True,source_views=len(views),empty_keys=len(empty),unique_descriptor_addresses=len(descriptors),
  descriptor_pages=sorted(pages),all_body_common_pages=sorted(physical),
  actual_cache_sha256=hashlib.sha256(m.ram[2][:0x17f2]).hexdigest(),
  actual_forced_blank_loader=cold,warm_check=warm,buffered_PPU_reads=reads,
  original_fast_and_clipped_emitter_cases=render_cases,maximum_emitter_cycles=maxcycles,
  fallback_contract='Original loader accepts canonical header page0..8 or15 only; stores100..108 or255.255 is explicitly no-publish. Fast and clipped paths both read the same authenticated descriptor header before geometry branching. Invalid/missing cache fails closed; no alternative graphics loader is invented.',
  records_sha256=hashlib.sha256(json.dumps(views,separators=(',',':')).encode()).hexdigest())

def source_inventory(s,previous):
 targets=r'(?:CurrentCHRBank|AreaChrBank|PlayerChrBank|EnemyChrBank|SmChrBank|X5ChrMode|X5SpecialChrUpper|X5HudChrUpper|SsChrPhysical|InvHudPhysical|SsChrActive|InvHudActive)'
 hits=[];unread=[]
 for ref in previous['source_refs']:
  p=Path(ref['path'])
  if p.is_relative_to(R/'build/karnov-host-resource-base-1101-v1'):
   unread.append(dict(path=p.as_posix(),reason='Root active Karnov-only source; frozen original site clauses retained by previous checkpoint.'))
   continue
  source=s.read(p);lines=source.splitlines()
  for i,line in enumerate(lines):
   bare=line.split(';',1)[0].strip()
   if re.search(r'\b(?:sta|stx|sty|inc|dec|asl|lsr|rol|ror)\s+'+targets+r'\b',bare,re.I):
    hits.append(dict(path=p.as_posix(),line=i+1,instruction=bare,clause='\n'.join(lines[max(0,i-10):min(len(lines),i+4)])))
 return dict(sites=hits,unread_active_Karnov_sources=unread,source_units=len(s.used))

def overrides(b,s,inventory):
 # Stronger than scene sampling: both independent override upper-bit fields
 # have the inductive domain0..2. Any retained low byte then stays below768,
 # irrespective of active flag, scene, death/pause or mid-update low writes.
 core=s.build('bt-ready-menu-1031-v2/joint/src/mmc5_expanded.s')
 equipment=s.build('bt-ready-menu-1031-v2/joint/src/tmnt_equipment_draw.s')
 assert re.search(r'lda #\.hibyte\(628\)\s*\n\s*sta X5SpecialChrUpper',equipment)
 upper=[q for q in inventory['sites']if re.search(r'\b(?:sta|stx|sty|inc|dec|asl|lsr|rol|ror)\s+X5SpecialChrUpper\b',q['instruction'],re.I)]
 assert [(Path(q['path']).name,q['line'])for q in upper]==[('mmc5_expanded.s',25),('mmc5_expanded.s',277),('mmc5_expanded.s',292),('tmnt_equipment_draw.s',13)]
 # Exact callsite inventory. All arguments into the only generic upper-bit
 # setter are constant upper1/2, even where the low byte is data-dependent.
 calls=[]
 for p,text in s.cache.items():
  lines=text.splitlines()
  for i,line in enumerate(lines):
   bare=line.split(';',1)[0].strip()
   if re.search(r'\b(?:farcall|jsr|jmp)\s+X5SetSpecialChr\b',bare,re.I):
    recent=[q.split(';',1)[0].strip()for q in lines[max(0,i-7):i]]
    ldx=next((q for q in reversed(recent)if q.lower().startswith('ldx ')),None)
    calls.append(dict(path=p,line=i+1,ldx=ldx))
 expected={'darkwing_weapons.s':'ldx #>DW_WEAPON_CHR','zelda2_link_draw_world.s':'ldx #.hibyte(335)',
  'chip_dale_render.s':'ldx #.hibyte(CdWorldChr)','mike_jones_render.s':'ldx #>(JN_FIRST_CHR+2)',
  'cv3_draw.s':'ldx #>518','little_mac_render.s':'ldx #>704','smb3_mario_world.s':'ldx #.hibyte(544)',
  'mac_roster.s':'ldx #>704'}
 assert len(calls)==len(expected)
 for q in calls:assert q['ldx']==expected[Path(q['path']).name],q
 args=[address(b,'DW_WEAPON_CHR')>>8,335>>8,address(b,'CdWorldChr')>>8,
  (address(b,'JN_FIRST_CHR')+2)>>8,518>>8,704>>8,544>>8,704>>8]
 assert set(args)=={1,2}
 # No hidden numeric absolute alias of either upper field appears in these
 # exact declared sources. The ABI declarations themselves are harmless.
 literals=[]
 for p,text in s.cache.items():
  for i,line in enumerate(text.splitlines()):
   bare=line.split(';',1)[0]
   if re.search(r'\$73e[c-d]\b',bare,re.I):
    assert re.fullmatch(r'\s*X5(?:Special|Hud)ChrUpper\s*=\s*\$73e[c-d]\s*',bare,re.I),(p,i+1,bare)
    literals.append(dict(path=p,line=i+1,declaration=bare.strip()))
 hud=[q for q in inventory['sites']if re.search(r'\sX5HudChrUpper\b',q['instruction'],re.I)]
 hud_cases=[]
 for q in hud:
  name=Path(q['path']).name;line=q['line'];clause=q['clause']
  if name=='mmc5_expanded.s':assert line in[26,293];rule='zeroed by cold/clear owner'
  elif name=='vic_render.s':assert line in[249,350] and'lda #>394'in clause;rule='upper1 constant'
  elif name=='parodius_render.s':assert line==471 and'lda #.hibyte(396)'in clause;rule='upper1 constant'
  elif name=='smb3_mario_world.s':assert line==130 and'lda #>545'in clause;rule='upper2 constant'
  elif name=='parodius_hud_queue.s':
   if line in[22,176,337]:assert re.search(r'lda #(?:\.hibyte\(396\)|1)\s*\n\s*sta X5HudChrUpper',clause);rule='upper1 constant'
   elif line in[166,189]:assert 'asl\n asl\n ora #$81\n sta X5HudChrUpper'in clause;rule='metadata upper bits, low2 exactly1 for every input byte'
   else:assert 'and #3\n sta X5HudChrUpper'in clause;rule='AND3 retains inductive0..2 domain'
  else:raise AssertionError(('Unclosed HUD upper writer',q))
  hud_cases.append(dict(path=q['path'],line=line,rule=rule))
 assert len(hud_cases)==18
 # Execute the genuine publisher for every possible low byte with every
 # reachable upper2-bit value. This proves stale lows cannot reach1019/1020.
 m=Menu.Bus(b);put(m,X5WideChrActive=1,ReloadCHRBank=1,SelectedCharacter=0,MarioVariant=0)
 count=0
 for upper,low in itertools.product(range(3),range(256)):
  put(m,SsChrPhysical=low,X5SpecialChrUpper=upper,SsChrActive=1,
   InvHudPhysical=low,X5HudChrUpper=upper,InvHudActive=1)
  invoke(m,'X5PublishChr')
  assert m.chr_latches[4]==m.chr_latches[8]==256*upper+low
  assert m.chr_latches[4]<768 and not set(m.chr_latches)&{1019,1020}
  count+=1
 for upper,low in itertools.product([1,2],range(256)):
  invoke(m,'X5SetSpecialChr',a=low,x=upper)
  assert Menu.get(m,'X5SpecialChrUpper')==upper and Menu.get(m,'SsChrPhysical')==low
 return dict(closed=True,upper2_domain=[0,1,2],all_low_bytes_allowed=True,
  scene_death_pause_stale_low_safe=True,numeric_alias_declarations=literals,
  special_upper_writers=upper,special_setter_callers=calls,special_legal_upper_arguments=args,
  HUD_upper_writers=hud_cases,actual_publisher_low_upper_cases=count,
  actual_special_setter_cases=512,
  scope='Explicit typed override producers/cold-clear owners only; generic indirect WRAM corruption and retained ordinary-window shadows are not qualified by this invariant.')

def physical_calls(b,s):
 calls=[]
 for p,text in s.cache.items():
  lines=text.splitlines()
  for i,line in enumerate(lines):
   bare=line.split(';',1)[0].strip()
   if not re.search(r'\b(?:farcall|\w*far|jsr|jmp)\s+X5SetPhysicalChr\b',bare,re.I):continue
   recent=[q.split(';',1)[0].strip()for q in lines[max(0,i-9):i]]
   ldx=next((q for q in reversed(recent)if q.lower().startswith('ldx ')),None)
   calls.append(dict(path=p,line=i+1,instruction=bare,ldx=ldx,clause='\n'.join(lines[max(0,i-9):i+1])))
 def expression(t):
  n=ast.parse(t,mode='eval').body
  def val(n):
   if isinstance(n,ast.Constant)and isinstance(n.value,int):return n.value
   if isinstance(n,ast.Name):return address(b,n.id)
   assert isinstance(n,ast.BinOp)and isinstance(n.op,(ast.Add,ast.Sub)),ast.dump(n)
   return val(n.left)+val(n.right)*(1 if isinstance(n.op,ast.Add)else -1)
  return val(n)
 def byte_table(n,source):
  match=re.search(r'^'+re.escape(n)+r':\s*\.byte\s+([0-9,]+)',source,re.M);assert match,n
  values=bytes(map(int,match[1].split(',')));at=location(b,n)
  assert b['raw'][at:at+len(values)]==values,(n,'Actual compiled values differ')
  return values
 cv=s.build('bt-ready-menu-1031-v2/joint/src/cv3_art.inc')
 cv_domains={n:sorted(set(byte_table(n,cv)))for n in['Cv3V'+str(v)+'Chr'+side+'Upper'for v in range(1,4)for side in['R','L']]}
 assert all(set(v)<={1,2}for v in cv_domains.values())
 roll=byte_table('RlPoolChrHi',s.build('bt-ready-menu-1031-v2/joint/src/roll_art.inc'));assert set(roll)=={1}and len(roll)==6
 high3=[]
 for q in calls:
  name=Path(q['path']).name;ldx=q['ldx'];domain=None
  if ldx.startswith('ldx #>'):domain=[expression(ldx[6:])>>8]
  elif ldx.startswith('ldx #.hibyte('):domain=[expression(ldx[13:-1])>>8]
  elif re.fullmatch(r'ldx #[0-9]+',ldx):domain=[int(ldx[5:])]
  elif ldx=='ldx Cv3BodyChrUpper':domain=sorted({x for a in cv_domains.values()for x in a})
  elif ldx=='ldx RlPoolChrHi,y':domain=[1]
  elif ldx.startswith('ldx PnPool'):
   table=ldx[4:-2];at=location(b,table);domain=sorted(set(b['raw'][at:at+18]));assert domain==[3]
  elif ldx=='ldx M3SpritePageHi':domain=[2,3]
  else:raise AssertionError(('Unclassified physical setter argument',q))
  if name in['final_fantasy_render.s','preview.s']:
   assert domain==[2]and' inx'in q['clause'];domain=[2,3]
  if name=='runtime.s':domain=[1,2] # genuine WfMapBodyPage three branches
  q['upper_domain']=domain
  if max(domain)<=2:q['argument_bound']='Any low byte remains below768.'
  else:
   if name=='cache-wrapper.s':owner='Arthur authenticated headers/common windows868..880'
   elif name in['parodius_render.s','parodius_death.s']:owner='Parodius actual18-pool tables/death constants832..867'
   elif name=='smb3_mario_render.s':owner='SMB3Plus3584 selector closure969..1018; legacy growth pages useupper2'
   elif name=='gimmick_render.s':owner='Gimmick fixed816/818'
   elif name=='donkey_kong_render.s':owner='Donkey Kong actual9-pose table820..823'
   elif name in['final_fantasy_render.s','preview.s']:owner='Final Fantasy AND31 + carry arithmetic756..787'
   elif name in['host.s','cold.s']:owner='Bowser actual9-pose table/cold constants824..826'
   elif name=='api.s':owner='Battletoads fixed915 preview/typed pose pages915..918'
   else:raise AssertionError(('Unclosed high3 physical caller',q))
   q['argument_bound']=owner;high3.append(dict(path=q['path'],line=q['line'],owner=owner))
 assert len(calls)==43
 return dict(callers=calls,declared_arguments_classified=True,closed=False,
  CV3_actual_upper_table_domains=cv_domains,Roll_actual6_pool_upper_domain=[1],
  high3_calls=high3,
  scope='Exact direct/macro call inventory and legal argument owners. Other-owner typed ranges retained from frozen v3. This does not itself prove ordinary retained-shadow scene/IRQ ownership or hidden indirect/numeric writers.')

def ff_body_pairing(b,s):
 source=s.build('current-character-composition-v2/joint/ff-render.s')
 native=s.build('bt-ready-menu-1031-v2/joint/src/metasprite_engine.s')
 reset=s.build('bt-ready-menu-1031-v2/joint/src/reset.s')
 game=s.build('bt-ready-menu-1031-v2/joint/src/game.s')
 assert 'jsr FfHostGraphics\n lda ObjectMetasprite\n beq Return\n jsr FfPublishChunk'in source
 assert 'PublishOnly:\n lda #0\n sta FfTemp2\n jmp FfPublishChunk'in source
 assert 'lda SelectedCharacter\n bne Skip'in game
 assert 'jsr MaaLagChrGuard\n    bcs KeepLagChr'in reset
 assert 'sta PlayerChrBank\n        inc ReloadCHRBank'in native
 m=Menu.Bus(b)
 put(m,SelectedCharacter=22,OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,
  Mirror_PPUCTRL=160,NmiDisable=255,FfVariant=0,PlayerFacingDir=1,
  PlayerOutlinesOff=1,GameEngineSubroutine=8,CurrentOAMOffset=0)
 m.ppuctrl=160
 loaded=invoke(m,'FwLoad');assert loaded['P']&1 and m.ram[3][0x1fe0]==167
 def ram(name,a=0,x=0,y=0):
  m.raw_page(1,3);put(m,CurrentBank=3)
  c=NesMPU(memory=m,pc=address(b,name));c.a=a;c.x=x;c.y=y;c.sp=224;c.stPushWord(0x5aff)
  for _ in range(50000):
   if c.pc==0x5b00:break
   assert m[c.pc]!=0,('Real FF RAM BRK',name,hex(c.pc),m.rawtags);c.step()
  else:raise AssertionError(('Real FF RAM bound',name,hex(c.pc)))
  assert c.sp==224
  return c
 native_at=location(b,'PlayerBankReady');prefix=b['raw'][native_at:native_at+11]
 assert prefix[0]==0xcd and prefix[3]==0xf0 and prefix[5]==0x8d and prefix[8]==0xee
 pages=set();cases=0;danger_lows=0
 for variant,tier,pose,face in itertools.product(range(4),range(3),range(1,19),[1,2]):
  put(m,FfVariant=variant,FfPower=tier,PlayerFacingDir=face,FfReady=247)
  ram('FfSetPose',a=pose)
  assert Menu.get(m,'ObjectMetasprite')
  page=756+Menu.get(m,'FfRenderPage');assert 756<=page<=787
  # Genuine source publisher then the exact native alias-store prefix.
  ram('FfPublishChunk')
  m.raw_page(1,((native_at-16)//8192)|128)
  put(m,CurrentBank=m.rawtags[1]);c=NesMPU(memory=m,pc=address(b,'PlayerBankReady'))
  c.a=Menu.get(m,'SmChrBank');c.sp=224
  while c.pc!=address(b,'PlayerBankReady')+11:
   assert address(b,'PlayerBankReady')<=c.pc<address(b,'PlayerBankReady')+11
   c.step()
  low=Menu.get(m,'CurrentCHRBank');mode=Menu.get(m,'X5ChrMode')
  assert low+256*(mode&3)==page,(variant,tier,pose,face,low,mode,page)
  invoke(m,'X5PublishChr');assert m.chr_latches[0]==page
  assert not set(m.chr_latches)&{1019,1020}
  pages.add(page);cases+=1;danger_lows+=int(low in[251,252])
 return dict(passed=True,closed_for_declared_body_pairing=True,
  actual_forced_blank_loader=loaded,buffered_PPU_reads=m.ppu_reads,
  class_tier_pose_facing_cases=cases,pages=sorted(pages),low251_252_cases=danger_lows,
  native_PlayerBankReady_prefix_bytes=list(prefix),
  lag_guard='SelectedCharacter22 always returns Cset from actual MaaLagChrGuard; active lag NMIs skip BankSwitchCHR, so partial low/high publication cannot be committed by that path.',
  limits=['This closes declared FF body0 pairing plus the source restore/PublishOnly owners. It is not an all-Main scene/IRQ or all ordinary-window ownership proof.'])

def main():
 O.mkdir(exist_ok=True)
 assert sha(F/'candidate.nes')=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
 assert sha(PACKET)=='e5f8074e35b2dcdd1388f99aa88408a8e5ed45c7d4bb1fd3774cc230bfc98b8c'
 with zipfile.ZipFile(PACKET)as z:
  previous=json.loads(z.read('build/karnov-combat-carrier-design-1101-v3/other-consumer-closure.json'))
 assert not previous['carrier_granted']
 s=FrozenSources(previous);b=scoped_load(F/'candidate.nes')
 result=dict(passed=False,audit_only=True,carrier_granted=False,proposed_pages=[1019,1020],
  source_ROM_sha256=sha(F/'candidate.nes'),frozen_inventory_ROM_sha256=previous['current_ROM_sha256'])
 result['Arthur']=arthur(b,s)
 result['retained_shadow_writer_inventory']=source_inventory(s,previous)
 result['special_and_HUD_overrides']=overrides(b,s,result['retained_shadow_writer_inventory'])
 result['physical_publisher_calls']=physical_calls(b,s)
 result['FF_body_pairing']=ff_body_pairing(b,s)
 result['passed']=True
 result['remaining_gates']=[
  dict(owner='Ordinary CurrentCHRBank/X5ChrMode windows0..11',
   sources=['build/bt-ready-menu-1031-v2/joint/src/mmc5_expanded.s:X5WidePublication/X5Direct0..11',
    'build/bt-ready-menu-1031-v2/joint/src/metasprite_engine.s:PlayerBankReady',
    'current host character_select.s:QueueSelection/FmNativePrepare'],
   next='Bind the202 named mutation sites and43 typed caller argument owners to every actual executable (including private copied images/indirect aliases), then complete the inductive retained-window ownership proof across character/alternate admission, lives, scene resets and Zelda2 pause restore. An unqualified arbitrary upper3+low251/252 is1019/1020; no generic API clamp exists.'),
  dict(owner='Actual Main/interrupt commit paths',
   sources=['build/bt-ready-menu-1031-v2/joint/src/reset.s:NonMaskableInterrupt/BankSwitchCHR',
    'build/bt-ready-menu-1031-v2/joint/src/game.s:MaaLagChrGuard',
    'build/current-character-composition-v2/joint/ff-render.s:FfHostDrawShots'],
   next='Extend the432 declared FF body0-pairing checks to actual Main scene/cold/death/pause entry and every relevant normal/lag NMI/IRQ publication seam, including all ordinary windows and later PlayerBankReady writes. The source lag guard and source early-shot restoration narrow this gate; they are not an all-Main proof.'),
  dict(owner='Remaining direct high3 forced-blank map owners',
   sources=['build/current-character-quick-cold-v12/joint/quick/loader.s:QwMapPage',
    'build/contra-force-p1-coherent-cart-v2/joint/loader.s:FwMapPage',
    'build/bowser-current64-v3/joint/bowser/copy.s:BwMapPage',
    'build/bt-cf-coherent-source-1031-v1/joint/bt/loader.s:BtMapPage',
    'build/contra-force-projectile-contact-1031-v3/joint/cf-loader.s:CfMapSourcePage'],
   next='Prove the actual loop-index/control-flow domains and map arithmetic, including restore paths: Quick source index0..8→884..892; FF destination C0/C4/..DC→893..900; Bowser destination C0/C4/..DC→927..934; BT destination C0/C4/..DC→919..926; CF index0..23→935..958. Arthur actual881..883 and FF actual893..900 were exercised by the loaders in this receipt; the remaining bounds are next tasks, not grants.'),
  dict(owner='Current integrated image binding',sources=['Root-owned current host source/ROM'],
   next='Root must compare the final candidate against these exact frozen graphics and source owners, including21 deliberately unread active Karnov host source units. This audit never reads the mutable host output and never grants1019/1020 from zero fill or prior menu sweeps.')]
 result['sources']=s.used
 result['limits']=['Carrier remains ungranted. Completed Arthur/override/FF-pairing components do not establish the remaining ordinary-window or complete executable ownership gates.',
  'All fixtures are source CPU scenes using exact old frozen85 executable plus the exact indexed/current-hash source inventory bound to e8. No native emulator, controller-earned route, final-current Main stack or new ROM qualification.',
  'No live root integration build, dependency tree, donor ROM copy, per-frame output or capture was created.']
 result['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),F/'candidate.nes',F/'candidate.dbg',PACKET,R/'tools/audit/check_hogan_current_bounded_v1.py',R/'tools/audit/arthur_cache_host_controls_v1.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py']}
 save(O/'closure.json',result)
 print(json.dumps(dict(passed=True,carrier_granted=False,Arthur=result['Arthur'],shadow_sites=len(result['retained_shadow_writer_inventory']['sites']),source_units=len(s.used))))

if __name__=='__main__':main()
