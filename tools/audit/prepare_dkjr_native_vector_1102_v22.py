"""Compile the genuine38-entry DK vector and first native owner leaves.

Private component under the conditional v20 resource lease. No shared route,
menu byte, carrier ROM, admission cookie or cartridge is modified/emitted.
Unimplemented vector rows remain explicit CLCRTS, never a native-ready claim.
"""
import json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O;W=A.W


def main():
    grant=R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json';g=json.loads(grant.read_text());assert g['raw_identity']==40 and g['shared_bytes_granted']==0
    source=(O/'native-body-v10.s').read_text();q=json.loads((O/'native-body-v10-layout.json').read_text());assert A.sha((O/'native-body-v10.bin').read_bytes())==q['code_SHA256']
    vector='.export DkServices,DkUnavailable,DkConstruct\nDkServices:\n'
    targets={0:'DkNativeMain',2:'DkjrNativeDrawBody',15:'DkConstruct'}
    for i in range(38):vector+=' jmp '+targets.get(i,'DkUnavailable')+'\n'
    assert source.count('.segment "DKJR"\n')==1;source=source.replace('.segment "DKJR"\n','.segment "DKJR"\n'+vector,1)
    source=source.replace('DkjrComponentEnd:\n.export DkjrNativeBodyEnd,DkjrComponentEnd','')
    source+='''
; Fresh is a real constructor, not a header or seeded source actor shortcut.
; Original CA82 supplies its defeat counter36 and active source state. There
; is one active donor actor0; native CurrentPlayer still selects native life
; and score ownership in the previously qualified imports.
DkConstruct:
 lda #1
 sta $c04a
 lda #0
 sta $c049
 jsr DkjrInitialize
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sec
 sbc #8
 sta $c000
 lda Player_Y_Position
 clc
 adc #15
 sta $c001
 lda #$18
 sta $c002
 lda #0
 jsr DkjrPose
 ldx #28
 lda #1
DkConstructAttributes:
 sta $c212,x
 dex
 dex
 dex
 dex
 bpl DkConstructAttributes
 jsr DkjrNativeWorldEnable
 jsr DkjrNativeFruitReset
 jsr DkjrNativeLifeReset
 lda #1
 sta $c8fe
 sec
 rts
DkUnavailable:
 clc
 rts
DkjrComponentEnd:
.export DkjrComponentEnd
'''
    # Main/meta helper is linked in its owned helper row, after the measured
    #286B native-pause leaf. It is not an expanded resident allocation.
    source+='''
.segment "DK_MAIN"
.export DkNativeMain,DkNativeMainEnd
Player_X_Scroll=$06ff
Player_X_Speed=$0057
Player_Y_Speed=$009f
Player_State=$001e
DkNativeMain:
 lda $c8fe
 beq DkMainNo
 lda Player_X_Position
 sta $c8fb
 lda Player_Y_Position
 sta $c8fc
 jsr DkPauseMain
 bcc DkMainNo
 lda Player_X_Position
 sec
 sbc $c8fb
 sta Player_X_Scroll
 asl
 asl
 asl
 asl
 sta Player_X_Speed
 lda Player_Y_Position
 sec
 sbc $c8fc
 sta Player_Y_Speed
 lda $c06b
 cmp #1
 beq DkMainGround
 cmp #2
 beq DkMainVine
 lda #2
 bne DkMainState
DkMainVine:
 lda #3
 bne DkMainState
DkMainGround:
 lda #0
DkMainState:
 sta Player_State
 sec
 rts
DkMainNo:
 clc
 rts
DkNativeMainEnd:
'''
    # Bind all native cache names through actual current metadata, never a
    # remembered source address. The four values above are verified below.
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes')
    for name in ['Player_X_Scroll','Player_X_Speed','Player_Y_Speed','Player_State']:
        source=re.sub(r'^'+name+r'=\$[0-9a-f]+$',name+'=$%04x'%W.address(b,name),source,flags=re.M)
    pause=(O/'native-pause-v16.s').read_text()
    pause=pause.replace('.macpack longbranch\n','')
    # First resolve the new relocated source labels with the fixed Main/pause
    # layout. Then relink the exact same pause instructions to those labels.
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-vector-pause-v22.bin').as_posix()+'";M:start=$d65e,size=$1a2,file="'+(O/'native-vector-main-v22.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;}'
    pause=re.sub(r'^DkjrNativePhase=\$[0-9a-f]+\n','',pause,flags=re.M);pause=re.sub(r'^DkjrFruitHit=\$[0-9a-f]+\n','',pause,flags=re.M)
    # Duplicated equal constant definitions are unnecessary in one translation
    # unit; remove them from the consumed standalone pause leaf only.
    defined=set(re.findall(r'^([A-Za-z_]\w*)=',source,re.M))
    pause='\n'.join(line for line in pause.splitlines()if not(re.match(r'^(\w+)=',line)and re.match(r'^(\w+)=',line)[1]in defined))+'\n'
    blob,L=A.assemble('native-vector-v22',source+'\n'+pause,cfg)
    mainpart=(O/'native-vector-main-v22.bin').read_bytes();pausepart=(O/'native-vector-pause-v22.bin').read_bytes()
    assert L['DkServices']==0xa000 and len(blob)<=8160 and len(pausepart)==286
    for i in range(38):
        target=L[targets.get(i,'DkUnavailable')];assert blob[3*i:3*i+3]==bytes([76,target&255,target>>8])
    out=dict(passed=True,qualified=False,native_owner_admitted=False,ROM_written=False,shared_source_written=False,vector_entries=38,vector_bytes=114,compiled_body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),Main_helper_bytes=len(mainpart),Main_helper_span=[0xd65e,L['DkNativeMainEnd']],pause_helper_bytes=len(pausepart),pause_helper_span=[0xd540,L['DkPauseEnd']],labels=L,implemented_vector_rows={str(k):v for k,v in targets.items()},unimplemented_rows=[i for i in range(38)if i not in targets],
        declared_private_writes=['Existing source state/terrain/fruit/native ports from frozenv10.','C8FB/C8FC Main previous native cache;C8FE private constructed flag, within conditional C000..C900 grant.'],
        remaining=['Fresh/Main/Draw CPU qualification against original source plus full actual native phase/callers.','Graphics/palette/status/scene/life/contact/fullbox/head/side/pickup/shot/bounce/retirement typed rows and actual native ingress must be implemented or caller-proven before admission. CLCRTS rows are unfinished, not functional public adapters.','Complete source CHR/fruit/points publication and bounded native renderer, full payload header/cookie; exact current Prince/Bub rebind and all owner/IRQ proofs.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),grant,O/'native-body-v10.s',O/'native-body-v10.bin',O/'native-body-v10-layout.json',O/'native-pause-v16.s',O/'native-vector-v22.s',O/'native-vector-v22.bin',O/'native-vector-main-v22.bin',O/'native-vector-pause-v22.bin']})
    (O/'native-vector-v22-layout.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','compiled_body_bytes','body_end','header_spare','vector_entries','Main_helper_bytes','pause_helper_bytes','implemented_vector_rows']}))


if __name__=='__main__':main()
