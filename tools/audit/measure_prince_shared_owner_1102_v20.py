"""Exact symbolic third-owner cost; stable foreign manager remains immutable."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
from private_build_outputs_v1 import validate
O=L.O;BB=R/'build/bubble-bobble-source-1101-v1'


def main():
 source=BB/'native-visible-owner.s';text=source.read_text();old=(BB/'native-visible-owner.bin').read_bytes();assert len(old)==531
 # Preserve AE00 cold, AE0B retire, AEF3 auth, all old helper/data addresses
 # and all downstream code. Extra routines are linked at a virtual address
 # solely to measure cost; B400 is not proposed as a physical lease.
 assert text.count(' jsr CoSelect\n')==3;text=text.replace(' jsr CoSelect\n',' jsr PrSelect\n')
 assert text.count(' CoFar CoWorker,$fb\n')==1;text=text.replace(' CoFar CoWorker,$fb\n',' jsr PrTypedWorker\n .res 15,$ea\n')
 assert text.count(' jsr ShRetire\n rts\n')==1;text=text.replace(' jsr ShRetire\n rts\n',' jmp PrRetire\n nop\n')
 for name in ['common-current-Ex-cookie.bin','native-visible-BB-cookie.bin']:
  data=(BB/name).read_bytes();needle=f'.incbin "{name}"';assert needle in text;text=text.replace(needle,'.byte '+','.join(f'${v:02x}'for v in data))
 native=L.P.T.labels(O/'host-services-v18.lbl');cold=L.P.T.labels(O/'cold-worker-v19.lbl');cookie=bytes([0xa7,38,1])+hashlib.sha256((O/'cold-pool-v19.bin').read_bytes()).digest()[:13]
 text+='''
.segment "PR_OWNER_EXTRA"
.export PrSelect,PrTypedWorker,PrRetire,PrOwnerExtraEnd,PrCookie
PrSelect:
 lda SelectedCharacter
 cmp #38
 beq PrSelected
 jmp CoSelect
PrSelected:
 lda #<PrCookie
 sta R5
 lda #>PrCookie
 sta R6
 lda #<PrDescriptor
 sta R3
 lda #>PrDescriptor
 sta R4
 sec
 rts
PrTypedWorker:
 CoFar CoWorker,$fb
 bcc PrWorkerDone
 lda SelectedCharacter
 cmp #38
 bne PrWorkerDone
 CoFar PrColdBoot,3
PrWorkerDone:
 rts
PrRetire:
 lda #<PrCookie
 sta R5
 lda #>PrCookie
 sta R6
 jsr CoCheckHeaders
 bcc PrNoRetire
 lda #2
 sta CurrentBankC
 sta $5116
 jsr PrNativeRetire
 jsr CoInvalidate
PrNoRetire:
 jmp ShRetire
PrCookie:
'''+'.byte '+','.join(f'${v:02x}'for v in cookie)+'\nPrOwnerExtraEnd:\n'
 definitions=f'PrDescriptor=$bf93\nPrColdBoot=${cold["PpColdBoot"]:04x}\nPrNativeRetire=${native["PpNativeRetire"]:04x}\n'
 asm=O/'shared-owner-v20.s';asm.write_text(definitions+text);cfg=O/'shared-owner-v20.cfg';cfg.write_text('MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$b400,size=$1000,file="'+(O/'shared-owner-extra-v20.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_OWNER_EXTRA:load=X,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'shared-owner-v20.o'],[cc/'ld65.exe','-C',cfg,O/'shared-owner-v20.o','-o',O/'shared-owner-v20.bin','-Ln',O/'shared-owner-v20.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 lab=L.P.T.labels(O/'shared-owner-v20.lbl');prior=L.P.T.labels(BB/'native-visible-owner.lbl')
 for n,a in prior.items():assert lab[n]==a,('Legacy label moved',n,hex(a),hex(lab[n]))
 extra=(O/'shared-owner-extra-v20.bin').read_bytes();after=(O/'shared-owner-v20.bin').read_bytes();diff=[i for i,(a,z)in enumerate(zip(old,after))if a!=z]
 q=dict(measured=True,qualified=False,symbolic_only=True,ROM_written=False,shared_sources_written=False,base_manager='Stable native-passed4395 source only; not a cumulative composition baseline. Rebind after parent Bub stabilizes. Installed f5c helper successor is authoritative for eventual compose.',original_manager_bytes=len(old),fixed_manager_bytes=len(after),all_existing_manager_labels_unchanged=True,changed_old_manager_bytes=len(diff),extra_third_owner_bytes=len(extra),extra_cookie_bytes=16,bootstrap_descriptor_bytes=8,additional_typed_cold_auth_retire_storage=len(extra)+8,virtual_measurement_address_not_a_lease=0xb400,existing_common_worker_spare=18,remaining_common_after_descriptor=10,existing_dispatcher_spare=8,unfunded_third_owner_manager_bytes=len(extra),Prince_public_service_dispatch_and_scene_reset_not_counted=True,precise_blocker='New manager routines require '+str(len(extra))+' source-funded resident bytes, plus measured public service routing. Existing full manager footprint and downstream addresses are retained. No resident grant inferred.',proposed_source_factor='Current1966 Shinobi dispatch AAF7..ABD4 is221B, byte-identical to authenticated original compiled source. It duplicates the existing Ex frame/SMC/result transport. A shared frame may source-fund this extension, but no reclamation is claimed without exact foreign ABI/row/header/ISR proof.',Prince_cookie=cookie.hex(),bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,BB/'native-visible-owner.bin',BB/'common-split.s',R/'docs/qa/allocations/bubble-shared-native-1102-v5.json',R/'docs/qa/allocations/common-cold-1102-v1.json',O/'shared-owner-v20.bin',O/'shared-owner-extra-v20.bin',O/'cold-worker-CPU-v19.json']})
 (O/'shared-owner-measurement-v20.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
