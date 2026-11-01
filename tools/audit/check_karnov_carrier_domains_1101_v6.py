"""Bounded current-image bank-domain checks; aggregate CPU evidence, no emulator."""
from pathlib import Path
import argparse,collections,hashlib,json,re,sys,time,traceback,zipfile,itertools
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from audit_karnov_carrier_final_1101_v6 import O,P,PIN,sha,save
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as Menu

def cf():
 C=R/'build/contra-force-projectile-contact-1031-v3';K=C/'kernel';b=dict(syms={},segs={})
 for line in (K/'runtime.dbg').read_text().splitlines():
  kind,_,tail=line.partition('\t');z=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',tail))
  if kind=='seg':b['segs'][z['id']]=z
  elif kind=='sym'and'val'in z:b['syms'][z['name'].strip('"')]=z
 stream=(C/'joint/cf-stream.bin').read_bytes();raw=(O/'candidate.nes').read_bytes()
 assert sha(O/'candidate.nes')==PIN
 assert stream==raw[1048592+935*1024:1048592+959*1024]
 images=[]
 for i in [1,2,3]:
  image=bytearray((K/f'ram{i}.bin').read_bytes());image.extend(bytes(8192-len(image)))
  if i in[2,3]:image[8160:]=bytes(32)
  images.append(image)
 assert b''.join(images)==stream
 # Original full link metadata describes every executable source instruction,
 # including its resolved WRAM image. No relink/recovery/tree copy is needed.
 spans={};files={};lines=[]
 for line in (K/'runtime.dbg').read_text().splitlines():
  kind,_,tail=line.partition('\t');q=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',tail))
  if kind=='span':spans[q['id']]=q
  elif kind=='file':files[q['id']]=q
  elif kind=='line'and'span'in q:lines.append(q)
 ins={};segs=[];sources={}
 for key,s in b['segs'].items():
  if 'ooffs'not in s:continue
  name=Path(s['oname'].strip('"'));name=name if name.is_absolute()else K/name;size=int(s['size'],0);off=int(s['ooffs'],0)
  image=name.read_bytes()
  if name.name not in['ram1.bin','ram2.bin','ram3.bin']:continue
  number=int(name.stem[-1]);assert image[off:off+size]==images[number-1][off:off+size]
  segs.append(dict(name=s['name'].strip('"'),bank=number,start=int(s['start'],0),offset=off,bytes=size,sha256=hashlib.sha256(image[off:off+size]).hexdigest()))
 for key,s in spans.items():
  g=b['segs'][s['seg']]
  if int(s['size'],0)not in[2,3]or'ooffs'not in g:continue
  path=Path(g['oname'].strip('"'));path=path if path.is_absolute()else K/path
  if path.name not in['ram1.bin','ram2.bin','ram3.bin']:continue
  offset=int(g['ooffs'],0)+int(s['start'],0);code=path.read_bytes()[offset:offset+int(s['size'],0)]
  if len(code)==2 and code[0]in[0x81,0x91]:ins[key]=dict(kind='indirect',bytes=code.hex(),PC=int(g['start'],0)+int(s['start'],0),source=[])
  elif len(code)==3 and code[0]in[0x8d,0x9d,0x99,0x8e,0x8c,0xee,0xfe,0xce,0xde]:
   target=code[1]+256*code[2];high=target+(255 if code[0]in[0x9d,0x99,0xfe,0xde]else 0)
   if any(target<hi and high>=lo for lo,hi in[(0x147,0x153),(0x73e0,0x73f0),(0x6b08,0x6b09),(0x7e06,0x7e07),(0x7d9f,0x7da0),(0x5120,0x512c),(0x5130,0x5131)]):
    ins[key]=dict(kind='absolute',bytes=code.hex(),PC=int(g['start'],0)+int(s['start'],0),target=target,source=[])
 for row in lines:
  for key in row['span'].split('+'):
   if key not in ins:continue
   path=Path(files[row['file']]['name'].strip('"'));path=path if path.is_absolute()else K/path
   if path not in sources:sources[path]=path.read_text().splitlines()
   n=int(row['line']);text=sources[path][n-1].split(';')[0].strip()
   if re.match(r'(?:(?:[\w@]+)?:\s*)?(?:sta|stx|sty|inc|dec)\b',text,re.I):ins[key]['source'].append(dict(path=path.as_posix(),line=n,text=text,clause='\n'.join(sources[path][max(0,n-12):n+6])))
 actual=[q for q in ins.values()if q['source']]
 indirect=[q for q in actual if q['kind']=='indirect'];assert len(indirect)==1
 assert indirect[0]['source'][0]['text']=='STA (CfPointers),Y'
 src=(K/'component.s').read_text();assert '.word ram_score + $03'in src and'LDY #$03'in src
 score=address(b,'ram_score');assert 0xc000<=score<0xc7fa
 def table(name,count):
  sym=b['syms'][name];g=b['segs'][sym['seg']];path=Path(g['oname'].strip('"'));path=path if path.is_absolute()else K/path
  at=int(g['ooffs'],0)+int(sym['val'],0)-int(g['start'],0);return path.read_bytes()[at:at+count]
 frame=table('CfBodyFrameIndex',192);pages=table('CfBodyPage',156)
 assert all(x==255 or x<156 for x in frame)and set(pages)==set(range(9))
 for w in actual:
  s=w['source'][0];name=Path(s['path']).name;text=s['text'].lower()
  if w['kind']=='indirect':w['finite_target_range']=[score,score+5];w['domain']='Two immutable P1/P2 score pointers, rowY2..0.'
  elif re.search(r'\$01[0-9a-f]{2}',text):w['finite_target_range']=[0x17b,0x1ff];w['domain']='TSX own live stack-frame restore with existing12-byte stack-reserve ABI.'
  elif 'floateynum'in text:w['finite_target_range']=[0x10d,0x113];w['domain']='Native enemy score popup slot0..6.'
  elif name=='render.s':w['domain']='Body low191+page0..8 with upper3/window0; source frame index<192, all156 accepted table entries0..8. Shot constant968 with upper3/window6; wide-active is boolean.'
  elif name=='scroll-publisher.s':w['finite_index_range']=[1,3];w['domain']='Exact native world window restoreX3..1, native initializer bytes and modezero.'
  else:raise AssertionError(('Unclassified CF writer',w))
 q=dict(passed=True,current_ROM_sha256=PIN,carrier_pages=[935,958],all_carrier_bytes_exact=True,segments=segs,
  actual_writers=actual,indirect_score_domain=[score,score+5],
  body_frame_entries=192,body_page_entries=156,body_physical_pages=[959+i for i in sorted(set(pages))],shot_physical_page=968,unclassified=[],
  indirect_contract='Only CfPointers store is score P1/P2 table, Y=2..0; table targets ram_score and ram_score+3 in own C2 state. No CHR shadow/hardware alias.',
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',K/'runtime.dbg',K/'runtime.cfg',K/'ram1.bin',K/'ram2.bin',K/'ram3.bin',K/'component.s',K/'state.inc',C/'joint/cf-stream.bin']})
 save(O/'cf-current-binding.json',q);print(json.dumps(dict(CF_binding=True,segments=len(segs),writers=len(actual),indirect=len(indirect),score=score)),flush=True)

class Bus(Menu.Bus):
 def __init__(self,b):
  self.page_counts=collections.Counter();self.bad=[];self.phase='construction';self.shadow_serial=0
  super().__init__(b)
 def __setitem__(self,i,v):
  super().__setitem__(i,v)
  if isinstance(i,int)and 0x5120<=i<=0x512b:
   page=self.chr_latches[i-0x5120];self.page_counts[page]+=1
   if page in[1019,1020]:self.bad.append((self.phase,i,v,self.upper))
  if isinstance(i,int)and(i in range(0x147,0x153)or i in range(0x73e0,0x73ec)):self.shadow_serial+=1

def irq(m):
 c=NesMPU(memory=m,pc=0x5b00);c.sp=224;c.p=0x30;c.irq()
 for _ in range(200):
  if c.pc==0x5b00 and c.sp==224:break
  assert m[c.pc]!=0,('IRQ BRK',hex(c.pc));c.step()
 else:raise AssertionError('IRQ return bound')

def scenes(limit=None):
 assert sha(O/'candidate.nes')==PIN;b=scoped_load(O/'candidate.nes');Menu.Bus=Bus
 counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
 report=dict(passed=False,carrier_granted=False,current_ROM_sha256=PIN,source_CPU=True,native=False,rows=[],scope='Actual legal menu identities, complete Start/parser/entrance Main, normal NMI and IRQ. Finite domain checks complement compiled writer/source bounds; no video or full-stage qualification.')
 try:
  for slot,count in enumerate(counts):
   m=Menu.fresh(b);Menu.put(m,CrossoverMenuIndex=slot);Menu.invoke(m,'MenuResolveCharacter');Menu.invoke(m,'QueueSelection')
   for variant in range(count):
    if limit and len(report['rows'])>=limit:break
    if variant:
     Menu.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);Menu.invoke(m,'CrossoverMenuInput')
    m.phase=f'menu:{slot}:{variant}';Menu.invoke(m,'DrawSelectionPreview');Menu.consume(m);irq(m)
    n=Menu.fork(m);n.phase=f'Start:{slot}:{variant}'
    pending=bool(Menu.invoke(n,'FmPending')['P']&1)
    row=dict(slot=slot,variant=variant,raw=Menu.get(n,'SelectedCharacter'),pending=pending,minimum_SP=224,Main=0,NMI=1,IRQ=1)
    if not pending:
     Menu.put(n,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0,VRAM_Buffer1_Offset=0)
     start=Menu.invoke(n,'CrossoverMenuInput');Menu.invoke(n,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P']);Menu.invoke(n,'PauseRoutine',a=0)
     for frame in range(700):
      if Menu.get(n,'OperMode_Task')==3 and Menu.get(n,'GameEngineSubroutine')==8:break
      Menu.put(n,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
      result=Menu.invoke(n,'GameLoop');row['minimum_SP']=min(row['minimum_SP'],result['minimum_SP']);row['Main']+=1
      Menu.consume(n);irq(n);row['NMI']+=1;row['IRQ']+=1
      n.writes.clear();n.ram_writes.clear();n.ppu_log.clear()
     else:raise AssertionError(('Parser/entrance bound',slot,variant,Menu.get(n,'OperMode_Task'),Menu.get(n,'GameEngineSubroutine')))
     for frame in range(6):
      Menu.put(n,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
      result=Menu.invoke(n,'GameLoop');row['minimum_SP']=min(row['minimum_SP'],result['minimum_SP']);row['Main']+=1
      Menu.consume(n);irq(n);row['NMI']+=1;row['IRQ']+=1;n.writes.clear();n.ram_writes.clear();n.ppu_log.clear()
     n.phase=f'pause:{slot}:{variant}';Menu.put(n,GamePauseStatus=1,SavedJoypad1Bits=0,SavedJoypadBits=0,NmiDisable=255)
     Menu.invoke(n,'GameLoop');Menu.consume(n);irq(n);row['Main']+=1;row['NMI']+=1;row['IRQ']+=1
    row.update(page_writes=sum(n.page_counts.values()),physical_pages=sorted(n.page_counts),bad=n.bad)
    report['rows'].append(row);assert not n.bad,row
    print(json.dumps({k:row[k]for k in['slot','variant','raw','pending','Main','bad']}),flush=True)
   if limit and len(report['rows'])>=limit:break
  report.update(passed=True,identities=len(report['rows']),ready=sum(not q['pending']for q in report['rows']),Main=sum(q['Main']for q in report['rows']),NMI=sum(q['NMI']for q in report['rows']),IRQ=sum(q['IRQ']for q in report['rows']))
 except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc());raise
 finally:
  report['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',R/'tools/audit/check_hogan_current_bounded_v1.py',R/'tools/audit/arthur_cache_host_controls_v1.py']}
  save(O/'scene-publication.json',report)

def ownership():
 """Close conservative aliases with the source's declared, finite ABI domains.

 This is a source review backed by resolved compiler spans, not a claim that
 arbitrary corrupt RAM/registers are safe. In particular no upper3+251/252
 API clamp exists. The actual FF publication barrier is checked separately.
 """
 b=scoped_load(O/'candidate.nes');q=json.loads((O/'compiled-writers.json').read_text())
 old=json.loads((R/'build/karnov-carrier-closure-1101-v4/closure.json').read_text())
 known={(z['path'],z['instruction'].strip().lower())for z in old['retained_shadow_writer_inventory']['sites']}
 archive=zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip');idx={z['path']:z for z in json.loads(archive.read('index.json'))};used={}
 def read(path):
  p=Path(path)
  if p.is_file():data=p.read_bytes()
  else:
   row=idx[p.relative_to(R/'build').as_posix()];data=archive.read('objects/'+row['sha256']);assert hashlib.sha256(data).hexdigest()==row['sha256']
  used[p.as_posix()]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data));return data.decode('utf-8',errors='replace')
 # Every previous typed argument owner must still be exactly the audited source.
 caller_bindings=[]
 for z in old['physical_publisher_calls']['callers']:
  text=read(z['path']);expected=old['sources'][z['path']]['sha256'];assert used[z['path']]['sha256']==expected,z['path']
  assert z['instruction'].strip()in text
  caller_bindings.append(dict(path=z['path'],line=z['line'],upper_domain=z['upper_domain'],argument_bound=z['argument_bound'],sha256=expected))
 # Sound-test's only arbitrary-looking native pointer is a fixed table target.
 count=address(b,'SoundTestHeroCount');lo=location(b,'SoundTestVariantLo');hi=location(b,'SoundTestVariantHi')
 variant_targets=sorted({b['raw'][lo+i]+256*b['raw'][hi+i]for i in range(count)if b['raw'][hi+i]})
 targets=[(address(b,'CurrentCHRBank'),12),(address(b,'X5ChrMode'),15),(address(b,'SmChrBank'),1),(address(b,'SsChrPhysical'),1),(address(b,'InvHudPhysical'),1)]
 assert all(not any(a<=p<a+n for a,n in targets)for p in variant_targets)
 native_map=[(0x300,0x5fe)]
 def disjoint(ranges):return all(not any(lo<a+n and hi>=a for a,n in targets)for lo,hi in ranges)
 classified=[];unclassified=[];counts=collections.Counter()
 for w in q['writers']:
  s=w['witnesses'][0];name=Path(s['path']).name;text=s['text'];low=text.lower();op=w['operand'];kind=w['kind'];domain=None;zero=False;rule=None
  if kind=='indirect':
   if name=='imported.s'and op==0xec:domain=[(0x6900,0x697b)];rule='MM2 four channels: pointer starts6900, advances31 exactly3 times; rowY<=30. The only high-byte writers initialize69 and add carry (no low-byte carry in0/31/62/93).'
   elif name=='expanded_audio.s':domain=[(0x7400,0x7bff)];rule='ResetLz sets7400; WriteHistory usesY0, increments and wraps at7C00; eight-page history.'
   elif name=='reset.s':domain=[(0,0x7ff)];zero=True;rule='InitializeMemory: A=0 is invariant; descending pageX7..0, stack/OAM/preserved-ZP guards. Zeroing cannot create forbidden page.'
   elif op==9:domain=native_map;rule='Native R6/R7 block-buffer address producer; high03/04, Ybyte<=255. Conservative0300..05FE excludes every graphics field.'
   elif name=='megaman_weapons.s':
    domain=[(0x6007,0x68d3)];zero=s['line']==425;rule='MegaManRam clear or MmMapPointer: five declared416-cell maps and collision-owned cell index, entirely6007..68D3.'
   elif name=='roster.s':domain=[(0x6c06,0x6f36)];zero=True;rule='RosterRamStart..RosterRamEnd bounded byte clear.'
   elif name in['roster_weapons.s','easy_link_order.s']:
    if s['line']in[1580]:domain=native_map;rule='RosterBlockSeen native cell clear: highBlock_Buffer_1, original cellY.'
    else:domain=[(0x6d12,0x6eb1)];rule='RosterBlockSeen/clear: declared416-byte RgMeleeBlocks; pointer macro uses native block-buffer cell.'
   elif name=='inventory.s':domain=[(0x7c36,0x7da0)];zero=True;rule='InventoryInit exact start/end clear, invariant zero. InvHudPhysical cleared, never arbitrary data.'
   elif name=='special_weapons.s':domain=native_map;rule='Native terrain cell pointer (Block_Buffer_1/high, Block_BBuf_Low/Ycell).'
   elif name=='sound_test.s':domain=[(p,p)for p in variant_targets];rule='Sound-test immutable37-row variant pointer table. Restore uses the same saved target; no gameplay character changes while sound browser active.'
   elif name=='ff-render.s':domain=[(0x5c40,0x5cff)];rule='FfRenderBuffer NativeSubset header temporary count; HStart is bounded source packed-part offset within5C40..5CFF.'
   elif name=='kr-terrain.inc':domain=[(0xc000,0xc7ff)];zero=True;rule='Karnov original actor/options state boundedC000..C7FF clear.'
   elif name=='kr-render.inc':domain=[(0xd000,0xd540)];rule='Karnov metadata loader D000..D540, exact terminal pointer.'
   elif name=='component.s'and'thomas-'in s['path']:domain=[(0xc300,0xc3ff)];rule='Original Thomas cold state zero page relocated to ThomasState+C300; indexY byte only.'
   elif name in['kr-resident.inc','cache-loader.s','loader.s','copy.s','cf-loader.s','owner.s','th-resident.s','cold.s']:
    domain=[(0xa000,0xdfff)];rule='Selected private WRAM code/metadata copy and readback; pointer high startsA0/C0 and reaches boundedBE/DE only. No host low RAM/SRAM target.'
  elif kind=='absolute_indexed'and not any(z in low for z in['currentchrbank','x5chrmode']):
   if op==0x5120:domain=[(0x5120,0x512b)];rule='X5ColdInit X=0..11 hardware publication; initialized native table, upper latch0.'
   elif re.search(r'\$01[0-9a-f]{2}|\$0100\+',low):domain=[(0x17b,0x1ff)];rule='TSX stack-frame patch, offset>=1; owned Main/farcall stack ABI has12-byte reserve above17A. Offsets rewrite only live own frame. Separate actual Main stack qualification required for new combat.'
   elif op<0xe0:domain=[(op,op+11)];rule='Native enemy/misc/player object slot index0..11 (conservative union), below ordinary shadow0147.'
   elif op==0xe0:domain=[(0xe0,0xe3)];rule='Rogue Dawn source four-byte instrument header loopY=0..3; compare4 terminates.'
   elif 0x10d<=op<=0x131:domain=[(op,op+7)];rule='Native floatey/score/digit arrays; object index0..6 or decimal digit index1..6; conservative0..7.'
   elif 'mm2audiozp'in low:domain=[(op,op+53)];rule='Audio ZP copy loopX35..0, exact54-byte shadow.'
   elif 'mmrushland'in low:domain=[(op,op+15)];rule='Rush landing image/music/dirty16-byte APU rows. Immutable decoded register/value stream carries only register0..15.'
   elif 'samusramstart'in low:domain=[(0x6b00,0x6b4f)];zero=True;rule='SamusInit exact80-byte zero loop; SmChrBank is cleared, no arbitrary alias.'
   elif 'guestexpansionlast'in low:domain=[(op,op+7)];rule='SoundTestReset invalidates8-byte expansion APU shadow.'
   elif 'xgmusicapu'in low:domain=[(op,op+15)];rule='Expanded audio APU rowX0..15.'
   elif 'xgaudiostack'in low:domain=[(op,op+31)];rule='Expanded macro depth has explicit CPX#32/BCS stop before all32-entry stack writes.'
   elif 'vgaudioram'in low:domain=[(op+0xb0,op+0xe3)];rule='Original Gradius per-channel X belongs to immutable ECE0 table{B0,C1,D2,E3}; saved/restored indices48/49 come from these same rows. Effective range7400..7443 excludes73E0..73EE.'
   elif 'hpramstart'in low:domain=[(0x7382,0x73dc)];zero=True;rule='HpConfigure91-byte clear, declared HpRamEnd73DD.'
   elif any(z in low for z in['hpactorowner','hpactorslot']):domain=[(op,op+5)];rule='Native helper actor slot0..5 (owner six-entry array; platform slots0..2).'
   elif any(z in low for z in['hpnativedrawlo','hpnativedrawhi']):domain=[(op,op+6)];rule='Native draw seven pointers, object slot0..6.'
   elif 'hpnativesmalldescriptor'in low:domain=[(op,op+8)];rule='Native small platform descriptor exactly9 bytes.'
   elif low.split(None,1)[-1].startswith('hp'):domain=[(op,op+2)];rule='Helper source platform index0..2, declared three-entry arrays.'
   elif 'soundtestvariantactive'in low:domain=[(op,op+11)];zero=True;rule='SoundTestEnter clearX11..0, inactive native draw-buffer overlay.'
   elif 'dwhealth'in low:domain=[(op,op+8)];rule='Adjacent Darkwing9-byte state starts73EF, strictly after last graphics byte73EE.'
   elif 'invammo'in low:domain=[(op,op+191)];rule='Inventory192-byte ammo table: owner0..11 times16 plus local item0..15.'
   elif any(z in low for z in['invpickup','invrisephase']):domain=[(op,op+5)];rule='Native six object pickup slots index0..5 (saved/view arrays share exact index).'
   elif 'specialramstart'in low:domain=[(0x7da2,0x7e1d)];zero=True;rule='SpecialClear exact124-byte zero loop, includes low art selector zero only.'
   elif 'sswaterscale'in low:domain=[(op,op+3)];rule='Four products and mirrored four rows: scale builderX3..0; +4 expressions already accounted in operand.'
   elif any(z in low for z in['ssmode','ssangle','sshidden','ssart','sshittimer']):domain=[(op,op+9)];rule='Roster shared ten projectile slots, allocation/update iteration9..0.'
  else:
   if 'hardware'in w['ranges']or'upper_latch'in w['ranges']:
    if name=='reset.s':rule='Actual IRQ writes bank5128 low0 only; any current upper latch gives physical0/256/512/768.'
    elif name in['mmc5_expanded.s','skin.s']:rule='Normal X5 publication: legacy ChrPhysicalMap byte<256 or admitted low/mode physical pair. Kamikaze84 mode uses upper2. All12 windows restore upper latch0 on exit.'
    elif name in['remaining_audio.s','rogue_dawn_audio_scheduler_hooks_v5.s']:rule='NMI audio HUD font override uses X5HudChrUpper&3, proven retained upper domain0..2, then resets hardware latch0.'
    elif name=='kr-resident.inc':rule='Karnov kernel row R2=0..7 -> original carrier399..406; upper1 fixed, so any row byte cannot reach1019/1020.'
    elif name=='cache-loader.s':rule='Arthur forcedblank maps exactly881,882,883; actual loader/header proof v4 binds source.'
    elif name in['loader.s','copy.s','cf-loader.s']:
     if 'quick/'in s['path']:rule='Quick forcedblank source884..892; restore512B from admitted currentwindow11. Actual complete loader/negative restore v5.'
     elif '/bowser/'in s['path']:rule='Bowser forcedblank927..934. Actual loop destinationC0/C4/..DC and readback bounded v5.'
     elif '/bt/'in s['path']:rule='Battletoads forcedblank919..926. Actual loop destinationC0/C4/..DC and readback bounded v5.'
     elif name=='cf-loader.s':rule='ContraForce forcedblank935..958; restore512B from admitted currentwindow11. Actual loop R2=0..23 and readback v5.'
     else:rule='FinalFantasy forcedblank893..900, destinationC0/C4/..DC. Whole loader/readback/visiblefail and admitted restore v5.'
    elif name in['owner.s','cold.s']:rule='WWF declared source-page table below768, upper2. Loader restore512B uses admitted currentwindow11; metadata offsets bounded by six authenticated source rosters.'
    elif name=='th-resident.s':rule='Thomas declared ThLoadCHR byte table with fixed upper1; any lowbyte remains below512.'
   elif op==0x73ef:domain=[(op,op)];rule='Adjacent Darkwing health73EF is outside the15 actual graphics-state bytes.'
   elif (s['path'],low)in known:
    assert q['source_bindings'][s['path']]['sha256']==old['sources'][s['path']]['sha256'],('Prior named source changed',s['path'])
    rule='Previously source-closed named graphics writer, now bound to exact current resolved compiler instruction and identical source hash.'
   elif op==0x73ee:rule='Boolean wide-active flag only; never changes any low/upper page selector.'
   elif name=='character_select.s'and op in range(0x14f,0x153):rule='Menu area page constants CHR_BG_GROUND..+3, all lowbytes0..250; safe with every upper2 value.'
   elif name=='kr-menu.inc'and op==0x6b08:rule='Karnov cold body408: low152 paired with upper1 through genuine typed setter, before native alias copy.'
   elif name=='screen_render.s'and op==0x147:rule='Native lives body field stores CHRBankInitValues first page (authenticated native constant, not251/252).'
   elif name=='full_roster_menu.s'and op==0x147:rule='FmNativePrepare: clear all12 modes then reload native first8 lowbytes; X7..0. No retained upper3 can reinterpret another character.'
  row=dict(segment=w['segment'],offset=w['offset'],PC=w['PC'],bytes=w['bytes'],source=s,rule=rule,finite_target_ranges=domain,invariant_zero=zero)
  if rule:
   if domain and not zero and not op==0x5120:assert disjoint(domain),(text,domain)
   counts[rule]+=1;classified.append(row)
  else:unclassified.append(row)
 assert not unclassified,[(z['source']['path'],z['source']['line'],z['source']['text'])for z in unclassified]
 before=(R/'build/doki-current-component-1101-v1/candidate.nes').read_bytes();after=(O/'candidate.nes').read_bytes();chrbase=1048592
 assert hashlib.sha256(before).hexdigest()==old['source_ROM_sha256']
 changed=[i for i in range(1024)if before[chrbase+i*1024:chrbase+(i+1)*1024]!=after[chrbase+i*1024:chrbase+(i+1)*1024]]
 assert changed==list(range(399,412)),changed
 result=dict(passed=True,current_ROM_sha256=PIN,carrier_granted=False,compiled_writers=len(classified),indirect_writers=sum(w['kind']=='indirect'for w in q['writers']),
  old_resource_ROM_sha256=old['source_ROM_sha256'],changed_CHR_pages=changed,all_non_Karnov_CHR_resource_bytes_identical=True,
  unclassified=[],rules=dict(counts),writers=classified,typed_callers=caller_bindings,sound_test_targets=variant_targets,source_bindings=used,
  proof_scope='Legal original-source call and index domains, compiled exact image. Arbitrary memory corruption and invalid externally fabricated register arguments are outside the contract. FF interrupt barrier and current-image table ownership are separate required receipts.',
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'compiled-writers.json',R/'build/karnov-carrier-closure-1101-v4/closure.json',O/'cf-current-binding.json']})
 save(O/'finite-writer-domains.json',result);print(json.dumps(dict(finite_writers=len(classified),unclassified=0,typed_callers=len(caller_bindings),sound_table_targets=len(variant_targets))),flush=True)

