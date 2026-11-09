"""Exercise the original D297 support decision against the observed native pipe lip."""

import argparse
import json
from pathlib import Path
import tempfile

import qualify_prince_climb_typed_shaft_1110_v3 as V3


M, P, R, N, I, E = V3.M, V3.P, V3.R, V3.N, V3.I, V3.E
CAPTURE = R / 'build/prince-third-pipe-writer-1110/capture/full11.json'
ROM = R / 'build/prince-shaft-native-1110/prince-private.nes'
MANIFEST = R / 'build/prince-climb-descent-1110/shaft-proof.json'
PROBE, CALL, TERRAIN = 0x7000, 0xa6f6, 0xa5d9

SOURCE = '''.setcpu "6502"
.segment "CODE"
.export PpD297Support
WorldTile=$bde2
ReadPoint=$b310
QueryX=$b369
QueryY=$b36b
Foot=$c084
OldFoot=$c086
Surface=$c07f
ActorAction=$c616
ActorFrame=$c617
ActorMode=$c618
Facing=$c615
NativeX=$75
NativePage=$5c
NativeY=$bd
NativeYHigh=$a4
NativeState=$1e

PpD297Support:
 jsr WorldTile
 bne Done
 php
 lda ActorAction
 cmp #1
 bne Empty
 lda ActorFrame
 cmp #15
 bne Empty
 lda ActorMode
 cmp #$ff
 bne Empty
 lda Foot+1
 ora OldFoot+1
 ora NativeState
 bne Empty
 lda NativeYHigh
 cmp #1
 bne Empty
 lda Foot
 cmp OldFoot
 bne Empty
 lda NativeY
 adc #32                        ; Exact source sole one pixel into native support.
 bcs Empty
 cmp Foot
 bne Empty
 sbc #1
 sta QueryY
 lda #0
 sta QueryY+1
 lda Facing
 and #11
 adc #1                         ; Carry was left set by subtracting one.
 adc NativeX
 sta QueryX
 lda NativePage
 adc #0
 sta QueryX+1
 jsr ReadPoint
 bcc Empty
 and #$fc
 cmp #$10
 bne Empty
 dec QueryY
 jsr ReadPoint
 bcs Empty
 lda QueryY
 adc #1
 sta Surface
 lda #0
 sta Surface+1
 plp
 lda #1
 rts
Empty:
 plp
 lda #0
Done:
 rts
'''


def fixture(seed, *, x=723, facing=255, foot=145, old=145, native_y=112, native_state=0,
            cap=True, covered=False, action=1, mode=255, frame=15):
    m = N.fork(seed)
    for y in (208,224):
        for dx in range(0,512,16):
            m[E.block(dx,y)] = 0x54
    for y in (160,176,192):
        m[E.block(736,y)] = 0x14
        m[E.block(752,y)] = 0x15
    if cap:
        m[E.block(736,144)] = 0x12
        m[E.block(752,144)] = 0x13
    if covered:
        m[E.block(736,128)] = 0x54
        m[E.block(752,128)] = 0x54
    N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=38,GameEngineSubroutine=8,
          OperMode=1,Player_State=native_state,Player_Y_HighPos=1,Player_Y_Position=native_y,
          Player_X_Position=x&255,Player_PageLoc=x>>8,TimerControl=0)
    m.raw_page(1,3);m.raw_page(2,2)
    E.put(m,0xc60f,x+8);E.put(m,0xc089,77)
    m[0xc611] = m[0xc08b] = foot - 80
    m[0xc088] = 3
    m[0xc615] = facing;m[0xc616] = action;m[0xc617] = frame;m[0xc618] = mode
    m[0xc6d1] = 5;m[0xc02c] = 4
    E.put(m,0xc084,foot);E.put(m,0xc086,old)
    return m


def result(m, path):
    assert m[CALL] == 0x20
    actual = N.NesMPU
    entered = []
    class Trace(actual):
        def step(self):
            if self.pc in (CALL,PROBE,0xc42a,0xb310):
                row = dict(PC=self.pc,A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp)
                if self.pc==0xb310:
                    row.update(qx=E.word(m,0xb369),qy=E.word(m,0xb36b))
                entered.append(row)
            return super().step()
    N.NesMPU=Trace
    try:
        ret=I.invoke(m,3,path,(0,0,0,0x21))
    finally:
        N.NesMPU=actual
    return dict(X=E.word(m,0xc60f),Y=m[0xc611],foot=E.word(m,0xc084),surface=E.word(m,0xc07f),
                action=m[0xc616],mode=m[0xc618],frame=m[0xc617],ret=ret['regs'],events=entered)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    q, proof=(json.loads(p.read_text()) for p in (CAPTURE,MANIFEST))
    raw=ROM.read_bytes()
    assert P.sha(raw)==q['ROM_sha256']==proof['expected_memory_only_SHA256']
    events=q['route']['third_pipe_writers']
    event, = [r for r in events if r['Main']==1192 and r['PC']==0xc42a]
    assert (event['source_x'],event['world_x'],event['oldFoot'],event['physical_foot'],event['native_y'],event['Y'])==(731,723,145,145,112,36)
    assert all(r['PC']!=0xa2dc for r in events if r['Main']==1192)
    base=dict(M.image(),raw=raw)
    seed,_=P.Q.C.C.cold(base,38)
    args.output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output) as directory:
        worker,labels=P.assemble(Path(directory),'source-support',SOURCE,P.one_segment(PROBE,160))
    assert labels['PpD297Support']==PROBE

    def make(options, changed):
        m=fixture(seed,**options)
        assert bytes(m[CALL:CALL+6])==bytes.fromhex('20e2bdc911f0')
        if changed:
            for i,value in enumerate(worker):
                m[PROBE+i]=value
            E.put(m,CALL+1,PROBE)
        return m

    rows=[]
    for name,options in (('recorded-approach',{}),('already-supported',{'x':739}),
            ('no-cap',{'cap':False}),('covered',{'covered':True}),('outside-foot',{'x':722}),
            ('ordinary-empty',{'x':694}),('moving-sole',{'old':144}),('native-airborne',{'native_state':2}),
            ('other-frame',{'frame':14}),('other-action',{'action':4})):
        original,after=(result(make(options,k),TERRAIN) for k in (False,True))
        fields=('X','Y','foot','surface','action','mode','frame','ret')
        if name=='recorded-approach':
            assert original['X']==708 and original['action']==7,(name,original)
            assert after['X']==731 and after['Y']==65 and after['action']==1,(name,after)
            assert after['surface']==144 and after['mode']==255
        else:
            assert all(original[k]==after[k] for k in fields),(name,original,after)
        rows.append(dict(name=name,original=original,successor=after))
    receipt=dict(passed=True,prototype_CPU_only=True,ROM_written=False,Mesen_run=False,
        ROM_sha256=P.sha(raw),prototype_bytes=len(worker),actual_D297_CPU=CALL,
        original_snap_write=event,cases=rows,live_storage_measured=False,
        bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in (Path(__file__),CAPTURE,ROM,MANIFEST)})
    (args.output/'source-support-CPU.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(passed=True,prototype_bytes=len(worker),cases=len(rows))))


if __name__=='__main__':
    main()
