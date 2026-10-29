"""Freeze only owned SMB2 adapter source/CPU unit, not common/native admission."""
from pathlib import Path
import collections,difflib,json,re,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
import prepare_smb2_roster_audio_host_v8 as B
import smb2_roster_audio_host_controls_v8 as T
import smb2_roster_palette_lifecycle_freeze_v7 as F
R,O,OLD,bind=B.R,B.O,B.OLD,B.bind

def main():
 assert not(O/'handoff.json').exists()
 parent=json.loads((OLD/'handoff.json').read_text())
 for key in ['owned_files','input_bindings','output_bindings']:
  for row in parent[key]:assert bind(row['path'])==row
 build=json.loads((O/'build-proof.json').read_text());tests=json.loads((O/'host-controls.json').read_text())
 assert tests['passed']and tests['candidate']==build['candidate']==bind(O/'candidate.nes')
 assert tests['tool']==bind(T.__file__)and build['tool']==bind(B.__file__)
 closure=json.loads((OLD/'source-closure.json').read_text());cmd=closure['command'].copy()
 for option,name in [('--create-full-dep','source-closure.d'),('-o','source-closure.o')]:cmd[cmd.index(option)+1]=str(O/name)
 cmd[-1]=str(O/'objects/entrypoint.s')
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'source-closure-launcher.txt').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
 line=(O/'source-closure.d').read_text().splitlines()[0].split(':\t',1)[1]
 deps={Path(x.replace('\\ ',' ')).resolve()for x in re.split(r'(?<!\\)\s+',line.strip())}
 leaf=R/'src/smb2_roster_audio_host_v8.s';assert leaf in deps
 before=F.symbols(OLD/'candidate.dbg');after=F.symbols(O/'candidate.dbg');missing=before-after
 for identity,count in missing.items():
  assert identity[1]=='"_FARCALL_COUNT"'and after[identity[:-1]+(identity[-1]+1,)]>=count,('unexpected old qualified symbol move',identity)
 assert len(missing)==1,'one genuine new clock farcall constant only'
 b=T.A.scoped_load(O/'candidate.nes');state=T.A.address(b,'RgAudioRam');cache=range(state+69,state+77)
 assert T.A.address(b,'S2HostWorld')==state+69 and T.A.address(b,'S2HostValid')==state+76
 oldleaf=R/'src/smb2_roster_audio.s';text=oldleaf.read_text()
 assert 'ldx #68' in text and 'sta S2AudioState,x' in text
 assert T.A.address(b,'S2AudioEnable')==state+68 and T.A.address(b,'RgContraRam')==T.A.address(b,'RgZeldaRam')==state
 # Audit ALL actual consumed source files for the union of audio-RAM aliases.
 # Other identities intentionally alias these bytes: exclusive consumer
 # ownership, not globally unused SRAM, is the allocation contract.
 consumers=[]
 for path in sorted(deps):
  if path.suffix.lower()not in['.s','.inc']:continue
  lines=path.read_text(errors='strict').splitlines()
  hits=[i+1 for i,line in enumerate(lines)if re.search(r'\b(?:RgAudioRam|RgContraRam|RgZeldaRam|S2AudioState|S2Host\w+)\b',line.split(';',1)[0])]
  if hits:consumers.append(dict(file=bind(path),reference_lines=hits))
 own=[row for row in consumers if Path(row['file']['path']).name.startswith('smb2_roster_audio')]
 prior_own=[row for row in own if Path(row['file']['path'])!=leaf]
 assert prior_own and all('RgAudioRam+69'not in Path(row['file']['path']).read_text()for row in prior_own)
 audit=dict(passed=True,cache=[hex(cache.start),hex(cache.stop-1)],declared_container=dict(name='RgAudioRam',start=hex(state),bytes=512),
  current_SMB2_source_allocation='Source52B+private12ZP+pause/E/C/status5B=69B, offsets0..68. Actual original differential checks all52 state/12ZP and complete non-stack RAM; new host callback controls exclude every unexpected cache/application mutation.',
  cache_contract='Offsets69..76 NMI-only under actual initialized RgAudioCharacter25 and external GuestAudioCharacter25; raw25 is admitted before private reads. These bytes are NOT globally free. Other native drivers, Dragon and Rogue intentionally reuse the same512B under disjoint audio owners. No concurrent driver can run under25; final common dispatcher must enforce that.',
  cold_reset='Acquire only after previous owner retirement; declines a foreign busy DMC before private writes. Clears69B+8B, preserves Main three pending STA fields. Common commits GuestAudioCharacter25 last only after RgAudioCharacter readback25. SoundTest clears the whole512B on reset, so final common must retire25 BEFORE entering it; Tick state8 declines without touching cache/clock.',
  foreground='The existing complete Main uses5C00/5F98 overlays and three effect STA fields; no Main call writes audio cache or private audio record. No RgAudioZp borrowing. Foreground BB..C6 preserved through12-byte CpuZp lease.',
  actual_consumed_alias_sources=consumers,existing_SMB2_audio_sources=prior_own,source_ownership_scope='Actual linked current6305+owned append, not a proof of an as-yet-unlinked final common owner/mixer union.')
 (O/'cache-owner-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 a=(OLD/'candidate.nes').read_bytes();z=(O/'candidate.nes').read_bytes();diff=[i for i,(x,y)in enumerate(zip(a,z))if x!=y]
 begin=16+74*8192+0x1cb7;end=16+74*8192+(T.A.address(b,'S2HostAudioEnd')-0xa000)
 assert all(begin<=i<end for i in diff)and a[:begin]==z[:begin]and a[end:]==z[end:]
 # Fresh ordinary builds use the same guarded entrypoint and actual current
 # flag-off closure; they are not inferred from an expanded-only branch.
 ov=O/'overlay/src';ov.mkdir(parents=True,exist_ok=True);(ov/'entrypoint.s').write_bytes((O/'objects/entrypoint.s').read_bytes())
 def ordinary(mode):
  dest=O/('flagoff-'+mode+'.nes');command=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(O/'overlay'),'--output',str(dest),'--flag-off',mode]
  p=subprocess.run(command,cwd=R,capture_output=True,text=True);(O/('flagoff-'+mode+'-launcher.txt')).write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr[-1500:]
  ref=OLD/('flagoff-'+mode+'.nes');assert dest.read_bytes()==ref.read_bytes()
  return dict(mapper=mode,actual=bind(dest),reference=bind(ref),command=command)
 with ThreadPoolExecutor(max_workers=2)as pool:ordinary_rows=list(pool.map(ordinary,['mmc3','mmc5']))
 negatives=dict(draft_silence_map=bind(O/'first-control-negative.json'),draft_event_priority=bind(O/'event-priority-draft-negative.json'),
  retained_setup_findings=['First allRAM comparison had typed hardware5115=0 while shadow/current-map202. Initialize both genuine mapper-register/shadow inputs consistently, no output mask.',
   'Initial direct endpoint assertion expected fixed E even when original source started/stopped DMC. Compare actual original-selected E while requiring A/C exact and all33SMC preserved.',
   'Initial first-music+DPCM lifecycle test assumed every request remained active; literal original music init may stop it. Busy/complete/retire witnesses use explicitly context-busy/no-new-song source state, all8 original request paths actually active.',
   'Initial report counted only saved cost rows rather than all literal paired callbacks; final control counter counts every successful paired call.'],
  actual_game_draft_fixes=['Silence mapped0 instead of original Q3Stop80; fixed table80.',
   'Scene fallback now retains active source Star theme and bounds AreaType to native2bits.',
   'Native MusicHandler admits pending event before area. Draft processed both; now suppresses/consumes area when event exists, including unmapped hurry retaining previous theme. All81 nonzero combined masks compared.'],
  drafts_not_frozen='Unbound draft ROM outputs were overwritten in this single private directory; exact original negative hashes/events retained. They are not claimed passing/current evidence.')
 (O/'retained-negatives.json').write_text(json.dumps(negatives,indent=2)+'\n')
 note=R/'docs/qa/smb2-roster-audio-host-source-2026-10-29.txt'
 note.write_text('''PRIVATE SMB2 OWNED REAL-NMI ADAPTER ENDPOINTS — NOT COMMON/NATIVE ADMISSION

Parent63051820 is immutable palette-lifecycle-v7, genuine f56a shared source
plus frozen gameplay, palette, Roll relocation, authentic driver and mailbox.
Only A74 owned tail changes. No shared AudioUpdate, NMI, Main, GuestDmcStatus,
menu, mixer or foreign assembly edits. No native launch or installed output.

Public APIs and exact addresses/sizes are in host-controls.json. Direct APIs
preserve AXYP/SP and A/C/shadows/all33SMC. Tick legitimately selects source
E119/120 while DMC is active; completion/stop returnsE127. Input Status A
returns the actual busy-adjusted status with X/Y/P/SP preserved. Genuine
incoming farcall recomputesNZ from returnedA, exactly as its actual caller.

COMMON CALLER CONTRACT (not installed here): retire prior native/expanded
audio owner and any DMC before reusing private audio RAM; initialize actual
shared images without an invented4011 clear; call Acquire and read back
RgAudioCharacter25 before committing GuestAudioCharacter25 LAST. Acquire
declines a foreign busy DMC. Cold menu/newgame constructor must already have
initialized gameplay state before clock/private reads. Tick requires both
owners25/raw25/non-title/non-SoundTest. Exactly one call per genuine OUTER
regular/lag/pause NMI; never Main or inner SoundTest. Owner25 retirement must
run even AFTER raw identity changes: stopDMC thenE127 then release. No new
global flags or extra per-Main ticks. Context reads only common5FB6 bit0,
never writes/assigns its other bits. Busy context still consumes all three
STA effects and advances source clock/driver on that NMI.

Six source queues retain actual assignment, clear and source event priority.
Three actual Main STA fields feed Q1/Q2/Q4; Q0/Q3/Q5 remain consumer-only.
Native host MusicHandler gives pending event priority over pending area;
both source theme/event bit selection uses its real lowest-set-bit rule.
Approved SMB->SMB2 mapping is an authored crossover policy, not original
SMB2 room script equality. Hurry retains theme and native world warning.
Star source theme persists across scenes, returns cached normal on expiry.
Life count is cached without any driver reset on positive1Up changes.
Actual native scene cues own restart; no invented reset on lives inequality.

Pause uses literal original41: music advances, effect processors skip,
all6Q clear, source4015=0C. Unpaused status0F/start1F is literal source.
All original DAC/sample payloads/source stores remain; no4011 is added.

REMAINING COMMON DEPENDENCIES: resident GuestDmcStatus currently knows only
Bass. It must route OLD owner25 to S2HostDmcStatus before final mix status;
do not fake Bass ownership or call current wrong status path. Shared world
SFX begin/finish, pause-world silent buffers/5015 without clearing native
image/DAC, owner acquisition/retirement, complete NMI depth and source clock
admission must be composed once with Rogue/Goku. This unit intentionally
does NOT call the known-wrong shared mixer. Final127 changes require same-
final127 regeneration of E119/120/125 and all protected callable outside
F140..FE10; this packet regenerates current clones from its own SAME127 and
proves all existing E bytes exact. Native DMC/lag/cadence/listening/render
qualification remains open. Do not label a manually called endpoint native.

Controls compare actual original ROM driver against actual compiled adapter:
all52 sourceRAM,12 sourceZP/pointer, ordered APU intent, complete hardware
sample fetch payload/rate/length, foreground BB..C6, full non-stack RAM,
all33SMC, A/C and genuine E lifetime. All256area/256event masks,81combined
nonzero masks, pause/Star/scene/1Up/effects,256flag bytes,510foreign raw
calls,510foreign old-owner status/retire calls, actual IRQ and incoming
farcall/IRQ contexts are finite source evidence. cache-owner-audit.json
records all actual consumed alias sources: +69..76 is owner-exclusive
space, never globally unused RAM. Costs and ambient192 stack are measured
in host-controls.json; common/NMI stack and hardware costs are not inferred.
Draft defects/oracle setup negatives remain separately recorded.
''',newline='\n')
 patch=''.join(difflib.unified_diff([],leaf.read_text().splitlines(True),fromfile='/dev/null',tofile='audio-host-v8/src/'+leaf.name))
 (O/'implementation.patch').write_text(patch,newline='\n')
 inputs=deps|{Path(row['path'])for row in parent['input_bindings']}|{Path(sys.executable)}
 for mod in list(sys.modules.values()):
  f=getattr(mod,'__file__',None)
  if f:
   p=Path(f).resolve()
   if p.suffix=='.py'and(p.is_relative_to(R)or'py65'in p.parts):inputs.add(p)
 source=dict(passed=True,source_CPU_only=True,native=False,candidate=build['candidate'],parent=build['parent'],actual_ASM_dependencies=len(deps),command=cmd,changed_bytes=len(diff),changed_banks=[74],all_preexisting_qualified_symbols_exact_except_actual_FARCALL_COUNT_plus1=True,header_CHR_all_E_and_other_banks_exact=True,ordinary=ordinary_rows,cache_audit=bind(O/'cache-owner-audit.json'),input_bindings=[bind(p)for p in sorted(inputs)],tool=bind(__file__))
 (O/'source-closure.json').write_text(json.dumps(source,indent=2)+'\n')
 owned={leaf,Path(B.__file__),Path(T.__file__),Path(__file__),note,O/'objects/entrypoint.s',O/'overlay/src/entrypoint.s',O/'implementation.patch'}
 outputs={p for p in O.iterdir()if p.is_file()and p.name!='handoff.json'}
 h=dict(status='PRIVATE_OWNED_ADAPTER_SOURCE_CPU_IRQ_PASS_NO_COMMON_MIXER_NATIVE_ADMISSION',candidate=build['candidate'],parent_handoff=bind(OLD/'handoff.json'),build=bind(O/'build-proof.json'),controls=bind(O/'host-controls.json'),source=bind(O/'source-closure.json'),owned_files=[bind(p)for p in sorted(owned)],input_bindings=[bind(p)for p in sorted(inputs)],output_bindings=[bind(p)for p in sorted(outputs)],native=False,common_hooks_installed=False,remaining='One composed common owner/mixer/DMC-status/clock dispatch plus full NMI stack/native hardware/cadence/listening. No blanket playable admission.')
 (O/'handoff.json').write_text(json.dumps(h,indent=2)+'\n')
 for key in ['owned_files','input_bindings','output_bindings']:
  for row in h[key]:assert bind(row['path'])==row
 print(json.dumps(dict(status=h['status'],handoff=bind(O/'handoff.json'),candidate=h['candidate'],dependencies=len(deps),inputs=len(inputs),owned=len(owned),outputs=len(outputs),costs=tests['costs'],bytes=tests['adapter_bytes'],spare=tests['spare'])))
if __name__=='__main__':main()