def interrupts():
 b=scoped_load(O/'candidate.nes');Menu.Bus=Bus;m=Menu.fresh(b)
 Menu.put(m,SelectedCharacter=22,OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255,FfVariant=0,PlayerFacingDir=1,PlayerOutlinesOff=1,GameEngineSubroutine=8,CurrentOAMOffset=0)
 m.ppuctrl=160;loaded=Menu.invoke(m,'FwLoad');assert loaded['P']&1
 cuts=0;cut_pcs=collections.Counter();minimum=224
 def interrupt(c,which):
  nonlocal minimum
  back=(c.pc,c.sp,c.a,c.x,c.y,c.p&~0x10);getattr(c,which)()
  for _ in range(200000):
   if(c.pc,c.sp)==back[:2]:break
   minimum=min(minimum,c.sp);assert m[c.pc]!=0,(which,hex(c.pc));c.step()
  else:raise AssertionError(('IRQ/NMI return bound',which))
  assert(c.a,c.x,c.y,c.p&~0x10)==back[2:],(which,back,(c.a,c.x,c.y,c.p))
 def ram(name,a=0):
  nonlocal cuts
  m.raw_page(1,3);Menu.put(m,CurrentBank=3,NmiDisable=255)
  c=NesMPU(memory=m,pc=address(b,name));c.a=a;c.x=0;c.y=0;c.p=0x31;c.sp=224;c.stPushWord(0x5aff)
  for _ in range(60000):
   if c.pc==0x5b00:break
   serial=m.shadow_serial;assert m[c.pc]!=0,('FF RAM BRK',name,hex(c.pc));c.step()
   if serial!=m.shadow_serial and any(Menu.get(m,'CurrentCHRBank',i)in[251,252]and Menu.get(m,'X5ChrMode',i)&0x83==0x83 for i in range(12)):
    assert Menu.get(m,'NmiDisable')&128
    cut_pcs[c.pc]+=1;interrupt(c,'nmi');interrupt(c,'irq');cuts+=1
  else:raise AssertionError(('FF source call bound',name))
  assert c.sp==224
 pages=set();pairs=0
 for variant,tier,pose,face in itertools.product(range(4),range(3),range(1,19),[1,2]):
  m.phase=f'FF:{variant}:{tier}:{pose}:{face}'
  Menu.put(m,FfVariant=variant,FfPower=tier,PlayerFacingDir=face,FfReady=247,DisableScreenFlag=0,Mirror_PPUMASK=30)
  ram('FfSetPose',pose);ram('FfPublishChunk')
  page=756+Menu.get(m,'FfRenderPage');assert Menu.get(m,'CurrentCHRBank')+256*(Menu.get(m,'X5ChrMode')&3)==page
  assert 756<=page<=787;Menu.consume(m);irq(m);assert m.chr_latches[0]==page
  pages.add(page);pairs+=1;assert not m.bad,m.bad
  m.writes.clear();m.ram_writes.clear();m.ppu_log.clear()
 assert cuts>0,'No genuine low/high update seams reached'
 # Closing the pane is a value-preserving two-byte transaction. Boundary
 # representatives cover every upper pair including high3's final legal page.
 panel_cases=0
 for page in[0,1,255,256,511,512,756,767,768,787,915,968,969,1018]:
  z=Menu.fresh(b);z.phase='ZeldaIIpanel';Menu.put(z,SelectedCharacter=2,OperMode=1,GamePauseStatus=1,DisableScreenFlag=0,Mirror_PPUMASK=0,NmiDisable=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Z2PanelActive=0,Z2PanelPending=0,Z2UiState=0,X5WideChrActive=1)
  z[address(b,'CurrentCHRBank')+11]=page&255;z[address(b,'X5ChrMode')+11]=0x80|(page>>8)
  for _ in range(2):Menu.invoke(z,'Z2PanelTick')
  assert Menu.get(z,'Z2PanelActive')==1 and Menu.get(z,'CurrentCHRBank',11)==139 and Menu.get(z,'X5ChrMode',11)==129
  Menu.put(z,GamePauseStatus=0,Mirror_PPUMASK=0)
  for _ in range(2):Menu.invoke(z,'Z2PanelSync')
  assert Menu.get(z,'Z2PanelActive')==0 and Menu.get(z,'CurrentCHRBank',11)==page&255 and Menu.get(z,'X5ChrMode',11)==0x80|(page>>8)
  Menu.consume(z);irq(z);assert z.chr_latches[11]==page and not z.bad;panel_cases+=1
 q=dict(passed=True,current_ROM_sha256=PIN,FF_actual_pose_publish_normal_NMI_IRQ=pairs,FF_pages=sorted(pages),genuine_partial_pair_busy_NMI_IRQ_cuts=cuts,cut_resume_PCs={hex(k):v for k,v in cut_pcs.items()},cut_minimum_SP=minimum,ZeldaII_complete_open_close_restore_cases=panel_cases,
  actual_Interrupt_return_AXYP_preserved=True,all12_hardware_slots_observed=True,forbidden_page_writes=0,
  scope='432 actual FF class/tier/pose/facing executions, actual in-flight source-publisher NMI and IRQ at dangerous low/high store seams, normal completed-frame publication;14 complete ZeldaII pane backup/draw/restore paths. Service entrySP224; this is resource ownership evidence, not the separate composed actual Main combat stack qualification.',
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',R/'tools/audit/check_hogan_current_bounded_v1.py']})
 save(O/'interrupt-publication.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','scope','cut_resume_PCs','FF_pages']}),flush=True)

def main():
 a=argparse.ArgumentParser();a.add_argument('--cf',action='store_true');a.add_argument('--scenes',action='store_true');a.add_argument('--ownership',action='store_true');a.add_argument('--interrupts',action='store_true');a.add_argument('--limit',type=int);v=a.parse_args()
 if v.cf:cf()
 if v.scenes:scenes(v.limit)
 if v.ownership:ownership()
 if v.interrupts:interrupts()
if __name__=='__main__':main()
