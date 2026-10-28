"""Small executable-original-ROM witnesses and sprite provenance, no host port.

CPU arenas supply source RAM/input/collision data. They do not emulate the PPU,
controller polling schedule, NMI, native campaign, or a proposed host adapter.
"""
from pathlib import Path
import hashlib,json,sys,statistics
from py65.devices.mpu6502 import MPU
from PIL import Image,ImageDraw
import dragon_power_map_v1 as D

class Memory:
    def __init__(self,bank=3):
        r=D.raw();self.banks=[r[16+i*32768:16+(i+1)*32768]for i in range(4)]
        self.ram=bytearray(32768);self.bank=bank;self.chr=0;self.writes=[]
    def __getitem__(self,a):
        if isinstance(a,slice):return bytes(self[i]for i in range(*a.indices(65536)))
        a&=65535;return self.banks[self.bank][a-32768]if a>=32768 else self.ram[a]
    def __setitem__(self,a,v):
        assert isinstance(a,int);v&=255;a&=65535;self.writes.append((a,v))
        if a>=32768:
            v&=self[a];self.bank=(v>>4)&3;self.chr=v&3
        else:self.ram[a]=v

def call(m,pc,a=0,x=0,y=0,stop=0x600):
    c=MPU(memory=m,pc=pc);c.a=a;c.x=x;c.y=y;c.p=0x24;c.sp=0xfd
    m.ram[0x1fe]=0xff;m.ram[0x1ff]=5
    m.writes=[];seen=[]
    for i in range(30000):
        if c.pc==stop:
            assert c.sp==0xff if stop==0x600 else True
            return dict(cycles=c.processorCycles,instructions=i,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,
                        apu=[(p,v)for p,v in m.writes if 0x4000<=p<=0x4017])
        seen.append((m.bank,c.pc));c.step()
    raise AssertionError((hex(pc),hex(c.pc),seen[-12:]))

def arena():
    m=Memory();m.ram[0x2d]=1;m.ram[0x2e]=100;m.ram[0xf7]=80;m.ram[0xf8]=160
    # The original native 16x16 collision map, tile75 -> source solid property1.
    m.ram[0x3b0:0x400]=bytes([0x75])*80
    for p in range(0x688,0x700,20):m.ram[p]=255
    return m

def step(m,held=0,fresh=0):
    m.ram[0xdf]=held;m.ram[0xe0]=fresh
    r=call(m,0xe82e);m.ram[0x26]=(m.ram[0x26]+1)&255
    return r

def records(m,ptr):
    out=[]
    for i in range(64):
        if m[ptr]==0x80:return out
        out.append(list(m[ptr:ptr+4]));ptr+=4
    raise AssertionError('unterminated original metasprite')

def pointer(m,p):return m[p]+256*m[p+1]

