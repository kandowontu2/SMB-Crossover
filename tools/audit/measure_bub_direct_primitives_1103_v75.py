"""Measure direct full-auth primitive entry; test kernel remains unfunded."""
import inspect,json
from pathlib import Path
import measure_bub_complete_auth_transport_1103_v74 as P
F,O,R=P.F,P.O,P.R


def build():
    old,auth,route,q,head,manifest,ol,nl,changes=F.build()
    source='''.setcpu "6502"
.segment "TEST_KERNEL"
.export NativePrimitives,NativeNormal,NativeSide,NativeSec,NativeNo,NativeEnd
NativePrimitives:
 php
 pha
 lda $6002
 cmp #39
 bne NativeNormal
 txa
 pha
 tya
 pha
 jsr $a e e f
 bcc NativeNo
 lda $016c
 cmp #$b6
 beq NativeSide
NativeSec:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
NativeSide:
 pla
 tay
 pla
 tax
 pla
 plp
 jmp $958b
NativeNo:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
NativeNormal:
 pla
 plp
 jmp $a740
NativeEnd:
'''.replace('$a e e f',f'${nl["CoCheckCode"]:04x}')
    cfg='MEMORY{K:start=$5800,size=$80,file=%O;}SEGMENTS{TEST_KERNEL:load=K,type=ro;}'
    labels=F.L.assemble('direct-primitives-v75-kernel',source,cfg)
    kernel=(O/'direct-primitives-v75-kernel.bin').read_bytes();assert len(kernel)==55
    raw=bytearray(auth['raw'])
    for row in [9,14,34]:
        at=16+65*8192+0x108c+3*row
        assert raw[at:at+3]==bytes.fromhex('4c40a7')
        raw[at:at+3]=bytes([76,P.TEST&255,P.TEST>>8])
    return old,auth,dict(auth,raw=bytes(raw)),route,q,ol,nl,kernel,labels


def main():
    text=inspect.getsource(P.main)
    text=text.replace('complete-auth-v74-measurement.json','direct-primitives-v75-measurement.json')
    text=text.replace('complete-auth-v74-kernel','direct-primitives-v75-kernel')
    text=text.replace("primitive_calls[1]==dict(side=48,sec=24,normal=84)","primitive_calls[1]==dict(side=48,sec=24,normal=0)")
    text=text.replace("side='Raw39 only; exact immutable fixed958B getter with originalY/P; capture through existing AB38 result copy.'", "side='Raw39 only; exact immutable fixed958B getter after complete auth, originalAXYP restored, return through original outer FRC. No shared five-SMC frame/private RAM transport.'")
    text=text.replace("sec='Raw39 only; rows9/34 have actual SEC/RTS B57C. Sets original savedP carry, restores current frame, and returns via existing outer FRC which sets NZ from returnedA.'", "sec='Raw39 only; rows9/34 have actual SEC/RTS B57C. Complete auth then exact savedAXYP restore and SEC; outer FRC normalizesNZ from returnedA.'")
    text=text.replace('The57B executable kernel','The55B executable kernel')
    text=text.replace('The 57-byte','The 55-byte')
    text=text.replace("Path(F.__file__),", "Path(F.__file__),Path(P.__file__),")
    env=dict(P.__dict__,P=P,build=build,__file__=__file__)
    exec(compile(text,__file__,'exec'),env);env['main']()


if __name__=='__main__':main()
