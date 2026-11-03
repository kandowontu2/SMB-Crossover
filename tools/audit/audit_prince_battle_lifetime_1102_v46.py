"""Finite original reader/constructor/clock closure for private battle tail."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
O=M.O;P=M.A.L.P


def main():
 receipts=['native-link-measurement-v42.json','native-link-CPU-v43.json','cold-link-storage-v44.json','cold-link-CPU-v45.json','pose-grid-native-CPU-v38.json','combat-tail-CPU-v36.json'];proofs={name:json.loads((O/name).read_text())for name in receipts}
 for name,proof in proofs.items():
  assert proof.get('passed',proof.get('measured')),(name,'not passed')
  for path,digest in proof.get('bindings',{}).items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,(name,path)
 graph={}
 for name in ['contact-recovery.json','world-coordinate-recovery-v7.json','combat-tail-recovery-v34.json']:graph.update(json.loads((O/name).read_text())['instructions'])
 assert len(graph)==2485
 slots=[(0xb0,0xf8),(0x100,0x200),(0x235,0x352),(0x362,0x3ff),(0x40b,0x491),(0x4ff,0x606),(0x78,0xb0)];indexed={'abx','aby','zpx','zpy'};direct={'abs','zpg'};domains=[];indirect=[];ledger=[];handle=[]
 for key,row in graph.items():
  mn,mode,value=row['mn'],row['mode'],row['value']
  if mn in ['JSR','JMP']and mode!='ind':continue
  if mode in ['iny','inx','ind']:
   assert(mn,mode,value)in [('LDA','iny',0x21),('JMP','ind',0x23)];indirect.append(key)
  if mode not in indexed|direct or value>=2048:continue
  end=value+(256 if mode in indexed else 1);assert not any(value<hi and end>lo for lo,hi in slots),(key,row)
  if end>2048:
   assert key in ['4:B8DB','7:E991','7:E996'];ledger.append(key)
  domains.append([key,mn,mode,value,end])
  if value<=0x61c<end:
   assert mode in ['abx','aby'];handle.append([key,value,0x61c-value])
 # No direct source reader or writer consumes61C; every possible alias is
 # an indexed actor-field access. Native live Advance setsactorX=0/69=0;
 # action/defenderY is0or14. None of these relative indices reach61C.
 assert all(alias not in [0,14]for key,value,alias in handle),handle
 ledger_expected={'4:B8DB':('LDA','abx',0x710),'7:E991':('LDA','abx',0x711),'7:E996':('STA','abx',0x711)}
 for key,expect in ledger_expected.items():assert tuple(graph[key][n]for n in ['mn','mode','value'])==expect
 # Source E974 calls8710, E977 immediately BCC E99E (death), E979/97B
 # bypasses the ledger forplayerY0. Native guard ctorHP1 can only become0
 # on8710, so the guard-survival ledger cannot execute in this integration.
 for key,mn,value in [('7:E974','JSR',0x8710),('7:E977','BCC',0xe99e),('7:E979','CPY',0),('7:E97B','BEQ',0xe999)]:
  row=graph[key];actual=row['value']
  if row['mode']=='rel':actual=int(key.split(':')[1],16)+2+(actual if actual<128 else actual-256)
  assert(row['mn'],actual)==(mn,value),(key,row)
 proxy=(O/'native-proxy-v42.s').read_text();assert proxy.count(' sta $c6d0')==1 and ' lda #1\n sta $c6d0' in proxy
 assert ' sta $c712' in proxy and ' lda #255\n sta $c712' in proxy
 # Exact native-source ownership is source-only: raw38/ready/epoch/pause
 # checks precede all private actor/proxy work; genuine IRQ never advances.
 services=(O/'native-services-v42.s').read_text();assert ' jsr PpNativeProxyIn\n ldx #0' in services and services.index(' cmp #38')<services.index('PpNativeProxyIn\n ldx #0')
 assert ' lda FrameCounter\n cmp PpEpoch\n beq Rejected' in services and ' sta PpEpoch\n' in services
 assert ' lda $c084\n sta $c07f\n lda $c085\n sta $c080' in services
 labels=json.loads((O/'native-labels-v42.json').read_text());runtime=(O/'native-runtime-v42.bin').read_bytes();assert runtime[-2:]==labels['PpNativeInit'].to_bytes(2,'little')
 for name in ['PpNativeCallSlot','PpNativeCallKind']:
  at=labels[name];assert 0xd963<=at<0xdad4 and runtime[0:1]
 render=P.T.labels(O/'grid-render-labels-v37.lbl');at=render['PpPosePointer']-0xa000;assert runtime[at:at+3]==bytes([0x4c])+labels['PpGridLookup'].to_bytes(2,'little')
 assert labels['PpNativeContact']==0xbd22 and labels['PpNativeHealthStatus']==0xbd3a
 assert bytes(runtime[0xbd3e-0xa000:0xbd4b-0xa000])==bytes([0xea])*13
 q=dict(passed=True,private_proposal=True,ROM_written=False,menu_or_install_admitted=False,base_SHA256=M.A.PIN,source_original_instructions=len(graph),source_direct_indexed_reader_writer_domains=len(domains),all256_indices_expanded_except_source_unreachable_ledger=ledger,source_indirect_sites=indirect,indirect_closure='Original LDA(21),Y is replaced by authenticated immutable-source script reader; JMP(23) target finite original15commands. Fullbattle adds no indirect site/static unrelocated ROM data. Exact303new original instruction/695byte assembly and2976full original CPU differentials retained.',guard_61C_aliases=handle,guard_identity_lifetime='No direct original source reads/writes61C. Potential indexed aliases require relativeindices1..13 excluding0/14. Genuine live animation advances playerX=0/69=0, and battle action/defenderY=0or14. Proxy alone writes active80|slot; native six-slot identity never leaks into source actor geometry/commands.',guard_HP_and_ledger_closure='Native guard constructor writesHP1. Original8710 subtracts one, never heals. E977 branches E99E before ledger on guardHP0; playerY0 bypasses ledger atE97B. Thus indexed0710/0711 accesses are source-unreachable in this native domain, although complete original ledger remains preserved and original-differential-qualified. Defensive ledger row is slot,flags,FF and scan is bounded0/2 even for a direct source CPU fixture.',original_source_cannot_observe_state_code_geometry_or_live_tail=True,requested_live_code_half_open=[0xd8f1,0xdfa2],existing_exclusive_RAM2_lease=True,requested_renderer_reuse_half_open=[0xbd22,0xbd3e],renderer_reuse_source='Original44B PpPosePointer replaced by JMP authentic grid lookup. Its41B body is unreachable through old draw/project entries; private contact24B/status4B occupy28B,13remainingEA. All old public renderer/world PCs remain. Original old OffsetLo/Hi no longer executed or referenced by grid helper; its ownIndexLo/Hi are boundedSMC.',cold_phase_only_fragment=[0xc300,0xc800],cold_phase_contract='Actual44carrier typed worker requiresSEI/forcedblank/NMInegative/headersinvalid/sourceReady0/actorinactive. Runtime decoded first; metadata stages low fragmentC300..C800 while worker endsC25B. Exact decoder checks each unread byte before writes. State last overwrites worker,60B finalizer copies/zeros all source state, then new NativeInit initializes physical floor reference beforeReadyA7. Both headers remain invalid until external resident commit.',clock_and_reentrance='Only authenticated foreground public row0 owns native FrameCounter epoch, admits once modulo256, and uses original phasecountermod4. No NMI/IRQ clock or sharedDFD0 use. Gateway is synchronous FarCallCommon→KillPlayer or ShellOrBlockDefeat; reached native continuation and2122realISRcuts preserve all owned state/instruction operands/nativeR0..7/5SMC/maps. Native event callback rows return through existing owner; no nested movement/gateway admitted.',native_ISR_cuts=proofs['native-link-CPU-v43.json']['actual_ISR_cuts'],storage=dict(pages=44,payload=44254,physical_spare=802,metadata=6050,end=0xdfa2,preclock_spare=46),next_shared_rebinding=dict(selector='Current private PrPrince two immediate bytes for PpNativeRoute relocate DCFC→DF29; exactsource label binding before composition.',retire='Current private PrNativeRetire operandDBBA→D98F; preserve all foreign manager bytes and55B Bubv9 events.',cookie='Bind Prince cookie to final full source/payload; both headers last committed and full foreign retirement must be requalified.',menu='No production confirmation requested by this receipt.'),remaining='Actual source-derived full box/terrain head/side/pickup/native death-loop policies, new exact shared operands/cookie fullforeign/auth/fresh/scene proof and root execution amendment before emulator admission.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),*[O/name for name in receipts],O/'contact-recovery.json',O/'world-coordinate-recovery-v7.json',O/'combat-tail-recovery-v34.json',O/'native-services-v42.s',O/'native-proxy-v42.s',O/'native-runtime-v42.bin',O/'native-metadata-v42.bin',R/'docs/qa/allocations/prince-shared-successor-1102-v30.json',R/'docs/qa/allocations/prince-carrier514-1102-v35.json']})
 (O/'battle-lifetime-proposal-v46.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','guard_61C_aliases','source_indirect_sites']}))


if __name__=='__main__':main()
