"""Rogue weapon source differential; no native emulator or host world emulation.

Original external render/world calls are genuine stop boundaries. Port emits
their explicit class/phase/delta and requires the host to honor those calls.
"""
from pathlib import Path
import argparse,itertools,json,re,subprocess
from py65.devices.mpu6502 import MPU
import rogue_dawn_map_v1 as ref
import rogue_dawn_kernel_controls_v1 as kernel
ROOT=Path(__file__).resolve().parents[1]
P=dict(kernel.PROJECTION)
P.update({0x03d0+i:0x5c40+i for i in range(48)})
for slot in range(3):
    P.update({0x05d0+16*slot+i:0x5c70+3*slot+i for i in range(3)})
P.update({0x061f:0x5c7a,0x92:0x5c7b,0x1c:0x5c7c,0x69b3:0x5c7d,
          0x6b:0x5c3c,0x71:0x5c3d,0x04:0x5c3f,0x05:0x5c3e})

class Memory(bytearray):
    def __init__(self,data):
        super().__init__(data);self.writes=[]
    def __setitem__(self,k,v):
        if isinstance(k,int):self.writes.append(k)
        return super().__setitem__(k,v)

def build(folder):
    folder.mkdir(parents=True,exist_ok=True)
    wrapper=folder/'weapons.s'
    wrapper.write_text('.include "rogue_dawn.s"\n.include "rogue_dawn_weapons.s"\n')
    cfg=folder/'weapons.cfg'
    cfg.write_text('MEMORY { K:start=$B000,size=$1000,file=%O; }\nSEGMENTS { ROGUE_DAWN_CORE:load=K,type=ro; }\n')
    cc=ROOT/'tools/Windows/cc65/bin'
    subprocess.run([str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(wrapper),'-o',str(folder/'weapons.o')],check=True,cwd=ROOT)
    subprocess.run([str(cc/'ld65.exe'),'-C',str(cfg),'-o',str(folder/'weapons.bin'),'-Ln',str(folder/'weapons.lbl'),
                    '--dbgfile',str(folder/'weapons.dbg'),str(folder/'weapons.o')],check=True,cwd=ROOT)
    labels={}
    for line in (folder/'weapons.lbl').read_text().splitlines():
        m=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
        if m:labels[m[2]]=int(m[1],16)
    code=(folder/'weapons.bin').read_bytes()
    assert code[:632]==(ROOT/'build/rogue-dawn-kernel-v1/kernel.bin').read_bytes(), 'frozen kernel changed'
    return code,labels

