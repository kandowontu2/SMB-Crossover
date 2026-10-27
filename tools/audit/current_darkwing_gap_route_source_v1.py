"""Actual failed-route chronology plus finite typed-gap full GameLoop controls.

The model authors a32px empty floor gap consistent with the actual failed RGB.
It is not an unlogged native Block_Buffer/DwPrevious snapshot or Lua execution.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import struct
import zlib

from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from current_rygar_powerups_prepare_v1 import setup as base_scene
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
ROM=ROOT/'build/mega_proto_body_palette_9ea.nes'
EXPECTED='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
POLICY=ROOT/'tools/playthroughs/current_roster_darkwing_gap_v1.lua'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def world(q):return q.get('Player_X_Position')+256*q.get('Player_PageLoc')


def cell(q,x,y):
    if y<32 or y>=240:return 0
    return q.get('Block_Buffer_1',x//256%2*208+(y-32)//16*16+x%256//16)


def supported(q,x):
    return any(cell(q,x,y)not in [0,0x23,0x26,0xc2,0xc3]for y in range(min(q.get('Player_Y_Position')+40,232),233,16))


class Controller:
    """Reviewed Lua first-gap state-machine mirror, one poll per update."""
    def __init__(self):self.phase='find';self.edge=self.landing=None;self.transitions=[]
    def buttons(self,q):
        x=world(q);ground=q.get('Player_State')==0;prev=q.get('DwPrevious')
        if self.phase=='find'and ground and x>450 and supported(q,x+8):
            first=(x//16+1)*16
            for at in range(first,first+33,16):
                if supported(q,at):continue
                far=at
                while far<at+80 and not supported(q,far):far+=16
                if at<far<=at+64 and supported(q,far):
                    self.edge,self.landing,self.phase=at,far,'runup'
                break
        if self.phase=='runup':
            bits=1 if x<self.edge-16 or not prev&128 else 0
            if ground and x>=self.edge-14 and not prev&128:self.phase='press';bits=129
            return bits
        if self.phase=='press':
            if not ground and q.get('Player_Y_Speed')>=128:self.phase='cross'
            return 129
        if self.phase=='cross':
            if ground and x>=self.landing-15:self.phase='done'
            return 129
        return 1


def scene(b,x):
    q=Arena(b,12);q.put(DarkwingVariant=1,CrossoverBehaviorVersion=0,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('DwInventoryInit');base_scene(q,dict(kind='idle',face=1,hit=False))
    q.put(Player_X_Position=x&255,Player_PageLoc=x>>8,MmOldX=x&255,ScreenLeft_X_Pos=176,ScreenLeft_PageLoc=3,ScreenRight_X_Pos=175,ScreenRight_PageLoc=4)
    for tile in [1104,1120]:
        for row in [11,12]:q.set('Block_Buffer_1',0,tile//256%2*208+row*16+tile%256//16)
    return q


def run_case(b,kind):
    q=scene(b,1008 if kind in ['held-history','held-no-release']else 1056);ctrl=Controller();rows=[];owners={};jumps=[];calls=0
    original=NesMPU.step
    names=['DwScroogeMovement','DwScroogePhysics','DwHangUpdate','GameLoop']
    pcs={(address(b,n),(location(b,n)-16)//8192):n for n in names}
    def step(cpu):
        k=q.m.banks[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1;n=pcs.get((cpu.pc,k))
        if n:owners[n]=owners.get(n,0)+1
        original(cpu)
    def tick(bits,stage):
        nonlocal calls
        previous=q.get('Player_State');q.put(SavedJoypadBits=bits);q.invoke('GameLoop');calls+=1
        row=dict(update=calls,stage=stage,phase=ctrl.phase,buttons=bits,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),previous=q.get('DwPrevious'),fresh=q.get('ScFresh'),engine=q.get('GameEngineSubroutine'))
        rows.append(row)
        if previous==0 and row['state']==1 and row['vy']>=128:jumps.append(row.copy())
        ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
    NesMPU.step=step
    try:
        if kind in ['held-history','held-no-release']:
            # A real earlier jump/landing supplies the held consumer state;
            # DwPrevious, ScFresh and jump outcomes are never initialized here.
            for i in range(75):
                tick(129,'prior-real-jump')
                if i>5 and q.get('Player_State')==0:break
            assert jumps and q.get('DwPrevious')&128 and q.get('Player_State')==0
        for i in range(130):
            bits=129 if kind=='held-no-release'or kind=='early-held'and world(q)>=1072 else ctrl.buttons(q)if kind!='early-held'else 1
            tick(bits,'gap')
            if q.get('GameEngineSubroutine')==11:break
            if(kind=='early-held'or ctrl.phase=='done')and world(q)>1144 and q.get('Player_State')==0:break
    finally:NesMPU.step=original
    result=dict(kind=kind,calls=calls,edge=ctrl.edge,landing=ctrl.landing,owners=owners,jumps=jumps,rows=rows,minimum_y=min(r['y']for r in rows),ending=rows[-1])
    if kind=='held-no-release':assert result['ending']['engine']==11,('No new source A edge after prior real jump',result['ending'])
    elif kind=='early-held':
        assert result['ending']['engine']==8 and result['ending']['x']>1144 and result['ending']['state']==0
        assert len(jumps)==1 and 1072<=jumps[0]['x']<=1075
    else:
        assert ctrl.edge==1104 and ctrl.landing==1136 and ctrl.phase=='done',(kind,ctrl.edge,ctrl.landing,ctrl.phase,result['ending'],jumps)
        assert result['ending']['engine']==8 and result['ending']['x']>1144 and result['ending']['state']==0
        assert any(j['stage']=='gap'and 1090<=j['x']<=1094 and j['fresh']&128 for j in jumps)
    return result


def image_gaps(path):
    raw=path.read_bytes();at=8;data=b''
    while at<len(raw):
        n=struct.unpack_from('>I',raw,at)[0];kind=raw[at+4:at+8];part=raw[at+8:at+8+n];at+=n+12
        if kind==b'IHDR':w,h=struct.unpack_from('>II',part)
        if kind==b'IDAT':data+=part
    pixels=zlib.decompress(data);assert(w,h)==(512,240)
    def px(x,y):return pixels[y*(w*4+1)+1+x*4:y*(w*4+1)+1+x*4+4]
    assert all(pixels[y*(w*4+1)]==0 for y in range(h))
    parts=[]
    for offset in [0,256]:
        sky=px(offset+8,100);runs=[];start=None
        for x in range(257):
            hit=x<256 and all(px(offset+x,y)==sky for y in [208,216,224,232])
            if hit and start is None:start=x
            if not hit and start is not None:runs.append([start,x-1]);start=None
        parts.append(runs)
    assert parts==[[[153,184]],[[94,125]]]
    return dict(frames=[2390,2448],horizontal_source_regions=parts,measured_width=32,
        failure_camera=1010,failure_world_interval=[1104,1135],
        limits='Actual RGB empty floor interval, not Block_Buffer dump. Earlier2390 visible scroll is2px behind current foreground camera; failure camera+RGB aligns native16px cells. Controller derives actual live cells and never hardcodes this interval.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists()and sha(ROM)==EXPECTED
    old=ROOT/'build/verification/compact-ab221e-darkwing-easy-v2';trace=list(csv.DictReader((old/'trace.csv').open(newline='')))
    window=[q for q in trace if int(q['x'])>=970]
    assert not any(q['state']=='1'and int(q['vy'])>=128 for q in window)
    fall=next(q for q in window if q['state']=='2');assert(fall['frame'],fall['x'])==('2419','1102')
    image=ROOT/'build/current-ab221e-darkwing-gap-actual-v1.png';geometry=image_gaps(image)
    b=scoped_load(ROM);cases=[run_case(b,k)for k in ['early-held','held-no-release','fresh-neutral','held-history']]
    files=[ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),POLICY,Path(__file__),image,old/'trace.csv',old/'inputs.csv',old/'result.json']
    proof=dict(passed=True,native_run=False,source_CPU_only=True,Lua_executed=False,ROM_sha256=EXPECTED,
        actual_native_false=dict(result_sha256=sha(old/'result.json'),reason='Zero-death route; first pit death2448/X1133/Y245',first_fall={k:fall[k]for k in ['frame','x','y','state','mask']},observed_rising_after_x970=False,unlogged='DwPrevious,ScFresh and Block_Buffer were not recorded; no missing-edge or early-jump causal claim.'),
        actual_RGB_geometry=geometry,modeled_scene=dict(initial_x=[1056,1008],floor_y=208,empty_gap=[1104,1135],normal_clock=399),
        source_cases=cases,limits=__doc__+'\nNo native clear, PPU timing, Lua execution, exact actual RAM reconstruction or causal diagnosis from model. Unchanged native guards/cap apply.',
        bindings={str(f):sha(f)for f in files})
    a.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,path=str(a.output),sha256=sha(a.output),source_GameLoops=sum(c['calls']for c in cases),cases=[dict(kind=c['kind'],ending=c['ending'])for c in cases])))


if __name__=='__main__':main()
