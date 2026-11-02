"""Original cooldown state differential and complete host recovery regression."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit'),str(R/'tools/reference')]
import excitebike_original_cpu_1101_v2 as E
import check_hogan_current_bounded_v1 as M
from check_excitebike_host_1101_v1 import fixture,tick,wx
from prepare_excitebike_heat_1102_v2 import memory_image
from prepare_excitebike_dispatch_1101_v1 import O,labels,sha,save


def differential():
    lab=labels(O/'heat-host.lbl');image=(O/'heat-kernel.bin').read_bytes()
    seed=(R/'build/excite-prince-component-1101-v2/state-799.bin').read_bytes()
    cases=0
    for case in range(1024):
        ram=bytearray(seed);ram[0x3c]=[0,1,7,8,9,16,32,255][case&7]
        ram[0x3e0]=[0,32][case>>3&1];ram[0x94]=[0,1][case>>4&1]
        ram[0x98]=[0,255][case>>5&1];ram[0x9c]=[0,5][case>>6&1]
        ram[0x58]=[0,1][case>>7&1];ram[0xb8]=[14,50,57,58][case>>8&3]
        old=E.machine();list.__setitem__(old.memory,slice(0,2048),ram)
        for pc in [0xccdd,0xcd13]:list.__setitem__(old.memory,pc,0x60)
        class Flat(list):pass
        new=E.T.NesMPU(memory=Flat([0]*65536));new.memory[0xa000:0xb800]=image;new.memory[0xc000:0xc800]=ram
        args=dict(a=0x55,x=case&3,y=91,p=0x20|(case&13))
        a=E.call(old,0xdd8d,**args);z=E.T.run(new,lab['ExHeatRelease'],**args)
        assert bytes(old.memory[:256]+old.memory[512:2048])==bytes(new.memory[0xc000:0xc100]+new.memory[0xc200:0xc800]),case
        assert a[:3]==z[:3]and a[3]&0xef==z[3]&0xef and a[4]==z[4],(case,a,z)
        assert not any(new.memory[:256])
        cases+=1
    for name,pc,count in [('ExSourceTimers',0xd310,512),('ExSourceThrottleGate',0xdcde,512)]:
      for case in range(count):
        ram=bytearray(seed);ram[0x20]=case%11
        for i in range(0x21,0x3e):ram[i]=[0,1,5,255][(case+i)&3]
        for actor in range(4):
            ram[0x374+actor]=[0,1,5,255][(case+actor)&3]
            ram[0x5c+actor]=[0,2,64,128][(case//4+actor)&3]
        old=E.machine();list.__setitem__(old.memory,slice(0,2048),ram)
        class Flat(list):pass
        new=E.T.NesMPU(memory=Flat([0]*65536));new.memory[0xa000:0xb800]=image;new.memory[0xc000:0xc800]=ram
        args=dict(a=0x55,x=case&3,y=91,p=0x20|(case&13))
        a=E.call(old,pc,**args);z=E.T.run(new,lab[name],**args)
        assert bytes(old.memory[:256]+old.memory[512:2048])==bytes(new.memory[0xc000:0xc100]+new.memory[0xc200:0xc800]),(name,case)
        assert a[:3]==z[:3]and a[3]&0xef==z[3]&0xef and a[4]==z[4],(name,case,a,z)
        assert not any(new.memory[:256]);cases+=1
    return cases


def machine(raw):
    original=M.fresh
    def fresh(b):b['raw']=raw;return original(b)
    M.fresh=fresh
    try:return fixture()[0]
    finally:M.fresh=original


def journey(raw):
    m=machine(raw);heat=set();recovery=set();events=[];frame=0;last=None
    for pad,count in [(65,900),(1,600)]:
        for _ in range(count):
            tick(m,frame,pad);frame+=1
            state=(m.ram[2][0x3e0],m.ram[2][0x9c]);heat.add(state[0]);recovery.add(state[1])
            if state!=last and len(events)<80:
                events.append(dict(epoch=frame,heat=state[0],recovery=state[1],timer=m.ram[2][0x3c],lane=m.ram[2][0xb8],lane_speed=m.ram[2][0xdc]));last=state
    return dict(updates=frame,heat_states=sorted(heat),recovery_states=sorted(recovery),events=events,
                final_heat=m.ram[2][0x3e0],final_recovery=m.ram[2][0x9c],final_lane=m.ram[2][0xb8],
                final_lane_speed=m.ram[2][0xdc],final_speed=m.ram[2][0x90]+256*m.ram[2][0x94],final_x=wx(m))


def main():
    cases=differential();raw,_=memory_image()
    old=journey((O/'current3.nes').read_bytes());new=journey(raw)
    injuries=[]
    for pad in [1,65]:
        m=machine(raw);M.invoke(m,'ExService5');phases=set()
        for frame in range(1200):
            z=tick(m,frame,pad);phases.add(m.ram[2][0x9c])
            assert [z[k]for k in ['A','X','Y']]==[0x55,7,91]and z['P']&1
        injuries.append(dict(pad=pad,recovery_states=sorted(phases),final_crash=m.ram[2][0x98],
                             final_recovery=m.ram[2][0x9c],final_speed=m.ram[2][0x90]+256*m.ram[2][0x94]))
    m=machine(raw);_,cookie=memory_image()
    cold=bytes(m.ram[3][:6144])==(O/'heat-kernel.bin').read_bytes()and bytes(m.ram[2][0x1000:0x1800])==(O/'host-metadata.bin').read_bytes()and all(bytes(m.ram[k][0x1fe0:0x1ff0])==cookie for k in [2,3])and m.ppu_reads==16400
    M.put(m,DisableScreenFlag=1,Mirror_PPUMASK=0)
    before=([bytes(z)for z in m.ram],m.ppu_reads,list(m.rawtags),m.upper)
    warm=M.invoke(m,'ExLoad',a=0x55,x=7,y=91,p=0xf1)
    checks=dict(original_phase_exact=cases==2048,original_heat_observed=32 in old['heat_states'],
                old_cooling_motion_stall_reproduced=old['final_speed']==0,
                full_original_cooling_recovers=new['final_recovery']==0 and new['final_heat']==0 and new['final_speed']>0,
                original_injury_recovers=all(q['final_crash']==0 and q['final_recovery']==0 and q['final_speed']>0 for q in injuries),
                cold_all8192_bytes_and_headers=cold,warm_unchanged=warm['P']&1 and before==([bytes(z)for z in m.ram],m.ppu_reads,list(m.rawtags),m.upper))
    q=dict(passed=all(checks.values()),checks=checks,original_source_cases=cases,old=old,new=new,injuries=injuries,
           memory_candidate_SHA256=hashlib.sha256(raw).hexdigest(),ROM_written=False,native=False,installed=False,
           scope='Exact original DD8D phase with UI tails typed to returns, plus original motor/temperature/air/lane/recovery through genuine host input. Complete recovery0+resumed speed required; recovery5 is not accepted as recovered.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'heat-assembly.json',O/'heat-kernel.bin',O/'heat-host.lbl',O/'current3.nes']})
    save('heat-CPU.json',q);print(json.dumps(q));assert q['passed'],checks


if __name__=='__main__':main()