def run(raw,code,labels,entry,state,ported=False,x=0,y=0,a=0,p=0x30,stop=None):
    m=Memory(bytes(65536) if ported else ref.cpu_image(raw,lower_bank=2))
    if ported:m[0xb000:0xb000+len(code)]=code
    for k,v in state.items():m[P[k] if ported else k]=v
    c=MPU(memory=m,pc=labels[entry] if ported else entry)
    c.x,c.y,c.a,c.p,c.sp=x,y,a,p,0xfd;c.stPushWord(0x5aff)
    m.writes.clear()
    target=0x5b00 if stop is None else stop
    for _ in range(12000):
        if c.pc==target:
            allowed=(set(P.values())|set(range(0x5c35,0x5c38))|{0x5c3a,0x5c3b}) if ported else set(P)|{0x0a,0x0b}
            assert all(k in allowed or 0x100<=k<0x200 for k in m.writes), ('unownedwrite',ported,[hex(k) for k in m.writes if k not in allowed and not 0x100<=k<0x200])
            return c,m
        assert m[c.pc]!=0,('BRK',ported,hex(c.pc),entry)
        c.step()
    raise AssertionError(('no return',entry,ported,hex(c.pc)))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-weapons-v1/controls.json')
    args=ap.parse_args();proof=dict(passed=False,native_run=False,scope=__doc__)
    try:
        code,labels=build(args.output.parent);raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
        tables=[]
        for name,bank,address,size in [('WaveHorizontal',62,0xd58f,25),('WaveVertical',62,0xd5a8,25),
                                        ('WeaponAnimationLow',2,0x858d,5),('WeaponAnimationHigh',2,0x85ef,28)]:
            expected=raw[16+bank*8192+(address&8191):16+bank*8192+(address&8191)+size]
            actual=code[labels[name]-0xb000:labels[name]-0xb000+size]
            assert actual==expected,(name,'tablebytes',actual.hex(),expected.hex())
            tables.append(dict(name=name,physical_bank=bank,cpu_address=f'{address:04X}',bytes=size,sha256=ref.digest(actual)))
        proof.update(rom=ref.binding(ref.ROM),combined_bytes=len(code),weapons_bytes=len(code)-632,
                     end_exclusive=f'{0xb000+len(code):04X}',projection={f'{s:04X}':f'{t:04X}' for s,t in P.items()},
                     inputs=[ref.binding(ROOT/p) for p in ['src/rogue_dawn_weapons.s','src/rogue_dawn.s','src/rogue_dawn_state.inc','src/rogue_dawn_core.s',
                             'tools/rogue_dawn_weapons_controls_v1.py','build/rogue-dawn-kernel-v1/handoff.json']],
                     original_private_pointer_exception='Wave source0A/0B table pointer has no port SRAM analogue: direct indexed immutable tables. This is declared, not a fake unused pointer. Actual world/render calls remain external boundaries.')
        proof['exact_original_tables']=tables
        costs={};n=0
        def compare(name,pc,state,stop=None,event=None,**kw):
            nonlocal n
            c,m=run(raw,code,labels,pc,state,stop=stop,**kw)
            d,q=run(raw,code,labels,name,state,ported=True,**kw)
            assert all(m[s]==q[t] for s,t in P.items()),(name,'RAM',[(hex(s),m[s],q[t]) for s,t in P.items() if m[s]!=q[t]],state)
            assert (c.a,c.x,c.y,c.p)==(d.a,d.x,d.y,d.p),(name,'AXYP',(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p),state,kw)
            assert c.sp==(0xfb if stop is not None else 0xfd) and d.sp==0xfd,(name,'SP',c.sp,d.sp)
            if event:
                address,value=event;assert q[address]==value,(name,'event',q[address],value)
            costs.setdefault(name,[]).append([c.processorCycles,d.processorCycles]);n+=1
        for gear,b,repeat,elevator,occupied,vy in itertools.product([0,1],[0,64,128],[0,64],[0,1],range(4),[0,0xfc]):
            state={0x6878:gear,0x12:b,0x16:repeat,0x0307:elevator,0x0308:vy,0x030c:1,0x030d:100,0x030e:120}
            state.update({0x03d0+16*i:1 if i<occupied else 0 for i in range(3)})
            compare('RdBombAllocate',0xd150,state)
        for slot in [0xd0,0xe0,0xf0]:
            compare('RdBombInitialize',0xd65e,{0x0300+slot:8},x=slot,stop=0xde47,event=(0x5c3a,3))
            for clock,fuse in itertools.product([0,1],[1,2,12,255]):
                compare('RdBombFuseStep',0xd670,{0x0300+slot:9,0x030f+slot:fuse,0x2d:clock},x=slot,stop=0xde47,event=(0x5c3a,3))
            for frame in [0,0x82,0xf7]:
                compare('RdBombExplosionFinish',0xd697,{0x4b:slot,0x0300+slot:10,0x0303+slot:frame},x=slot,stop=0xde47,event=(0x5c3a,3))
                compare('RdProjectileExplosion',0xd5c8,{0x0300+slot:4,0x0303+slot:frame},x=slot,stop=0xd519,event=(0x5c3a,1))
            for anim in [0,0x1b,0x7d,0x82,0x91]:
                compare('RdSetProjectileAnimation',0xd2fa,{},x=slot,a=anim)
            compare('RdInitProjectile',0xd2eb,{},y=slot)
            for gear,mode,face,carry in itertools.product([0,64,128,192],[0,1],[0,1],[0,1]):
                for name,pc in [('RdInitWaveHorizontal',0xd359),('RdInitWaveUp',0xd38a),('RdInitIce',0xd38e)]:
                    compare(name,pc,{0x6878:gear,0x010e:mode,0x4d:face},x=slot,y=slot,p=0x30|carry)
            for action,hit in itertools.product([1,2,3,4,11],[0,1,128]):
                compare('RdProjectileImpact',0xd5da,{0x0300+slot:action,0x030a+slot:hit},x=slot)
            for action in [0,1,2,3,4,7,10,11]:
                compare('RdProjectileTerrainImpact',0xd5e4,{0x0300+slot:action},x=slot)
            for screen in range(256):
                compare('RdCheckProjectileOnScreen',0xd5fc,{0x0300+slot:2,0x030b+slot:screen},x=slot)
            for vx,vy in itertools.product([0,4,0xfc],[0,2,0xfe]):
                compare('RdProjectileMotionDelta',0xd624,{0x4b:slot,0x0309+slot:vx,0x0308+slot:vy},stop=0xd630)
            for direction,phase,clock,flags in itertools.product(range(4),range(0,25,2),[0,1,2],[0,1,64,65]):
                compare('RdWaveKinematics',0xd536,{0x4b:slot,0x0500+slot:phase,0x0501+slot:clock,0x0502+slot:direction},x=slot,stop=0xd580,p=0x30|flags)
        for occupied,mode in itertools.product(range(4),[0,1]):
            state={0x0300+0xd0+16*i:1 if i<occupied else 0 for i in range(3)};state[0x010e]=mode
            compare('RdFindProjectileSlot',0xd1f7,state)
        for gear in [0,64,128,192]:
            compare('RdIceUpdateAdmission',0xd5c1,{0x6878:gear},stop=0xda8a)
        for updating in [0,1,2,255]:
            compare('RdFinishProjectileRender',0xd51c,{0x71:updating})
        for color in [0,0x81,255]:
            compare('RdClearProjectileColor',0xdf2d,{0x6b:color})
        for value in range(256):
            compare('DecodeVertical',0x8296,{},a=value)
            compare('DecodeHorizontal',0x832f,{},a=value)
        for gear,mode,face,occupied,grabbed,stock_case in itertools.product([0,64,128,192],[0,1],[0,1],range(4),[0,1],[0,1]):
            state={0x6878:gear,0x010e:mode,0x4d:face,0x92:grabbed,0x6879:([0,5] if not mode else [1,5])[stock_case]}
            state.update({0x03d0+16*i:1 if i<occupied else 0 for i in range(3)})
            admitted=not grabbed and occupied<3
            compare('RdPrepareHorizontalShot',0xd210,state,stop=0xd24e if admitted else None,event=(0x5c3a,1 if admitted else 0))
            compare('RdPrepareUpShot',0xd275,state,stop=0xd2b0 if admitted else None,event=(0x5c3a,1 if admitted else 0))
        for slot,action,player_action,gravity in itertools.product([0xd0,0xe0,0xf0],[1,2,3,11],[0,1,2],[0,24]):
            state={0x0300+slot:action,0x0300:player_action,0x0314:gravity}
            compare('RdFireHorizontalFinish',0xd251,state,y=slot,x=slot)
            compare('RdFireUpFinish',0xd2b3,state,y=slot,x=slot)
        for slot,mode,gear,alt,stock in itertools.product([0xd0,0xe0,0xf0],[0,1],[0,32],[0,1],[1,5]):
            state={0x010e:mode,0x6878:gear,0x69b3:alt,0x6879:stock}
            compare('RdApplyHorizontalMissile',0xd315,state,y=slot)
            compare('RdApplyUpMissile',0xd340,state,y=slot)
        for ammo,mode,fresh,repeat,gear,alt in itertools.product([0,1,5],[0,1],[0,32],[0,32],[0,32],[0,1]):
            compare('RdToggleMissile',0xa22a,{0x6879:ammo,0x010e:mode,0x12:fresh,0x16:repeat,0x6878:gear,0x69b3:alt})
        # Actual source animation, not an invented countdown or seeded endflag.
        animation_ranges=[range(0x1b,0x1d),range(0x1d,0x20),range(0x7d,0x7f),range(0x7f,0x82),
                          range(0x82,0x8b),range(0x8b,0x8d),range(0x8d,0x8f),range(0x8f,0x91),range(0x91,0x99)]
        for slot,rng,delay,draw in itertools.product([0xd0,0xe0,0xf0],animation_ranges,[0,1,2,3],[1,3]):
            for index in rng:
                compare('RdAnimateProjectile',0xdc8f,{0x4b:slot,0x0304+slot:delay,0x0305+slot:rng.start,0x0306+slot:index},x=slot,a=draw)
        for slot,age in itertools.product([0xd0,0xe0,0xf0],range(256)):
            state={0x4b:slot,0x0300+slot:10,0x030f+slot:age}
            c,m=run(raw,code,labels,0xd691,state,x=slot,stop=0xd694)
            d,q=run(raw,code,labels,'RdBombExplosionBegin',state,x=slot,ported=True)
            assert all(m[s]==q[t] for s,t in P.items())
            next_age=(age+1)&255
            assert q[0x5c3b]==(next_age if 1<=next_age<=5 else 0)
        proof['bomb_terrain_event_cases']=768
        for slot,action in itertools.product([0xd0,0xe0,0xf0],range(256)):
            allowed=action in [1,2,3,7,10,11]
            state={0x0300+slot:action}
            c,m=run(raw,code,labels,0xf0b4,state,y=slot,stop=0xf0c9 if allowed else 0xf0cf)
            d,q=run(raw,code,labels,'RdAttackAdmission',state,x=slot,ported=True)
            assert c.a==d.a==action and bool(d.p&1)==allowed
            assert all(m[s]==q[t] for s,t in P.items())
        proof['actual_attack_admission_cases']=768
        proof['attack_admission_limit']='New Cflag result means native action eligible only. Actual geometry and enemy-specific effects remain mandatory host collision hook; ticking bombs8/9 and impact4 never count as attacks.'
        timelines=[]
        for slot,birth_parity in itertools.product([0xd0,0xe0,0xf0],[0,1]):
            ss={0x4b:slot,0x0300+slot:8};ps=dict(ss);rows=[]
            for tick in range(100):
                clock=(birth_parity+tick)&255;ss[0x2d]=clock;ps[0x2d]=clock
                old_action=ss[0x0300+slot]
                if old_action==10:
                    c,m=run(raw,code,labels,0xd691,ss,x=slot,stop=0xd694)
                    ss={s:m[s] for s in P}
                    expected_phase=ss[0x030f+slot] if 1<=ss[0x030f+slot]<=5 else 0
                    c,m=run(raw,code,labels,0xd697,ss,x=slot,stop=0xde47)
                else:
                    expected_phase=0
                    c,m=run(raw,code,labels,0xd65e if old_action==8 else 0xd670,ss,x=slot,stop=0xde47)
                ss={s:m[s] for s in P}
                # Native UpdateObjAnim is called by original DE47 before rendering.
                c,m=run(raw,code,labels,0xdc8f,ss,x=slot,a=3)
                ss={s:m[s] for s in P}
                d,q=run(raw,code,labels,'RdBombStepBegin',ps,x=slot,ported=True)
                assert bool(d.p&1)==(old_action==10)
                assert q[0x5c3b]==expected_phase
                ps={s:q[t] for s,t in P.items()}
                if old_action==10:
                    # Explicit source terrain call boundary: host owns tile effects.
                    d,q=run(raw,code,labels,'RdBombStepFinish',ps,x=slot,ported=True)
                    ps={s:q[t] for s,t in P.items()}
                assert ss==ps,('bombtimeline',slot,birth_parity,tick,[(hex(s),ss[s],ps[s]) for s in ss if ss[s]!=ps[s]])
                rows.append(dict(tick=tick,clock_parity=clock&1,action=ss[0x0300+slot],age=ss[0x030f+slot],
                                 frame=ss[0x0303+slot],animation_delay=ss[0x0304+slot],terrain_phase=expected_phase))
                if not ss[0x0300+slot]:break
            assert rows[-1]['action']==0 and rows[-1]['frame']==0xf7
            assert [r['terrain_phase'] for r in rows if r['terrain_phase']]==[1,2,3,4,5]
            timelines.append(dict(slot=slot,birth_parity=birth_parity,updates=len(rows),rows=rows))
        proof['complete_bomb_state_animation_timelines']=timelines
        proof['bomb_timeline_limit']='Actual allocation is separately qualified. Full source state/animation timeline is compared across explicit source terrain/render boundaries; native tile damage, enemy contact and actual pixels remain host hooks, not simulated Metroid worldRAM.'
        proof['allocation_check']={'main_record_addresses':[hex(0x5b70+x+i) for x in [0xd0,0xe0,0xf0] for i in range(16)],
                                   'packed_wave_range':'5C70..5C78','private_metadata':'5C35..37',
                                   'persistent_writes':'No B8..BF; source kernel B0..B5 only'}
        proof['cases']=n
        proof['costs']={name:dict(cases=len(v),source_min=min(p[0] for p in v),source_max=max(p[0] for p in v),
                                port_min=min(p[1] for p in v),port_max=max(p[1] for p in v),
                                delta_min=min(p[1]-p[0] for p in v),delta_max=max(p[1]-p[0] for p in v)) for name,v in costs.items()}
        proof['passed']=True
    except Exception as e:
        proof['error']=repr(e);raise
    finally:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proof[k] for k in ['passed','combined_bytes','weapons_bytes','cases','costs']}))

if __name__=='__main__':main()
