"""Source-funded private descriptor/CHR ownership repair; no ROM emission."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as V
import build_storage_guard_v1 as G
from py65.devices.mpu6502 import MPU

O=R/'build/prince-body-owner-1103-v178'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda b:hashlib.sha256(b).hexdigest()


def assemble(text,cfg):
    cc=R/'tools/Windows/cc65/bin'
    (O/'body-owner.s').write_text(text)
    (O/'body-owner.cfg').write_text(cfg)
    for cmd in [[cc/'ca65.exe',O/'body-owner.s','-o',O/'body-owner.o'],
                [cc/'ld65.exe','-C',O/'body-owner.cfg',O/'body-owner.o','-o',O/'body-owner.bin','-Ln',O/'body-owner.lbl']]:
        out=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
        assert out.returncode==0,out.stderr
    (O/'body-owner.o').unlink()
    return (O/'body-owner.bin').read_bytes()


def leaf(code,pc,*,a=83,x=71,y=109,p=0x21):
    mem=[0x9d]*65536
    for at,b in code.items():mem[at:at+len(b)]=b
    cpu=MPU(memory=mem,pc=pc);cpu.a,cpu.x,cpu.y,cpu.p=a,x,y,p;cpu.sp=224;cpu.stPushWord(0x5aff)
    for _ in range(100):
        if cpu.pc==0x5b00:break
        cpu.step()
    else:raise AssertionError(('Leaf bound',hex(cpu.pc)))
    assert cpu.sp==224
    return cpu,mem


def main():
    G.preflight(private_root=O,reserved_bytes=300000,reserved_files=12,fresh=True)
    O.mkdir(exist_ok=True)
    runtime,meta,state=V.M.B.images();runtime=bytearray(runtime);meta=bytearray(meta)
    hi=0xbdc3;table=bytes([1]*22+[2]*9)
    assert runtime[hi-0xa000:hi-0xa000+31]==table
    render=(V.O/'grid-render-labels-v37.s').read_text()
    assert render.count('PhysicalHi:\n .byte '+','.join(map(str,table)))==1
    needle=bytes([0xbd,hi&255,hi>>8,0xaa]);sites=[i for i in range(len(runtime))if runtime[i:i+4]==needle]
    assert len(sites)==1
    upper_call=0xa000+sites[0]
    route=0xdf1e;end=0xdf96
    slots=[i for i in range(route-0xc800,end-0xc800-3)if meta[i:i+3]==bytes.fromhex('c903f0')]
    assert len(slots)==1
    graphics_call=0xc800+slots[0]
    source=f'''; Exact source PhysicalHi31B storage, no new state/code/RAM grant.
; Immutable native pose-page indices are0..30. Original table22*1+9*2.
; Upper helper changes C/V; the actual renderer continuation does not read
; them before its explicit CLC, and restores the caller P at its epilogue.
.setcpu "6502"
.segment "UPPER_CALL"
 jsr PpPhysicalUpper
 nop
.segment "GRAPHICS_CALL"
 jsr PpGraphicsCheck
 nop
.segment "STORAGE"
.export PpPhysicalUpper,PpGraphicsCheck,PpBodyOwnerEnd
PpPhysicalUpper:
 cpx #22
 lda #1
 adc #0
 tax
 rts
PpGraphicsCheck:
 cmp #3
 bne Done
 lda #0
 sta $06e1                 ; Native descriptor absent: private draw owns body.
 lda #<$06e1
 sta $6b06
 lda #>$06e1
 sta $6b07                 ; Stable unbanked zero header, through all FarCalls.
 lda #69                   ; Existing pure SEC row restores original A.
Done:rts
PpBodyOwnerEnd:
 .res 31-(*-PpPhysicalUpper),$ea
'''
    cfg=f'MEMORY{{U:start=${upper_call:04x},size=4,file=%O;G:start=${graphics_call:04x},size=4,file=%O;S:start=$bdc3,size=31,file=%O;}}SEGMENTS{{UPPER_CALL:load=U,type=ro;GRAPHICS_CALL:load=G,type=ro;STORAGE:load=S,type=ro;}}'
    code=assemble(source,cfg);assert len(code)==39
    before=[bytes(runtime[sites[0]:sites[0]+4]),bytes(meta[slots[0]:slots[0]+4]),table]
    runtime[sites[0]:sites[0]+4]=code[:4];meta[slots[0]:slots[0]+4]=code[4:8];runtime[hi-0xa000:hi-0xa000+31]=code[8:]
    assert code[8:16]==bytes.fromhex('e016a9016900aa60')
    assert code[-1]==0xea
    # Pure leaf measurements. They are not claimed to be actual cold or IRQ tests.
    upper_cases=0
    for index in range(31):
        for flags in [0x20,0x21,0x60,0xe1]:
            cpu,mem=leaf({hi:code[8:]},hi,x=index,p=flags)
            assert(cpu.a,cpu.x,cpu.y)==(table[index],table[index],109)
            upper_cases+=1
    graphics_cases=0;allowed={0x6e1,0x6b06,0x6b07}
    for value in range(256):
        for mask in range(64):
            flags=0x30|(mask&15)|((mask&48)<<2)
            cpu,mem=leaf({hi:code[8:]},hi+8,a=value,p=flags)
            if value==3:
                assert cpu.a==69 and [mem[a]for a in [0x6e1,0x6b06,0x6b07]]==[0,0xe1,6]
            else:
                old,oldmem=leaf({0x5800:bytes.fromhex('c90360')},0x5800,a=value,p=flags)
                assert(cpu.a,cpu.x,cpu.y,cpu.p)==(old.a,old.x,old.y,old.p)
                assert all(mem[a]==0x9d for a in allowed)
            assert(cpu.x,cpu.y)==(71,109)
            graphics_cases+=1
    # Finite page selectors and their original packed pose records.
    original_meta=V.M.B.images()[1];used=set();poses=0;read_sites=[]
    art=json.loads((V.O/'source-art.json').read_text())
    for pose in art['poses']:
        frame=pose['source_frame'];tagged=int.from_bytes(original_meta[frame*2:frame*2+2],'little')
        assert tagged!=65535
        off=tagged&0x7fff # Existing source-qualified compact-grid flag.
        count=(original_meta[off]>>4)&3;indices=list(original_meta[off+1:off+1+count])
        assert count in range(1,5)and all(0<=i<31 for i in indices)
        expected=sorted({p['pattern_pair']//32 for p in pose['parts_8x16']})
        assert indices==expected,(frame,indices,expected)
        used.update(indices);poses+=1
    assert poses==408 and used==set(range(31))
    # Bind the actual177 native first-write proof without interpreting a table
    # value as a free resource. A22C is the native postdraw shadow clobber.
    native=R/'build/prince-chr-owner-1103-v177/native/capture/render-evidence.json'
    observed=json.loads(native.read_text());events=observed['CHR0_events']
    assert any(e['address']==0x147 and e['stamp']['PC']==0xa278 and e['value']==85 for e in events)
    assert any(e['address']==0x147 and e['stamp']['PC']==0xa22c and e['value']==64 and e['writer_physical']==33324 for e in events)
    assert observed['DMA']['banks'][0]==320
    for name,data in [('runtime',runtime),('metadata',meta)]:
        (O/f'body-{name}.bin').write_bytes(data)
    patches=[dict(region='runtime',CPU=upper_call,old_hex=before[0].hex(),new_hex=code[:4].hex()),
             dict(region='metadata',CPU=graphics_call,old_hex=before[1].hex(),new_hex=code[4:8].hex()),
             dict(region='runtime',CPU=hi,old_hex=table.hex(),new_hex=code[8:].hex())]
    q=dict(measured=True,qualified_current_cold=False,ROM_written=False,menu_or_shared_source_changed=False,
           parent_manifest_SHA256=sha(V.O/'backdrop-manifest-v159.json'),patches=patches,
           source_funding=dict(table_half_open=[hi,hi+31],upper_bytes=8,graphics_bytes=22,padding_bytes=1,
                               runtime_bytes=len(runtime),metadata_bytes=len(meta),state_bytes=len(state),new_RAM=0,new_carriers=0),
           source_pose_records=poses,finite_page_domain=sorted(used),upper_leaf_cases=upper_cases,graphics_leaf_cases=graphics_cases,
           intended_first_idle_page=341,native_observed_clobber=320,
           ABI='All non3 GraphicsCheck inputs exactly match oldCMP3 AXYP; own3 clears only three native descriptor cells and maps routingA3->69, whose existing PLA/SEC/RTS restores sourceA/C1. Upper helper AX/Y match original lookup on all31indices; C/V differ and require complete actual continuation proof, not arbitrary ingress parity.',
           pending=['Complete direct/indirect table consumer and constructor/retire lifetime closure.','Actual whole renderer/PlayerGfxHandler/DrawAllMetasprites/BankSwitchCHR against original408poses and native first8.','Actual new source-backed codec/pool/cookie/fullcold/current-owner/foreign/IRQ/FF/nested withnew2byteJSRstackdepth.','Explicit final rebase to root combined83/80d3 preserving its granted shared changes; no blind oldcookie application.','Root resource/manifest review and native fullbody validation.'],
           bindings={str(p.relative_to(R)):sha(p)for p in [Path(__file__),O/'body-owner.s',O/'body-owner.cfg',O/'body-owner.bin',O/'body-owner.lbl',O/'body-runtime.bin',O/'body-metadata.bin',V.O/'native-runtime-v153.bin',V.O/'native-metadata-v149.bin',V.O/'native-services-v157.s',V.O/'grid-render-labels-v37.s',V.O/'grid-render-labels-v37.lbl',V.O/'source-art.json',native,R/'src/metasprite_engine.s']})
    (O/'measurement.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','patches']}))


if __name__=='__main__':main()
