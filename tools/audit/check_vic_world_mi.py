"""Exercise real linked SMB metatile queries behind the native missile port."""
from pathlib import Path
import hashlib
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
sys.path.insert(0,str(R/'tools/audit'))
from verify_native_relocation import load
O=R/'build/vic-viper-mh-private'


def main():
    rom=O/'vic-components.nes';cpu,L=load(rom)
    def put(name,value,i=0):cpu.memory[L[name]+i]=value&255
    start=L['__SMCCODE_RUN__'];cpu.memory[start:start+len(cpu.memory.smc)]=cpu.memory.smc
    count=0
    for x,y,cam,page,tile in itertools.product(
        (0,7,8,15,239,247,248,255),(0,15,16,143,191,199,203,207,208,239,255),
        (0,7,15,247,255),(0,1,2),(0,0x23,0x26,0xc2,0xc3,0x51,0x10,0x24,0x25,0xc4)):
        cpu.memory[L['Block_Buffer_1']:L['Block_Buffer_1']+416]=[0]*416
        cpu.memory.switch(75);put('CurrentBank',0xcb)
        put('ScreenLeft_X_Pos',cam);put('ScreenLeft_PageLoc',page)
        put('VvProbeX',x);put('VvProbeY',y)
        physical_y=y+32;world_x=page*256+cam+x+8
        valid=32<=physical_y<240
        if valid:
            index=((world_x//256)&1)*208+((physical_y//16)-2)*16+world_x%256//16
            put('Block_Buffer_1',tile,index)
        attr=cpu.memory[L['MTileAttribute']+tile]
        expected=int(valid and tile not in (0,0x23,0x26,0xc2) and bool(attr&1))
        # Sentinel all real actor/world/player coordinates; queries may only
        # touch their declared scratch and mapper/farcall infrastructure.
        player=bytes(cpu.memory[L['Player_PageLoc']:L['Player_PageLoc']+1])
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=0x75,7,0x93,0x24,0xed
        cpu.stPushWord(0x5aff);cpu.pc=L['VvTerrainSide'];steps=0
        while cpu.pc!=0x5b00:
            cpu.step();steps+=1;assert steps<1500,hex(cpu.pc)
        assert cpu.a==expected,(x,y,cam,page,hex(tile),cpu.a,expected)
        assert (cpu.x,cpu.y,cpu.sp)==(7,0x93,0xed)
        assert bytes(cpu.memory[L['Player_PageLoc']:L['Player_PageLoc']+1])==player
        count+=1
    report=dict(passed=True,cases=count,real_SMB_map_reader=True,
        fixture_callbacks_removed=True,original_A4_X_A5_Y_mapping_corrected=True,
        actual_rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
        scope='Linked CPU world-query arenas; not playable admission, native camera or controller proof.')
    (O/'world-query-proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
