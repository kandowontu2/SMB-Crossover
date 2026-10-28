"""Freeze the exact source-qualified Celeste integration, without native/install/Git."""
from pathlib import Path
import base64,configparser,difflib,hashlib,json,re,subprocess,sys,zlib
R=Path(__file__).resolve().parents[1];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 out=B/'celeste_host_handoff.json';assert not out.exists()
 rom=B/'celeste-host-final.nes';parent=B/'sunny-integrated-final.nes';overlay=B/'celeste-host-overlay'
 assert sha(rom)=='83db8bdf74dddc4055a52f5ec12526dcddc7a2fe418f24c3e9e1d5252fb6c9e0'
 assert sha(rom)==sha(B/'celeste-host-rebuild.nes')
 proofs=[B/('celeste_host_final_'+n+'.json')for n in['controls','callers_v4','kernel','art','pickup']]
 for p in proofs:
  q=json.loads(p.read_text());assert q['passed'] and q.get('native_run')is False
  if 'ROM_sha256'in q:assert q['ROM_sha256']==sha(rom)
  else:assert q['bindings'][str(Path('build/celeste-host-final.nes'))]==sha(rom)
 assert sha(B/'celeste-host-final-mmc3.nes')=='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'
 assert sha(B/'celeste-host-final-mmc5.nes')=='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'
 # The actual dependency closure proves that no in-progress Mac terrain or
 # probes entered this historical Mac-v5-based candidate.
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 dep=B/'celeste_host_closure.d';obj=B/'celeste_host_closure.o'
 cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(overlay/'src'),'-I',str(R/'src'),'-I',str(R),'--bin-include-dir',str(overlay),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(obj)]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 cmd+=[str(B/'celeste-host-final-objects/entrypoint.s')]
 result=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_host_closure.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
 words=re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':'));deps={}
 for word in words:
  p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file(),p;deps[str(p)]=sha(p)
 for n in ['little_mac_terrain.s','tmnt_mac_probes.inc']:
  assert str((overlay/'src'/n).resolve())in deps
  assert str((R/'src'/n).resolve())not in deps
 assert str((R/'src/celeste_mario_host_state.inc').resolve())in deps
 assert str((R/'src/celeste_mario_state.inc').resolve())not in deps
 pre=json.loads((B/'celeste_host_preimages.json').read_text());changes={};patch=[]
 for n,v in pre.items():
  if n=='src/celeste_mario_host.s':continue # New complete leaf, not an old source preimage.
  raw=zlib.decompress(base64.b64decode(v['zlib_base64']));current=(R/n).read_bytes()
  if raw==current:continue
  before=raw.decode().replace('\r\n','\n');after=current.decode().replace('\r\n','\n')
  assert before!=after,('EOL-only change',n)
  assert (b'\r\n'in raw)==(b'\r\n'in current),('EOL convention changed',n)
  changes[n]=dict(before_sha256=hashlib.sha256(raw).hexdigest(),after_sha256=sha(R/n),bytes=len(current),CRLF=b'\r\n'in raw)
  patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+n,tofile='b/'+n))
 (B/'celeste_host.patch').write_text(''.join(patch),encoding='utf-8',newline='\n')
 new=['src/celeste_mario_host.s','src/celeste_mario_host_entry.s','src/celeste_mario_host_state.inc']
 old=parent.read_bytes();now=rom.read_bytes();protect={}
 def guard(name,lo,hi):assert old[lo:hi]==now[lo:hi],name;protect[name]=dict(bytes=hi-lo,sha256=hashlib.sha256(now[lo:hi]).hexdigest())
 for bank in[94,95]:guard('physical_PRG_'+str(bank),16+bank*8192,16+(bank+1)*8192)
 for bank in[71,72]:guard('physical_PRG_'+str(bank)+'_B000_BFFF',16+bank*8192+4096,16+(bank+1)*8192)
 guard('physical63_palette_and_tail',16+63*8192+0x1800,16+64*8192)
 # Untouched source owners may contain real farcalls to moved PLAYER/roster
 # labels. Prove those exact operand relocations instead of falsely claiming
 # their full linked banks remain byte-identical.
 b=scoped_load(rom);p=scoped_load(parent)
 def position(bundle,s):
  if 'seg' not in s:return None
  g=bundle['segs'][s['seg']];v=int(s.get('val','0'),0)
  if v<0x8000 or int(g.get('ooffs','0'),0)<16:return None
  return((int(g['ooffs'],0)-16)//8192,v)
 refguard={}
 for bank in[62,71,72,78,81,89,93]:
  limit=0x1700 if bank==81 else 8192
  changeset={i for i in range(limit)if old[16+bank*8192+i]!=now[16+bank*8192+i]};covered=set();entries=[]
  for i in range(limit-18):
   aa=old[16+bank*8192+i:16+bank*8192+i+18];bb=now[16+bank*8192+i:16+bank*8192+i+18]
   if aa==bb:continue
   if not(aa[0]==bb[0]==141 and aa[3]==bb[3]==169 and aa[5]==bb[5]==141 and aa[8]==bb[8]==169 and aa[10]==bb[10]==141 and aa[13]==bb[13]==169 and aa[15]==bb[15]and aa[15]in[32,76]):continue
   if any(aa[k]!=bb[k]for k in range(18)if k not in[4,9,14]):continue
   if int.from_bytes(aa[1:3],'little')!=int(p['syms']['SafecallA_SMC']['val'],0)+1:continue
   if int.from_bytes(aa[6:8],'little')!=int(p['syms']['FarcallJmpTarget_SMC']['val'],0)+1:continue
   if int.from_bytes(aa[11:13],'little')!=int(p['syms']['FarcallJmpTarget_SMC']['val'],0)+2:continue
   if int.from_bytes(aa[16:18],'little')!=int(p['syms']['FarCallCommon']['val'],0):continue
   oldtarget=(aa[14]&127,aa[4]+aa[9]*256);newtarget=(bb[14]&127,bb[4]+bb[9]*256)
   names=[n for n,z in p['syms'].items()if position(p,z)==oldtarget and n in b['syms']and position(b,b['syms'][n])==newtarget]
   if not names:continue
   changed={i+k for k in[4,9,14]if aa[k]!=bb[k]};covered|=changed;entries.append(dict(caller_bank=bank,caller_PC=0xa000+i,target_names=names,old_target=oldtarget,new_target=newtarget,changed_offsets=sorted(changed)))
  assert covered==changeset,('unexpected protected-owner modification',bank,sorted(changeset-covered))
  refguard[str(bank)]=dict(all_differences_genuine_farcall_target_operands=True,changed_bytes=len(changeset),entries=entries)
 write(B/'celeste_host_reference_relocations.json',refguard)
 guard('Rogue_A124_AE00_BFFF',16+124*8192+0xe00,16+125*8192)
 # Sunny/RCR prefix source is unchanged; its genuine farcall operands are
 # covered by the strict physical81 prefix relocation proof above.
 base=16+81*8192+0x1b10;assert set(old[base:16+82*8192])=={255}
 diff={}
 for i in range(1048576):
  if old[16+i]!=now[16+i]:diff[str(i//8192)]=diff.get(str(i//8192),0)+1
 assert old[16+1048576:16+1048576+740*1024]==now[16+1048576:16+1048576+740*1024]
 assert old[16+1048576+756*1024:]==now[16+1048576+756*1024:]
 b=scoped_load(rom);p=scoped_load(parent)
 def pos(bundle,s):
  if 'seg'not in s:return None
  g=bundle['segs'][s['seg']];addr=int(s.get('val','0'),0)
  if addr<0x8000 or int(g.get('ooffs','0'),0)<16:return None
  return[(int(g['ooffs'],0)-16)//8192,addr]
 moves=[];missing=[]
 for n,s in p['syms'].items():
  before=pos(p,s)
  if not before:continue
  mapped=n.replace('NrInjuryStatus::','NrLegacyInjuryStatus::')if n.startswith('NrInjuryStatus::')else n
  if mapped not in b['syms']:missing.append(n);continue
  after=pos(b,b['syms'][mapped])
  if before!=after:moves.append(dict(old_name=n,new_name=mapped,old_bank_PC=before,new_bank_PC=after))
 write(B/'celeste_host_symbol_moves.json',dict(genuine_moves=moves,removed_debug_symbols=missing,no_fake_aliases=True))
 calls=json.loads((B/'celeste_host_final_callers_v4.json').read_text())['checks'];rows=calls['foreign_complete_callers']['rows']
 limits=['Original MG WallGrip_Acquired bit2 gates wall grace (Bank08_BGEnemy03_Misc.65s:891). Roster tier0 has no grip; first real Mushroom/Flower projects tier1 grip, tier2 dash. The roughly51px ordinary jump can leave64px SMB pipes unreachable if grip is skipped/lost; no jump boost or hidden unlock is present. Full tier0 traversal accommodations require separate audit/review.','Source/CPU qualification only; no native acceptance or FPS claim. ROOT owns the independent83db native run.','Qualified parent is Sunny55e with preserved Mac-v5 terrain/probes. ROOT must separately compose current Mac33d; those collision fixes are not silently included.','Complete foreign GameLoop compares full final AXYP/SP/application RAM/banks and ordered OAM/nonbank hardware; internal JumpEngine code pointers and bank-routing write sequences are genuine documented changes, not byte-identical intermediate RAM.','Source arenas use typed empty maps; full traversal, dash/wall/camera/pipe/death/spring/body-visible/PPU cadence remain native gates.','Old a350 boolean-owner failure and6f4 status helper failure remain immutable. No source or native results were retagged after persistent relocation.']
 report=R/'docs/qa/celeste-mario-host-integration-2026-10-28.txt'
 report.write_text('Celeste Mario host integration83db -- SOURCE/CPU ONLY\n\nActual identity raw0/MarioVariant4; Select cycles0/1/4, no physics substitution in active8.\nPrivate allocator: Tier5FF8,Marker5FF9,Life5FFA,Area5FFB,World5FFC,Active5FFD; FE/FF untouched. Exact raw0/variant4 gates, never boolean ownership.\nOriginal5F98..9D overlaps Parodius history5F40..BF: bank77 B202 writes5F9D=88, a350 falsely admitted Celeste. Preserved caller-v1 negative. Original component leaves remain unchanged; new host entry/state defines the corrected allocation.\n\nFresh exact-ROM controls:31/2208 source movement;52 authored records/141 linked checks/24 IRQ+NMI seams;72 accepted pickups/36 native Star-life fallbacks/24 seams;144 whole Celeste GameLoops,144 host pickups,32 ForceInjury,96 real head/BG followups,8 full bounce/spring callers,123 host/resident IRQ boundaries. Full DrawAll48 source-art cases restore C98 after an intervening C12 owner.44 foreign profiles x2 modes=88 full callers preserve final CPU/application state; six high-slab canaries survive. Seven-cell name canary and direct-helper full P pass; public farcall retains its real A/NZ contract.\n\nForeign full GameLoop CPU delta '+str([min(x['CPU_delta']for x in rows),max(x['CPU_delta']for x in rows)])+' cycles on those finite arenas; no universal timing claim. Mario/Luigi movement dispatcher and native fireball attack body move to genuine bank81 helpers to fit full PLAYER/OBJECT banks. Nonbank outputs remain source exact.\n\nLayout: core98 B000..BDD7; names81 B700..BB0F; host81 BB10..BEBC; gate124 A000..AD9A, preserving AE00..BFFF. CHR740..755.\n\nCeiling observation owns SmTempY only from active CmMovement to complete raw0 BG. A pre-upward speed followed by the actual native +1 solid-head response marks SmCeilingHit before CmAfterBG;96 compiled native head cases prove this chain. No resident/NMI code growth.\n\nNegatives retained: first assembler expression/include errors; fixed/LOWCODE capacity; movement-return JumpEngine pointer comparison; wrong A-bank test fixture; real Parodius false admission; status-P bug; canary initialization and public-farcall/charmap oracle errors. No equality mask hides final application state.\n\n'+'\n'.join(limits)+'\n',encoding='utf-8')
 owned=new+['tools/prepare_celeste_host_integration_v1.py','tools/prepare_celeste_host_handoff_v1.py']+[f'tools/audit/celeste_host_controls_v{i}.py'for i in range(1,5)]+[f'tools/audit/celeste_host_caller_controls_v{i}.py'for i in range(1,5)]+[report.relative_to(R).as_posix()]
 bindings=dict(deps)
 for f in proofs+[rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),B/'celeste-host-rebuild.nes',B/'celeste_host.patch',B/'celeste_host_preimages.json',B/'celeste_host_symbol_moves.json',B/'celeste_host_reference_relocations.json',B/'celeste_host_handoff_export_negative.json']+[R/n for n in owned]:bindings[str(f.resolve())]=sha(f)
 hand=dict(passed=True,source_CPU_only=True,native_run_by_this_agent=False,ROM=str(rom),ROM_sha256=sha(rom),DBG_sha256=sha(rom.with_suffix('.dbg')),LBL_sha256=sha(rom.with_suffix('.lbl')),parent=str(parent),parent_sha256=sha(parent),source_changes=changes,new_owned_sources={n:sha(R/n)for n in new},owned_publication_files=owned,source_patch=str(B/'celeste_host.patch'),historical_apply_tool='prepare_celeste_host_integration_v1.py is the retained staged draft, NOT the final reproducer. Final source is current exact leaves + normalized patch + explicit private Mac-v5 overlay.',private_build_command=[sys.executable,'tools/build_mmc5_expanded.py','--source-overlay','build/celeste-host-overlay','--output','build/UNBOUND-celeste-rebuild.nes'],ordinary={'mmc3':sha(B/'celeste-host-final-mmc3.nes'),'mmc5':sha(B/'celeste-host-final-mmc5.nes')},source_proofs={str(f):sha(f)for f in proofs},changed_PRG_bytes_by_physical_bank=diff,protected_spans=protect,source_owner_farcall_relocations=str(B/'celeste_host_reference_relocations.json'),initial_host_tail_FF=True,assembly_dependency_count=len(deps),actual_assembly_command=cmd,bindings=bindings,limits=limits,shared_source_ownership_released=True)
 write(out,hand);print(json.dumps(dict(passed=True,handoff=str(out),sha256=sha(out),bindings=len(bindings),dependencies=len(deps),source_files=len(changes),genuine_symbol_moves=len(moves),missing_debug_symbols=len(missing))))
if __name__=='__main__':main()
