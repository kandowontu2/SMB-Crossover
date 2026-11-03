"""Close donor actor imports and compile the private native phase, not a ROM.

The source queue is deliberately private. Its packets do not name native
nametables. Native score/presentation and current enemy admission are distinct
remaining ports; this recipe does not make a new public owner functional.
"""
import json,re,subprocess
from pathlib import Path
import prepare_dkjr_native_world_1102_v3 as W
from py65.disassembler import Disassembler
R=W.R;O=W.O;D=W.P.D


def main():
    receipt=json.loads((O/'native-link-v5-proof.json').read_text());assert receipt['passed']
    for rel,sha in receipt['bindings'].items():assert W.P.sha((R/rel).read_bytes())==sha,rel
    prior=json.loads((O/'native-link-v5-layout.json').read_text())
    source=(O/'native-link-v5.s').read_text().replace('DkjrComponentEnd:\n.export DkjrNativeCarryEnd,DkjrComponentEnd','')
    # Close the actual leaf imports with original instructions. EC3B includes
    # the original score queue and two source popup slots. EFCE/F1C5 include
    # the original bounded63-byte source VRAM queue; no native PPU write occurs.
    ranges=[(0xec3b,0xecb7),(0xed44,0xed8e),(0xee7f,0xee9c),
            (0xefce,0xf040),(0xf1c5,0xf1f8)]
    ins={};m=D.Bus();dis=Disassembler(D.T.NesMPU(memory=m,pc=0))
    for lo,hi in ranges:
        pc=lo
        while pc<hi:
            n,s=dis.instruction_at(pc);assert pc+n<=hi
            ins[pc]=(n,s.lower());pc+=n
    # Native stages deliberately use donor contact profile1. The original
    # ECB7 stage1/4 early return is exact; profiles2/3 require donor level AI
    # and are rejected by the native phase before this private leaf is called.
    pc=0xecb7
    while pc<0xecc3:
        n,s=dis.instruction_at(pc);ins[pc]=(n,s.lower());pc+=n
    for target in [0xecb7,0xed44,0xed7b,0xefce,0xf1c5]:
        old='DImport_%04x: jmp DImport_%04x ; closed local trap until typed host binding'%(target,target)
        assert source.count(old)==1;source=source.replace(old,'DImport_%04x: jmp D_%04x'%(target,target))
    existing=set(int(x,16)for x in re.findall(r'^D_([0-9a-f]{4}):',source,re.M))
    for pc,(n,s) in sorted(ins.items()):
        source+='\nD_%04x: ; original $%04X: %s\n'%(pc,pc,s)
        op=s.split()[0]
        if op in ['jsr','jmp','bcc','bcs','beq','bne','bmi','bpl','bvc','bvs']:
            target=int(s.split('$')[1],16)
            if target==0xecc3:target_name='DkjrNativePhaseReject'
            else:
                assert target in ins or target in existing,(hex(pc),s)
                target_name='D_%04x'%target
            source+=' '+('j'+op[1:]if op.startswith('b')else op)+' '+target_name+'\n'
            continue
        indirect=re.fullmatch(r'(lda|sta) \(\$([0-9a-f]{2})\),y',s)
        if indirect:
            ptr=int(indirect[2],16);tag='DIndirect_%04x'%pc
            source+='\n'.join([' php',' pha',' lda $%04x'%(0xc000+ptr),' sta '+tag+'+1',
                ' lda $%04x'%(0xc001+ptr),' cmp #8',' bcs '+tag+'_rom',' ora #$c0',
                tag+'_rom:',' sta '+tag+'+2',' pla',' plp',tag+': '+indirect[1]+' $ffff,y'])+'\n'
            continue
        def remap(q):
            a=int(q[1],16)
            if a<0x800:return '$%04x'%(a+0xc000)
            if 0xc614<=a<0xc622:return 'DNativeData_%04x'%a
            raise AssertionError((hex(pc),s,hex(a)))
        if '#'not in s:s=re.sub(r'\$([0-9a-f]+)',remap,s)
        source+=' '+s+'\n'
    for pc in range(0xc614,0xc622):source+='DNativeData_%04x: .byte $%02x\n'%(pc,m[pc])
    source+='''
.export DkjrNativePhase,DkjrNativeSourcePhase,DkjrNativeSourceFruitInitialize
; Actual native input, current native platform boxes and source-format terrain
; feed this private phase. No new rawID, service row, loader or menu is patched.
; Profile1 means the source's normal walking/vine/jump/fruit actor, without its
; stage2/3 enemy-specific jump-over bonus scheduler. A new owner must enforce
; this constructor contract rather than silently indexing donor stage tables.
DkjrNativePhase:
 lda GameEngineSubroutine
 cmp #8
 bne DkjrNativePhaseReject
 lda TimerControl
 bne DkjrNativePhaseReject
 lda $c04a
 cmp #1
 bne DkjrNativePhaseReject
 lda $c06b
 cmp #1
 bcc DkjrNativePhaseReject
 cmp #6
 bcs DkjrNativePhaseReject
 jsr DkjrNativeControls
 lda $c068
 bne NativePhaseHit
 lda $c06b
 cmp #5
 beq NativePhaseDeath
 jsr DkjrNativeRefreshPlatforms
 jsr DkjrNativeSourcePhase
 jsr DkjrNativePublishAnchor
 rts
NativePhaseHit:
 jsr DkjrFruitHit
 sec
 rts
NativePhaseDeath:
 jsr DkjrDefeatTick
 sec
 rts
DkjrNativePhaseReject:
 clc
 rts
; CD91 order, with donor stage enemy scheduling/goal/demo/pause owned by the
; native engine. Source fruit hit and death freeze the original Clock. Air
; keeps its latched direction: CE6C must not run for source state3 or4.
DkjrNativeSourcePhase:
 lda $c068
 bne SourcePhaseHit
 lda $c06b
 cmp #5
 beq SourcePhaseDeath
 cmp #4
 beq SourcePhaseMove
 cmp #3
 beq SourcePhaseMove
 jsr DkjrInput
SourcePhaseMove:
 jsr DkjrLandPose
 jsr DkjrTransition
 jsr DkjrMove
 jsr DkjrFruitCollision
 jsr DkjrFruitAdvance
 jsr D_ec17
 jsr D_cec9
 jsr DkjrClock
 lda $c054
 sta $c055
 sec
 rts
SourcePhaseHit:
 jsr DkjrFruitHit
 sec
 rts
SourcePhaseDeath:
 jsr DkjrDefeatTick
 sec
 rts
; The original four stage1 records remain an explicitly private source fixture
; until a world-fruit producer supplies world coordinates and native draw/score
; consumers. It is not a claim that those fruits were placed in SMB1.
DkjrNativeSourceFruitInitialize:
 lda #<DData_c311
 sta $c091
 lda #>DData_c311
 sta $c092
 lda #28
 sta $c093
 ldx #3
SourceFruitAvailability:
 lda #1
 sta $c09a,x
 lda DData_c2cd,x
 sta $c08d,x
 dex
 bpl SourceFruitAvailability
 ; Empty, one-entry original victim lists avoid zero-count source loops. Real
 ; native enemies are not admitted by this fixture constructor.
 lda #1
 sta $c0a0
 sta $c0b0
 lda #$ff
 sta $c2c0
 sta $c2e0
 rts
DkjrNativePhaseEnd:
DkjrComponentEnd:
.export DkjrNativePhaseEnd,DkjrComponentEnd
'''
    (O/'native-phase-v6.s').write_text(source)
    (O/'native-phase-v6.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'native-phase-v6.s','-g','-o',O/'native-phase-v6.o'],
                [cc/'ld65.exe','-C',O/'native-phase-v6.cfg',O/'native-phase-v6.o','-o',O/'native-phase-v6.bin','-Ln',O/'native-phase-v6.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    blob=(O/'native-phase-v6.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-phase-v6.lbl').read_text(),re.M)}
    assert len(blob)<=8160 and not re.search(r'^DImport_(\w+): jmp DImport_\1',source,re.M)
    native_bindings=dict(prior['native_bindings'])
    for name in ['GameEngineSubroutine','TimerControl']:
        native_bindings[name]=int(re.search(r'^'+name+r'=\$([0-9a-f]+)$',source,re.M)[1],16)
    q=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,component_bytes=len(blob),header_reserved_spare=8160-len(blob),
        code_SHA256=W.P.sha(blob),labels=labels,base_ROM_SHA256=W.PIN,source_bytes_added=sum(hi-lo for lo,hi in ranges)+12,
        original_ranges_added=ranges+[(0xecb7,0xecc3)],remaining_unbound_source_imports=0,native_phase_implemented=True,
        source_queue_is_private=True,native_score_and_fruit_presentation_implemented=False,current_native_enemy_admission=False,
        private_state_half_open=[0xc000,0xc900],native_calls=prior.get('native_calls',[]),native_bindings=native_bindings,
        scope='Compiled native gated movement/terrain/platform/source fruit phase. Original source queues are functional private state, not native VRAM/score. No native enemy proxy, fruit world producer, draw/CHR/palette/HUD, current camera transport, owner/event routes or physical resources are admitted.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in [Path(__file__),O/'native-link-v5-proof.json',O/'native-link-v5.s',O/'native-phase-v6.s',O/'native-phase-v6.bin']})
    (O/'native-phase-v6-layout.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','qualified','component_bytes','header_reserved_spare','code_SHA256','remaining_unbound_source_imports','native_phase_implemented','native_score_and_fruit_presentation_implemented']}))


if __name__=='__main__':main()
