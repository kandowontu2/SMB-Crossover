"""Original contact rectangle and real native CHR/palette leaf CPU controls."""
import itertools,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
import audit_bub_menu_frontend_1102_v1 as F
R=A.R;O=A.O;W=A.W;D=W.P.D


def main():
    donor=D.donor();palette_source=donor[16+0x33a1:16+0x33ad];assert palette_source==bytes.fromhex('0f302a160f3006360f2a1737')
    q=json.loads((O/'native-display-v24-layout.json').read_text());L=q['labels'];core=(O/'native-display-v24.bin').read_bytes();parts={k:(O/('native-display-'+k+'-v24.bin')).read_bytes()for k in ['pause','main','ports']}
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=A.BASE.read_bytes();assert A.sha(b['raw'])==A.PIN
    def call(m,target):
        c=N.NesMPU(memory=m,pc=target);c.a,c.x,c.y,c.p,c.sp=0x55,7,91,0xb1,224;c.stPushWord(0x5ffe)
        for _ in range(100000):
            if c.pc==0x5fff:break
            assert m[c.pc]!=0,('display BRK',hex(target),hex(c.pc));c.step()
        else:raise AssertionError(('display bound',hex(target)))
        assert c.sp==224;return c
    def fresh():
        m=N.Bus(b);m.ram[3][:len(core)]=core
        for k,at in [('pause',0x1540),('main',0x165e),('ports',0x16a4)]:m.ram[2][at:at+len(parts[k])]=parts[k]
        m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,AreaType=1,Player_X_Position=40,Player_Y_Position=176,Player_Y_HighPos=1,VRAM_Buffer1_Offset=0)
        call(m,0xa02d);return m
    bounds=0
    for state,facing,grip,x,y in itertools.product(range(1,6),[0,1],[0,1,2],[32,96],[64,191]):
        m=fresh();oracle=D.Bus();oracle[:2048]=bytes(m.ram[2][:2048])
        for mem in [m.ram[2],oracle]:
            mem[0x6b]=state;mem[0x6d]=facing;mem[0x71]=grip;mem[0x210]=y;mem[0x213]=x
        c=D.T.NesMPU(memory=oracle,pc=0);D.T.run(c,0xd2bd)
        z=call(m,0xa000+16*3);at=W.address(b,'BoundingBox_UL_Corner')
        assert z.p&1 and bytes(m[at:at+4])==bytes(oracle[0x5fc:0x600])==bytes(m.ram[2][0x5fc:0x600]);bounds+=1
    graphics=[]
    for selected in [0,40]:
        m=fresh();N.put(m,SelectedCharacter=selected);z=call(m,0xa003);assert z.p&1 and z.a==0
        modes=W.address(b,'X5ChrMode');pages=W.address(b,'CurrentCHRBank')
        assert list(m[pages+4:pages+8])==[191,192,193,193]and list(m[modes+4:modes+8])==[131]*4
        assert N.get(m,'ObjectMetasprite')==0 and N.get(m,'SmPosePtr')+256*m[W.address(b,'SmPosePtr')+1]==W.address(b,'ObjectMetasprite')
        N.invoke(m,'X5PublishChr');assert m.chr_latches[4:8]==[959,960,961,961],(selected,m.chr_latches)
        graphics.append(dict(selected=selected,actual_typed_modes=[131]*4,actual_hardware_CHR=list(m.chr_latches[4:8])))
    palettes=0;busy=0;data=bytes.fromhex('3f1d033006363f1903302a163f15032a1737')
    backdrop=[34,34,15,15,15,34,15,15]
    for background,area,offset in itertools.product(range(8),range(4),[0,1,20,40,61,62,83,110]):
        m=fresh();N.put(m,BackgroundColorCtrl=background,AreaType=area,VRAM_Buffer1_Offset=offset)
        at=W.address(b,'VRAM_Buffer1');m[at:at+160]=[0xa5]*160;before=bytes(m[at:at+160]);state=bytes(m.ram[2]);z=call(m,0xa000+26*3)
        assert(z.a,z.x,z.y,z.p)==(0x55,7,91,0xb1)and bytes(m.ram[2])==state
        if offset<=61:
            expected=bytearray(before);expected[offset:offset+22]=bytes([63,16,1,backdrop[background or area]])+data;expected[offset+22]=0
            assert bytes(m[at:at+160])==expected and N.get(m,'VRAM_Buffer1_Offset')==offset+22
            palettes+=1
        else:
            assert bytes(m[at:at+160])==before and N.get(m,'VRAM_Buffer1_Offset')==offset;busy+=1
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,compiled_body_bytes=len(core),metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],original_palette_PC=0xf3a1,original_palette_bytes=palette_source.hex(),checks=dict(actual_source_bounds_original_vs_native_fullbox=bounds,actual_native_CHR_mode_and_hardware_publication=graphics,actual_all_background_area_nonzero_buffer_palette_packets=palettes,busy_buffer_no_write_cases=busy),
        semantics='Original D2BD/EB69 contact rectangle remains authoritative across state/facing/grip. Actual native typed CHR setter+publisher selects959/960/961. Body/fruit opaque RGB is original; authentic native area backdrop uses3F10 and no owned universal color is queued. Busy buffers receive no partial packet.',
        remaining=['Real full public native ingresses and cold/transition palette retry lifetime, complete source atlas/fruit/points OAM and cookies.','All unfinished row APIs/lifecycle/IRQ plus latest Prince/Bub rebind; no native-ready claim.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),A.BASE,O/'native-display-v24-layout.json',O/'native-display-v24.bin',O/'native-display-ports-v24.bin']})
    (O/'native-display-v25-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','compiled_body_bytes','metadata_end','metadata_spare','checks']}))


if __name__=='__main__':main()