def checks():
    result={};m=arena();walk=[]
    for i in range(16):
        q=step(m,0x40);walk.append(m[0xf7])
    assert walk[-1]==60 and m[0x35]&128 # source bit40 is LEFT, not RIGHT!
    result['walk_left_16']=dict(x=walk,delta=walk[-1]-80,cycles=q['cycles'])
    m=arena();walk=[]
    for i in range(16):q=step(m,0x80);walk.append(m[0xf7])
    assert walk[-1]==100 and not m[0x35]&128
    result['walk_right_16']=dict(x=walk,delta=walk[-1]-80,cycles=q['cycles'])
    m=arena();trail=[]
    for i in range(80):
        q=step(m,0x81 if i<2 else 0,1 if i==0 else 0)
        trail.append([i+1,m[0x2d],m[0xf7],m[0xf8],m[0x34],q['cycles']])
        if i>3 and m[0x2d]==1:break
    assert min(t[3]for t in trail)==100
    assert trail[-1][3]==160 and trail[-1][1]==1
    result['complete_original_jump']=dict(fields=['update','action','x','y','phase','cycles'],trail=trail,
        rise=160-min(t[3]for t in trail),source_control_scope='actual E82E incl E834/EDC9/EE25, source flat tile75 arena; no NMI/PPU')
    air=[]
    for name,policy in [('heldRight',lambda i:0x80),('released',lambda i:0x80 if i<2 else 0),
                        ('reversed',lambda i:0x80 if i<20 else 0x40)]:
        m=arena();rows=[]
        for i in range(80):
            step(m,policy(i)|(1 if i==0 else 0),1 if i==0 else 0)
            rows.append([i+1,m[0xf7],m[0xf8],m[0x35],m[0x2d]])
            if i>3 and m[0x2d]==1:break
        assert min(v[2]for v in rows)==100 and rows[-1][2]==160
        air.append(dict(policy=name,fields=['update','x','y','horizontalPhase','action'],trail=rows))
    assert air[0]['trail'][-1][1]>air[1]['trail'][-1][1]
    assert air[2]['trail'][-1][1]<air[2]['trail'][19][1]
    result['actual_air_input_control']=dict(cases=air,correction='E9B3 AND CF removes Up/Down, preserves Left/Right; early locked-air inference rejected by actual executable path')
    attacks=[]
    for pole in [0,1]:
        m=arena();m.ram[0x32]=pole;trail=[]
        for i in range(40):
            q=step(m,2,2 if i==0 else 0);trail.append([i+1,m[0x2d],m[0x33],m[0x30]])
            if i>1 and m[0x2d]==1:break
        assert len(trail)==(13 if pole==0 else 21)
        attacks.append(dict(pole=pole,updates=len(trail),trail=trail,allocation_timer=12 if pole==0 else 20))
    result['complete_original_attacks']=attacks
    m=arena();m.ram[0x3b]=3;charge=[]
    for i in range(70):
        fresh=2 if i==0 else (1 if m[0x2d]==8 else 0)
        q=step(m,2|fresh,fresh);call(m,0xec4d)
        charge.append([i+1,m[0x2d],m[0x33],m[0x3a],m[0x3b],m[0x3e]])
        if m[0x3b]==2 and m[0x2d]==1:break
    assert any(v[1]==8 for v in charge)and m[0x3b]==2
    result['original_hold_B_fresh_A_wave']=dict(fields=['update','action','timer','wave','stock','waveX'],trail=charge,
        source_note='EA20 timer decremented on init update; wave32 charge starts only after attack finishes; fresh A required in state8')
    waves=[]
    for facing,expected in [(0,7),(0x80,-7)]:
        m=arena();m.ram[0x35]=facing;m.ram[0x3a]=1;m.ram[0x3e]=128
        q=call(m,0xec4d);assert m[0x3e]==128+expected
        waves.append(dict(facing=facing,delta=expected,cycles=q['cycles'],state=m[0x3a]))
    result['original_wave_speed']=waves
    # Original gain helper, including the genuine D9-bit40 250 cap.
    hp=[]
    for flags in [0,0x40]:
        for start in [1,100,140,149,150,240,250]:
            for food in [20,100]:
                m=Memory(0);m.ram[0x2e]=start;m.ram[0xd9]=flags;q=call(m,0x9a98,a=food)
                expected=min(250 if flags else 150,start+food)
                assert m[0x2e]==expected
                hp.append([flags,start,food,m[0x2e],q['cycles']])
    result['original_food_helper']=dict(fields=['D9','priorHP','food','afterHP','cycles'],cases=hp)
    # Real pickup collector for ordinary Magic Pole with actual source contact predicate.
    m=Memory(0);m.ram[0x2d]=1;m.ram[0xf7]=80;m.ram[0xf8]=80
    m.ram[0x614]=80;m.ram[0x600]=80;m.ram[0x632]=0
    q=call(m,0x9257,x=0)
    assert m[0x32]&1
    result['original_pole_collector']=dict(cycles=q['cycles'],pole=m[0x32]&1,actorType=m[0x628],rewardState=m[0x632],
        note='actual0:97FC spatial predicate, pickup at source arena center; world emergence/drop not exercised')
    pickups=[]
    for typ,states in [(0x83,[0,1]),(0x84,[0,1]),(0x85,[0,1,2]),(0x86,[0,2,4])]:
        for state in states:
            m=Memory(0);m.ram[0xf7]=80;m.ram[0xf8]=80;m.ram[0x2d]=1;m.ram[0x2e]=100
            m.ram[0x628]=typ;m.ram[0x632]=state;m.ram[0x600]=80;m.ram[0x614]=80
            for p in range(0x688,0x700,20):m.ram[p]=255
            q=call(m,0x8eeb,x=0)
            v=dict(type=typ,subtype=state,HP=m[0x2e],D9=m[0xd9],pole=m[0x32]&1,
                   seconds=m[0x36],waveStockAndKind=m[0x3b],actor=m[0x628],rewardState=m[0x632],cycles=q['cycles'])
            if typ==0x83:assert v['HP']==[120,150][state]
            elif typ==0x84:assert v['D9']==[16,32][state]and v['seconds']==16
            elif typ==0x85:assert v['pole']==1 and v['D9']==state
            elif typ==0x86:assert v['waveStockAndKind']==[3,67,129][state//2]
            pickups.append(v)
    result['actual_pickup_actor_wrapper']=dict(source='0:8EEB actual dispatcher +97A7 relative geometry +97FC contact +native collector',
        arena='mature source actor at genuine center, no natural spawn/emergence/drop; source-RAM-only controlled arena',cases=pickups)
    class Pads(Memory):
        def __init__(self,now):super().__init__();self.now=now;self.pos=[0,0]
        def __getitem__(self,a):
            if isinstance(a,int)and a in [0x4016,0x4017]:
                i=a-0x4016;p=self.pos[i];self.pos[i]+=1
                return (self.now if i==0 else 0)>>p&1 if p<8 else 1
            return super().__getitem__(a)
        def __setitem__(self,a,v):
            if a==0x4016 and v&1:self.pos=[0,0]
            super().__setitem__(a,v)
    pads=[]
    for prior,now in [(0,1),(1,1),(1,0),(0,2),(0,4),(0,8),(0,0x10),(0,0x20),(0,0x40),
                      (0,0x80),(0x40,0x80),(0x81,0x82)]:
        m=Pads(now);m.ram[0xdf]=prior;q=call(m,0x9799,stop=0xffdc)
        assert m[0xdf]==now and m[0xe0]==((now^prior)&now)
        pads.append(dict(prior=prior,held=m[0xdf],fresh=m[0xe0],serial_reads=m.pos,cycles=q['cycles']))
    result['original_controller_reader']=dict(entry='3:9799..97DC,stop at genuine far-return FFDC',
        hardware='controlled serial4016/4017 bit input only; all source reader instructions executed',
        masks=dict(A=1,B=2,Select=4,Start=8,Up=16,Down=32,Left=64,Right=128),cases=pads)
    m=Memory();m.ram[0xf2]=3
    for p in range(0x688,0x700,20):m.ram[p]=255
    for event in [0,1,2,3]:call(m,0x98a8,a=event)
    costs=[];stores=[];frames=[]
    for i in range(120):
        q=call(m,0x8f68);costs.append(q['cycles']);stores+=q['apu']
        frames.append([i,q['cycles'],q['apu'],list(m.ram[0x688:0x700]),list(m.ram[0x3f0:0x3fc])])
    assert stores and all(not 0x4010<=p<=0x4014 for p,v in stores)
    result['original_audio_120ticks']=dict(entry='3:8F68 (far entry8F62)',requests='source initial0:8CE5 requests0/1/2/3 via actual3:98A8',
        ordered_store_count=len(stores),first20=stores[:20],p50=statistics.median(costs),p95=sorted(costs)[113],
        min=min(costs),max=max(costs),frames_state_and_bus_sha256=D.digest(json.dumps(frames,separators=(',',':')).encode()),
        final_driver_state_sha256=D.digest(bytes(m.ram[0x688:0x700])+bytes(m.ram[0x3f0:0x3fc])),
        limits='first source initialization cue group, original CPU only; no host mixer/borrow/bank/interrupt cost, soundtrack/native/audio waveform not qualified')
    return result

def artwork():
    m=Memory();poses=[];alltiles=set();allparts=0
    for pose in range(32):
        m.ram[0x30]=pose;m.ram[0xf9]=3;m.ram[0x31]=0;m.ram[0x23]=4
        m.ram[0xf7]=80;m.ram[0xf8]=80;m.ram[0x449]=0
        r=call(m,0xbaab);oam=bytes(m.ram[0x704:0x700+m[0x23]])
        spec=records(m,pointer(m,0xbafa+pose*2));head=records(m,0xbae9)if pose&15<9 else[]
        expected=head+spec;assert len(oam)==4*len(expected)
        for i,(yo,tile,attr,xo)in enumerate(expected):
            yy=(80+(yo if yo<128 else yo-256)-1)&255;xx=(80+(xo if xo<128 else xo-256))&255
            assert oam[i*4:i*4+4]==bytes([yy,tile,attr,xx])
            alltiles.add(tile)
        allparts+=len(expected)
        poses.append(dict(key=pose,record=f'3:{pointer(m,0xbafa+pose*2):04X}',head=bool(head),parts=len(expected),
                          record_sha256=D.digest(bytes(v for part in expected for v in part)),oam=oam.hex(),cycles=r['cycles']))
    # Source palette setter2:83C8 copies19B+two fixed sprite palettes; final upload0:9977.
    p=pointer(D.memory(2),pointer(D.memory(2),0x83ed+6))
    palette_record=list(D.memory(2)[p:p+19]);constants=list(D.memory(2)[0x83e7:0x83ed])
    palette=[palette_record[0]]+palette_record[13:19]+constants
    assert palette_record[13:16]==[0x30,0x36,0x0f]and constants==[0x36,0x26,4,0x30,0x36,0x0f]
    # Full source 8x8 OAM decoder output, source tile bytes, original role colors.
    # RGB palette is a conventional static NES preview; not a captured NES PPU image.
    colors={0x30:(236,238,236),0x36:(236,180,176),0x0f:(0,0,0),0x22:(76,154,236),
            0x26:(228,84,76),0x16:(152,34,32),4:(68,0,100)}
    groups=[palette_record[13:16],palette_record[16:19],constants[:3],constants[3:]]
    im=Image.new('RGB',(8*82,4*82),(44,54,68));dr=ImageDraw.Draw(im)
    chrdata=D.raw()[16+131072+3*8192:16+131072+4*8192]
    for pose in poses:
        layer=Image.new('RGB',(64,64),(102,113,130));px=layer.load();o=bytes.fromhex(pose['oam'])
        # Earlier OAM wins. Iterate backwards for original priority composition.
        for i in range(len(o)-4,-1,-4):
            yy,t,a,xx=o[i:i+4];tile=chrdata[t*16:t*16+16]
            for y in range(8):
                for x in range(8):
                    sx=7-x if a&64 else x;sy=7-y if a&128 else y
                    v=((tile[sy]>>(7-sx))&1)|(((tile[sy+8]>>(7-sx))&1)<<1)
                    dx=xx-80+24+x;dy=yy-79+24+y
                    if v and 0<=dx<64 and 0<=dy<64:px[dx,dy]=colors[groups[a&3][v-1]]
        x=(pose['key']%8)*82+9;y=(pose['key']//8)*82+15
        im.paste(layer,(x,y));dr.text((x,y-12),f'{pose["key"]:02X}',fill='white')
    target=D.OUT/'side-view-original-preview.png';im.save(target)
    return dict(source_renderer='3:BAAB -> BACE/BAD6 ->9941',part_format='signedY,tile,attribute,signedX;80 terminator',
                source_CHR_bank=3,sprite_pattern_table=0,source_CHR_page_bytes=4096,source_tiles=sorted(alltiles),
                source_tile_count=len(alltiles),source_tile_bytes=len(alltiles)*16,poses=poses,total_original_parts=allparts,
                palette_record_pointer=f'2:{p:04X}',palette_record19=palette_record,sprite_palette_roles=groups,
                palette_setter='2:838C/83AF/83C8;2:83E7fixedP2/P3;0:9977uploads3F00',
                palette_limit='source colors proven for selected D5=0 record; no source PPU/native capture/other area palette proof',
                preview=D.binding(target))

def main():
    D.OUT.mkdir(exist_ok=True)
    result=dict(status='SOURCE_EXECUTABLE_ONLY; no host allocation/port/native',ROM=D.binding(D.ROM),
                control_scope='original2A03-compatible6502 execution,Dflag0,noPPU/NMI/IRQ; no original instruction stubs',
                controls=checks(),art=artwork())
    result['tool']=D.binding(__file__);result['map_tool']=D.binding(D.__file__)
    p=D.OUT/'reference-controls.json';p.write_text(json.dumps(result,indent=2)+'\n')
    spans=[
        (0,0x800b,0x8097,'original NMI; gameplay dispatch and OAM/APU sequencing'),
        (0,0x80dd,0x8136,'native side-view gameplay NMI path'),
        (3,0x9799,0x97df,'actual pad read; heldDF/freshE0'),
        (3,0xe82e,0xe867,'side-view state caller'),
        (3,0xe906,0xe99a,'ground/select direction'),
        (3,0xe99a,0xea20,'jump and air kick admission'),
        (3,0xea20,0xea80,'punch/pole'),
        (3,0xea80,0xeae1,'Wind Wave charge/ready/fire/recovery'),
        (3,0xeae1,0xeb32,'air kick'),
        (3,0xeb32,0xeb6d,'crouch/low pole'),
        (3,0xebe1,0xec4d,'hurt/death/exit'),
        (3,0xec4d,0xecba,'side-view Wind Wave'),
        (3,0xed2c,0xee25,'source tile queries and collision sampling'),
        (3,0xee25,0xeef9,'source horizontal/vertical integrators'),
        (0,0xfbb9,0xfc4f,'side-view attack point and enemy acceptance'),
        (0,0x8edd,0x8f00,'mature actor full dispatcher'),
        (0,0x919d,0x91d2,'food collector/table'),
        (0,0x9235,0x927d,'timed flags and pole collectors'),
        (0,0x927d,0x92ca,'Wind/Super/Thunder stock collector'),
        (0,0x9a2e,0x9ab5,'hunger and heal/cap helper'),
        (3,0xe1aa,0xe226,'separate overhead caller and timed flags'),
        (3,0xe476,0xe53b,'overhead red/green pole attack/timing/pose tables'),
        (3,0xe620,0xe757,'overhead multidirection Wind/Thunder updater'),
        (3,0xaddc,0xae62,'source normal body/overlay selection'),
        (3,0xbaab,0xbafa,'side-view source body selection'),
        (3,0x9941,0x99e9,'original OAM decoder; trailing bound includes next entry padding only as disassembly'),
        (2,0x838c,0x83f5,'source palette initialization and fixed sprite roles'),
        (0,0x9977,0x99c3,'native palette upload'),
        (3,0x8f68,0x9345,'audio interpreter and ordered APU writer'),
        (3,0x98a8,0x98fb,'event request and descriptor dispatch'),
    ]
    sm=dict(status='bounded annotated original map, not complete disassembly or host implementation',
            ROM=D.binding(D.ROM),bank_model='32KB GNROM PRG bank0..3; fileoffset=16+bank*32768+(CPU-8000)',
            routines=[dict(bank=b,start=f'{s:04X}',end_exclusive=f'{e:04X}',bytes=e-s,
                           sha256=D.digest(D.memory(b)[s:e]),role=role)for b,s,e,role in spans],
            unresolved=['full damage table for every original enemy/boss','Super Wave collision multiplicity versus manual wording',
                        'red versus green named palette/behavior correspondence beyond native subtype1/2 flags',
                        'original US/JP choice if user expects Japanese Goku visual; US source is selected here',
                        'host terrain/input/injury/palette/audio lifecycle and cost; no host adapter exists'],
            correction='Early locked-air inference rejected: AND CF removes Up/Down, preserves Left/Right; actual release/reversal controls retained.')
    mp=D.OUT/'source-map.json';mp.write_text(json.dumps(sm,indent=2)+'\n')
    (D.OUT/'source-excerpts.txt').write_text('\n\n'.join(f'; {role}\n'+D.disassembly(b,s,e-s)for b,s,e,role in spans)+'\n')
    print(json.dumps(dict(path=str(p),sha256=D.digest(p.read_bytes()),artParts=result['art']['total_original_parts'],
                         tiles=result['art']['source_tile_count'],jump=result['controls']['complete_original_jump']['rise']),indent=2))
if __name__=='__main__':main()
