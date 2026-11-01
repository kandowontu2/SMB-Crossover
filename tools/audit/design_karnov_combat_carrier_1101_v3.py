"""Bounded carrier design: actual graphic closure, helper assembly, copy test.

No root build/source/ROM is changed. CHR1019/1020 remains a proposal until
whole-host runtime closure is proved; source pixels, not zero-byte scans,
establish that the existing Karnov body has only448B available.
"""
from pathlib import Path
import hashlib,itertools,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
from arthur_cache_host_controls_v1 import OverlayMemory
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as Menu
O=R/'build/karnov-combat-carrier-design-1101-v3';P=R/'build/karnov-host-resource-base-1101-v1'
F=R/'build/doki-current-component-1101-v1';C=R/'build/karnov-combat-component-1101-v2';A=R/'build/karnov-original-art-1101-v1'
HELP=R/'tools/reference/karnov_combat_carrier_loader_1101_v3.inc'
BASE=R/'tools/reference/karnov_cache_resident_1101_v1.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def once(t,a,z):assert t.count(a)==1,a;return t.replace(a,z)

def main():
 O.mkdir(exist_ok=True);bindings=[Path(__file__).resolve(),HELP,BASE,F/'candidate.nes',F/'candidate.dbg',P/'render-art.json',P/'kr-body.chr',P/'kr-pose-meta.bin',P/'kr-shot-tiles.bin',A/'art-controls.json',A/'body.chr',C/'resident.bin',C/'handoff.json']
 art=json.loads((P/'render-art.json').read_text());old=json.loads((A/'art-controls.json').read_text());component=json.loads((C/'handoff.json').read_text())
 assert art['passed']and old['passed']and component['passed']
 body=(P/'kr-body.chr').read_bytes();assert len(body)==5120
 used=[set()for _ in range(5)];pairs=set()
 def mark(page,packet):
  assert packet[0]==len(packet)-1 and packet[0]%4==0
  for i in range(1,len(packet),4):
   tile=packet[i];assert tile%2==0 and tile<64
   used[page].update([tile,tile+1]);pairs.add((page,tile))
 for row in art['profiles']:mark(row['page'],row['packet'])
 hostbody=[set(s)for s in used]
 donorbody=(A/'body.chr').read_bytes()
 for row in old['poses']:
  mark(row['packed_page'],row['packet'])
  for i in range(1,len(row['packet']),4):
   at=row['packed_page']*1024+row['packet'][i]*16
   assert body[at:at+32]==donorbody[at:at+32]
 assert used==hostbody,'All256 original poses must close under64 host profiles'
 # The cold menu/lives portrait is exactly original state0, facing0, page1;
 # changing coordinates/order never changes its referenced patterns.
 cold=next(z for z in old['poses']if z['state']==z['facing']==z['hurt']==z['phase']==0)
 assert cold['packed_page']==1;mark(1,cold['packet'])
 for tile in(P/'kr-shot-tiles.bin').read_bytes():
  assert 192<=tile<=254 and tile%2==0
  used[3].update([tile-192,tile-191])
 free=[p*1024+t*16 for p in range(5)for t in range(64)if t not in used[p]];runs=[]
 for at in free:
  if runs and runs[-1][0]+runs[-1][1]==at:runs[-1][1]+=16
  else:runs.append([at,16])
 assert len(free)*16==448 and runs==[[0,32],[896,160],[1984,96],[3040,32],[4000,128]]
 # Audit every original/ported state operand including worst-case indexed255.
 sourcefiles=[R/'build/karnov-original-source-1101-v1/source'/n for n in ['portable_actor.inc','portable_dispatch.inc']]+[R/'build/karnov-original-weapons-1101-v1/source'/n for n in ['portable_weapon.inc','portable_clear.inc']]+[R/'tools/reference'/n for n in ['karnov_health_1101_v2.inc','karnov_pickups_1101_v2.inc']]
 bounds=[]
 for p in sourcefiles:
  text=p.read_text();assert not re.search(r'\b(?:STA|STX|STY|INC|DEC)\s+\(',text,re.I),(p,'unproved indirect state write')
  operands=[(int(m[1],16),bool(m[2]))for m in re.finditer(r'KrState\+\$([0-9a-fA-F]+)(,[XYxy])?',text)]
  hi=max((n+(255 if ix else 0)for n,ix in operands),default=0)
  assert hi<0x900,(p,hex(hi));bounds.append(dict(source=p.as_posix(),maximum_conservative_offset=hi,index_domain='0..255'))
 bindings+=sourcefiles
 # Named final emission: exact50 SMB3Plus pages969..1018; candidate tail
 # pages1019/1020 must still be proven unused by every other live consumer.
 b=scoped_load(F/'candidate.nes');assert sha(F/'candidate.nes')=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
 segment=next(s for s in b['segs'].values()if s['name']=='"SMB3PLUS_BODY_CHR"')
 assert(int(segment['start'],0),int(segment['size'],0))==(969*1024,50*1024)
 for page in [1019,1020]:
  at=1048592+page*1024;assert b['raw'][at:at+1024]==bytes(1024)
  assert not any('ooffs'in s and int(s['ooffs'],0)<at+1024 and int(s['ooffs'],0)+int(s['size'],0)>at for s in b['segs'].values())
 def table(n,count):at=location(b,n);return b['raw'][at:at+count]
 low=table('M3Form0ChrLo',81);offs=table('MbChrOffsets',7);pages=set();selectors=0
 for variant,form,frame in itertools.product([2,3],range(7),range(256)):
  f=frame if frame<81 else 14;legacy=(low[f]+offs[form])&255
  index=20 if form==4 and 57<=f<60 else(legacy-12)&255
  page=969+index+(25 if variant==3 else 0);pages.add(page);assert 969<=page<=1018
  selectors+=1
 for legacy in range(20,24):
  for base in[legacy,legacy+8]:
   for variant in[2,3]:assert 969+base-12+25*(variant==3)<=1018
 # Partial whole-host evidence: actual existing90 menu identities publish
 # physical CHR through the native publisher; this is not campaign closure.
 counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
 menu_count=0;menu_pages=set()
 for slot,total in enumerate(counts):
  m=Menu.fresh(b);Menu.put(m,CrossoverMenuIndex=slot);Menu.invoke(m,'MenuResolveCharacter');Menu.invoke(m,'QueueSelection')
  for variant in range(total):
   if variant:
    Menu.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);Menu.invoke(m,'CrossoverMenuInput')
   Menu.invoke(m,'DrawSelectionPreview');Menu.invoke(m,'X5PublishChr');menu_pages.update(m.chr_latches)
   assert not set(m.chr_latches)&{1019,1020},(slot,variant,m.chr_latches)
   menu_count+=1
 assert menu_count==90
 # Assemble the helpers at the old authenticated resident tail. They consume
 #70B tail and reclaim15B before alignment; pickup713+70 fits802 with19B left.
 origin=0xbc8e;imports={n:address(b,n)for n in['CurrentBankC','R0','R1','R2','R4']}
 setup=''.join(f'{n}=${v:04x}\n.export'+('zp 'if n.startswith('R')else' ')+n+'\n'for n,v in imports.items())
 (O/'bindings.s').write_text(setup)
 source=BASE.read_text();copy=source[source.index('KrCopyRow:\n'):source.index(' ; Image header is not an early validity publication.')]
 oldinit=' lda R2\n asl\n asl\n ora #$c0\n sta R1'
 copy=once(copy,oldinit,' jsr KrCarrierRowSetup');assert copy.count(' ldx #4')==2
 copy=copy.replace(' ldx #4',' ldx R4');copy=once(copy,' sbc #4',' sbc R4');copy=once(copy,' cmp #8',' cmp #10')
 mapper=source[source.index('KrMapRow:\n'):source.index('KrRestorePPU:\n')]
 oldmap=' lda #1\n sta $5130\n lda R2\n clc\n adc #<399\n sta $512b'
 mapper=once(mapper,oldmap,' jsr KrCarrierMap')
 publication=source[source.index(' ldx #3\nKrPublishBank:'):source.index(' jsr KrRestorePPU\nKrLoadYes:')]
 cookie=bytes([167,34,1,12])+hashlib.sha256((C/'resident.bin').read_bytes()).digest()[:12]
 program='.setcpu "6502"\n.macpack longbranch\n.import CurrentBankC\n.importzp R0,R1,R2,R4\n.import KrCarrierRowSetup,KrCarrierMap\n.segment "PROTO"\n.export PrototypeStart,PrototypePublish,PrototypeFailure\nPrototypeStart:\n lda #3\n sta CurrentBankC\n sta $5116\n lda #0\n sta R2\n'+copy+'PrototypePublish:\n'+publication+' sec\n rts\nKrLoadFailed:\nPrototypeFailure:\n ldx #3\nClearFailure:\n stx CurrentBankC\n stx $5116\n lda #0\n sta $dfe0\n dex\n cpx #1\n bne ClearFailure\n clc\n rts\n'+mapper+'KrCookie:.byte '+','.join(map(str,cookie))+'\n'
 (O/'prototype.s').write_text(program);(O/'helpers.s').write_text('.setcpu "6502"\n.include "karnov_combat_carrier_loader_1101_v3.inc"\n')
 (O/'prototype.cfg').write_text('MEMORY{P:start=$a000,size=$1000,file="'+(O/'prototype.bin').as_posix()+'";H:start=$bc8e,size=$0322,file="'+(O/'helpers.bin').as_posix()+'";}SEGMENTS{PROTO:load=P,type=ro;KR_CARRIER_HELPERS:load=H,type=ro;}\n')
 cc=R/'tools/Windows/cc65/bin';commands=[]
 for n in['prototype','helpers','bindings']:
  cmd=list(map(str,[cc/'ca65.exe','-g','-I',HELP.parent,O/(n+'.s'),'-o',O/(n+'.o')]))
  guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=z.returncode,stderr=z.stderr));assert z.returncode==0,z.stderr
 cmd=list(map(str,[cc/'ld65.exe','-C',O/'prototype.cfg',O/'prototype.o',O/'helpers.o',O/'bindings.o','-o',O/'unused.bin','-Ln',O/'prototype.lbl','--dbgfile',O/'prototype.dbg']))
 guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=z.returncode,stderr=z.stderr));save(O/'commands.json',commands);assert z.returncode==0,z.stderr
 helpers=(O/'helpers.bin').read_bytes();assert len(helpers)==70,len(helpers)
 labs={m[2]:int(m[1],16)for l in(O/'prototype.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',l))}
 raw=bytearray(b['raw']);kernel=bytearray((i*31+17)&255 for i in range(8192));kernel[0x1fe0:0x1ff0]=cookie
 raw[1048592+399*1024:1048592+407*1024]=kernel
 code=(C/'resident.bin').read_bytes();carrier=code+bytes(1280-len(code));raw[1048592+1019*1024:1048592+1019*1024+1280]=carrier
 for at,data in[(0xa000,(O/'prototype.bin').read_bytes()),(origin,helpers)]:raw[16+29*8192+at-0xa000:16+29*8192+at-0xa000+len(data)]=data
 bb=dict(b,raw=bytes(raw));cpu_cases=[]
 for corrupt in[None,(3,0),(3,0x1fdf),(2,0x900),(2,0xd0f),(2,0xdff)]:
  m=OverlayMemory(bb);m.raw_page(1,157);m.raw_page(2,3);m[imports['CurrentBankC']]=3;m.ppuctrl=32;m.corrupt_at=corrupt
  c=NesMPU(memory=m,pc=labs['PrototypeStart']);c.sp=224;c.stPushWord(0x5aff);published=False;lowSP=c.sp
  for step in range(300000):
   if c.pc==0x5b00:break
   lowSP=min(lowSP,c.sp)
   if c.pc==labs['PrototypePublish']:published=True
   assert published or not(m.ram[2][0x1fe0]==167 and m.ram[3][0x1fe0]==167),'Early paired-cookie publication'
   assert m[c.pc]!=0;c.step()
  else:raise AssertionError('Bounded native copy/verify prototype')
  if corrupt is None:
   assert c.p&1 and published and m.ram[2][0x900:0xe00]==carrier and m.ram[3]==kernel
   assert m.ram[2][0x1fe0:0x1ff0]==cookie and m.ppu_reads==18964
   assert m.ram_writes[-1]==(2,0x1fe0,167)
  else:assert not c.p&1 and not published and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
  cpu_cases.append(dict(corrupt=corrupt,success=bool(c.p&1),publish_reached=published,buffered_PPU_reads=m.ppu_reads,minimum_SP=lowSP,cycles=c.processorCycles))
 rows=[dict(row=i,CHR=399+i,bank=3,destination=0xc000+i*1024,bytes=1024)for i in range(8)]+[dict(row=8,CHR=1019,bank=2,destination=0xc900,bytes=1024),dict(row=9,CHR=1020,bank=2,destination=0xcd00,bytes=256)]
 result=dict(passed=True,design_only=True,root_modified=False,installed=False,body_carrier_fits=False,body_used_16B_blocks=sum(map(len,used)),body_unused_bytes=448,body_unused_runs=runs,body_profiles=64,original_pose_cases=256,cold_portrait_closed=True,source_shot_render_cases=art['shot_render_cases'],source_shot_patterns=7,C2_state_bounds=bounds,C2_code=[0xc900,0xcd10],proposed_C2_copy_range=[0xc900,0xce00],proposed_CHR_pages=[1019,1020],carrier_lease_granted=False,SMB3Plus_table_closure_cases=selectors,SMB3Plus_pages=sorted(pages),old_menu_identities=menu_count,old_menu_physical_CHR_pages=sorted(menu_pages),other_owner_campaign_runtime_closure=False,rows=rows,loader_helper_bytes=70,loader_pre_align_bytes_reclaimed=15,pickup_tail_budget=dict(total=802,pickup=713,loader_helpers=70,remaining=19),pickup_alignment_budget=dict(old=70,new=85,pickup=66,remaining=19),native_copy_verify_CPU=cpu_cases,limits=['CHR1019/1020 source-emission gap and SMB3Plus selector closure are proved; full other-owner runtime/table closure is not. No carrier grant or candidate patch.','All90 existing menu identity publishers avoid1019/1020 in the frozen85 baseline. This is partial whole-host evidence; it does not cover gameplay/effects/IRQ scene variants.','Prototype executes the original copied-byte/verify/publication owners plus proposed mapper helpers in an explicit synthetic image. It omits the outer real KrLoad guard/save/PPU restoration; those need integration tests.','Readback precedes paired validity; all five injected failures deny both cookies. No unverified RAM opcode executes.','Component service ISR SP136 gives13B aboveSMC at serviceentrySP224 only. Actual Main depth, all native IRQ seams and complete loader cold/warm/negative contracts remain root gates.'],bindings={str(p.resolve()):sha(p)for p in bindings+[Path(Menu.__file__),O/'prototype.s',O/'helpers.s',O/'bindings.s',O/'prototype.cfg',O/'prototype.bin',O/'helpers.bin',O/'prototype.lbl',O/'prototype.dbg',O/'commands.json']})
 save(O/'design.json',result)
 print(json.dumps({k:result[k]for k in['passed','body_unused_bytes','carrier_lease_granted','SMB3Plus_table_closure_cases','loader_helper_bytes','loader_pre_align_bytes_reclaimed','pickup_tail_budget','native_copy_verify_CPU']}))

if __name__=='__main__':main()
