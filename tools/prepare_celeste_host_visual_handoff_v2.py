"""Freeze the compact two-leaf83db visual successor, without native or install."""
from pathlib import Path
import configparser,difflib,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=B/'celeste_host_visual_v2_handoff.json';assert not out.exists()
 base=B/'celeste-host-final.nes';rom=B/'celeste-host-visual-v2.nes';overlay=B/'celeste-host-visual-v2-overlay'
 old=json.loads((B/'celeste_host_handoff.json').read_text());proof=B/'celeste_host_visual_v2_controls.json';q=json.loads(proof.read_text());assert q['passed']and not q['native_run']
 for p,h in old['bindings'].items():assert sha(p)==h,('old frozen dependency',p)
 for p,h in q['bindings'].items():assert sha(p)==h,('new proof dependency',p)
 assert sha(rom)=='413239865daea7ec056567f4f53b9ba90ec44866b2fc23a1585a3a548b615615'and sha(rom)==sha(B/'celeste-host-visual-v2-rebuild.nes')
 assert sha(B/'celeste-host-visual-v2-mmc3.nes')=='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'
 assert sha(B/'celeste-host-visual-v2-mmc5.nes')=='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'
 pre=base.read_bytes();now=rom.read_bytes();fflo=16+81*8192+0x1ebd;ffhi=16+81*8192+0x1f60
 assert set(pre[fflo:ffhi])=={255}
 patch=[];source={}
 for name in['celeste_mario_host.s','x5_menu_ui.s']:
  a=(R/'src'/name).read_text();z=(overlay/'src'/name).read_text();source['src/'+name]=dict(original_sha256=sha(R/'src'/name),successor_path=str(overlay/'src'/name),successor_sha256=sha(overlay/'src'/name))
  patch+=list(difflib.unified_diff(a.splitlines(True),z.splitlines(True),fromfile='a/src/'+name,tofile='b/src/'+name))
 patchpath=B/'celeste_host_visual_v2.patch';patchpath.write_text(''.join(patch),encoding='utf-8')
 options=configparser.ConfigParser();options.optionxform=str;options.read(R/'build_options.ini');defs={k:v for s in options.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 dep=B/'celeste_host_visual_v2.d';obj=B/'celeste_host_visual_v2.o'
 cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(overlay/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(overlay),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(obj)]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 cmd+=[str(B/'celeste-host-visual-v2-objects/entrypoint.s')]
 result=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_host_visual_v2_closure.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
 words=re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':'));deps={}
 for word in words:
  p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file(),p;deps[str(p)]=sha(p)
 for name in['little_mac_terrain.s','tmnt_mac_probes.inc']:
  assert str((B/'celeste-host-overlay/src'/name).resolve())in deps
  assert str((R/'src'/name).resolve())not in deps
 for name in['celeste_mario_host.s','x5_menu_ui.s']:
  assert str((overlay/'src'/name).resolve())in deps
  assert str((R/'src'/name).resolve())not in deps
 owned=['tools/prepare_celeste_host_visual_v2.py','tools/prepare_celeste_host_visual_handoff_v2.py','tools/audit/celeste_host_portrait_counterexample_v1.py','tools/audit/celeste_host_visual_controls_v2.py','docs/qa/celeste-mario-host-visual-successor-2026-10-28.txt']
 report=R/owned[-1]
 report.write_text('Celeste visual successor413239 -- SOURCE/CPU ONLY\n\nParent83db and2f3d handoff remain unchanged. ROOT native83db showed black sky; actual CPU confirms cold menu/lives render native small-Mario record29 (8OAM bytes) under C98. Retained negative fa10ea25. No physics, tier, movement, collision or art bytes change.\n\nTwo sparse leaves only: X5PortraitRender same-span tail targets a genuine cold host wrapper. Exact raw0/variant4 selects authenticated pose25, publishes C98/CHR and refreshes real HpPrepareNativePointers before DrawMetasprite. Foreign portraits use their original renderer. CmHostColors keeps its original span and queues the existing X5QueueAreaBackdrop before CmColors. BackgroundColorCtrl/AreaType retain native ownership; no constant sky replacement. The84B queue admits backdrop only offset<80; body palette requires resulting offset<78. Busy calls defer rather than overwrite the next byte.\n\nAll old named code/RAM addresses exact; only compile-time _FARCALL_COUNT1372->1378. PRG81 changes181B and PRG99 changes3 target bytes; CHR/all otherbanks exact. New genuine host tail endsBF5F in original FF; no allocator changes. Frozen Mac-v5 terrain/probes remain pinned, not current ROOT Mac33d.\n\nFresh actual-CPU controls:24 whole menu/lives portrait calls,48 foreign portraits/full AXYP/SP/application RAM/orderedwrites/banks,32 complete GetPlayerColors->UpdateScreen native background cases,84offsets x64flags=5376 queue-canary cases,22 complete hot GameLoops byte/cycleexact,99 real-vector IRQ seams. Menu/lives show actual four8x16 authored parts; this is source OAM/CHR evidence, not native pixels. Foreign cold portrait cost+135..142CPU; GetColors+158..161CPU plus120UpdateScreen cycles for the required background store. No hot-loop/FPS improvement claim.\n\nIndependent rebuild reproduces413239; ordinary MMC3d444/MMC5f4ffd exact. Helper99 unchanged apart from real target; new host81 IRQ seams covered. Finite source arenas do not establish every menu/lives/area native visual or deadline. ROOT must run exact successor and inspect true backdrop/portrait. Original83db powered route passed only earned walljump traversal; tier0 accommodations and dash/flower native coverage remain open.\n\nQualification-tool negatives retained: no-ooffs RAM symbols and compile-time FARCALL_COUNT were mistaken metadata assumptions, corrected without masking any code/RAM symbol. Initial zero-OAM portrait hypothesis was rejected; actual old two-partMario output retained. Initial unqualified compile5532 lacked the final explicit84B admission; its build receipt is retained, never native-run/qualified.\n\nIntegration after review: apply normalized build/celeste_host_visual_v2.patch to the same exact two frozen source preimages while preserving original EOL. No shared source installed by this tool. Use sparse build command in handoff; parent Mac-v5 bindings must remain explicit in later composition.\n',encoding='utf-8')
 bindings=dict(deps)
 files=[Path(__file__),B/'celeste_host_handoff.json',proof,B/'celeste_host_portrait_negative.json',B/'celeste_host_visual_v2_metadata_negative.json',B/'celeste_host_visual_v2_macro_count_negative.json',B/'celeste_host_visual_v2_build.json',base,base.with_suffix('.dbg'),base.with_suffix('.lbl'),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),B/'celeste-host-visual-v2-rebuild.nes',B/'celeste-host-visual-v2-mmc3.nes',B/'celeste-host-visual-v2-mmc5.nes',patchpath,overlay/'smb1base-mmc5-expanded.cfg',dep]+[R/f for f in owned]
 for p in files:bindings[str(p.resolve())]=sha(p)
 hand=dict(passed=True,source_CPU_only=True,native_run_by_this_agent=False,parent_ROM_sha256=sha(base),parent_handoff_sha256=sha(B/'celeste_host_handoff.json'),ROM=str(rom),ROM_sha256=sha(rom),DBG_sha256=sha(rom.with_suffix('.dbg')),LBL_sha256=sha(rom.with_suffix('.lbl')),source_changes=source,source_patch=str(patchpath),source_patch_sha256=sha(patchpath),proof=str(proof),proof_sha256=sha(proof),ordinary=dict(mmc3=sha(B/'celeste-host-visual-v2-mmc3.nes'),mmc5=sha(B/'celeste-host-visual-v2-mmc5.nes')),independent_rebuild_exact=True,actual_ASM_dependencies=len(deps),assembly_dependency_command=cmd,owned_publication_files=owned,bindings=bindings,build_command=[sys.executable,'tools/build_mmc5_expanded.py','--source-overlay','build/celeste-host-visual-v2-overlay','--output','build/UNBOUND-celeste-visual-rebuild.nes'],limits=['No native acceptance or adoption; ROOT owns native.','Mac-v5 collision baseline remains pinned; current Mac33d needs separate composition.','Tier0 traversal and full earned dash/flower scope remain open.','Added actual backdrop command costs120 decoderCPU and requires native deadline review.'])
 out.write_text(json.dumps(hand,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,handoff=str(out),sha256=sha(out),bindings=len(bindings),dependencies=len(deps))))
if __name__=='__main__':main()
