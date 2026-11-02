"""Rebind finite consumer evidence for a pooled Prince resource proposal."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/prince-actor-1101-v1'
ROM=R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes'
SHA='d8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05'
BUB_RESERVED={301,305,337,362,363,440,819,666,441}
POOL=sorted({*range(341,356,2),357,359,361,365,369,373,377,*range(381,394,2),544,545,*range(605,628,2),690,691,692,693,695,795})
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def adapt(name,replacements):
 p=R/'tools/audit'/name;s=p.read_text()
 for a,b in replacements:
  assert a in s,(name,a);s=s.replace(a,b)
 env={'__name__':'prince_resource_rebinding','__file__':str(p)}
 exec(compile(s,str(p),'exec'),env);env['main']()


def main():
 assert sha(ROM)==SHA and len(POOL)==42 and not set(POOL)&BUB_RESERVED
 common=[("R/'build/excitebike-pose-1101-v3'","R/'build/prince-actor-1101-v1'"),("R/'build/shinobi-camera-1101-v20/candidate.nes'","R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes'")]
 adapt('audit_excitebike_writer_preservation_1101_v1.py',common+[
  ('set(range(728,740))','set('+repr(POOL)+')'),
  ('*range(827,832)}','*range(827,832),*range(728,740)}')])
 adapt('check_excitebike_new_owner_pages_1101_v1.py',common+[('range(728,740)',repr(POOL))])
 adapt('check_excitebike_smb3_pages_1101_v1.py',common+[('range(728,740)',repr(POOL))])
 adapt('audit_shinobi_upper2_chr_1101_v1.py',[
  ("R/'build/shinobi-chr-closure-1101-v1'","R/'build/prince-actor-1101-v1'"),
  ("R/'build/kirby-approach-owner-1101-v3/candidate.nes'","R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes'"),
  ('TARGETS=set(range(503,511))|{513,515,516,517}','TARGETS=set('+repr(POOL)+')'),
  ("domains['SMB3 seven forms81frames']=sorted(m3)","current_m3=json.loads((O/'smb3-pages.json').read_text());assert current_m3['passed']and current_m3['ROM_SHA256']==sha(ROM);domains['SMB3 seven forms81frames']=current_m3['pages']")])
 b=scoped_load(ROM);raw=b['raw'];domains=dict(json.loads((O/'upper2-finite-domains.json').read_text())['domains']);del domains['SMB3 seven forms81frames']
 # Current source factor: every low pointer names Form0; the sole helper
 # applies a typed form offset. High CHR is literal2, so old retired form
 # labels cannot be interpreted as live page tables (notably the false795).
 def word(n):return list(address(b,n).to_bytes(2,'little'))
 def data(n,size):at=location(b,n);return raw[at:at+size]
 caller=bytes([0xae,*word('M3RenderForm'),0xe0,7,0x90,2,0xa2,0,0xbd,*word('M3ChrLoTableLo'),0x85,address(b,'R0'),0xbd,*word('M3ChrLoTableHi'),0x85,address(b,'R1'),0xac,*word('M3RenderFrame'),0x20,*word('MbFloatReadChrLow'),0xea,0xea,0xbd,*word('M3ChrHiTableLo'),0x85,address(b,'R0'),0xbd,*word('M3ChrHiTableHi'),0x85,address(b,'R1'),0xa9,2,0x8d,*word('M3SpritePageHi')])
 helper=bytes([8,0xb1,address(b,'R0'),0x18,0x7d,*word('MbChrOffsets'),0x8d,*word('SmChrBank'),0x28,0x60])
 assert data('M3SetFrame::Chr',len(caller))==caller
 assert data('MbFloatReadChrLow',len(helper))==helper
 base=data('M3Form0ChrLo',81);offsets=data('MbChrOffsets',7)
 assert offsets==bytes([0,4,4,244,0,248,252])
 for i in range(7):assert data('M3ChrLoTableLo',7)[i]+256*data('M3ChrLoTableHi',7)[i]==address(b,'M3Form0ChrLo')
 predicted=sorted({512+((v+d)&255)for v in base for d in offsets})
 m3=json.loads((O/'smb3-pages.json').read_text());assert predicted==m3['pages']==list(range(524,544))
 m3['current_source_constraint']=dict(sole_caller_clamps_form='LDX form;CPX7;BCC;LDX0',all7_low_pointers='M3Form0ChrLo',form_offsets=list(offsets),base_low_values=sorted(set(base)),high_CHR_literal=2,exact_live_caller_bytes=caller.hex(),exact_live_helper_bytes=helper.hex(),formula='512 + ((Form0ChrLo[frame] + offsets[clampedForm]) &255)',why_old795_is_not_live='M3Form1/2/3/4/6ChrLo arrays were retired by low-table factor; no live pointer selects them.',source_producer='tools/audit/prepare_smb3plus_low_table_factor_host_1031_v4.py')
 m3['bindings']={str(p.relative_to(R)):sha(p)for p in[ROM,R/'tools/audit/check_excitebike_smb3_pages_1101_v1.py',R/'tools/audit/prepare_smb3plus_low_table_factor_host_1031_v4.py',Path(__file__)]}
 (O/'smb3-pages.json').write_text(json.dumps(m3,indent=2)+'\n')
 domains['SMB3 current actual selector']=json.loads((O/'smb3-pages.json').read_text())['pages']
 historical=json.loads((R/'build/metal-storm-chr-closure-1101-v10/source-domains.json').read_text())
 for n,q in historical['exact_source_domains'].items():
  if n!='WWF every input byte':domains[n]=q['physical_pages']
 writer=json.loads((O/'writer-preservation.json').read_text());new=json.loads((O/'new-owner-pages.json').read_text())
 domains['WWF source cold kernel']=writer['WWF_cold_kernel_pages'];domains['WWF source cold metadata']=writer['WWF_cold_metadata_pages'];domains.update(new['actual_cold_map_rows']);domains['Shinobi body']=new['Shinobi_body_table'];domains['Metal body']=new['Metal_body_table'];domains['Tank source/body']=[501,502]
 tableproof={}
 def source_table(file,name,base=256):
  text=(R/'src'/file).read_text().split(name+':',1)[1];values=[]
  for line in text.splitlines():
   line=line.strip()
   if not line:continue
   if not line.startswith('.byte '):break
   values.extend(int(x)for x in line[6:].split(','))
  at=location(b,name);assert values and raw[at:at+len(values)]==bytes(values),(file,name)
  pages=sorted({base+x for x in values});domains[name]=pages;tableproof[name]=dict(file=file,rows=len(values),file_offset=at,sha256=hashlib.sha256(bytes(values)).hexdigest(),physical_pages=pages)
 source_table('kirby_art.inc','KbBodyChr');source_table('kirby_art.inc','KbFullChr');source_table('meta_knight_art.inc','MkBodyChr');source_table('tmnt_art.inc','TnBodyChr',512)
 # Existing exact-source body domains already include Roll's +2/+3 weapon
 # windows and all Viper/death selectors. Bind the actual publication source
 # contracts; a sequential body base is never an implied adjacent1KB reader.
 contracts={
  'src/tmnt_draw.s':['lda SmChrBank\n ldx #>TN_FIRST_CHR\n ldy #0\n farcall X5SetPhysicalChr'],
  'src/tmnt_equipment_draw.s':['lda #.lobyte(628)','sta SsChrPhysical'],
  'src/kirby_draw.s':['lda SmChrBank\n  ldx #>KB_FIRST_CHR\n  ldy #0\n  farcall X5SetPhysicalChr'],
  'src/kirby_core.s':['lda KbBodyChr,x','lda KbFullChr,x','lda SmChrBank\n  ldx #>KB_FIRST_CHR\n  ldy #0\n  farcall X5SetPhysicalChr,jmp'],
  'src/meta_knight.s':['lda MkBodyChr,x\n  sta SmChrBank'],
  'src/roll_render.s':['adc #2\n ldx RlPoolChrHi,y\n ldy #6','adc #3\n ldx RlPoolChrHi,y\n ldy #7'],
  'src/vic_render.s':['lda SmChrBank\n ldx #1\n ldy #0\n farcall X5SetPhysicalChr,jmp'],
  'src/metasprite_engine.s':['PlayerBankReady:\n      cmp PlayerChrBank','sta PlayerChrBank\n        inc ReloadCHRBank']}
 for p,clauses in contracts.items():
  t=(R/p).read_text()
  for clause in clauses:assert clause in t,(p,clause)
 # Later declared owners were absent from the older target-specific upper2
 # proposal. Retain their full spans conservatively, not inferred gaps.
 for name,lo,hi in [('RCR extra',677,680),('Kamikaze',696,700),('Full roster preview',700,704),('RCR',716,724),('Ex granted',728,740),('Celeste',740,756),('SMB2 roster',796,808),('GB Pit',808,813),('MAAA',813,816),('Gimmick',816,820),('DonkeyKong',820,824),('Bowser',824,827),('Later upper3 owners',832,1024)]:domains[name]=list(range(lo,hi))
 replacement=json.loads((O/'replacement-pages.json').read_text())
 assert replacement['passed']and replacement['ROM_sha256']==SHA
 assert replacement['replacement_candidates']==[690,691,692,693,695,795]
 for name,pages in replacement['Rogue_actual_domains'].items():domains['Rogue '+name]=pages
 domains['DragonPower actual body and wave']=replacement['DP_actual_body_and_both_shots_pages']
 domains['Bub Bob root reservation']=sorted(BUB_RESERVED)
 collisions={n:sorted(set(p)&set(POOL))for n,p in domains.items()if set(p)&set(POOL)};assert not collisions,collisions
 proposed=[dict(page=p,preimage_sha256=hashlib.sha256(raw[1048592+p*1024:1048592+(p+1)*1024]).hexdigest())for p in POOL]
 q=dict(passed=True,proposal_only=True,resource_granted=False,ROM_sha256=SHA,proposed_physical_CHR_pages=POOL,physical_page_count=len(POOL),bytes=1024*len(POOL),complete_publication_retest=False,domains=domains,current_table_proofs=tableproof,source_publication_contracts=contracts,preimages=proposed,remaining=['Current native setter/publication/lag-NMI cuts must be rerun for every proposed upper1+upper2 pair.','Root must review original/current consumer closure and grant these exact pages before any ROM write.','No resident PRG grant; exact current source funding and measured loader/router fit still required.','42579-byte source payload fits42pages only with packed tails and typed offsets; no loader or packed host admission implemented.'],bindings={str(p.relative_to(R)):sha(p)for p in [Path(__file__),ROM,O/'writer-preservation.json',O/'new-owner-pages.json',O/'upper2-finite-domains.json',O/'smb3-pages.json',*[R/p for p in contracts]]})
 pubpath=O/'publication-CPU-controls.json'
 if pubpath.exists():
  pub=json.loads(pubpath.read_text())
  assert pub['passed']and pub['current_ROM_sha256']==SHA and pub['proposed_pages']==POOL
  q['complete_publication_retest']=True
  q['publication_controls']=dict(setter_cuts=pub['actual_typed_setter_instruction_cuts'],native_menu_cuts=pub['actual_native_Mario_menu_clear_restore_cuts'],real_lag_NMI_returns=pub['real_NMI_returns'],no_proposed_page_published=pub['no_proposed_page_published'])
  q['remaining'].pop(0);q['bindings'][str(pubpath.relative_to(R))]=sha(pubpath)
 q['consumer_closure_scope']='Finite declared selector domains plus current inherited831 writer preservation and explicit new-owner/cold-loader domains. This is a proposal for root review, not a grant or a universal arbitrary-shadow-value guarantee.'
 q['bindings'][str((O/'replacement-pages.json').relative_to(R))]=sha(O/'replacement-pages.json')
 (O/'pool-proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','domains','source_publication_contracts','preimages','current_table_proofs']}))


if __name__=='__main__':main()
