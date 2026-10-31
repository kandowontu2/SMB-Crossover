"""Assemble unlinked P1 proposal and source-authenticated native mask table."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/contra-force-presentation-shared-cart-v3';O=R/'build/contra-force-p1-epoch-proposal-v2'
S=R/'tools/reference/contra_force_p1_epoch_proposal_v1.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not O.exists();O.mkdir();logs=[];out=dict(passed=False,linked_or_installed=False,resource_granted=False,native=False)
 try:
  b=qualified(P/'joint/candidate.nes');raw=b['raw'];table=[];rows=[]
  for ident in range(145):
   masks=[]
   for face in ['Left','Right']:
    lo=location(b,'MetaspriteTable'+face+'Lo');hi=location(b,'MetaspriteTable'+face+'Hi')
    ptr=raw[lo+ident]+256*raw[hi+ident];at=16+4*8192+ptr-0xa000
    if ident==0:mask=0
    else:
     count=raw[at];assert count%4==0 and count<=252
     roles=[];mask=0
     for attr in range(4):
      effective=[((v&3)if v&32 else(v|attr)&3)for v in raw[at+2:at+1+count:4]]
      if 1 in effective:mask|=1<<attr
      roles.append(sorted(set(effective)))
     rows.append(dict(ident=ident,face=face,record=ptr,parts=count//4,effective_palettes_by_actor_attr=roles,P1_presence_bits=mask))
    masks.append(mask)
   assert masks[0]==masks[1],('no one-table-facing assumption',ident,masks)
   table.append(masks[0])
  (O/'proposal.s').write_bytes(S.read_bytes());(O/'native-mask-table.s').write_text('.export CfNativeP1Mask\n.segment "CF_P1_MASK_PROPOSAL"\nCfNativeP1Mask:\n'+''.join(' .byte '+','.join('$%02x'%n for n in table[i:i+16])+'\n'for i in range(0,len(table),16)))
  ca=R/'tools/Windows/cc65/bin/ca65.exe';od=ca.with_name('od65.exe');sizes={}
  for name in ['proposal','native-mask-table']:
   cmd=[str(ca),'--cpu','6502x','-g','--create-full-dep',str(O/(name+'.dep')),'--listing',str(O/(name+'.lst')),'-o',str(O/(name+'.o')),str(O/(name+'.s'))]
   guard=validate(cmd,O,cwd=O);q=subprocess.run(cmd,cwd=O,capture_output=True,text=True);logs.append(dict(command=cmd,cwd=str(O),output_guard=guard,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));(O/'build-log.json').write_text(json.dumps(logs,indent=2)+'\n');assert q.returncode==0,logs[-1]
   r=subprocess.run([str(od),'--dump-segments',str(O/(name+'.o'))],capture_output=True,text=True);assert r.returncode==0
   (O/(name+'-segments.txt')).write_text(r.stdout)
   for block in re.split(r'(?=\s+Name:)',r.stdout)[1:]:
    n=re.search(r'Name:\s*"([^"]+)"',block);v=re.search(r'Size:\s+(\d+)',block)
    if n and v:sizes[n.group(1)]=int(v.group(1))
  assert sizes['CF_P1_STATE_PROPOSAL']==25 and sizes['CF_P1_MASK_PROPOSAL']==145 and sizes['CF_P1_HEARTBEAT_PROPOSAL']==48
  out.update(passed=True,emitted_segment_sizes=sizes,native_table_records=len(rows),native_facing_masks_equal=True,native_records=rows,
   shared_hook=dict(current='FwNativeDrawAll A62 B3C5..<B40059B, including15B trailing authored EA padding',
    proposed_selector_bytes=sizes['CF_SHARED_DRAW_PROPOSAL'],replaces_current_native_tail_bytes=3,current_padding=15,
    measured_additional_A62_bytes_needed=sizes['CF_SHARED_DRAW_PROPOSAL']-18,
    revision='Earlier25B estimate omitted originalP/A preservation. This conservative actual assembled selector is authoritative; no shared code adopted.',
    target='Genuine existing B020+18 row6/raw31 ROM full-cookie gate; row6 becomes own CfWholeDrawAll, no unguarded A2/RAM3 entry.'),
   own_RAM_request=dict(C2_new=25,proposed_range='DDB8..<DDD1, after current DD4E..<DDB8 callback gates and before DE00 router',
    new_fields=['24B transient saved native SprObject_SprAttrib','1B actual completed DrawAll C output'],
    reused_own=['02DF emitter-context tag0/8 replacing uncommitted CfShotPaletteOwned','02F7/02FA/02FB declared renderer scratch after early draw','02EE target-bank highbit as explicit returned-C transport code after final worker return'],
    global_alias_request=['SmFreezePalettePacket7','SmFreezePalettePending1','SmFreezeLastBlue1','SmFreezeTurn1'],
    global_protected='SmFreezePaletteControl is native read-only input; no original FF bodyACK/State writes proposed by this worker. Native SmFreezeRenderState arbitration before current wrapper remains a prerequisite until source lifecycle proof or explicit acquisition repair.'),
   planned_source_changes=['A2 row6=>CfWholeDrawAll; actual A2 return consumes own highbit returned-C code without self-unmapping CfCallA','Early CfHostDraw calls CfTagNativeObjects after source body/shots; normal world parser carries bit4','Whole loan-requiring source projectile emitter marks every part bit3; no added cells/patterns','Late worker removes both complete conflicting groups fairly and all tags before DMA; body0/unrelated native P2/P3 exact','Native epoch PendingC0 beforequeue; CF epoch Pending80 afterqueue; stable CF heartbeat only after full cookie guard','Menu/life/scene/newgame/player/abandon protocol requires actual current f523 chain proof and stale Samus-state acquisition closure before any producer adoption'],
   retained_reporting_negative='V1 parser required whitespace after od65 Name: and omitted the actually emitted48B heartbeat. V2 accepts zero whitespace and asserts the real48B segment; source bytes unchanged.',
   limitations=['UNLINKED objects only; no actual scheduler/ISR/pixel/native qualification','Dynamic guest metasprites>=145 are not assigned invented mask semantics; actual raw31 legal-world/typed native helper census still required','Paired queue/OAM commit, fullqueue/malformed/lag/pause/lateBowser/CFnative precedence require actual sourcecart controls','Shared ROM and global alias grants explicitly pending; own A3 worker total includes native-table data but no new CHR pages.'])
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),S,P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',R/'build/contra-force-presentation-qualified-v1/handoff.json',R/'build/contra-force-p2-mask-audit-v3/audit.json',R/'tools/audit/private_build_outputs_v1.py',R/'build/contra-force-p1-epoch-proposal-v1/proposal.json',*[p for p in O.iterdir()if p.is_file()]]
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'proposal.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],sizes=out.get('emitted_segment_sizes'),error=out.get('error'))),flush=True)
if __name__=='__main__':main()
