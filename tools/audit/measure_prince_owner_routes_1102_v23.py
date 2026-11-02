"""Measure complete Prince manager/service route cost over exact Bubv9 source."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
from private_build_outputs_v1 import validate
O=L.O;B=R/'build/bubble-bobble-source-1101-v1'
BASE=R/'build/bub-menu-candidate-1102-v2/combined-event.nes';PIN='613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'


def assemble(name,text,cfg):
 asm=O/f'{name}.s';asm.write_text(text);config=O/f'{name}.cfg';config.write_text(cfg);cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/f'{name}.o'],[cc/'ld65.exe','-C',config,O/f'{name}.o','-o',O/f'{name}.bin','-Ln',O/f'{name}.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 return (O/f'{name}.bin').read_bytes(),L.P.T.labels(O/f'{name}.lbl')


def main():
 raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN;p65=16+65*8192;old=raw[p65+0xe00:p65+0x1013]
 source=B/'native-event-v9-owner.s';text=source.read_text();assert old==(B/'native-event-v9-owner.bin').read_bytes()
 # Replace a two-ID selector by a bounded three-ID selector in the same41B
 # span. Its six saved bytes hold the three cookie pointers; the previous
 # eight pointer bytes hold two three-byte descriptor tables plus2padding.
 start=text.index('CoSelect:\n');end=text.index('\nCoCheckHeaders:',start)
 text=text[:start]+'''CoSelect:
 lda SelectedCharacter
 sec
 sbc #37
 cmp #3
 bcs CoSelectNo
 tax
 lda CoCookieLo,x
 sta R5
 lda CoCookieHi,x
 sta R6
 lda CoDescriptorLo,x
 sta R3
 lda CoDescriptorHi,x
 sta R4
 sec
 rts
CoSelectNo:
 clc
 rts
CoCookieLo:.byte <CoExCookie,<PrCookie,<CoBBCookie
CoCookieHi:.byte >CoExCookie,>PrCookie,>CoBBCookie
'''+text[end:]
 pattern=r'CoCookieLo:\.byte <CoExCookie,<CoBBCookie\nCoCookieHi:\.byte >CoExCookie,>CoBBCookie\nCoDescriptorLo:\.byte <CoExDescriptor,<CoBBDescriptor\nCoDescriptorHi:\.byte >CoExDescriptor,>CoBBDescriptor'
 text,n=re.subn(pattern,'CoDescriptorLo:.byte <CoExDescriptor,<PrDescriptor,<CoBBDescriptor\nCoDescriptorHi:.byte >CoExDescriptor,>PrDescriptor,>CoBBDescriptor\n .res 2,$ea',text);assert n==1
 assert text.count(' CoFar CoWorker,$fb\n')==1;text=text.replace(' CoFar CoWorker,$fb\n',' jsr PrTypedWorker\n .res 15,$ea\n')
 assert text.count(' jsr ShRetire\n rts\n')==1;text=text.replace(' jsr ShRetire\n rts\n',' jmp PrRetire\n nop\n')
 for symbol in ['CoExCookie','CoBBCookie']:
  match=re.search(symbol+r':\.incbin "([^"\n]+)"',text);assert match
  cookie=(B/match[1]).read_bytes();assert len(cookie)==16
  text=text.replace(match[0],symbol+':.byte '+','.join(f'${v:02x}'for v in cookie))
 native=L.P.T.labels(O/'host-services-v18.lbl');cold=L.P.T.labels(O/'cold-worker-v25.lbl');cookie=bytes([0xa7,38,1])+hashlib.sha256((O/'cold-pool-v25.bin').read_bytes()).digest()[:13]
 text=f'PrDescriptor=$bf93\nPrColdBoot=${cold["PpColdBoot"]:04x}\nPrNativeRetire=${native["PpNativeRetire"]:04x}\n'+text+'''
.segment "PR_EXTRA"
.export PrTypedWorker,PrRetire,PrCookie,PrExtraEnd,CoCookieLo,CoCookieHi,CoDescriptorLo,CoDescriptorHi
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
'''+'.byte '+','.join(f'${v:02x}'for v in cookie)+'\nPrExtraEnd:\n'
 blob,lab=assemble('owner-third-v23',text,'MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'owner-third-extra-v23.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;}')
 prior=L.P.T.labels(B/'native-event-v9-owner.lbl')
 for name,a in prior.items():assert lab[name]==a,('Original public label moved',name,a,lab[name])
 assert blob[0x1f3:0x213]==old[0x1f3:0x213]and blob[0x1e6:0x1eb]==old[0x1e6:0x1eb]
 extra=(O/'owner-third-extra-v23.bin').read_bytes()
 q=dict(measured=True,qualified=False,proposal_only=True,ROM_written=False,shared_sources_written=False,base_ROM=BASE.relative_to(R).as_posix(),base_SHA256=PIN,all_original_public_manager_labels_unchanged=True,existing_Ex_BB_cookies_and_SMC_table_exact=True,original_manager_bytes=len(old),successor_manager_bytes=len(blob),third_owner_extra_bytes=len(extra),extra_half_open=[0xab72,0xab72+len(extra)],source_factor_capacity=141,remaining_after_manager=141-len(extra),common_descriptor_bytes=8,common_descriptor_proposed_half_open=[0xbf93,0xbf9b],common_descriptor_remaining_granted_worker_spare=10,Prince_public_routing_not_yet_included=True,grant=False,scope='Measured three-ID table selector in original41B and original8B data footprint, nativev9 BBretire target/cookie retained. Extra typed cold/retire/cookie now fits within141B conditional frame factor; no shared mutation or entry grant.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,B/'native-event-v9-owner.bin',B/'native-event-v9-owner.lbl',BASE,O/'owner-third-v23.bin',O/'owner-third-extra-v23.bin',O/'cold-pool-v25.bin']})
 (O/'owner-routes-measurement-v23.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
