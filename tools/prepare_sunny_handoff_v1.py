"""Freeze the actual sparse Sunny integration; no install, Git or native run."""
from pathlib import Path
import base64,configparser,difflib,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,indent=2)+'\n',newline='\n')
def main():
 rom=B/'sunny-integrated-final.nes';parent=B/'roster-expansion-mac-integrated-v5.nes';out=B/'sunny_integrated_handoff.json';assert not out.exists()
 assert sha(rom)=='55e874822160c3ab20f9ccfbca8b46cfe3b71c00bc4466a9fa8c5789bf7c0217'
 proofs=[B/'sunny-integrated-final-controls.json',B/'sunny-integrated-final-pipeline.json']
 for p in proofs:
  q=json.loads(p.read_text());assert q['passed'] and q['bindings'][str(Path('build/sunny-integrated-final.nes'))]==sha(rom)
  assert all(sha(Path(k))==v for k,v in q['bindings'].items())
 assert sha(B/'sunny-ordinary-mmc3.nes')=='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'
 assert sha(B/'sunny-ordinary-mmc5.nes')=='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'
 # Capture actual assembler include closure, not a snapshot/copy of the tree.
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for s in cfg.values() for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 dep=B/'sunny_integrated.d';obj=B/'sunny_integrated.o';overlay=B/'sunny-integration-overlay'
 command=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(overlay/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(overlay),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(obj)]
 for k,v in defs.items():command+=['-D',k+'='+v]
 command +=[str(B/'sunny-integrated-final-objects/entrypoint.s')]
 result=subprocess.run(command,cwd=R,capture_output=True,text=True);(B/'sunny_integrated_assembly.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 words=re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':'));deps={}
 for word in words:
  p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file(),p;deps[str(p)]=sha(p)
 assert str((overlay/'src/little_mac_terrain.s').resolve()) in deps
 assert str((R/'src/little_mac_terrain.s').resolve()) not in deps
 assert str((overlay/'src/tmnt_mac_probes.inc').resolve()) in deps
 assert str((R/'src/tmnt_mac_probes.inc').resolve()) not in deps
 # Export exact final diff against the actual shared preimages, not the initial
 # apply-once draft generator (whose layout-negative is intentionally retained).
 pre=json.loads((B/'sunny_integration_preimages.json').read_text());audio=json.loads((B/'sunny_audio_preimage.json').read_text());pre[audio['path']]=audio
 edits={};patch=[]
 for name,v in pre.items():
  before=base64.b64decode(v['base64']).decode().replace('\r\n','\n');after=(R/name).read_text().replace('\r\n','\n')
  if before==after:continue
  edits[name]=dict(before_sha256=v['sha256'],after_sha256=sha(R/name))
  patch+=list(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 name='src/sunny_integration.s';patch+=list(difflib.unified_diff([], (R/name).read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+name));edits[name]=dict(before=None,after_sha256=sha(R/name))
 (B/'sunny_integrated.patch').write_text(''.join(patch),newline='\n')
 old=scoped_load(parent);new=scoped_load(rom);moves=[];missing=[];ram=[]
 def place(bundle,s):
  g=bundle['segs'].get(s.get('seg'),{});return [(int(g['ooffs'],0)-16)//8192 if 'ooffs'in g else None,int(s['val'],0)]
 for name,s in old['syms'].items():
  if name=='_FARCALL_COUNT':continue
  if name not in new['syms']:missing.append(name);continue
  t=new['syms'][name];x,y=place(old,s),place(new,t)
  if x==y:continue
  v=dict(name=name,old=x,new=y)
  if x[1]<0x8000 and name!='_FARCALL_COUNT':ram.append(v)
  else:moves.append(v)
 assert not ram,ram
 write(B/'sunny_integrated_symbol_moves.json',dict(actual_genuine_symbols=moves,missing=missing,RAM_and_SMC_addresses_exact=True,assembler_only_counter='_FARCALL_COUNT1296â†’1331'))
 spans={};guards=[]
 for name,bank,start,end in [('SUNNY_CORE',81,0xb200,0xb700),('NEW_ROSTER_NAMES',81,0xb700,0xc000),('SUNNY_ART',94,0xce00,0xd300)]:
  seg=next(g for g in new['segs'].values()if g['name']=='"'+name+'"');size=int(seg['size'],0);at=16+bank*8192+(start&8191)
  assert int(seg['start'],0)==start and int(seg['ooffs'],0)==at and start+size<=end
  assert old['raw'][at:at+end-start]==bytes([255])*(end-start),(name,'old capacity not FF')
  spans[name]=dict(bank=bank,start=start,bytes=size,end_exclusive=start+size,reservation_end=end,parent_all_FF=True)
 # Leave actual Rogue kernel/art and Celeste pages byte-identical.
 for label,bank,start,end in [('RogueKernel',124,0xb000,0xc000),('RogueArt',94,0xd300,0xe000)]:
  at=16+bank*8192+(start&8191);assert old['raw'][at:at+end-start]==new['raw'][at:at+end-start];guards.append(label)
 chrbase=16+1048576;at=chrbase+724*1024;assert old['raw'][at:at+16384]==bytes(16384);assert new['raw'][at:at+16384]==(R/'chr/characters/sunny.chr').read_bytes();assert old['raw'][chrbase+740*1024:chrbase+756*1024]==new['raw'][chrbase+740*1024:chrbase+756*1024]
 spans['SUNNY_CHR']=dict(pages=[724,739],bytes=16384,parent_all_zero=True,used_native_pages=[724,727]);guards.append('Celeste740..755')
 bank_changes={str(bank):sum(x!=y for x,y in zip(old['raw'][16+bank*8192:16+(bank+1)*8192],new['raw'][16+bank*8192:16+(bank+1)*8192])) for bank in range(128)};bank_changes={k:v for k,v in bank_changes.items()if v}
 write(B/'sunny_integrated_layout.json',dict(passed=True,segments=spans,protected_exact=guards,actual_PRG_changed_bytes=bank_changes,all_old_RAM_SMC_symbols_exact=True,actual_symbol_moves=len(moves)))
 owned=['tools/prepare_sunny_integration_v1.py','tools/prepare_sunny_handoff_v1.py','tools/audit/sunny_integrated_controls_v1.py','tools/audit/sunny_integrated_pipeline_v1.py','src/sunny_integration.s','tools/reference/build_roster_expansion_menu.py']
 relevant=['src/sunny.s','src/sunny_state.inc','src/sunny_art.inc','chr/characters/sunny.chr','chr/characters/sunny-manifest.json','chr/characters/sunny-integration.txt','src/roster_expansion_menu.inc','chr/raw/roster-expansion-menu.bin','chr/characters/roster-expansion-menu.chr','chr/characters/packed-mmc5-roster-expanded.chr','chr/characters/roster-expansion-menu-review.png']
 extra=[B/'sunny-integrated-rebuild.build.json',B/'sunny_integrated_assembly.log',B/'sunny_handoff_export_negative.json',B/'sunny_handoff.json',B/'sunny_component.json',B/'sunny_integrated.patch',B/'sunny_integrated_layout.json',B/'sunny_integrated_symbol_moves.json',B/'sunny_menu_preimages.json',B/'sunny_audio_preimage.json',B/'sunny_integration_preimages.json',B/'sunny-injury-carry-negative.json',B/'sunny-integrated-controls-v1.json',B/'sunny-integrated-pipeline-v1.json',B/'sunny-integrated-link-space-negative.log',B/'sunny-terrain-unqualified-link-negative.log']+proofs
 deps.update({str((R/n).resolve()):sha(R/n)for n in owned+relevant+list(edits)});deps.update({str(p.resolve()):sha(p)for p in extra+[rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),rom.with_suffix('.map'),parent,parent.with_suffix('.dbg')]})
 note='''Sunny runtime integration â€” private source/CPU handoff, 2026-10-28\n\nExact candidate55e87482; source CPU only, no native launch/adoption. New raw23/slot22;0..19 remain,20/21 hidden. Genuine supplied Super Sunny World art,35 original records, inherited Mario-family behavior; no original Sunny powers/music imported. Native SMB music/SFX now used. Mac gray thumbnail uses actual frame48.\n\nFrozen Macv5bc346 is the comparison parent. A tiny sparse overlay retains its old Mac terrain; B's concurrent terrain/probe drafts are deliberately excluded. Apply final normalized sunny_integrated.patch plus generated Sunny menu/assets; initial prepare_sunny_integration_v1.py is historical first-draft only, not the final reproducer. Build command in handoff uses standard builder and explicit sparse overlay.\n\nPASS:7,200 Sunny/Mario native audio updates with exact state/ordered stores; real event buffers complete;66 foreign audio calls;54 full resident caller cases,48 old selector variants,512 native box/adder rows,12 Easy/Hard pickup pipelinesÃ—60ticks, injury60ticks,16 full ForceInjury carry/mode/form pipelines,20 native two-shot/bubble calls,96 graphics/draw cases,90 whole GameLoop source calls,176 foreign dispatcher controls,481 IRQ injections across two suites,actual linked menu navigation/name/ID. Ordinaryd444/f4ffd exact.\n\nCosts measured: resident CV3 helperâˆ’4; expanded selector0; audio foreignâˆ’4..+1, Sunny versus same-build Mario+8. Space-constrained foreground routing adds up to96 on foreign size/flower freeze caller and171 on expanded weapon-tail caller; generic new-dispatch comparisons add0..5. These are real regressions to evaluate natively. No frame-rate/deadline/physical sprite acceptance claim.\n\nLimits: Memory CPU model has no true PPU/DMC/DMA clocks. Leaf native raster proof is inherited exact frozen art; integrated PPUs/native traversal/menu still unrun. Full GameLoop arenas are typed empty-map fixtures, not earned native campaigns. Some internal SMC last-call operands/dead stack slots change with added genuine calls; tests compare full live return/application state and exact IRQ restoration, not dead stack equality. Head/side supplement explicitly checks live AXYP/SP (no full-RAM claim for that isolated comparison).\n\nNegatives retained: direct audio addition exceeded fixed capacity; initial inline admissions exceeded hot bank capacity; audio fixture originally initialized private states unequally; first fireball fixture omitted right viewport boundary. Actual product counterexample: ForceInjury withC0 used frozen leaf's unqualified carry and wrote PlayerStatus9; five-byte integration wrapper now SEC before returning, tested through real caller. B terrain branch-range failure was excluded using preserved baseline.\n'''
 report=R/'docs/qa/sunny-integrated-source-2026-10-28.txt';report.write_text(note,encoding='utf-8',newline='\n');deps[str(report)]=sha(report)
 hand=dict(passed=True,source_CPU_only=True,native_run=False,candidate=str(rom),ROM_sha256=sha(rom),parent=str(parent),parent_sha256=sha(parent),source_changes=edits,owned_files=owned+[report.relative_to(R).as_posix()],generated_assets=relevant[6:],source_bindings=deps,assembly_dependency_count=len(words),actual_assembly_command=command,independent_rebuild=dict(ROM_sha256=sha(B/'sunny-integrated-rebuild.nes'),same_as_final=(sha(B/'sunny-integrated-rebuild.nes')==sha(rom))),build_command=[sys.executable,'tools/build_mmc5_expanded.py','--source-overlay','build/sunny-integration-overlay','--output','build/sunny-integrated-final.nes'],protected_other_owner_spans=guards,menu=dict(rawID=23,slot=22,hidden_slots=[20,21],thumbnail_Mac_frame=48),cost_and_limits_report=str(report),no_shared_character_select_edit=True,ordinary_hashes={'mmc3':sha(B/'sunny-ordinary-mmc3.nes'),'mmc5':sha(B/'sunny-ordinary-mmc5.nes')},native_required=['cold menu/start/reset/area/death','same-work foreign timing cost and Sunny OAM/CHR/PPU deadlines','real pickups/fireballs/bubbles/pause/events/end-level audio'])
 assert all(sha(p)==h for p,h in deps.items());write(out,hand);print(json.dumps(dict(handoff=str(out),sha256=sha(out),bindings=len(deps),ROM=sha(rom))))
if __name__=='__main__':main()
