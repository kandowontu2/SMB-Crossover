"""Execute assembled Zelda II terrain probes, cell receipts and separation."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, address, location, Memory
from verify_native_relocation import NesMPU


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();b=load(a.rom);m=Memory(b);cpu=NesMPU(memory=m)
    def get(n):return m[address(b,n)]
    def put(n,v):m[address(b,n)]=v&255
    def field(**kw):
        for n,v in kw.items():put(n,v)
    def call(name,y=0):
        pos=location(b,name);bank=(pos-16)//8192;pc=address(b,name)
        if 0xa000<=pc<0xc000:m.page(1,bank);put('CurrentBank',bank|128)
        elif 0xc000<=pc<0xe000:m.page(2,bank);put('CurrentBankC',bank|128)
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=0x53,0x71,y,0x35,0xfd
        cpu.stPushWord(0x7eff);cpu.pc=pc
        banks=m.banks[:];m.writes=[]
        for _ in range(12000):
            if cpu.pc==0x7f00:break
            cpu.step()
        else:raise AssertionError((name,'timeout',hex(cpu.pc)))
        assert cpu.sp==0xfd,(name,'SP',cpu.sp)
        assert m.banks==banks,(name,'unrestored banks',m.banks,banks)
        return cpu.a,cpu.x,cpu.y,cpu.p
    def cell(x,y):
        return address(b,'Block_Buffer_2'if(x//256)&1 else'Block_Buffer_1')+(x%256)//16+(y//16*16-32)
    def setup(x,y,fairy):
        m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416]=[0]*416
        field(SelectedCharacter=4,Z2Variant=1,GameEngineSubroutine=8,Player_X_Position=x&255,
              Player_PageLoc=x//256,Player_Y_Position=y,Player_Y_HighPos=1,
              Player_Y_Speed=0,Z2ActiveSpells=8 if fairy else 0,SmCeilingHit=0,
              Player_CollisionBits=255,Player_State=1,R0=0x62,R1=0x91,
              Local_eb=head_index,CurrentBank=129,CurrentBankC=137)
        m.page(1,1);m.page(2,9)
    head_index=m[address(b,'BlockBufferAdderData')+9]
    total=dict(head=0,feet=0,side=0,wall=0,after=0,admission=0)
    for fairy,x,y,which,vy,old_delta in itertools.product(
            [0,1],[0,1,3,4,11,12,15,16,239,244,250,252,255,256,511,512],
            [33,47,78,111,126,127,159,174],[0,1],[0,1,255,252],[0,1,6]):
        setup(x,y,fairy);dy=8 if fairy else 0;points=[6,10]if fairy else[4,12]
        at=cell(x+points[which],y+dy);m[at]=0xc4
        field(Player_Y_Speed=vy)
        m[address(b,'Z2BodyScratch')+11]=y+old_delta
        selected=0 if cell(x+points[0],y+dy)==at else which
        target=(y+dy)//16*16+16-dy
        separate=vy>=128 and y+old_delta+dy>=(y+dy)//16*16+16
        result=call('Z2TerrainHead',head_index)
        assert result[:3]==(0xc4,0,head_index),('head result',fairy,x,y,which,vy,old_delta,result,at,get('R2'),get('R5'),get('R6'),get('R7'),address(b,'Block_Buffer_1'))
        assert get('R6')+256*get('R7')+get('R2')==at
        assert get('R5')==(x+points[selected])%256
        assert get('Player_Y_Position')==(target if separate else y)
        assert get('SmCeilingHit')==int(separate)
        assert get('R4')==(4 if separate else y%16)
        assert get('Player_X_Position')==x%256 and get('Player_PageLoc')==x//256
        assert get('R0')==0x62 and get('R1')==0x91
        total['head']+=1
        if separate:
            put('Player_Y_Position',target-2)
            call('Z2AfterBGDispatch')
            assert get('Player_Y_Position')==target and get('Player_Y_Speed')==1
            assert get('Z2NativeVY')==1 and get('SmCeilingHit')==0
            total['after']+=1
    for fairy,x,y,foot in itertools.product([0,1],range(0,512,7),range(34,205,5),[0,1]):
        setup(x,y,fairy);dx=([6,10]if fairy else[4,12])[foot];dy=26 if fairy else 32
        at=cell(x+dx,y+dy);m[at]=0xc4
        result=call('CrossoverSourceFootProbe',head_index+foot)
        assert result[:3]==(0xc4,0,head_index+foot+1),('foot result',fairy,x,y,foot,result)
        assert get('R6')+256*get('R7')+get('R2')==at
        assert get('R5')==(x+dx)%256 and get('R4')==(y+dy)%16
        assert get('Player_Y_Position')==y and get('Player_X_Position')==x%256
        assert get('SmCeilingHit')==(128 if fairy and(y+dy)%16<5 else 0)
        assert get('R0')==0x62 and get('R1')==0x91
        total['feet']+=1
        if get('SmCeilingHit'):
            field(Player_State=0,Player_Y_Position=y&240)
            call('Z2AfterBGDispatch')
            assert get('Player_Y_Position')==(y+dy)//16*16-26
            assert get('SmCeilingHit')==0
            total['after']+=1
    for fairy,x,y,right,lower in itertools.product([0,1],range(0,512,3),[36,63,95,127,158,192],[0,1],[0,1]):
        setup(x,y,fairy);dx=([3,13]if fairy else[1,15])[right]
        dy=([12,24]if fairy else[6,26])[lower]
        at=cell(x+dx,y+dy);m[at]=0xc4
        index=head_index+3+right*2+lower
        field(R0=1 if right else 2,Local_eb=head_index+3+right*2)
        result=call('CrossoverSourceSideProbe',index)
        assert result[:3]==(0xc4,0,index),('side result',fairy,x,y,right,lower,result)
        assert get('R6')+256*get('R7')+get('R2')==at
        assert get('R5')==(x+dx)%256 and get('R4')==x%16
        assert get('Player_X_Position')==x%256 and get('Player_PageLoc')==x//256
        assert get('Player_Y_Position')==y and get('Local_eb')==head_index+3+right*2
        total['side']+=1
        expected=((x+dx)//16*16-(dx+1)if right else(x+dx)//16*16+16-dx)&65535
        result=call('LmWallGate')
        assert result[3]&1
        assert get('Player_X_Position')+256*get('Player_PageLoc')==expected,('wall',fairy,x,right,expected,get('Player_X_Position'),get('Player_PageLoc'))
        assert get('Player_CollisionBits')==255-(1 if right else 2)
        assert get('Player_Y_Position')==y and get('Player_X_Scroll')==0
        assert get('Z2NativeVX')==get('Z2NativeXFraction')==0
        total['wall']+=1
    # Exercise the real public head dispatch, including its pre-existing A/P save.
    for variant,engine in itertools.product([0,1],[4,7,8,9]):
        setup(95,127,0);field(Z2Variant=variant,GameEngineSubroutine=engine,Player_Y_Speed=252)
        m[address(b,'Z2BodyScratch')+11]=132
        m[cell(99,127)]=0xc4
        # Legacy short Link head is at144 and remains empty.
        result=call('TnFastHeadGate',head_index)
        own=variant==1 and engine==8
        assert result[0]==(0xc4 if own else 0),(variant,engine,result)
        assert get('Player_Y_Position')==(128 if own else 127)
        total['admission']+=1
    proof=dict(passed=True,goal_complete=False,ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),cases=total,
               scope='Actual assembled public head/feet/side/wall dispatch and cold queries. Normal/Fairy points, both page parities, edge carries, caller query indices, authoritative cell receipts, ceiling crossings versus overlaps, exact floor depth and wall separation. Unmodified player origins during reads; R0/R1 ownership and real bank/SP restoration checked. This is a seeded CPU component oracle, not native PPU/gameplay, moving-platform or source enemy-hitbox evidence.')
    a.output.write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
