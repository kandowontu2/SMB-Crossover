"""Exact authenticated row7 factoring proposal; no grant or ROM mutation."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_native_lifecycle_1102_v71 as C
import measure_prince_collision_services_1102_v49 as A
O=C.O;N=C.C.N;address=C.C.address


def measure():
 text=(O/'collision-selector-v59.s').read_text()
 needle='PrPrince:\n lda FarcallJmpTarget_SMC+1\n sta $c09e\n'
 assert text.count(needle)==1
 # CoCheckCode, B0 public page and full0..113 tag validation are before
 # PrPrince. Map the already authenticated C2 only for this exact row.
 text=text.replace(needle,needle+''' cmp #21
 bne PrRegular
 lda #2
 sta CurrentBankC
 sta $5116
 jmp PpAfterAuthDeathAck
PrRegular:
''')
 text='CurrentBankC=$7da1\nPpAfterAuthDeathAck=$c766\n'+text
 blob,labels=A.A.assemble('death-ack-selector-v73',text,(O/'collision-selector-v59.cfg').read_text())
 assert len(blob)==171 and labels['PrSelectEnd']==0xa7eb
 shared=A.P.T.labels(O/'shared-frame-v22.lbl');restore=shared['ShDispatchRestore']
 # The public scalar fallback restores A with PLA, so its N/Z come from A,
 # C is clear, and all other incoming flags survive. ShDispatchNo alone
 # would preserve incoming N/Z and is therefore not an exact replacement.
 source=f'''.setcpu "6502"
.segment "ACK"
.export PpAfterAuthDeathAck,PpAfterAuthDeathAckEnd
PpAfterAuthDeathAck:
 tsx
 lda $010a,x
 and #$7c
 sta $010a,x
 lda $0109,x
 php
 pla
 and #$82
 ora $010a,x
 sta $010a,x
 jmp ${restore:04x}
PpAfterAuthDeathAckEnd:
'''
 helper,hl=A.A.assemble('death-ack-private-v73',source,'MEMORY{M:start=$c766,size=$1a,file=%O;}SEGMENTS{ACK:load=M,type=ro;}')
 assert len(helper)==25 and hl['PpAfterAuthDeathAckEnd']==0xc77f
 return blob,helper


def install(m,blob,helper):
 raw=bytearray(m.bundle['raw']);at=16+65*8192+0x740;raw[at:at+len(blob)]=blob
 m.bundle=dict(m.bundle,raw=bytes(raw))
 for window,bank in enumerate(m.rawtags):
  if bank==193:m.raw_page(window,bank)
 m.ram[2][0x766:0x766+len(helper)]=helper


def loaded():
 b,m,lab=C.loaded();install(m,(O/'death-ack-selector-v73.bin').read_bytes(),(O/'death-ack-private-v73.bin').read_bytes());return b,m,lab


def main():
 blob,helper=measure();q=dict(measured=True,qualified=False,ROM_written=False,source_injected_CPU_only=True,selector_bytes=len(blob),selector_capacity=178,selector_growth=15,selector_spare=7,private_helper_half_open=[0xc766,0xc77f],private_helper_bytes=len(helper),requested_private_interval=[0xc766,0xc780],grant_status='Neither selector change nor new private execution interval is granted. Current DK175-byte proposal would need12additional selector bytes before composition.',provenance='The exact owner38 branch is reached only after complete CoCheckCode header check and fixedB0 page/full0..113 service-range admission. Only service21 (native DeathStart row7) takes the new leaf. Its existing public scalar fallback is pure C0 with N/Z restored from original A. New leaf reproduces the complete saved AXYP result; it does not mutate source death/action, pit, engine, native MmDeathFlag or timers. Genuine UnionDeathStartCore still executes all original initializers after this callback returns.',required='Full actual row7 binary/state/flag/header parity; genuine contact/pit/death/life/respawn and deep ISR; finite C766..C780 original-reader closure and cold/fresh copy/backing proof. No native-ready claim.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'collision-selector-v59.s',O/'collision-selector-v59.bin',O/'shared-frame-v22.s',O/'shared-frame-v22.bin',O/'death-ack-selector-v73.s',O/'death-ack-selector-v73.bin',O/'death-ack-private-v73.s',O/'death-ack-private-v73.bin',O/'native-stack-negative-v72.json']})
 (O/'death-ack-measurement-v73.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
