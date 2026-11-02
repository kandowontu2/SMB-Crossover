"""Focused exact-current finite readers/loaders; no ROM or shared mutations."""
import collections,hashlib,json,re,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_bubble_bobble_component_1101_v2 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import check_hogan_current_bounded_v1 as M
O=P.O;ROM=R/'build/excitebike-pose-1101-v3/current3.nes'
PIN='37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
CODE=[301,305,337,362,363,440,819,666];ART=[441];TARGETS=set(CODE+ART)
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
 b=scoped_load(ROM);raw=b['raw'];assert sha(raw)==PIN
 d=json.loads((R/'build/metal-storm-chr-closure-1101-v10/source-domains.json').read_text())
 f=json.loads((R/'build/shinobi-chr-closure-1101-v1/upper2-finite-domains.json').read_text())
 prior=json.loads((R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json').read_text())
 def table(name,n):
  at=location(b,name);v=raw[at:at+n];assert len(v)==n;return v
 tables=[]
 for name,x in d['current_linked_tables'].items():
  now=table(name,x['count']);assert list(now)==x['values'];tables.append(dict(name=name,bytes=len(now),SHA256=sha(now)))
 for name,x in f['tables'].items():
  now=table(name,x['bytes']);assert sha(now)==x['sha256'];tables.append(dict(name=name,bytes=len(now),SHA256=sha(now)))
 domains={k:v['physical_pages']for k,v in d['exact_source_domains'].items()if k!='WWF every input byte'}
 domains.update(f['domains'])
 # Complete current Parodius pools, including intentionally zero special846.
 pn={}
 for kind in['Body','Special','Pickup']:
  lo=table('PnPool'+kind+'Lo',18);hi=table('PnPool'+kind+'Hi',18)
  pn[kind]=[a+256*z for a,z in zip(lo,hi)];domains['Parodius '+kind]=pn[kind]
 domains['Parodius death']=[892,956,1020]
 assert 846 in pn['Special'];assert 846 not in TARGETS
 domains.update({'Arthur body/common':list(range(868,881)),'Gimmick typed constants':[816,818],'DonkeyKong typed body':list(range(820,824)),'Bowser typed body':list(range(824,827)),'Battletoads typed body':list(range(915,919))})
 # Actual WWF cold code source table and each source-bounded1687B metadata
 # copy.667 is deliberately read as a shared zero carrier;666 is not read.
 wf=[512+x for x in table('WfPageSourceTable',24)]
 offsets=[int.from_bytes(table('WfMetadataOffsets',12)[i:i+2],'little')for i in range(0,12,2)]
 meta=sorted({658+j//1024 for off in offsets for j in range(off,off+1687)})
 assert set(wf)==set(range(637,658))|{667} and meta==list(range(658,666))
 domains['WWF cold source']=wf;domains['WWF six metadata copies']=meta
 wf_old=Path(next(k for k in f['bindings']if k.replace('\\','/').endswith('/kirby-approach-owner-1101-v3/candidate.nes')))
 old=wf_old.read_bytes();assert sha(old)==f['bindings'][str(wf_old)]
 wfbank=16+96*8192;assert raw[wfbank:wfbank+8192]==old[wfbank:wfbank+8192]
 wfmeta=1048592+658*1024;assert raw[wfmeta:wfmeta+8192]==old[wfmeta:wfmeta+8192]
 runtime=R/'build/wwf-roster-native-1101-v1/runtime.s';runtime_key=next(k for k in f['bindings']if k.replace('\\','/').endswith('/wwf-roster-native-1101-v1/runtime.s'));assert sha(runtime.read_bytes())==f['bindings'][runtime_key]
 # The three newer owners' actual ROM map leaves, not historical map results.
 def labels(path):return P.labels(R/path)
 ms=labels('build/metal-storm-idle-shots-1101-v41/component.lbl')
 mt=labels('build/mario-tank-visible-host-1101-v5/graft.lbl')
 # Local labels are intentionally not exported by the release assembler.
 # Resolve each exact source instruction body uniquely in its owned span.
 bank65=raw[16+65*8192:16+66*8192]
 shpat=rb'\xa6\x05\xbd..\x8d\x30\x51\xbd..\x8d\x23\x51\xa9\x00\x8d\x30\x51'
 exhex=bytes.fromhex('a9028d3051a50509d88d2351a0008c3051')
 hit=list(re.finditer(shpat,bank65[0x800:0xe00],re.S));assert len(hit)==1
 shmap=0xa800+hit[0].start();at=bank65.find(exhex,0xe00,0x1108);assert at>=0 and bank65.find(exhex,at+1,0x1108)<0;exmap=0xa000+at
 maps=[('ShMapRow',shmap,65,9,3),('Ms8Map',ms['Ms8Map'],34,12,11),('MtMapCodeV4',mt['MtMapCodeV4'],82,1,11),('ExMapRow',exmap,65,8,3)]
 seed=M.fresh(b);mapped={}
 for name,pc,bank,count,window in maps:
  seg='BB_audit_'+name;b['segs'][seg]=dict(start=str(pc),ooffs=str(16+bank*8192+(pc&8191)));b['syms'][name]=dict(val=str(pc),seg=seg)
  pages=[]
  for row in range(count):
   m=M.fork(seed);M.put(m,R2=row);M.invoke(m,name);pages.append(m.chr_latches[window])
  mapped[name]=pages;domains[name+' current cold source']=pages
 assert mapped['ShMapRow']==[506,507,508,509,510,513,515,516,517]
 assert mapped['Ms8Map']==[247,248,249,250,827,828,829,830,831,500,494,499]
 assert mapped['MtMapCodeV4']==[501]and mapped['ExMapRow']==list(range(728,736))
 def romat(bank,pc,n):return raw[16+bank*8192+(pc&8191):16+bank*8192+(pc&8191)+n]
 shtab=bytes.fromhex('f7f8f90581818182');assert bank65.count(shtab)==1
 shbody=[a+256*(z&3)for a,z in zip(shtab[:4],shtab[4:])]
 assert shbody==[503,504,505,517];domains['Shinobi body']=shbody
 render=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in[831,500,494])
 lo=render[ms['MsBodyPhysicalLo']-0xcd00:ms['MsBodyPhysicalLo']-0xcd00+5];hi=render[ms['MsBodyPhysicalHi']-0xcd00:ms['MsBodyPhysicalHi']-0xcd00+5]
 metal=[a+256*z for a,z in zip(lo,hi)];assert metal==list(range(495,500));domains['Metal body/shot']=metal
 domains['Tank own art']=[502];domains['Excitebike body']=list(range(736,740))
 # Existing other cold-loader bounds are source-owned finite ranges. Their
 # individual hardware stores are rebound below; no old archive tree restored.
 domains.update({'Karnov cold actor/HUD':list(range(399,407))+list(range(1019,1024)),'FinalFantasy cold':list(range(788,796)),'Quick cold':list(range(884,893)),'Bowser cold':list(range(927,935)),'Battletoads cold':list(range(919,927)),'ContraForce cold':list(range(935,959))})
 collisions={k:sorted(TARGETS&set(v))for k,v in domains.items()if TARGETS&set(v)};assert not collisions,collisions
 # Rebind original native writes only to nativeROM, never confuse a WRAM
 # sideoutput offset with an offset into the complete cartridge.
 native=[];side=collections.defaultdict(list)
 for x in prior['unchanged_inherited_writers']:
  if x['file'].replace('\\','/').endswith('/candidate.nes'):
   at=x['file_offset'];old=bytes.fromhex(x['current_bytes']);assert raw[at:at+len(old)]==old,(x['segment'],at);native.append(x)
  else:side[x['file']].append(x)
 # Bind the exact source image containing each of15 prior WRAM writes to its
 # current complete1KB physical content. Only these four8KB inputs are read.
 sidebound=[];z=None
 for file,rows in side.items():
  ref=prior['readonly_image_inputs'][file];path=Path(file)
  if path.exists():image=path.read_bytes();origin='live exact input'
  else:
   if z is None:z=zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip')
   image=z.read('objects/'+ref['sha256']);origin='one indexed binary in memory'
  assert sha(image)==ref['sha256']
  chunks=[]
  for ix in sorted({x['file_offset']//1024 for x in rows}):
   data=image[ix*1024:(ix+1)*1024];pages=[p for p in range(1024)if raw[1048592+p*1024:1048592+(p+1)*1024]==data]
   assert pages,(file,ix);chunks.append(dict(chunk=ix,current_physical_pages=pages))
  sidebound.append(dict(input=path.name,SHA256=sha(image),writes=len(rows),origin=origin,chunks=chunks))
 if z:z.close()
 # All14 inherited replaced writer records belonged to the separately
 # source-closed Karnov lease. Bind its complete live lease and all actor/art/
 # HUD carrier bytes to that exact c864 receipt, rather than ignoring them.
 kr=json.loads((R/'build/metal-storm-chr-closure-1101-v10/replaced-owner-controls.json').read_text())
 oldpath=Path(next(k for k in prior['readonly_image_inputs']if k.replace('\\','/').endswith('/candidate.nes')));krraw=oldpath.read_bytes();assert sha(krraw)==kr['current_ROM_sha256']
 lo,hi=kr['resident_owned_interval'];krlease_changes=[i for i in range(lo,hi)if raw[i]!=krraw[i]]
 kmap=kr['current_native_carrier_map'];at=kmap['file_offset'];body=bytes.fromhex(kmap['hex']);assert raw[at:at+len(body)]==body
 for page in list(range(407,412))+list(range(1019,1024)):
  lo=1048592+page*1024;assert raw[lo:lo+1024]==krraw[lo:lo+1024],page
 # Known later Start trampoline and source-platform cookie are explicit.
 # Three older restore-call immediate operands remain separate review input.
 known=[]
 for path in[R/'build/karnov-native-platform-1101-v1/assembly.json',R/'build/metal-storm-menu-1101-v15/menu-assembly.json']:
  packet=json.loads(path.read_text())
  for p in packet['patches']:
   at=p['offset'];after=bytes.fromhex(p['new'])
   if 243264<=at<245696:
    assert raw[at:at+len(after)]==after,p['role'];known.extend(range(at,at+len(after)))
 tank_manifest=json.loads((R/'build/mario-tank-visible-host-1101-v5/candidate-patches.json').read_text())
 for p in tank_manifest['patches']:
  if p['owner']!='MtFreshV5':continue
  at=p['file_offset'];after=bytes.fromhex(p['new_hex']);assert raw[at:at+len(after)]==after;known.extend(range(at,at+len(after)))
 # Exact owning-source continuation preserves genuine ThSceneInit, then
 # invokes the already audited Tank own-carrier loader.
 fresh=(R/'build/mario-tank-visible-host-1101-v5/MT_CONTACT.bin').read_bytes()
 grant=json.loads((R/'build/mario-tank-visible-host-1101-v5/graft-assembly.json').read_text());lease=next(x for x in grant['source_owner_intervals']if x['name']=='MT_CONTACT')
 assert sha(fresh)==lease['sha256'];at=16+78*8192+lease['physical_offset'];assert raw[at:at+len(fresh)]==fresh
 fresh=fresh[mt['MtFreshV5']-lease['run_PC']:]
 assert fresh[:18]==bytes.fromhex('8d6a01a97e8d6c01a9b58d6d01a9d5205a01')
 assert fresh[18:36]==bytes.fromhex('8d6a01a9698d6c01a9bf8d6d01a99f205a01')and fresh[36]==96
 kunknown=[dict(file_offset=i,PC=0xa000+(i-16)%8192,old=krraw[i],new=raw[i])for i in krlease_changes if i not in known]
 assert not kunknown,kunknown
 # Re-run all established menu states through the actual current resolver,
 # retirement/queue and publisher. Slot29 now has the exact new raw37 gate.
 inventory=json.loads((R/'build/playable-menu-1101-v4/inventory.json').read_text());variants=sorted({n for x in inventory['rows']for n in x['variants']});menupages=set();menu=[]
 for row in inventory['rows']:
  m=M.fresh(b);M.put(m,**{n:0 for n in variants});M.put(m,CrossoverMenuIndex=row['slot'],**row['variants']);M.invoke(m,'MenuResolveCharacter');actual=M.get(m,'SelectedCharacter')
  expected=37 if row['slot']==29 and not row['variants'].get('FmAlts',0)&16 else row['raw'];assert actual==expected,(row['name'],actual,expected)
  M.invoke(m,'QueueSelection');M.invoke(m,'X5PublishChr');pages=list(m.chr_latches);assert not TARGETS&set(pages),(row['name'],pages);menupages.update(pages);menu.append(dict(slot=row['slot'],raw=actual,pages=pages))
 # Current Ex delta is the single explicit new writer/loader owner over6f.
 manifest=json.loads((R/'build/excitebike-pose-1101-v3/current3-composition.json').read_text());assert manifest['ROM_SHA256']==PIN and manifest['exact_disjoint_delta']
 private=json.loads((O/'native-leaves-layout.json').read_text())
 q=dict(passed=True,ROM_SHA256=PIN,host_bytes_written=False,resource_granted=False,complete_current_publisher_closure=False,proposed_code=CODE,proposed_art=ART,preimage_SHA256={str(p):sha(raw[1048592+p*1024:1048592+(p+1)*1024])for p in CODE+ART},all_proposed_zero=all(not any(raw[1048592+p*1024:1048592+(p+1)*1024])for p in CODE+ART),current_table_bindings=tables,finite_domains={k:sorted(set(v))for k,v in domains.items()},actual_current_cold_maps=mapped,WWF_metadata_offsets=offsets,WWF_zero_carrier667_retained=True,WWF_runtime_PRG96_and_metadata_current_exact=True,WWF_existing_source_selector_cases=f['WWF_selector_cases'],rejected846=dict(owner='Parodius pool3 special',actual_page=pn['Special'][3]),native_inherited_writes_exact=len(native),private_image_write_bindings=sidebound,Karnov_cold_map_art_HUD_exact=True,Karnov_known_source_changes_bound=True,Karnov_unrebound_restore_operands=kunknown,menu_states=menu,menu_published_pages=sorted(menupages),private_code_bytes=private['total_used_bytes'],private_code_carriers=private['physical_code_carriers_needed'],remaining=['Actual current typed-setter/native-menu/lag-NMI instruction cuts for this nine-page set.','Three Karnov restore-call immediate operands atPRG29 B925/B92A/B92F changed versus c864: identify/bind later source target (actual map/art/HUD are unchanged).','Owner retirement seam is not implemented for Bub/Bob: only private compiled BbNativeRetire exists; new two-header authenticated resident owner transition must be designed/funded.','Bub/Bob resident loader/authentication/shared route funding remains unimplemented; no assumed reuse of owner-specific Ex556B loader.'],scope='Focused existing44tables, actual current Tank/Metal/Sh/Ex cold mapping leaves, exact live body/source/WWF loader domains, source-clamped WWF code+metadata,816 native +15 private inherited writes; known Karnov later changes identified, three restore operands remain explicit.92 actual current menu publication states include raw37. Physical grant pending publication/retirement review. No ROM/menu/native emulator/install changes.')
 assert q['all_proposed_zero'];(O/'current3-domain-rebind.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ROM_SHA256=PIN,code=CODE,art=ART,table_bindings=len(tables),native_writes=len(native),private_writes=sum(x['writes']for x in sidebound),cold_map_rows=sum(map(len,mapped.values())),grant=False)))


if __name__=='__main__':main()
