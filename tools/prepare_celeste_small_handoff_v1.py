"""Compact all-flags/continuation supplement and actual dependency freeze."""
from pathlib import Path
import configparser,itertools,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from celeste_small_controls_v5 import *
def main():
 out=B/'celeste_small_handoff_v1.json';assert not out.exists()
 proof=B/'celeste_small_controls_v5.json';p=json.loads(proof.read_text());assert p['passed']
 for n,h in p['bindings'].items():assert sha(n)==h,n
 old,b=[scoped_load(B/n)for n in['roster-shared-rcr-adopted-v8.nes','celeste-small-v1.nes']];spec=ref_bundle(old,b)
 rows=[]
 for pose,face,flags in itertools.product(list(range(11))+[22,23,25],[1,2],[p for p in range(256)if p&0x30==0x30]):
  pair=[]
  for bundle in[spec,b]:
   q=cmseed(bundle,2);q.put(PlayerFacingDir=face);c,w,_=(mapped_run if bundle is spec else run)(q,'CmGraphics::Select',a=87,x=pose,y=91,p=flags);pair.append((snap(q,c),cleanwrites(q,w),c.processorCycles))
  assert pair[0][:2]==pair[1][:2],('selector flags',pose,face,flags);rows.append(pair[1][2]-pair[0][2])
 supplement=dict(passed=True,selector_all64_flags_cases=len(rows),selector_extra_CPU=[min(rows),max(rows)])
 # No physical normalization was needed in v5 IRQ setup; its initial page()
 # assignment is an identity before every measured entry. Do not normalize
 # the real interrupted publication gap: complete caller is the oracle there.
 coherent=[]
 for entry in['CmGraphics::Select','CmMovement','CmAfterBG','CmCollisionBox']:
  q=cmseed(b,2);assert q.m.banks[2]==q.get('CurrentBankC')&127;coherent.append([entry,q.m.banks[2],q.get('CurrentBankC')])
 at=location(b,'CmGraphicsBank');pub=b['raw'][at:at+11];assert pub==bytes.fromhex('a9e28da17da9e28d165160')
 supplement['NMI_publication_exact_bytes']=dict(bank=98,entry=address(b,'CmGraphicsBank'),bytes=pub.hex(),interrupt_PC=address(b,'CmGraphicsBank')+5,shadow=address(b,'CurrentBankC'),physical_before=88,published_shadow=226,physical_after_NMI=98,continuation='LDA#E2; STA5116; RTS',all_initial_C_mappings_already_coherent=coherent,no_in_interrupt_mapper_normalization=True)
 # Complete actual death handler caller, full state against small spec.
 death=[]
 for mode,tier in itertools.product([0,1],range(3)):
  pair=eqspec(spec,b,'GameLoop',dict(CrossoverBehaviorVersion=mode,CmTier=tier,GameEngineSubroutine=11,Player_Y_Position=160,Player_Y_HighPos=1,DeathMusicLoaded=1,GameTimerDisplay=4),p=0x71)
  q=pair[1][3];assert q.get('PlayerSize')==1 and q.get('CmPose')==22;death.append([mode,tier,q.get('CmPose'),q.get('Player_BoundBoxCtrl')])
 supplement['complete_death_GameLoop']=death
 # Real sequential upgrade grants retain grip then dash; source setup writes
 # only typed actors, not acquired tier/resource or outcomes.
 grants=[]
 for mode,face in itertools.product([0,1],[1,2]):
  q=cmseed(b,0);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face)
  for typ in[0,1]:
   slot=5;q.set('Enemy_Flag',1,slot);q.set('Enemy_ID',46,slot);q.set('Enemy_State',128,slot);q.set('PowerUpType',typ,slot);run(q,'NrPickup',x=slot);assert q.get('CmTier')==typ+1 and q.get('PlayerSize')==1
  q.put(CmFresh=64,CmState=1,Player_State=1);run(q,'CmWeapons');assert q.get('CmDashReady')>0 and q.get('CmDashStock')==0
  grants.append([mode,face,q.get('CmTier'),q.get('CmDashReady'),q.get('PlayerSize')])
 supplement['sequential_actual_mush_flower_grants_then_dash']=grants
 # Genuine full assembler dependency list, no source clone.
 ov=B/'celeste-small-overlay';cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for v0 in cfg.values()for k,v in v0.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 dep=B/'celeste_small_current.d';obj=B/'celeste_small_current.o';cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(ov/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(ov),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(obj)]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 cmd+=[str(ov/'src/entrypoint.s')];z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_small_current.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stderr
 deps={}
 for word in re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':')):
  f=Path(word.replace('\\ ',' '));f=(f if f.is_absolute()else R/f).resolve();assert f.is_file(),str(f);deps[str(f)]=sha(f)
 for name in['celeste_mario_core_small_host.inc','celeste_mario_render_small_host.inc','celeste_mario_host_entry.s','celeste_mario_host.s']:assert str((ov/'src'/name).resolve())in deps
 for name in['celeste_mario_core.s','celeste_mario_render.s']:assert str((R/'src'/name).resolve())not in deps
 ordinary={m:sha(B/('celeste-small-'+m+'.nes'))for m in['mmc3','mmc5']};assert ordinary=={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}
 report=R/'docs/qa/celeste-always-small-private-2026-10-28.txt'
 report.write_text('''CELESTE MARIO ALWAYS SMALL -- PRIVATE SOURCE/CPU SUCCESSOR

User request: always small, independent of tier. Exact parent shared RCR4cbd; this is NOT the81cdc two-platform candidate. No native/installed/canonical/Downloads/settings changes. Root's previously big powered route is historical evidence only.

Original frozen core/render remain unchanged. Two new host derivative includes retain original instruction and record PCs, remove the core's PlayerSize0 store with three same-span NOPs, expose native small bbox1, and map the real selectors to ORIGINAL small records:0..9->12..21,10->23,22->22,25->23. HostEnsure always publishes PlayerSize1; portrait explicitly23. All runtime selectors stay0..10/22/23/25. Internal unproduced11/24 remain unchanged; no invented small throw/intermediate art. Authentic native SKilledGFX=pose22 and SStandGFX=pose23 verified against the original compiled bank7 table and ROM/CHR. Both-facing small parts retain native+16..31 rows and+32 feet, no world-position shift. Palette/source CHR remain exact.

PlayerStatus/CmTier still0/1/2. Genuine pickup still grants tier1 grip and tier2 dash. Tier0 does not gain wall grip. Kernel jump, acceleration, fractional motion, dash/boost/coyote/gravity constants and all map/actor/helper records remain exact. No new RAM, segment, CHR or NMI work. Previous145 traversal census/platform81cdc remains frozen, unlaunched and superseded for body-size assumptions; no universal unpowered-clear claim.

Actual PlayerCtrlRoutine now takes bbox1 from PlayerSize1; MegaManCollisionBox raw0 preserves incoming Y. Actual PlayerBGCollision raw0 rejects custom adder and uses native small row14: head+18, feet+32, sides+24. Original native bbox=[3,20,13,32] retains its transparent inset within the+16..31 visible art. Export CmCollisionBox has no current runtime callers, so its tiny fix is NOT the basis of collision acceptance. Real source BG->AfterBG detects correct side bits, gives tier1/2 wall grace10, then accepts fresh-A wall jumps both faces; tier0 keeps no grace/jump. A former big-head-only solid above the small body no longer bumps it; the real small head still stops upward movement.

Exact intentional source/spec equivalence: original parent with only requested size/store/bbox edits, and an independent CPU-side X translation at the original Select instruction from the authenticated mapping. Full final AXYP/SP/application RAM/ordered writes/banks/5SMC compare with no Celeste state or register exclusions. This is not equivalence to the intentionally superseded big body. Original foreign full GameLoops remain byte/state/cycle exact in92 finite cases. All old runtime labels/RAM/CHR/all other banks are unchanged. No broader stack-byte identity claim: inherited comparator excludes dead stack, and compares full returned SP plus live stack during IRQ/NMI.

Retained negatives: v1 incorrectly demanded Local_eb14 after later side probes advanced scratch to19; v2/v3/v4 demanded immediate physical C equality at the unchanged BankPRGC shadow-before-hardware publication seam BA12. Actual bytes A9E2 8DA17D A9E2 8D1651 60 publish CurrentBankC226 then write hardware98. A lag NMI between restores98 early; the resumed original store completes98. v5 checks this exact seam through the complete caller on BOTH source-spec and candidate, with full final state/orderedwrites/banks equal; no in-interrupt mapper normalization or bank mask. All338 executed core IRQ boundaries remain physical-entry exact, and9 lagNMI visits cover the new mapper/NOP/box instructions. The initial page assignment in the source IRQ helper is independently proven an identity before each entry, not a repair of interrupted banks.

Fresh ordinaryMMC3d444/MMC5f4ffd exact. New mapper34B98:BDD8..<BDFA within verified552FF-byte tail; only51 ROM bytes differ (81:2,98:49), no graphics data changed. Selector overhead+18CPU and movement padding+2CPU;18 typed empty-map completeGameLoops measure -205..-204 vs original big body because fewer OAM parts/native small branches. Source costs only; no native cadence/FPS or universal performance claim.

Integration after ROOT review: add the two derivative includes to src/, switch only the two includes in celeste_mario_host_entry.s, apply HostEnsure immediate0->1 and portrait25->23 from private host leaf. Original frozen core/render stay intact. Standard tools/build_mmc5_expanded.py --source-overlay build/celeste-small-overlay --output NEW_PRIVATE.nes reproduces candidate while current4cbd source dependencies remain bound. Do not launch old81cdc readiness or install this source-only candidate without ROOT native review. Existing source freeze is dependency bound, not a turnkey fresh-clone external toolchain promise.
''',encoding='utf-8')
 bindings=dict(deps)
 extra=[Path(__file__),proof,dep,report,B/'celeste_small_v1.patch',ov/'smb1base-mmc5-expanded.cfg',R/'tools/build_mmc5_expanded.py',R/'build_options.ini']+[B/('celeste_small_controls_v'+str(n)+'.json')for n in range(1,5)]+[R/('tools/audit/celeste_small_controls_v'+str(n)+'.py')for n in range(1,6)]+[R/'tools/prepare_celeste_small_v1.py']+[B/('celeste-small-v1'+ext)for ext in['.nes','.dbg','.lbl','.map','.build.json']]+[B/('celeste-small-'+m+ext)for m in['mmc3','mmc5']for ext in['.nes','.build.json']]+[B/'celeste_platform_rcr_handoff_v1.json']
 for f in extra:bindings[str(f.resolve())]=sha(f)
 hand=dict(passed=True,source_CPU_only=True,native_run=False,parent_ROM_sha256=sha(B/'roster-shared-rcr-adopted-v8.nes'),ROM=str(B/'celeste-small-v1.nes'),ROM_sha256=sha(B/'celeste-small-v1.nes'),DBG_sha256=sha(B/'celeste-small-v1.dbg'),LBL_sha256=sha(B/'celeste-small-v1.lbl'),proof=str(proof),proof_sha256=sha(proof),actual_ASM_dependencies=len(deps),assembly_command=cmd,layout=p['checks']['layout'],ordinary=ordinary,supplement=supplement,source_overlay=str(ov),report=str(report),owned_files=['tools/prepare_celeste_small_v1.py','tools/audit/celeste_small_controls_v1.py','tools/audit/celeste_small_controls_v2.py','tools/audit/celeste_small_controls_v3.py','tools/audit/celeste_small_controls_v4.py','tools/audit/celeste_small_controls_v5.py','tools/prepare_celeste_small_handoff_v1.py',str(report.relative_to(R))],bindings=bindings,limits=['No native claim or launch.','Old platform81cdc body assumptions superseded; frozen/unlaunched.','Native palette pixels unchanged; class decoding and sourceOAM checked, actual new display/cadence await ROOT.'])
 out.write_text(json.dumps(hand,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,ROM=hand['ROM_sha256'],handoff_sha256=sha(out),bindings=len(bindings),ASM_dependencies=len(deps),supplement=supplement)))
if __name__=='__main__':main()
