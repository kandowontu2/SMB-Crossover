"""Execute supplied CX palette owners, without a live-unlock or RGB claim."""
from pathlib import Path
import hashlib,json,sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
sys.path.insert(0,str(Path(__file__).parent))
import quickman_component_v2 as q
O=q.O/'palette';O.mkdir(parents=True,exist_ok=True)

class PaletteBus(q.CoreBus):
    def __init__(self):super().__init__(q.B);self.ppu=[]
    def __setitem__(self,a,v):
        if a in [0x2006,0x2007]:self.ppu.append([a,v&255])
        super().__setitem__(a,v)

def execute(b,pc,stop=None,limit=2000):
    b.ram[0x1fe]=0xfe;b.ram[0x1ff]=0x7f;m=MPU(memory=b);m.pc=pc;m.sp=0xfd;pcs=[]
    while m.pc!=(stop if stop is not None else 0x7fff):
        pcs.append(m.pc);m.step();assert len(pcs)<limit,(hex(m.pc),len(pcs))
    return dict(steps=len(pcs),cycles=m.processorCycles,PCs=[f'{x:04X}'for x in pcs],PC_trace_sha256=hashlib.sha256(b''.join(x.to_bytes(2,'little')for x in pcs)).hexdigest())

def source_text():
    b=PaletteBus();m=MPU(memory=b);d=Disassembler(m);rows=[]
    for bank,lo,hi,name in [(0x1f,0x9cfe,0x9d0c,'acquired form install'),(0x3c,0xbb82,0xbb90,'weapon palette restoration tail'),(0x3c,0xd2ea,0xd2ff,'weapon palette loader'),(0x1f,0x8070,0x8099,'encoded palette resolver'),(0x3c,0xc427,0xc42f,'fixed palette farcall'),(0x3c,0xd038,0xd04d,'NMI palette upload slice')]:
        b.bank=bank;p=lo;rows.append(f'; {name}; bank{bank:02X} core map, entry${lo:04X}')
        while p<hi:
            n,s=d.instruction_at(p);rows.append(f'{p:04X} '+bytes(b[p:p+n]).hex()+' '+s);p+=n
    (O/'native-palette-instructions.txt').write_text('\n'.join(rows)+'\n')

def main():
    source_text();cases=[]
    # Exact ROM stage-format palette bytes, supplied as DATA to the isolated
    # owners. Their stage selection/load path is not claimed here.
    stage_at=0x1bf12;encoded=q.B[stage_at:stage_at+32]
    (O/'stage-palette-source.bin').write_bytes(encoded)
    assert encoded[16:24]==bytes.fromhex('e0e0102de0e03038')
    for acquired in [False,True]:
        for fade in [0,16,32]:
            b=PaletteBus();b.bank=0x1f;b.ram[0x61]=0x3c;b.ram[0x62]=0x3d;b.ram[0x355]=0;b.ram[0x97]=fade;b.ram[0x356:0x376]=encoded;b.ram[0xa9]=0
            load=execute(b,0xd2ea)
            assert b.ram[0x367:0x36a]==bytes.fromhex('e0102d')
            install=execute(b,0x9cfe,stop=0x9d0c)if acquired else None
            if acquired:assert b.ram[0x9b]==128 and b.ram[0x368:0x36a]==bytes([40,21])
            # C427 pushes source8070 and enters original F8D3/C001 bank owner.
            b.bank=0x3c;b.ram[0x61]=0x3c
            resolved=execute(b,0xc427)
            expected=[]
            for v in b.ram[0x356:0x376]:
                v=(v-fade)&255
                if v&128:v=15
                if v>=64:v=48
                expected.append(v)
            assert list(b.ram[0x700:0x720])==expected
            upload=execute(b,0xd038,stop=0xd04d)
            assert b.ppu==[[0x2006,63],[0x2006,0]]+[[0x2007,v]for v in expected]
            if acquired and not fade:
                assert expected[16:24]==[15,15,40,21,15,15,48,56]
            cases.append(dict(acquired=acquired,fade=fade,input_encoded_hex=bytes(b.ram[0x356:0x376]).hex(),PPU_3F00_to_3F1F=expected,sprite_roles_0_1=expected[16:24],weapon_loader=load,form_palette_install=install,resolver=resolved,upload_slice=upload,PPU_writes=b.ppu))
    # Source BB82 restores the two QuickMan entries after native D2EA reload.
    b=PaletteBus();b.ram[0xa9]=0;b.ram[0x9b]=128;execute(b,0xd2ea);restore=execute(b,0xbb82,stop=0xbb90)
    assert b.ram[0x368:0x36a]==bytes([40,21])
    report=dict(status='ACTUAL_CX_PALETTE_INSTALL_RESOLVE_AND_UPLOAD_SLICES_PASS',source_ROM=str(q.ROM),source_ROM_sha256=q.sha(q.ROM),stage_data_fixture=dict(file_offset=f'{stage_at:X}',bytes=32,sha256=q.sha(O/'stage-palette-source.bin'),scope='ROM stage palette DATA fixture only; full live stage load/acquisition route not executed.'),source_owners=dict(form='bank1F:9CFE..9D0B writes9B=80 and0368=28/0369=15',weapon='fixedD2EA uses weaponA9 index intoD2FF, writes0367..0369; core3D:BB82 restoresQuickMan28/15',resolved_palette='C427 -> bank1F:8070. Encoded0356..0375 minusfade97, negative->0F, >=40->30, output0700..071F.',PPU='nativeNMI sliceD038..D04C writes3F00 then32bytes; LDA0620,X withX=E0 reads0700..071F'),unfaded_QuickMan_roles=dict(role0_NES_codes=['0F','0F','28','15'],role1_NES_codes=['0F','0F','30','38'],role1_condition='Face bytes E0 E0 30 38 supplied by exact ROM stage DATA fixture; a live acquired-game palette capture is still required.'),E0_meaning='At fade0 encodedE0 resolves to0F; it does not preserve an old palette color.',cases=cases,weapon_restore=restore,RGB_scope='Packed pose/contact PNG uses primary rip RGB as a geometry fixture. Verified native palette-role/index ownership does not establish live displayed RGB; no native QuickMan unlock replay was run.',host_contract='No use or lease of host0700. Host palette adapter must map logical roles0/1 to host sprite palettes and retain source NES codes, with actual host preview/NMI checks before admission.',no_native_emulator=True,no_host_lease=True)
    p=O/'palette-owner.json';p.write_text(json.dumps(report,indent=2)+'\n');print(p);print(q.sha(p))
if __name__=='__main__':main()
