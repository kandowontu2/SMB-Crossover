"""Real compiled cold constructor and accepted-video-frame phase comparisons."""
from pathlib import Path
import json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
import wwf_c2_relocation_model_v2 as M
from verify_native_relocation import NesMPU
M.MPU=M.T.MPU=M.T.W.MPU=NesMPU
T=M.T;L=R/'build/wwf-selected-contact-v2';O=R/'build/wwf-isolated-host-phase-controls-v4'

class NativePhaseBus(M.OracleBus):
    def __getitem__(self,a):
        if isinstance(a,int)and 0x6000<=a<0x6100:return self.phase[a-0x6000]
        return super().__getitem__(a)

def main():
    assert not O.exists();O.mkdir();report=dict(passed=False,source_CPU_lab=True,no_host_allocation=True,native_host=False,cold_cases=[],frame_cases=[])
    proof=json.loads((L/'build-proof.json').read_text());prior=json.loads((T.L/'build-proof.json').read_text())
    for p,h in proof['bindings'].items():assert T.sha(p)==h,p
    try:
        # A separate original-state phase capsule calls real donor entry points.
        text=(L/'host.s').read_text().split('WfHostFrameCore:\n',1)[1].split('.export WfHostCodeEnd',1)[0]
        text=text.replace(' sta WfHostContext+3\n','').replace(' stx WfHostContext+4\n','')
        text=re.sub(r'WfState\+\$([0-9a-f]+)',lambda m:'$'+m[1],text)
        text='.setcpu "6502"\nWfSelectActionCore=$af4d\nWfAdoptRequestsCore=$aed4\nWfVmTickCore=$e2e8\n.segment "CAPSULE"\n'+text
        (O/'native-phase.s').write_text(text)
        (O/'native-phase.cfg').write_text('MEMORY { M:start=$6000,size=$100,file="'+(O/'native-phase.bin').as_posix()+'",fill=yes; }\nSEGMENTS { CAPSULE:load=M,type=ro; }')
        commands=[['ca65.exe',str(O/'native-phase.s'),'-o',str(O/'native-phase.o'),'-l',str(O/'native-phase.lst'),'--create-dep',str(O/'native-phase.dep')],['ld65.exe','-C',str(O/'native-phase.cfg'),str(O/'native-phase.o'),'-o',str(O/'native-phase.bin')]]
        for i,cmd in enumerate(commands):
            cmd[0]=str(R/'tools/Windows/cc65/bin'/cmd[0]);guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);T.save(O/f'build-{i}.json',dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stderr
        prg=T.W.W.raw();phase=(O/'native-phase.bin').read_bytes();updates=0
        for character in range(6):
            for seed in [0,55,128,255]:
                a=NativePhaseBus(prg,bytes(2048),prior,None);a.phase=phase;a.labels={**a.labels,'WfHostFrame':0x6000};a.io[0x3000]=a.io[0x3001]=0
                b=M.C2Bus(prg,bytes(2048),prior,'relocated');b.mem[0xc000:0xe000]=(L/'c2.bin').read_bytes();b.labels={**b.labels,**proof['labels']}
                # Original descriptor + match initialization, no captured RAM.
                a.ram[0x2b],a.ram[0x2a],a.ram[0x82],a.ram[0x100],a.ram[0x12b]=character,(character+1)%6,seed,1,255
                n=NesMPU(memory=a,pc=0x8039);n.step();n.step();assert n.pc==0x803d
                M.old_call(a,'WfInitDescriptors');original_cold=T.W.call(a,0x8044,limit=100000)
                selected_cold=M.call(b,'WfHostCold',a=character,x=(character+1)%6,y=seed)
                assert T.cpu_state(original_cold)==T.cpu_state(selected_cold),('Cold returned ABI',character,seed,T.cpu_state(original_cold),T.cpu_state(selected_cold))
                assert all(a.ram[i]==b.shadow[i]for i in range(2048)if not 0x100<=i<0x200),('Cold projected state',character,seed)
                assert a.ram[0x100]==b.shadow[0x100]==1 and a.ram[0x12b]==b.shadow[0x12b]==255
                # Constructor's explicit clearing order is separately exact.
                clear=[(page+x,0)for x in range(256)for page in range(0,0x800,0x100)]
                events=[e for e in b.state_events if e is not None];assert events[:2048]==clear
                report['cold_cases'].append(dict(character=character,seed=seed,actual_source_constructor=True,source_state_SHA256=__import__('hashlib').sha256(b.shadow).hexdigest(),body_anchor=list(b.ram[0x42:0x44]),damage=list(b.ram[0x79:0x7b])))
                # Multiple full source input sequences and real pause intervals.
                previous=0;vm_ticks=0
                for frame in range(192):
                    held=[1,2,0x88,0x40,0xc0,0][frame//32];fresh=held&~previous;previous=held;pause=int(72<=frame<80)
                    starts=[len(a.state_events),len(b.state_events)];callbacks=[len(a.callbacks),len(b.callbacks)];oldphase=a.ram[0x71];oldvideo=a.ram[0x8d]
                    # Capsule's two host-only diagnostic stores are ordinary I/O.
                    ca=M.old_call(a,'WfHostFrame',a=held,x=fresh,y=pause);cb=M.call(b,'WfHostFrame',a=held,x=fresh,y=pause)
                    assert T.cpu_state(ca)==T.cpu_state(cb),('Phase returned ABI',character,seed,frame,T.cpu_state(ca),T.cpu_state(cb))
                    assert all(a.ram[i]==b.shadow[i]for i in range(2048)if not 0x100<=i<0x200),('Phase projected state',character,seed,frame)
                    aw=[e for e in a.state_events[starts[0]:]if e is not None];bw=[e for e in b.state_events[starts[1]:]if e is not None]
                    assert aw==bw,('Phase ordered source writes',character,seed,frame,aw,bw)
                    assert a.apu==b.apu and a.bank==b.bank,('Selected contact audio/map continuation',character,seed,frame)
                    assert a.ram[0x8d]==b.shadow[0x8d]==(oldvideo+1)&255
                    assert a.ram[0x71]==b.shadow[0x71]==(oldphase if pause else(oldphase+1)%6)
                    if not pause and oldphase%2==0:vm_ticks+=1
                    assert b.mem[:0x100]==b.host_seed[:0x100]and b.mem[0x200:0x800]==b.host_seed[0x200:]
                    updates+=1
                report['frame_cases'].append(dict(character=character,seed=seed,accepted_video_frames=192,pause_frames=8,source_actor0_updates=vm_ticks,source_phase=a.ram[0x71],source_video_counter=a.ram[0x8d]))
        report.update(passed=True,cold_constructors=len(report['cold_cases']),accepted_frame_pairs=updates,snapshot_used_as_constructor=False,selected_contact_source=True,callback_observer_scope='Contact/depth/RNG are now compiled source, so the old donor-only callback trace topology is not compared. Actual completeAPI AXYP/SP, projected ordered state, APU and mapper effects remain exact.',limits=proof['limits']+['The original-state comparison capsule is a fixture, not installed host source. It calls genuine native AF4D/AED4/E2E8; its phase policy is the declared single-hero adapter.','No real native SMB terrain/contact adapter or physical hostNMI clock is claimed. The full six original action scripts remain active.'])
    except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        files=[Path(__file__),Path(M.__file__),L/'build-proof.json',L/'host.s',L/'vm.bin',L/'c2.bin',O/'native-phase.s',O/'native-phase.cfg',O/'native-phase.bin',O/'build-0.json',O/'build-1.json']
        report['bindings']={str(p.resolve()):T.sha(p)for p in files if p.exists()};T.save(O/'controls.json',report);print(json.dumps({k:report.get(k)for k in ['passed','cold_constructors','accepted_frame_pairs','error']}))
if __name__=='__main__':main()
