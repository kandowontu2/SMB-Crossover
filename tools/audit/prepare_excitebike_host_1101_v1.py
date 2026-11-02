"""Assemble a source-backed side-view kernel; no ROM, menu or Mesen mutation."""
from pathlib import Path
import copy,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit'),str(R/'tools/reference')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from py65.disassembler import Disassembler
import excitebike_original_cpu_1101_v2 as E
from prepare_excitebike_dispatch_1101_v1 import labels,sha,save,O
BASE=R/'build/shinobi-bbox-candidate-1101-v30/candidate.nes'
PIN='6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428'

def recovery():
    c=E.machine();d=Disassembler(c);ins={}
    for lo,hi in [(0xd918,0xda26),(0xddd1,0xde31),(0xe96c,0xea07)]:
        pc=lo
        while pc<hi:
            n,t=d.instruction_at(pc);mn,mode=c.disassemble[c.memory[pc]]
            assert mn!='???';value=int.from_bytes(bytes(c.memory[pc+1:pc+n]),'little')
            ins[pc]=(mn,mode,value,n,t);pc+=n
        assert pc==hi
    branches={'BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BCS':'jcs','BCC':'jcc'}
    def code(a):
        if a==0xca85:return 'ExRecoveryUnsupported'
        if a==0xea07:return 'ExLaneReturn'
        if a==0xdd06:return 'ExN_DD06'
        assert a in ins,hex(a)
        return f'ExRec_{a:04X}'
    def data(a):
        if a<0x2000:return f'ExState+${a&2047:03x}'
        assert (0xd8c4<=a<0xd8c9)or(0xd8ff<=a<0xd916)or(0xe53d<=a<0xe541),hex(a)
        return f'ExRecData_{a:04X}'
    out=['.setcpu "6502"\n.macpack longbranch\n.import ExState,ExN_DD06\n.segment "EX_REC"\n.export ExCrashAll,ExRecoveryAll,ExLaneAll,ExHeatRelease\nExCrashAll=ExRec_DDD1\nExRecoveryAll=ExRec_D918\nExLaneAll=ExRec_E96C\n']
    for pc,(mn,mode,v,n,t)in ins.items():
        target=''
        if mode=='rel':target=code((pc+2+(v if v<128 else v-256))&65535);mn=branches[mn]
        elif mode in ['abs','abx','aby','zpg','zpx','zpy','ind']:
            target=code(v)if mn in['JSR','JMP']and mode!='ind'else data(v)
            target+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y',ind='')[mode]
            if mode=='ind':target='('+target+')'
        elif mode=='imm':target=f'#${v:02x}'
        elif mode=='acc':target='a'
        else:assert mode=='imp'
        out.append(f'.export ExRec_{pc:04X}\nExRec_{pc:04X}: {mn.lower()} {target} ; source${pc:04X}: {t}\n')
    # Source$03f7 is the donor's out-of-race routing flag. The owning SMB
    # constructor initializes it to0 and no admitted host entry writes it.
    out.append('ExRecoveryUnsupported: clc\n rts\nExLaneReturn:rts\n')
    roots=[c.memory[0xd8ff+i]+256*c.memory[0xd905+i]for i in range(6)]
    for lo,hi in [(0xd8c4,0xd8c9),(0xd8ff,0xd916),(0xe53d,0xe541)]:
        for a in range(lo,hi):
            v=f'${c.memory[a]:02x}'
            if 0xd8ff<=a<0xd905:v='<'+code(roots[a-0xd8ff])
            if 0xd905<=a<0xd90b:v='>'+code(roots[a-0xd905])
            out.append(f'ExRecData_{a:04X}: .byte {v}\n')
    out.append('''
ExHeatRelease:
 lda ExState+$03c
 cmp #8
 bne ExHeatReturn
 ; Genuine DDBF..DDCB state writes; original tail CD13 is a typed return.
 lda #0
 sta ExState+$3e0
 lda #5
 sta ExState+$3b6
 sta ExState+$09c
 sta ExState+$374
ExHeatReturn:rts
.export ExRecoveryEnd
ExRecoveryEnd:
''')
    (O/'host-recovery.s').write_text(''.join(out))
    return ins

