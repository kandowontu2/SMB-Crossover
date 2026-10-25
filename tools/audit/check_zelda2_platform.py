"""Check actual platform positioning, native controls and source body boxes."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,address,location,Memory
from verify_native_relocation import NesMPU


class Machine:
    def __init__(self,path):self.b=load(path);self.m=Memory(self.b);self.cpu=NesMPU(memory=self.m)
    def put(self,n,v):self.m[address(self.b,n)]=v&255
    def get(self,n):return self.m[address(self.b,n)]
    def call(self,n,fields,x=0,y=0,a=0):
        for k,v in fields.items():self.put(k,v)
        bank=(location(self.b,n)-16)//8192;self.m.page(1,bank);self.put('CurrentBank',bank|128)
        c=self.cpu;c.a,c.x,c.y,c.p,c.sp=a,x,y,0x35,0xfd;c.stPushWord(0x7eff);c.pc=address(self.b,n)
        for _ in range(12000):
            if c.pc==0x7f00:break
            c.step()
        else:raise AssertionError((n,hex(c.pc)))
        assert c.sp==0xfd and self.m.banks[1]==bank
        return c.a,c.x,c.y,c.p


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','rom','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();old,new=Machine(a.parent),Machine(a.rom);counts=dict(position=0,legacy_exact=0,body=0,small_lift=0)
    fields_out=['Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','Player_Y_MoveForce']
    for char,variant,spell,engine,high,ordinate in itertools.product([0,1,2,3,4,5,11,15,19],[0,1],[0,8],[7,8,11],[0,1,2],[0,15,25,26,31,32,100,160,239,255]):
        fields=dict(SelectedCharacter=char,Z2Variant=variant,Z2ActiveSpells=spell,GameEngineSubroutine=engine,
                    Enemy_Y_Position=ordinate,Enemy_Y_HighPos=high,Player_Y_Position=77,Player_Y_HighPos=3,
                    Player_Y_Speed=252,Player_Y_MoveForce=81)
        results=[m.call('PositionPlayerOnVPlat',fields)for m in [old,new]]
        own=char==4 and variant==1 and spell==8 and engine!=11 and high==1
        if own:
            want=ordinate-26
            assert new.get('Player_Y_Position')==want&255
            assert new.get('Player_Y_HighPos')==(1-(want<0))
            assert new.get('Player_Y_Speed')==new.get('Player_Y_MoveForce')==0
        else:
            assert [old.get(n)for n in fields_out]==[new.get(n)for n in fields_out]
            assert results[0][:3]==results[1][:3],('native AXY',fields,results)
            # Farcall reloads returnedA and therefore may alter transientN/Z.
            assert results[0][3]&0x7d==results[1][3]&0x7d,('native preservedP',fields,results)
            counts['legacy_exact']+=1
        counts['position']+=1
    for shield,spell,state,mode,rx,ry in itertools.product([0,1],[0,8],[0,1,2],[0,1],[0,1,95,127,224,239],[32,63,100,176]):
        fields=dict(SelectedCharacter=4,Z2Variant=1,Z2ActiveSpells=spell,GameEngineSubroutine=8,
                    Player_Rel_XPos=rx,Player_Rel_YPos=ry,Player_BoundBoxCtrl=18,Z2NativeShield=shield,
                    Player_State=state,Player_Y_Speed=2,CrossoverBehaviorVersion=mode)
        new.call('LmBoundingBoxGate',fields)
        assert new.get('BoundingBox_UL_XPos')==rx+1
        assert new.get('BoundingBox_LR_Corner')==rx+14
        assert new.get('BoundingBox_UL_YPos')==ry+(0 if shield else 4)
        bottom=ry+(31 if mode==0 and state==2 else 29)
        assert new.m[address(new.b,'BoundingBox_LR_Corner')+1]==bottom
        counts['body']+=1
    # Exercise the actual small-platform BIT skip and both original lift offsets.
    for slot,flag,fairy,ordinate in itertools.product(range(6),[1,2],[0,8],[40,128,176,239]):
        fields=dict(SelectedCharacter=4,Z2Variant=1,Z2ActiveSpells=fairy,GameEngineSubroutine=8,
                    AreaPointer=0,WorldNumber=0)
        for i in range(6):
            new.m[address(new.b,'Enemy_Y_Position')+i]=ordinate
            new.m[address(new.b,'Enemy_Y_HighPos')+i]=1
        new.call('PositionPlayerOnS_Plat',fields,x=slot,a=flag)
        platform=(ordinate+(128 if flag==1 else 0))&255
        assert new.get('Player_Y_Position')==(platform-(26 if fairy else 32))&255
        counts['small_lift']+=1
    proof=dict(passed=True,goal_complete=False,ROM_sha256=hashlib.sha256(new.b['raw']).hexdigest(),cases=counts,
               scope='Actual platform PositionV and small-platform BIT entry, original first/second lift offsets, all legacy profile controls, early exits/page borrows and E975-derived body rectangles. Easy sole extension retained. Native A/X/Y and C/V/D/I preserved; transient N/Z after farcall reloadA are not asserted. Interior viewport body projection only; edge clipping/native PPU/platform overlap/carry/full routes still pending.')
    a.output.write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
