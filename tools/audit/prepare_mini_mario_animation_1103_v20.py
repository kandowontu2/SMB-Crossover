"""Small original-frame Mini animation selector/tick leaf; source-only CPU proof."""
import hashlib,itertools,json,re,subprocess,zipfile
from pathlib import Path
from py65.devices.mpu6502 import MPU

R=Path(__file__).resolve().parents[2];O=R/'build/mini-mario-animation-1103-v20';ART=R/'build/mini-mario-art-1103-v12'
SOURCE='''.setcpu "6502"
.segment "CODE"
.export MiniAnimate,MiniAnimateEnd
MiniCurrent=$c240
MiniTier=$c244
MiniFacing=$c245
MiniClass=$c246
MiniAnimation=$c24d
MiniMoving=$c24e
MiniTick=$c206
MiniPose=$c310
MiniGameTime=$c320
MiniSequence=$c321
MiniFrame=$c322
MiniLength=$c323
; Call exactly once after each genuine Step, before Draw. Fresh clears
; C320..C323. A/X/Y and flags are caller-dead; no source/ZP state is changed.
MiniAnimate:
 lda MiniClass
 cmp #2
 bcc Air
 ldx MiniFacing
 lda MiniMoving
 beq NotMoving
 txa
 clc
 adc #4
 tax
NotMoving:
 lda MiniClass
 cmp #3
 bne Ground
 lda MiniTier
 beq SmallCrouch
 txa
 clc
 adc #8
 bne Form
SmallCrouch:
 txa
 clc
 adc #48
 bne Form
Ground:
 lda MiniCurrent
 cmp #9
 bcc Default
 cmp #12
 bcs Default
 txa
 clc
 adc #32
 bne Form
Default:
 txa
 jmp Form
Air:
 lda MiniAnimation
Form:
 ldy MiniTier
 beq Row
 clc
 adc #88
Row:
 asl a
 tax
 bcc LowPage
 lda $d100,x
 bcs GotSequence
LowPage:
 lda $d000,x
GotSequence:
 cmp MiniSequence
 beq SameSequence
 sta MiniSequence
 lda #0
 sta MiniFrame
SameSequence:
 ldy MiniSequence
 lda $d160,y
 sta MiniLength
 lda MiniGameTime
 and MiniTick
 bne Draw
 inc MiniFrame
 lda MiniFrame
 cmp MiniLength
 bcc Draw
 lda #0
 sta MiniFrame
Draw:
 tya
 clc
 adc MiniFrame
 tay
 iny
 lda $d160,y
 sta MiniPose
 inc MiniGameTime
 rts
MiniAnimateEnd:
'''


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    O.mkdir(exist_ok=True);assert not(O/'receipt.json').exists()
    source=O/'animate.s';source.write_text(SOURCE)
    cfg=O/'animate.cfg';cfg.write_text('MEMORY{P:start=$a000,size=$100,file=%O;}SEGMENTS{CODE:load=P,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for args in[[cc/'ca65.exe',source,'-o',O/'animate.o'],[cc/'ld65.exe','-C',cfg,O/'animate.o','-o',O/'animate.bin','-Ln',O/'animate.lbl']]:
        z=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert z.returncode==0,z.stderr
    body=(O/'animate.bin').read_bytes();assert len(body)<=200
    index=(ART/'engine-animation-index.bin').read_bytes();frames=(ART/'engine-animation-frames.bin').read_bytes()
    layout=json.loads((ART/'layout.json').read_text());engine=json.loads((ART/'engine-art-v13.json').read_text())
    assert len(index)==352 and len(frames)==217 and all(index[i]==0 for i in range(1,len(index),2))
    references={(r['form'],r['state']):r for r in engine['rows']}
    def expected(tier,cls,facing,moving,current,air,clock,tick,context):
        form='supamario'if tier else'smolmario'
        state='Crouch'if cls==3 else'Skid'if cls==2 and 9<=current<=11 else''
        animation=air if cls<2 else facing+4*moving
        row=references[form,state]['engine_rows'][animation];ids=row['pose_ids'];offset=row['offset']
        frame=context[1]if context[0]==offset else 0
        if(clock&tick)==0:
            frame+=1
            if frame==len(ids):frame=0
        return ids[frame],(offset,frame,len(ids)),(clock+1)&255
    def run(tier,cls,facing,moving,current,air,clock,tick,context=(0,0,0)):
        m=MPU();m.memory[0xa000:0xa000+len(body)]=body;m.memory[0xd000:0xd160]=index;m.memory[0xd160:0xd239]=frames
        for at,value in[(0xc244,tier),(0xc246,cls),(0xc245,facing),(0xc24e,moving),(0xc240,current),(0xc24d,air),(0xc206,tick),(0xc320,clock),(0xc321,context[0]),(0xc322,context[1]),(0xc323,context[2])]:m.memory[at]=value
        before=m.memory[:];m.pc=0xa000;m.sp=222;m.memory[0x1df]=0xfe;m.memory[0x1e0]=0x7f;cycles=m.processorCycles
        for step in range(200):
            m.step()
            if m.pc==0x7fff:break
        else:raise AssertionError('Bounded animate return')
        assert m.sp==224
        changed={i for i,(a,b)in enumerate(zip(before,m.memory))if a!=b}
        assert changed<={0xc310,0xc320,0xc321,0xc322,0xc323,0x1df,0x1e0}
        return m.memory[0xc310],tuple(m.memory[0xc321:0xc324]),m.memory[0xc320],m.processorCycles-cycles
    cases=0;costs=[]
    for tier,cls,facing,moving,current,air,tick,clock in itertools.product([0,1],range(4),[1,3],[0,1],[5,10],[0,2],[3,7],range(16)):
        # Crouch/air source always publishesMoving0; other fields retain
        # stale legitimate values. Ground uses any previous air index.
        if cls!=2 and moving:continue
        oracle=expected(tier,cls,facing,moving,current,air,clock,tick,(0,0,0));actual=run(tier,cls,facing,moving,current,air,clock,tick)
        assert actual[:3]==oracle,(tier,cls,facing,moving,current,air,clock,tick,actual,oracle)
        costs.append(actual[3]);cases+=1
    episodes=[]
    for tier in[0,1]:
        context=(0,0,0);clock=0;poses=[]
        for step in range(320):
            cls=2 if step<96 or step>=256 else 1 if step<128 else 0 if step<160 else 3 if step<224 else 2
            facing=1 if step<48 or step>=160 else 3;moving=int(cls==2 and(step%48)>7)
            current=10 if 224<=step<256 else 5;air=0 if facing==3 else 2;tick=3 if moving and step&1 else 7
            oracle=expected(tier,cls,facing,moving,current,air,clock,tick,context)
            actual=run(tier,cls,facing,moving,current,air,clock,tick,context);assert actual[:3]==oracle
            pose,context,clock=oracle;poses.append(pose);costs.append(actual[3])
        episodes.append(dict(tier=tier,updates=320,source_clock_wraps=1,distinct_original_poses=sorted(set(poses))))
    reference=R/'docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1/reference.zip'
    with zipfile.ZipFile(reference)as z:
        actor=z.read('plugins/GameSpecific/engine/src/core/actor.c').decode();platform=z.read('plugins/PlatformerPlus/engine/src/states/platform.c').decode()
    assert '(game_time & actor->anim_tick) == 0'in actor and 'actor->frame = frame_start;'in actor and 'actor->frame = actor->frame_start;'in actor
    assert 'STATE_SKID'in platform and 'STATE_CROUCH'in platform and 'PLAYER.anim_tick = 7;'in platform
    out=dict(passed=True,source_only=True,ROM_written=False,native_qualified=False,bytes=len(body),CPU_range=[min(costs),max(costs)],
        finite_engine_byte_cases=cases,composed_episodes=episodes,composed_updates=640,
        public_entry='MiniAnimate; relocatable source segment, standalonetest linkedA000. Call once after sourceStep beforeDraw.',
        input_contract='C240Current9..11Skid; C244Tier0small/positivepowered; C245Facing1Right/3Left; C246Class0Fall/1Jump/2Ground/3Crouch; C24Dactualairanimation0Left/2Right; C24EMoving0/1 (groundonly); C206originaltick3/7.',
        immutable_data=dict(engine_index=[0xd000,0xd160],frame_sequences=[0xd160,0xd239],index_high_bytes_all_zero=True),
        outputs=dict(pose_ID=0xc310,game_time=0xc320,sequence_offset=0xc321,frame_offset=0xc322,sequence_length=0xc323),
        ABI='FreshmustclearC320..C323. A/X/Y/Pclobbered, SPpreserved; noR0..7/ZP/sourceworld writes. C324..C32Funtouched. Updates caller-owned onebyte game_time after applying originalactor tick condition, modulo256.',
        state_scope='Initial idle/walk/jump/fall/crouch/skid only; originalsourceframes/sequenceorder/tickmask retained. No attack/swim/climb/death/power-transform state invented or claim of completeoriginalGBanimationdispatch. Empty sourceframe poses remain valid.',
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),source,cfg,O/'animate.bin',O/'animate.lbl',ART/'engine-art-v13.json',ART/'engine-animation-index.bin',ART/'engine-animation-frames.bin',ART/'layout.json',reference,R/'tools/reference/mini_mario_world_1103_v16.inc']})
    (O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','CPU_range','finite_engine_byte_cases','composed_updates','public_entry']}))


if __name__=='__main__':main()
