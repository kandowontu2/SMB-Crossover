"""Freeze exact small Celeste CHR-owner successor; no native/canonical action."""
from pathlib import Path
import configparser,hashlib,itertools,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[1];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from celeste_small_chr_controls_v2 import *
from celeste_host_visual_controls_v2 import consume,packet

def main():
 out=B/'celeste_small_chr_handoff_v1.json';assert not out.exists();proof=B/'celeste_small_chr_controls_v2.json';p=json.loads(proof.read_text());assert p['passed']
 for n,h in p['bindings'].items():assert sha(n)==h,n
 old,b=[scoped_load(B/n)for n in['celeste-small-v1.nes','celeste-small-chr-v2.nes']];supp={};rows=[]
 for area,outline,ctrl,stock in itertools.product(range(4),[0,1],range(8),[0,1]):
  vals=[]
  for bundle in[old,b]:
   q=setup(bundle,2,area,outline);q.put(BackgroundColorCtrl=ctrl,CmDashStock=stock,VRAM_Buffer1_Offset=0,CmPalette=0);c,w,_=run(q,'GetPlayerColors',p=0x71);data=packet(q);bus=consume(q);vals.append((registers(c),app(q),q.m.banks,data,bus))
  assert vals[0]==vals[1],('palette caller',area,outline,ctrl,stock);rows.append([area,outline,ctrl,stock])
 supp['all_area_backdrop_palette_producer_consumer']=dict(passed=True,cases=len(rows),all_entry_state_ordered_PPU_addresses_values_CPU_exact=True)
 # Real outline leaf runs with its actual bank4 containing its table.
 flags=[]
 for f in[p for p in range(256)if p&0x30==0x30]:
  q=setup(b);q.m.page(1,4);q.set('CurrentBank',132);c,_,_=run(q,'X5PlayerOutlineFlag',a=87,x=0,y=91,p=f);assert c.a==0 and c.x==0;flags.append(f)
 supp['actual_outline_owner']=dict(passed=True,cases=len(flags),raw0_flag=0,required_physical_A=4,original_table_byte=b['raw'][location(b,'PlayerOutlineCharacters')],no_extra_outline_tiles=True)
 # Actual serialized body pixels through mapper publication retain d52 body.
 shapes=[]
 for pose,face in itertools.product(range(12,24),[1,2]):
  vals=[]
  for bundle in[old,b]:
   q=setup(bundle,2);q.put(PlayerFacingDir=face);run(q,'CmGraphics::Select',x=pose);run(q,'CmDraw');run(q,'HpPrepareNativePointers');run(q,'DrawMetasprite',x=233);pages,_=publish(q);vals.append((bytes(q.m[0x200:0x208]),bitmap(q,pages,0,8),pages[0]))
  assert vals[0]==vals[1],('source body publication',pose,face);shapes.append([pose,face,vals[1][1],vals[1][2]])
 supp['all_small_body_published_classes']=dict(passed=True,cases=len(shapes),both_faces_all12_small_poses=True,actual_OAM_and_CHR0_classes_exact_d52=True,rows=shapes)
 ov=B/'celeste-small-chr-v2-overlay';cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for d in cfg.values()for k,v in d.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 dep=B/'celeste_small_chr_current.d';cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(ov/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(ov),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(B/'celeste_small_chr_current.o')]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 cmd+=[str(ov/'src/entrypoint.s')];q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_small_chr_current.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 deps={}
 for word in re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':')):
  f=Path(word.replace('\\ ',' '));f=(f if f.is_absolute()else R/f).resolve();assert f.is_file();deps[str(f)]=sha(f)
 assert str((ov/'src/celeste_mario_render_small_host.inc').resolve())in deps
 assert str((R/'src/celeste_mario_render_small_host.inc').resolve())not in deps
 ordinary={m:sha(B/('celeste-small-chr-'+m+'.nes'))for m in['mmc3','mmc5']};assert ordinary=={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}
 rollback=B/'celeste_small_chr_preimage.zip';assert not rollback.exists()
 with zipfile.ZipFile(rollback,'x',zipfile.ZIP_DEFLATED)as z:z.writestr('src/celeste_mario_render_small_host.inc',(B/'celeste-small-overlay/src/celeste_mario_render_small_host.inc').read_bytes())
 report=R/'docs/qa/celeste-small-chr-ownership-2026-10-28.txt'
 report.write_text('''CELESTE SMALL BODY -- PRIVATE CHR OWNERSHIP SUCCESSOR

Parent exactd52eeefe (always-small body) remains immutable. ROOT observed actual score/enemy glyph corruption on d52 despite successful powered traversal; that native failure is retained. This private source successor has no native run/adoption/install/settings action. Goku phase1 plan is paused; all Goku sources/allocations unchanged.

Cause: CmDraw published four1KB windows0..3. Every legal SMALL record12..23 in both faces has exactly2parts, even source tiles0..50 paired with<=51. Those tile addresses only use window0. Windows1(misc/score) and2/3(world enemies) belong to native area/CHR owners. Setting them to consecutive Celeste pattern pages corrupted actual native glyphs. No palette, source tile, pose, physics or actor data change is needed.

Fix is SAME-SPAN CPY#4->#1, plus a genuine JMP to17B appended98:BDFA..<BE0B. Completion executes three additional INC CmTemp, LDY#4, LDA#1, STA X5WideChrActive, RTS. It preserves original returned AXYP/SP and CmTemp=(source base+4) modulo256, including C/V/D/I/N/Z. No liveness assumption or X/flag mask. Only24 ROM bytes differ, allbank98, allold code/public/internal labels unchanged. CHR/RAM/allotherbanks exact. Native modes/pointers1..11 are preserved; mode0 alone publishes physical740+sourceGfxBank. No attempt to repair polluted old savestates is claimed; use genuine fresh startup/area lifecycle.

Finite source controls:768 leaf cases cover all64flag combinations, both legal source banks plus modulo-wrap stress and three native/already/direct-world states. Complete return registers/CmTemp/banks/5SMC, all other application RAM and ordered stores compare exactly; ONLY the six intended nonbody CHR/mode fields and ReloadCHRBank differ. Reload follows actual window0 dirty ownership. Leaf netCPU -115..-73 vs old4-window code in these cases, including tail repair.

288 actual body+nativeGoomba+score-number mixes across4areas, both outlines, all3tiers, representative walk/jump/swim/climb/death/stand poses/bothfaces: full real DrawMetasprite (enemy nativeY1) and FloateyNumberRender feed the original renderer. Actual X5PublishChr $5130/$5120..2B stores are decoded, and native world/score bitmap classes match the untouched native CHR source. All11 nonbody windows match native area initialization; body window0 matches original source. Additional24all-small records/facings compare serializedbodyOAM+publishedCHR0 classes directly against d52. This is source bitmap-class evidence, NOT captured PPU pixels.

144 whole actualGameLoops with one real Goomba+score actor, bothmodes/allareas/outlines/tiers/idle/walk/jump, preserve full returned AXYP/SP/OAM/banks/5SMC/allotherappRAM/orderedwrites; only those seven explicit CHR/reload fields are intentional.46 foreign wholeGameLoops have full state/store/CPU equality with no such exclusions.7realIRQ+7lagNMI instruction boundaries in new helper preserve full6CPUflags/AXY/PC/SP/live stack/R0..R7/banks/5SMC/Celeste state.128 actual GetPlayerColors->UpdateScreen caller pairs cover all area/backdrop controls, both outline settings and both dash palette states, exact complete queue/PPUstore/CPU; actual raw0 outline flag0 verified at requiredA4 table owner for all64flags. No extra mask/outline tiles are introduced.

Retained preparation negatives: first private CHR v1 rebuilt d52 unchanged because the root-relative host-entry include bypassed an identically named overlay derivative. v2 stages the unchanged host entry and the true dependency list proves the new leaf is consumed. First CPU mixed test used wrong physical CHR base788 (Goku's reservation, not Celeste740) and passed playerY0 to a native enemy renderer, selecting its prepared player pointer. Corrected v2 uses genuine enemyY1/source fields and actual Celeste740; original v1 false retained. No gameplay guard or assertion was waived.

ROOT acceptance still requires fresh actual corner/underground/full-PPU, hardwareDMA/NMI/IRQ/SMC/deadline/cadence inspection on the exact successor. Source cycle savings are not a native/FPS claim. All previous d52 source/native evidence stays historical and is not retagged.

Install after acceptance: ONLY src/celeste_mario_render_small_host.inc from build/celeste-small-chr-v2-overlay/src/. Host-entry overlay is unchanged staging for ca65 relative include correctness. Frozen original core/render and small lifecycle host remain unchanged; standard shared build must reproduce exact candidate. Normal ordinaryMMC3d444/MMC5f4ffd newly rebuilt exact. Exact rollback source is stored in compact preimageZIP; normalized source patch is celeste_small_chr_v2.patch.
''',encoding='utf-8')
 extra=[Path(__file__),proof,dep,rollback,report,B/'celeste_small_chr_v2.patch',B/'celeste_small_chr_build_v1.json',B/'celeste_small_chr_build_v2.json',B/'celeste_small_chr_controls_v1.json',R/'tools/prepare_celeste_small_chr_v1.py',R/'tools/prepare_celeste_small_chr_v2.py',R/'tools/audit/celeste_small_chr_controls_v1.py',R/'tools/audit/celeste_small_chr_controls_v2.py',R/'tools/build_mmc5_expanded.py',R/'build_options.ini',ov/'smb1base-mmc5-expanded.cfg']+[B/('celeste-small-chr-v2'+s)for s in['.nes','.dbg','.lbl','.map','.build.json']]+[B/('celeste-small-chr-'+m+s)for m in['mmc3','mmc5']for s in['.nes','.build.json']]
 bindings=dict(deps)
 for f in extra:bindings[str(f.resolve())]=sha(f)
 rec=dict(passed=True,source_CPU_only=True,native_run=False,parent_SHA256=sha(B/'celeste-small-v1.nes'),ROM=str(B/'celeste-small-chr-v2.nes'),ROM_SHA256=sha(B/'celeste-small-chr-v2.nes'),DBG_SHA256=sha(B/'celeste-small-chr-v2.dbg'),LBL_SHA256=sha(B/'celeste-small-chr-v2.lbl'),proof=str(proof),proof_SHA256=sha(proof),actual_ASM_dependencies=len(deps),assembly_command=cmd,layout=p['checks']['layout'],supplement=supp,ordinary=ordinary,source_leaf=str(ov/'src/celeste_mario_render_small_host.inc'),source_leaf_SHA256=sha(ov/'src/celeste_mario_render_small_host.inc'),report=str(report),owned_files=['tools/prepare_celeste_small_chr_v1.py','tools/prepare_celeste_small_chr_v2.py','tools/audit/celeste_small_chr_controls_v1.py','tools/audit/celeste_small_chr_controls_v2.py','tools/prepare_celeste_small_chr_handoff_v1.py',str(report.relative_to(R))],bindings=bindings)
 out.write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,handoff_SHA256=sha(out),bindings=len(bindings),ASM_dependencies=len(deps),ROM=rec['ROM_SHA256'],DBG=rec['DBG_SHA256'],LBL=rec['LBL_SHA256'],proof=rec['proof_SHA256'],source_leaf=rec['source_leaf_SHA256'])))
if __name__=='__main__':main()