def main():
    assert sha(BASE)==PIN
    b=scoped_load(BASE);ins=recovery()
    names=['R0','R1','R2','R3','R4','R5','R6','R7','OperMode','DisableScreenFlag','Mirror_PPUMASK',
           'NmiDisable','FamilyMainCommit','PlayerSize','CrouchingFlag','Player_X_Position','Player_PageLoc',
           'Player_Y_Position','Player_Y_HighPos','Player_X_Scroll','Player_X_Speed','Player_Y_Speed',
           'Player_State','PlayerFacingDir','Player_Pos_ForScroll','Player_BoundBoxCtrl','ScreenLeft_X_Pos','ScreenLeft_PageLoc',
           'GameEngineSubroutine','GamePauseStatus','FrameCounter','SavedJoypadBits','Block_Buffer_1','Block_Buffer_2',
           'CurrentCHRBank','X5ChrMode','SsChrActive','X5WideChrActive','ReloadCHRBank','MetaspriteRenderLoop',
           'Player_SprAttrib','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','HuNativeWorldPalette',
           'VRAM_Buffer1_Offset','VRAM_Buffer1','BlockBufferColli_Head','BlockBufferColli_Side',
           'ObjectMetasprite','SmPosePtr','BackgroundColorCtrl','AreaType']
    source='.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in names)
    for n in ['MetaspriteRenderLoop','HuNativeWorldPalette']:
        source+=f'Bank_{n}=${((location(b,n)-16)//8192)|128:02x}\n'
    source+='.include "excitebike_native_boundary_1101_v1.inc"\n'
    (O/'host.s').write_text(source)
    at=location(b,'BackgroundColors');(O/'host-background.bin').write_bytes(b['raw'][at:at+8])
    cc=R/'tools/Windows/cc65/bin'
    commands=[[cc/'ca65.exe','-I',R/'tools/reference','--bin-include-dir',O,O/'host.s','-o',O/'host.o'],
              [cc/'ca65.exe',O/'host-recovery.s','-o',O/'host-recovery.o']]
    cfg='MEMORY{K:start=$a000,size=$1800,file=%O,fill=yes;}SEGMENTS{EX_CODE:load=K,type=ro;EX_DATA:load=K,type=ro,start=$a900;EX_HOST:load=K,type=ro,start=$a950;CODE:load=K,type=ro,start=$b000;EX_REC:load=K,type=ro,start=$b100;}'
    (O/'host.cfg').write_text(cfg)
    commands.append([cc/'ld65.exe','-C',O/'host.cfg',R/'build/excite-prince-component-1101-v2/component.o',
                     O/'pose.o',O/'host.o',O/'host-recovery.o','-o',O/'host-kernel.bin','-Ln',O/'host.lbl'])
    for cmd in commands:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    lab=labels(O/'host.lbl');kernel=bytearray((O/'host-kernel.bin').read_bytes())
    vector=['ExHostReject']*37
    for row,name in {0:'ExHostMovement',1:'ExHostGraphics',2:'ExHostDraw',4:'ExHostWeapons',5:'ExHostInjury',6:'ExHostInjuryStatus',
                     10:'ExHostHead',11:'ExHostBody',12:'ExHostAdder',14:'ExHostSide',15:'ExHostConstruct',
                     26:'ExHostColors',30:'ExHostStatus',31:'ExHostBounce',32:'ExHostWorldColors',36:'ExHostScene'}.items():vector[row]=name
    kernel[0x500:0x56f]=b''.join(bytes([76,lab[n]&255,lab[n]>>8])if n!='ExHostReject'else bytes([76,0x6f,0xa5])for n in vector)
    kernel[0x56f:0x571]=bytes([24,96])
    (O/'host-kernel.bin').write_bytes(kernel)
    art=json.loads((O/'body-native.json').read_text());packets=bytearray();offsets=[]
    for pose in art['poses']:
        offsets.append(46+len(packets));cells=pose['cells'];packets.append(len(cells)*4)
        for cell in reversed(cells):packets.extend([cell['tile']*2+1,cell['attr'],cell['y']&255,(cell['x']-12)&255])
    metadata=b''.join(n.to_bytes(2,'little')for n in offsets)+bytes(packets)
    assert len(metadata)==513
    at=location(b,'MTileAttribute');metadata+=b['raw'][at:at+256]
    assert len(metadata)<=2048
    metadata+=bytes(2048-len(metadata));(O/'host-metadata.bin').write_bytes(metadata)
    cookie=bytes([167,37,1])+hashlib.sha256(kernel+metadata+(O/'body-native.chr').read_bytes()).digest()[:13]
    (O/'host-cookie.bin').write_bytes(cookie)
    q=dict(passed=True,component_only=True,ROM_written=False,base_ROM_SHA256=PIN,
           source_host_bytes=lab['ExHostEnd']-0xa950,recovery_bytes=lab['ExRecoveryEnd']-0xb100,
           private_kernel_bytes=len(kernel),private_metadata_used_bytes=769,code_pages=list(range(728,734)),
           host_entries={row:lab[name]for row,name in enumerate(vector)if name!='ExHostReject'},
           deliberate_controls='Right/Left source throttle; coast-to-zero reversal; B original turbo; A fresh source launch; Up/Down original lean.',
           source_recovery_ranges=[[0xd918,0xda26],[0xddd1,0xde31],[0xe96c,0xea07]],
           conditional_state=[0xc000,0xc800],context=[0xc800,0xc80f],transient=[0xc880,0xc899],
           native_body='SMB32px body, constructor preserves prior foot Y. Native head/pipe/coin/effect collision handoffs still require public-service ingress closure.',
           native=False,menu_unlock=False,installed=False,
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),R/'tools/reference/excitebike_native_boundary_1101_v1.inc',O/'host.s',O/'host-recovery.s',O/'host-kernel.bin',O/'host-metadata.bin',O/'host-cookie.bin',BASE]})
    save('host-assembly.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))

if __name__=='__main__':main()
