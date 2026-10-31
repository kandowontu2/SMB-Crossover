"""Measure1B shared-hook deficit and exact current linked-source mailbox consumers."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/contra-force-palette-names-cart-v2';F=R/'build/cf-owner-retirement-v2';O=R/'build/contra-force-p1-shared-factor-proposal-v3'
S=R/'tools/reference/contra_force_p1_shared_factor_proposal_v2.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FIELDS=['SmFreezePalettePacket','SmFreezePalettePending','SmFreezeLastBlue','SmFreezeTurn','SmFreezeRenderState','SmFreezePaletteControl']
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,linked_or_adopted=False,resource_granted=False)
 try:
  parent=json.loads((F/'handoff.json').read_text())
  for p,h in parent['bindings'].items():assert sha(p)==h,p
  b=qualified(P/'joint/candidate.nes');old=(F/'joint/ff-epoch-rom.inc').read_text()
  needle='FfMuxRomNative:\n pla\n plp\n sta SafecallA_SMC+1';assert old.count(needle)==1
  new=old.replace(needle,'FfMuxRomNative:\n pla\n plp\n.export FfMuxNativeTail\nFfMuxNativeTail:\n sta SafecallA_SMC+1')
  (O/'ff-epoch-native-tail-zero-label.inc').write_text(new)
  # Genuine emitted entry is obtained from the actual source label+two1B
  # PLA/PLP opcodes; the new public label introduces no instruction byte.
  tail=address(b,'FfMuxRomNative')+2;at=location(b,'FfMuxRomNative')+2
  expected=bytes([0x8d,address(b,'SafecallA_SMC')+1,0])if False else b['raw'][at:at+18]
  assert expected[0]==141 and expected[3]==169 and expected[5]==141 and expected[8]==169 and expected[10]==141 and expected[13]==169 and expected[15]==76
  assert expected[1]+256*expected[2]==address(b,'SafecallA_SMC')+1
  assert expected[-2]+256*expected[-1]==address(b,'FarCallCommon')
  ca=R/'tools/Windows/cc65/bin/ca65.exe';cmd=[str(ca),'--cpu','6502x','-g','--create-full-dep',str(O/'proposal.dep'),'--listing',str(O/'proposal.lst'),'-o',str(O/'proposal.o'),str(S)]
  g=validate(cmd,O,cwd=O);q=subprocess.run(cmd,cwd=O,capture_output=True,text=True);(O/'compile.json').write_text(json.dumps(dict(command=cmd,cwd=str(O),output_guard=g,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr),indent=2)+'\n');assert q.returncode==0,q.stderr
  od=ca.with_name('od65.exe');q=subprocess.run([str(od),'--dump-segments',str(O/'proposal.o')],capture_output=True,text=True);assert q.returncode==0
  (O/'segments.txt').write_text(q.stdout);assert 'CF_SHARED_DRAW_FACTOR_PROPOSAL' in q.stdout and re.search(r'Size:\s+57\b',q.stdout)
  cmds=json.loads((F/'final-link.json').read_text())['command'];objs=[Path(v)for v in cmds if Path(v).suffix=='.o'];sources=set();deps=[];missing=[];import_only=[]
  for obj in objs:
   dep=obj.with_suffix('.dep')
   if not dep.exists():dep=obj.with_suffix('.d')
   if not dep.exists():
    od=ca.with_name('od65.exe');z=subprocess.run([str(od),'--dump-imports',str(obj)],capture_output=True,text=True);assert z.returncode==0
    imports=re.findall(r'Name:\s*"([^"]+)"',z.stdout);used=[n for n in imports if n in FIELDS];assert not used,('missing dependency for actual mailbox importer',obj,used)
    import_only.append(dict(object=str(obj),sha256=sha(obj),actual_named_mailbox_imports=used));continue
   assert parent['bindings'].get(str(dep.resolve()))==sha(dep),str(dep)
   deps.append(dep)
   line=dep.read_text().splitlines()[0];assert '\t' in line,dep
   for f in re.split(r'(?<!\\)\s+',line.split('\t',1)[1]):
    p=Path(f.replace('\\ ',' '))
    if p.is_file()and p.suffix in ['.s','.inc']:sources.add(p.resolve())
  rows=[]
  for p in sorted(sources):
   for i,line in enumerate(p.read_text(errors='replace').splitlines(),1):
    used=[n for n in FIELDS if n in line and not line.lstrip().startswith(';')]
    if used:
     code=line.split(';',1)[0].strip();op=code.split()[0].lower()if code else ''
     rw='write'if op in['sta','stx','sty']else'read-write'if op in['asl','lsr','inc','dec','rol','ror']else'read'if op in['lda','ldx','ldy','cmp','cpx','cpy','and','ora','eor','adc','sbc','bit']else'declaration-or-alias'
     rows.append(dict(path=str(p),line=i,fields=used,operation=rw,source=line))
  (O/'current-linked-source-consumers.json').write_text(json.dumps(dict(actual_linked_objects=len(objs),dependency_files=len(deps),missing_object_deps=missing,remaining_objects_proven_no_mailbox_imports=import_only,source_files=len(sources),rows=rows),indent=2)+'\n')
  out.update(passed=True,current_bridge=dict(PC=address(b,'FwNativeDrawAll'),physical_bank=62,span=59),measured_source_size=57,net_additional_shared_bytes_required=0,remaining_original_padding=2,
   source_factoring=dict(existing_tail=tail,existing_tail_bytes=expected.hex(),same_A62_context=True,zero_byte_label='FfMuxNativeTail AFTER genuine FfMuxRomNative PLA/PLP',old_native_inline_bytes=18,new_true_near_JSR=3,saved_bytes=15,original_Samus_freeze_path_delta_cycles=3,stack_depth='Same2B caller return: old JSR SFC vsnew JSR native-tail+JMP SFC; actual returnaddresses naturally differ. Immediate old helper sequence/orderedSMC/nativeoutputs unchanged.'),
   selected31=dict(before_Samus_state_gate=True,protected_render_state_writes=0,old_stale_Samus_state_cannot_divert_CF=True,external_first_A2_auth='Actual B020+18 service6 ROM full16-cookie before any A2/RAM3 opcode',native_input='Equality via EOR#31 preserves incomingC/V/D/I; BOTH paths execute originalLDAstate replacing A/N/Z exactly. X/Y unchanged; no extra status stack or originalA assumption.'),
   layout=dict(own_C2_workspace='DDB9..<DDD2,25B AFTER grantedownLastLife DDB8; not yet allocated as P1state',own_A1_free=240,own_A3_free=551,
    proposed_phase_split={'A1':['89Bwhole worker','22B true CfCallA gate to A3late'], 'A3':['48Btag','145Bnative mask','127Blate','124Bpacket','48Bheartbeat','17Bacquire']},A1_total=111,A3_total=509,A2_output_C_transport='8..12B within current own97B router tail; genuine native completedC returned after restoring originA2, never self-unmap'),
   global_alias_request=dict(bytes=10,fields=['Packet7','Pending1','LastBlue1','Turn1'],protected=['SmFreezeRenderState','SmFreezePaletteControl','FFbodyACK'],valid_last='Packet completed -> LastBlueC0(native)/C1(CF) -> PendingC0 pre/native or80 post/CF LAST',mandatory_scope='Actual native producer retirement before foreign Selected/OAM/WRAM replacement; no late Samus rewriter, paused/skipped heartbeat and NMI consumers must be demonstrated before adopting any producer.'),
   consumer_census=dict(dependencies=len(deps),missing_object_deps=missing,remaining_objects_no_mailbox_imports=import_only,sources=len(sources),references=len(rows),scope='All84actualobjects: .dep/.d source dependencies OR actual od65 import-list exclusion. This closes named mailbox producer references, not dynamic indirect writes, executed lifecycle, or native timing.'),
   required_next=['Root approval still needed before modifying shared bridge, despite exact57/59B fit; no additional PRG lease needed','Globalalias lease/source lifecycle/commit proof needed; no scheduler readyclaim','Native complete-object tag/actual final OAM/pattern/palette model, queuefull and lag/pause/noFX/abandon tests required','Actual native deadline/performance unknown; no Mesen run'])
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),S,P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',F/'handoff.json',F/'joint/ff-epoch-rom.inc',F/'joint/ff-palette.s',R/'build/contra-force-p1-epoch-proposal-v2/proposal.json',R/'build/contra-force-palette-names-qualified-v1/handoff.json',R/'tools/audit/private_build_outputs_v1.py',*[p for p in O.iterdir()if p.is_file()]]
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'proposal.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],needed=out.get('net_additional_shared_bytes_required'),census=out.get('consumer_census'),error=out.get('error'))),flush=True)
if __name__=='__main__':main()
