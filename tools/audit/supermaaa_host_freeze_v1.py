"""Freeze one private genuine SuperMaaa build and finite CPU receipt; no native."""
from pathlib import Path
import json,re,subprocess,sys,difflib,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from sunny_integrated_controls_v1 import *
import supermaaa_host_controls_v1 as Controls
O=R/'build/supermaaa-host-v1';P=R/'build/pit-retold-host-v3'

def dependencies(path):
 text=path.read_text().split(':\t',1)[1].strip().removesuffix(':')
 files=[]
 for word in re.split(r'(?<!\\)\s+',text):
  p=Path(word.replace('\\ ',' '));p=p if p.is_absolute()else R/p
  assert p.is_file(),str(p);files.append(p.resolve())
 return files

def main():
 assert not(O/'handoff.json').exists(),'A frozen handoff is immutable'
 controls=json.loads((O/'controls-draft.json').read_text())
 assert controls['passed']and controls['checks']['foreign_complete_Main']['cases']==156
 assert controls['candidate']==sha(O/'candidate.nes')
 for p,h in controls['bindings'].items():assert sha(p)==h,p
 parent=json.loads((P/'closure.json').read_text())
 for p,h in parent['actual_dependencies'].items():assert sha(p)==h,p
 # A second real assembly/link, using the same true sources and independent
 # objects. Unchanged separate C/skin/GB objects retain their exact genuine
 # parent compile receipt; no binary aliasing or old-ROM patch is used.
 commands=json.loads((O/'draft-commands.json').read_text());executed=[]
 for command in commands:
  command=[v.replace(str(O/'main.o'),str(O/'independent-main.o')).replace(str(O/'main.d'),str(O/'independent-main.d')).replace(str(O/'component.o'),str(O/'independent-component.o')).replace(str(O/'component.d'),str(O/'independent-component.d')).replace(str(O/'candidate.nes'),str(O/'independent.nes')).replace(str(O/'candidate.dbg'),str(O/'independent.dbg')).replace(str(O/'candidate.lbl'),str(O/'independent.lbl'))for v in command]
  result=subprocess.run(command,cwd=R,capture_output=True,text=True);assert not result.returncode,result.stderr
  executed.append(command)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'independent.nes')
 assert(O/'candidate.nes').read_bytes()==(O/'independent.nes').read_bytes()
 assert(O/'candidate.lbl').read_bytes()==(O/'independent.lbl').read_bytes()
 old,b=[scoped_load(x/'candidate.nes')for x in[P,O]]
 # A source-counterfactual CPU negative replays only the exact parent5B lag
 # admission at the same PC. It proves the reason for the guard at a real
 # private body-build cut; no ROM/file is patched and this is not native.
 start=location(old,'NonMaskableInterrupt');oldbytes=old['raw'][start:start+200]
 literal=bytes([173,address(old,'SelectedCharacter')&255,address(old,'SelectedCharacter')>>8])
 at=oldbytes.index(literal);guardpc=address(old,'NonMaskableInterrupt')+at
 original5=oldbytes[at:at+5];assert original5[3]==208
 q=Controls.setup(b,length=80);q.put(SavedJoypadBits=129,NmiDisable=255,DisableScreenFlag=0,Mirror_PPUCTRL=168,Mirror_PPUMASK=30)
 original=NesMPU.step;hit=False;negative=None
 def step(c):
  nonlocal hit,negative
  bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
  if not hit and bank==68 and address(b,'MaaBodyDraw')<=c.pc<address(b,'MaaDrawNeck')and q.get('ReloadCHRBank')==1 and q.get('X5ChrMode')==0x83:
   hit=True;pc=c.pc;sp=c.sp;before=len(q.m.writes);oam=bytes(q.m[0x200:0x300]);fixed=bytes(q.m[guardpc:guardpc+5])
   assert fixed[0]==32 and fixed[3]==176
   for i,v in enumerate(original5):list.__setitem__(q.m,guardpc+i,v)
   c.nmi()
   for _ in range(50000):
    original(c)
    if c.pc==pc and c.sp==sp:break
   else:raise AssertionError('Parent-fragment lag negative timeout')
   writes=[(a,v)for a,v in q.m.writes[before:]if a==0x4014 or 0x5120<=a<=0x5130]
   assert writes and not any(a==0x4014 for a,v in writes)and bytes(q.m[0x200:0x300])==oam and q.get('ReloadCHRBank')==0
   negative=dict(source_counterfactual_CPU_only=True,not_native_or_a_separate_built_ROM=True,actual_private_cut=[bank,pc],same_public_PC=guardpc,exact_parent5B=original5.hex(),new_guard5B=fixed.hex(),observed_CHR_writes_without_DMA=writes,retained_OAM_exact=True,Reload_consumed=True)
   for i,v in enumerate(fixed):list.__setitem__(q.m,guardpc+i,v)
  original(c)
 NesMPU.step=step
 try:Controls.C.M.runtrace(q,'GameLoop')
 finally:NesMPU.step=original
 assert hit and negative
 (O/'lag-publication-negative.json').write_text(json.dumps(negative,indent=2)+'\n')
 for n in['RunGameTimer','ProcessWhirlpools','PlayerOAMReservation','HandleStompedShellE','SBnce','FarCallCommon','NonMaskableInterrupt','OAMandReadJoypad','PostDmaMaskEnable','IrqScrollSplit']:
  assert address(old,n)==address(b,n)and location(old,n)==location(b,n),('fixed/public entry',n)
 assert address(b,'MaaCoreEnd')<=0xb9a8 and address(b,'MaaArtEnd')<=0xdf20
 changed={}
 for bank in range(128):
  a=old['raw'][16+bank*8192:16+(bank+1)*8192];z=b['raw'][16+bank*8192:16+(bank+1)*8192]
  if a!=z:changed[bank]=sum(x!=y for x,y in zip(a,z))
 # Full relinking changes genuine external operands when PLAYER/OBJECT
 # labels move. Outside the edited-source banks accept ONLY authentic
 # complete farcall target fields or complete absolute code-label words.
 direct={0,1,4,9,62,66,68,124,125,126,127};targets={}
 for n,s in old['syms'].items():
  if s.get('type')!='lab'or'seg'not in s or n not in b['syms']or'ooffs'not in old['segs'][s['seg']]:continue
  if address(old,n)==address(b,n):continue
  bank=(location(old,n)-16)//8192
  if(location(b,n)-16)//8192!=bank:continue
  targets.setdefault((bank,address(old,n),address(b,n)),[]).append(n)
 relocations=[]
 for bank in set(changed)-direct:
  a=old['raw'][16+bank*8192:16+(bank+1)*8192];z=b['raw'][16+bank*8192:16+(bank+1)*8192]
  for i in range(8192):
   if a[i]==z[i]:continue
   hit=None
   for low in[i,i-5]:
    if low<1 or low+13>=8192:continue
    if a[low-1]!=169 or z[low-1]!=169 or a[low+4]!=169 or z[low+4]!=169:continue
    if a[low+1:low+4]!=bytes([141,(address(old,'FarcallJmpTarget_SMC')+1)&255,(address(old,'FarcallJmpTarget_SMC')+1)>>8])or z[low+1:low+4]!=a[low+1:low+4]:continue
    if a[low+6:low+9]!=bytes([141,(address(old,'FarcallJmpTarget_SMC')+2)&255,(address(old,'FarcallJmpTarget_SMC')+2)>>8])or z[low+6:low+9]!=a[low+6:low+9]:continue
    if a[low+9]!=169 or a[low+10]!=z[low+10]or a[low+11]not in[32,76]or z[low+11:low+14]!=a[low+11:low+14]:continue
    target=(a[low+10]&127,a[low]+256*a[low+5],z[low]+256*z[low+5])
    if target in targets:hit=['genuine complete farcall target',target,targets[target]];break
   if hit is None:
    for lo in[i,i-1]:
     if lo<1 or lo+1>=8192 or a[lo-1]not in[32,76]or z[lo-1]!=a[lo-1]:continue
     pair=(a[lo]+256*a[lo+1],z[lo]+256*z[lo+1])
     found=[(t,names)for t,names in targets.items()if t[1:]==pair]
     if found:hit=['genuine absolute JSR/JMP linked target',found];break
   assert hit,('Unqualified external relink byte',bank,hex(i),a[i],z[i])
   relocations.append([bank,i,a[i],z[i],hit])
 (O/'external-relink-consumers.json').write_text(json.dumps(relocations,indent=2)+'\n')
 assert old['raw'][1048592:1048592+813*1024]==b['raw'][1048592:1048592+813*1024]
 assert old['raw'][1048592+816*1024:]==b['raw'][1048592+816*1024:]
 assert old['raw'][16+9*8192+0x1fe1:16+9*8192+0x1fef]==bytes([255])*14
 segments=[]
 for v,tag in[(old,'parent'),(b,'candidate')]:
  for g in v['segs'].values():
   if g.get('name','').strip('"')in['PLAYER','OBJECT','BILL_BODY_COLD','MAAA_CORE','MAAA_ART','NEW_ROSTER_GATE']:
    segments.append(dict(build=tag,name=g['name'].strip('"'),start=int(g['start'],0),size=int(g['size'],0),physical=(int(g['ooffs'],0)-16)//8192))
 moved=[]
 for n,s in old['syms'].items():
  if '::'in n or s.get('type')!='lab'or'seg'not in s or n not in b['syms']:continue
  if 'ooffs'not in old['segs'][s['seg']]:continue
  if address(old,n)!=address(b,n)or location(old,n)!=location(b,n):moved.append([n,address(old,n),address(b,n),(location(old,n)-16)//8192,(location(b,n)-16)//8192])
 (O/'relocated-public-labels.json').write_text(json.dumps(moved,indent=2)+'\n')
 deps={str(p):sha(p)for d in['main.d','component.d','independent-main.d','independent-component.d']for p in dependencies(O/d)}
 # Retain exact raw sparse preimages, including CRLF. The human patch is
 # logical LF only; this ZIP permits exact historical-byte reconstruction.
 preimages=json.loads((O/'draft-preimages.json').read_text())
 with zipfile.ZipFile(O/'sparse-preimages.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n,row in preimages.items():
   p=Path(row['path']);assert sha(p)==row['sha256'],p
   info=zipfile.ZipInfo(n,(2026,10,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 ordinary={}
 for name,want in[('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
  p=O/('ordinary-'+name+'.nes');assert sha(p)==want;ordinary[name]=dict(sha256=want,bytes=p.stat().st_size,private_flag_off_build=True)
 closure=dict(passed=True,native_run=False,source_CPU_only=True,fresh_independent_main_and_component_assembly_ROM_and_LBL_exact=True,independent_DBG_byte_exact=sha(O/'candidate.dbg')==sha(O/'independent.dbg'),unchanged_separate_objects='Bound genuine parent C/skin/GB objects and parent compile commands; not relabeled as newly assembled.',actual_dependencies=deps,commands=executed,ordinary=ordinary,changed_PRG_bytes_by_physical_bank=changed,all_other_changed_bank_bytes_only_genuine_relink_operands=len(relocations),CHR_only_pages813_815=True,segments=segments,actual_public_label_moves=len(moved),BILL_BODY_COLD_tail=dict(physical=9,start=0xbfe1,end_exclusive=0xbfef,bytes=14,parent_exact_FF=True,parent_preimage_sha256=__import__('hashlib').sha256(bytes([255])*14).hexdigest(),candidate_end_below_C000=True),bindings={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'independent.nes',O/'independent.dbg',O/'independent.lbl',O/'controls-draft.json',O/'source.patch',O/'sparse-preimages.zip',O/'relocated-public-labels.json',O/'external-relink-consumers.json',P/'closure.json']})
 (O/'closure.json').write_text(json.dumps(closure,indent=2)+'\n')
 report=R/'docs/qa/supermaaa-private-host-2026-10-29.txt'
 ck=controls['checks']
 report.write_text('SuperMaaa private playable source successor\n29 October 2026\n\nParent ac126 GB-Pit v3; candidate '+sha(O/'candidate.nes')+'. No native run or promotion. Author source/ROM facts remain in the unchanged original audit.\n\nExact raw0 / MarioVariant2: Select cycles Mario, Luigi, SuperMaaa, Kamikaze, Celeste. Real Start constructs the active $5C7F counter before gameplay. Authentic timer cadence grows the neck to160; real ordinary stomps halve it; paratroopa demotion and actual 1-Up preserve it; real life loss/fresh game clear it. Existing Mario movement, feet, sides, upgrades, injury, fireballs, audio and scene flow remain the foundation.\n\nAll26 authored records plus23 genuine host throw/swim combinations are packed losslessly into three1KB pages813..815. Original special H-flips, isolated raised head, body/foot anchors and original lower-first neck sequence are retained. '+str(ck['authored_art_pixels']['cases'])+' both-facing pose/length indexed-pattern comparisons pass. No original palette/RGB or native visible-line certification is claimed. Six body slots reserve24B; neck uses only hidden physical slots24..255 after real world/score drawing, up to11 paired parts. Dense eight-sprite flicker remains unavoidable and needs native review; the native Vine40/44 writer is outside the reserved body prefix.\n\nThe raw0 lag NMI normally publishes CHR. The private exact-owner guard now retains CHR/OAM while the image is private and publishes the completed pair on normal NMI. This was found and corrected before freeze; every reached body-build cut and unchanged foreign normal/lag outputs were checked. The guard shares the reclaimed88B native timer span; the genuine stomp pre-bounce prefix moved to A66, retaining public HandleStompedShellE and SBnce addresses and all real score/drop/revival/bounce owners.\n\nNeck coins use the real native erase/credit/score functions, with loop scratch preserved. One additional physical coin can be collected only when its selected native queue is available; Ctrl6 immediately prevents a second grant and defers the area parser exactly as native coin collection does. Busy queues retain the physical coin. This deliberate host scheduling differs from the original scratch-corruption counterexample; no remote grant, repeated reward or queue reset is introduced. Source NMI counts exclude actual DMA stall/PPU alignment; strict native deadline validation remains required.\n\nFinite CPU scope: '+str(ck['foreign_complete_Main']['cases'])+' foreign complete Mains,54 owned Mains,200 consecutive Main/normalNMI timer updates,105 head getters,32 full fireball initializers,24 controller-jump real head/block scenes,3072 complete native stomp cases including all64 flag inputs,32 crowded DrawAll cases,64 capacity boundaries, real earned native pickups/life paths, and actual IRQ/lag seams. Foreign ordinary Main routing costs '+str(ck['foreign_complete_Main']['CPU_delta'])+' CPU; owned sparse Main costs '+str(ck['owned_complete_Main']['CPU'])+' CPU. These are source arenas, not FPS or complete campaign claims. Both ordinary target hashes remain exact d444/f4ffd.\n\nFresh independent assembly/link uses actual ca65 dependencies and genuine separate parent objects, records all real moved labels, and regenerates E125 from final E127. PLAYER grows17B within its23B tail. BILL_BODY_COLD grows14B throughBFEF on the explicit verified FF lease, with17B remaining beforeC000. CORE/ART remain within their approved spans; no new RAM/segment lease or foreign CHR changes.\n\nLimits: native cold Select/lives, real 1-1/scene transitions, actual CHR/PPU/DMA/deadline/camera/graphics/coin-pressure behavior, audio waveform/source-RGB fidelity and long-neck overload remain unrun. Earlier draft art/index/capacity and oracle failures remain in negative-ledger.jsonl. The frozen original audit/host plan is unchanged. Root owns all native tests and any adoption.\n',encoding='utf-8')
 files=[Path(__file__),R/'tools/prepare_supermaaa_host_v1.py',R/'tools/reference/supermaaa_host_core_v1.s',R/'tools/audit/supermaaa_host_controls_v1.py',report,O/'closure.json',O/'controls-draft.json',O/'asset-layout.json',O/'negative-ledger.jsonl',O/'lag-publication-negative.json',O/'source.patch',O/'sparse-preimages.zip',O/'component.s',O/'entrypoint.s',O/'smb1base-mmc5-expanded.cfg',O/'maaa.chr',O/'draft-commands.json',O/'draft-preimages.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'handoff.json',R/'build/supermaaa-neck-audit-v1/host-plan.json',R/'build/supermaaa-neck-audit-v1/proof.json',R/'build/supermaaa-neck-audit-v1/body-native.bin',R/'build/supermaaa-neck-audit-v1/body-native.lbl',R/'build/supermaaa-neck-audit-v1/draw-native.bin',Path(sys.executable)]+list((O/'src').glob('*.s'))
 for m in tuple(sys.modules.values()):
  path=getattr(m,'__file__',None)
  if path and Path(path).is_file()and(str(R/'tools')in str(Path(path).resolve())or'site-packages/py65'in Path(path).as_posix()):files.append(Path(path))
 for command in commands:
  files.extend(Path(v)for v in command if v.endswith(('.o','.exe'))and Path(v).is_file())
 bindings={**deps,**closure['bindings'],**{str(p.resolve()):sha(p)for p in files}}
 for p,h in bindings.items():assert sha(p)==h,p
 handoff=dict(passed=True,private_source_component_only=True,native_run=False,parent_ROM=sha(P/'candidate.nes'),candidate_ROM=sha(O/'candidate.nes'),candidate_DBG=sha(O/'candidate.dbg'),candidate_LBL=sha(O/'candidate.lbl'),report=str(report),controls_sha256=sha(O/'controls-draft.json'),closure_sha256=sha(O/'closure.json'),bindings=bindings,owned_tools=[str(p)for p in files[:4]],root_next_action='Review exact frozen source/closure, then prepare one bounded cold native raw0/variant2 route with unchanged strict hardware/capture guards. No native authorization inferred.',public_adoption=False)
 (O/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ROM=handoff['candidate_ROM'],handoff_sha256=sha(O/'handoff.json'),bindings=len(bindings),changed_banks=changed)))

if __name__=='__main__':main()
