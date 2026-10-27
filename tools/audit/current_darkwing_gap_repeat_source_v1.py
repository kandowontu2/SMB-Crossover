"""Finite repeated gap/readback source control, with actual v3 failure geometry."""
from pathlib import Path
import argparse,csv,hashlib,json,struct,zlib
from current_darkwing_gap_route_source_v1 import ROOT,ROM,EXPECTED,scene,world,Controller
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
POLICY=ROOT/'tools/playthroughs/current_roster_darkwing_gap_v2.lua'


class Repeated:
    def __init__(self):self.inner=Controller();self.resume=None;self.completed=[];self.detected=[]
    def buttons(self,q):
        if self.resume is not None:
            if world(q)<self.resume:return 1
            self.inner=Controller();self.resume=None
        was=self.inner.phase;bits=self.inner.buttons(q)
        if was=='find'and self.inner.phase!='find':
            pair=[self.inner.edge,self.inner.landing]
            assert not self.detected or pair[0]>=self.detected[-1][1]+8,('Forward terrain progress',pair,self.detected)
            self.detected.append(pair)
        if self.inner.phase=='done':
            self.completed.append(dict(edge=self.inner.edge,landing=self.inner.landing,x=world(q),y=q.get('Player_Y_Position')))
            self.resume=self.inner.landing+8
        return bits


def source(b):
    q=scene(b,1056)
    for x in [1376,1392,1408]:
        for row in [11,12]:q.set('Block_Buffer_1',0,x//256%2*208+row*16+x%256//16)
    c=Repeated();rows=[];jumps=[];calls=0
    for i in range(500):
        # The CPU arena supplies a normal following viewport so the first
        # fixed screen edge does not become an unrelated artificial wall.
        # No player, input-consumer, velocity, health or jump result is set.
        cam=max(944,world(q)-112)
        q.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8)
        old=q.get('Player_State');bits=c.buttons(q);q.put(SavedJoypadBits=bits);q.invoke('GameLoop');calls+=1
        row=dict(update=calls,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),buttons=bits,consumer_previous=q.get('DwPrevious'),fresh=q.get('ScFresh'),resume_after=c.resume,completed=len(c.completed))
        rows.append(row)
        if old==0 and row['state']==1 and row['vy']>=128:jumps.append(row.copy())
        assert q.get('GameEngineSubroutine')==8 and q.get('MmDeathFlag')==0 and q.get('DwHealth')==4
        ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
        if len(c.completed)==2 and world(q)>1432 and q.get('Player_State')==0:break
    assert c.detected==[[1104,1136],[1376,1424]]and len(c.completed)==2
    assert len(jumps)==2 and all(j['fresh']&128 for j in jumps)
    assert c.completed[0]['x']>=1121 and c.completed[1]['x']>=1409
    return dict(passed=True,calls=calls,detected=c.detected,completed=c.completed,jumps=jumps,rows=rows)


def actual_gap(path):
    raw=path.read_bytes();at=8;compressed=b''
    while at<len(raw):
        n=struct.unpack_from('>I',raw,at)[0];kind=raw[at+4:at+8];part=raw[at+8:at+8+n];at+=n+12
        if kind==b'IHDR':w,h=struct.unpack_from('>II',part)
        if kind==b'IDAT':compressed+=part
    assert(w,h)==(256,240);data=zlib.decompress(compressed)
    def pixel(x,y):return data[y*(w*4+1)+1+x*4:y*(w*4+1)+1+x*4+4]
    sky=pixel(8,100);columns=[x for x in range(256)if all(pixel(x,y)==sky for y in [208,216,224,232])]
    assert columns==list(range(81,129))
    return dict(actual_frame=2670,empty_floor_screen=[81,128],width=48,foreground_camera=1296,
        source_model_native_cell_interval=[1376,1423],
        limits='RGB+currentcamera gives1377..1424: visible carry is1px behind current foreground camera. Model uses aligned16px native cells; actual Block_Buffer was unlogged. Native controller reads live cells, not these coordinates.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists()and sha(ROM)==EXPECTED
    old=ROOT/'build/verification/compact-ab221e-darkwing-easy-v3';trace=list(csv.DictReader((old/'trace.csv').open(newline='')))
    window=[q for q in trace if 1296<=int(q['x'])<=1408]
    assert not any(q['state']=='1'and int(q['vy'])>=128 for q in window)
    pic=ROOT/'build/current-ab221e-darkwing-second-gap-actual-v1.png'
    z=dict(passed=True,native_run=False,source_CPU_only=True,Lua_executed=False,ROM_sha256=EXPECTED,
        original_v3_false=dict(frame=2670,x=1408,y=245,reason='real-death guard',observed_rise_after_x1296=False,
            first_gap_actual_logs='freshpress1090, actualrise1093/171, actuallanding1153/176'),
        actual_second_gap=actual_gap(pic),source=source(scoped_load(ROM)),
        scene='Typed32px and48px empty floor gaps; complete GameLoop. CPU-only normal following viewport environment; no player/velocity/consumer/jump/resource/outcome changes after setup.',
        scope='Repeated controller re-arms only after witnessed native landing and>=landing+8 forward progress. All original route physics/guards/caps. Source mirror, not Lua/native/PPU/campaign proof.',
        bindings={str(p):sha(p)for p in [ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),POLICY,Path(__file__),ROOT/'tools/audit/current_darkwing_gap_route_source_v1.py',pic,old/'trace.csv',old/'result.json',old/'mega_proto_body_palette_9ea-run.log']})
    a.output.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,path=str(a.output),sha256=sha(a.output),calls=z['source']['calls'],detected=z['source']['detected'],landings=z['source']['completed'])))


if __name__=='__main__':main()
