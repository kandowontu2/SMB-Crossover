"""Bounded actual F801/C40B/B310 CPU geometry prototype. Never writes a ROM."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

from verify_native_relocation import NesMPU
from private_build_outputs_v1 import validate

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'build/prince-actor-1101-v1'
POSE=ROOT/'build/prince-pose-reservation-1103-v185'
DEFAULT=ROOT/'build/prince-resume-1108/prince-current.nes'
PIN='b6df037eeb47743366586a1fe4c91bf9ebe0d922cd5ed6731c4248a86aae943b'
WORKER=ROOT/'tools/reference/prince_climb_edge_1108_v1.s'
TRACE=ROOT/'build/prince-climb-trace-1108/capture/prince-diagnostic.json'
PC=0xb0da
ARENA=0x7000


def sha(raw): return hashlib.sha256(raw).hexdigest()
def word(m, at): return m[at] | m[at+1]<<8
def put(m, at, v): m[at:at+2]=bytes((v&255, v>>8&255))
def block(x,y): return (0x3d0 if x&256 else 0x300)+((x>>4)&15)+(y&0xf0)-32


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rom',type=Path,default=DEFAULT)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    rom=a.rom.read_bytes();assert sha(rom)==PIN
    runtime=(POSE/'pose-runtime.bin').read_bytes()
    state=bytearray((DATA/'native-state-v153.bin').read_bytes())
    labels=json.loads((DATA/'native-labels-v153.json').read_bytes())
    lo,hi=(1375+labels[n]-0xc766 for n in ('NativeLo','NativeHi'))
    assert (state[lo],state[hi])==(0xe7,0xba)
    state[lo],state[hi]=0x96,0xa2  # Existing backdrop change, outside live align.
    stream=json.loads((POSE/'pose-source.json').read_bytes())['streams']
    assert sha(runtime)==stream[0]['SHA256'] and sha(state)==stream[2]['SHA256']
    assert runtime[PC-0xa000:PC-0xa000+3]==bytes.fromhex('200bc4')
    capture=json.loads(TRACE.read_bytes());assert capture['ROM_sha256']==PIN
    trace=next(r for r in capture['first_pipe_route']['alignments'] if r['caller']==PC+3)
    assert (trace['rawX'],trace['baseColumn'],trace['index'],trace['surface'],trace['cellX'])==(413,9,19,208,384)
    config=a.output/'worker.cfg'
    config.write_text('MEMORY{M:start=$7000,size=$0200,file=%O;}SEGMENTS{CLIMB_EDGE:load=M,type=ro;}')
    cc=ROOT/'tools/Windows/cc65/bin'
    obj=a.output/'worker.o'; binary=a.output/'worker.bin'
    for cmd in ([cc/'ca65.exe',WORKER,'-o',obj],[cc/'ld65.exe','-C',config,obj,'-o',binary]):
        cmd=list(map(str,cmd));validate(cmd,a.output,cwd=ROOT)
        r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        assert r.returncode==0,r.stderr
    worker=binary.read_bytes()
    template=bytearray(65536)
    for bank,at in [(126,0x8000),(127,0xe000)]:
        template[at:at+8192]=rom[16+bank*8192:16+(bank+1)*8192]
    assert template[0x95d8:0x95da]==bytes((0,0xd0))
    assert template[0xef36+0x54]&1
    non_solid=next(t for t in range(1,256) if not template[0xef36+t]&1)
    template[0xa000:0xa000+len(runtime)]=runtime
    template[0xc0b0:0xc60f]=state[:1375]
    template[ARENA:ARENA+len(worker)]=worker

    def execute(edge, face, foot, solid_side, other_side, blocked_above, changed, offset=None, ingress=PC):
        m=bytearray(template)
        if changed:put(m,PC+1,ARENA)
        x=(edge-15 if face else edge+15)&65535
        put(m,0xc60f,x);m[0xc615]=face;put(m,0xc084,foot)
        m[0xc616]=24;m[0xc618]=2;m[0xc617]=91;m[0xc611]=128
        put(m,0xc078,413);m[0xc07a]=9;m[0xc4b1]=19
        put(m,0xc07f,208);m[0xc081]=1;put(m,0xc089,77);m[0xc6d1]=5
        hand=foot-24
        if edge and 32<=hand<240:
            inside=edge if face else edge-1
            outside=edge-1 if face else edge
            m[block(inside,hand)]=solid_side;m[block(outside,hand)]=other_side
            if blocked_above and (hand&0xf0)>=48:m[block(inside,(hand&0xf0)-1)]=0x54
        if ingress!=PC: m[ingress:ingress+3]=bytes.fromhex('200bc4')
        c=NesMPU(memory=m,pc=ingress);c.a=43;c.x=19
        c.y=offset if offset is not None else (24 if face else 58)
        c.p=0x61;c.sp=0xf0
        probes=[];minsp=c.sp
        for _ in range(1500):
            if c.pc==ingress+3:break
            if c.pc==0xb310:probes.append((word(m,0xb369),word(m,0xb36b)))
            minsp=min(minsp,c.sp);c.step()
        else:raise AssertionError(('F801 instruction bound',hex(c.pc)))
        assert c.sp==0xf0
        return dict(x=word(m,0xc60f),y=m[0xc611],cell=word(m,0xc07d),
                    ABI=(c.a,c.x,c.y,c.p,c.sp),state=bytes(m[0xc000:0xc800]),
                    probes=probes,cycles=c.processorCycles,minsp=minsp)

    positive=[]
    negative=0
    max_cycles=0;minsp=255
    for edge,face,foot in itertools.product((0x10,0x100,448,0x210,0xfff0),(0,255),(56,88,203,255,263)):
        old=execute(edge,face,foot,0x54,non_solid,False,False)
        new=execute(edge,face,foot,0x54,non_solid,False,True)
        assert new['x']==edge+(-8 if face else 8),(edge,face,foot,old,new['x'],new['probes'])
        assert new['y']==old['y'] and new['ABI']==old['ABI']
        assert new['state'][:0x60f]==old['state'][:0x60f] and new['state'][0x611:]==old['state'][0x611:]
        assert len(new['probes'])==3
        positive.append(dict(edge=edge,face=face,foot=foot,baselineX=old['x'],candidateX=new['x']))
        max_cycles=max(max_cycles,new['cycles']);minsp=min(minsp,new['minsp'])
    for edge,face,foot,inside,outside,roof in itertools.product(
         (0,0x100,448,0x210),(0,255),(31,55,203,264,0xffff),(0,0x54),(0,0x54),(False,True)):
        admissible=edge!=0 and foot==203 and inside==0x54 and outside==0 and not roof
        if admissible:continue
        old=execute(edge,face,foot,inside,outside,roof,False)
        new=execute(edge,face,foot,inside,outside,roof,True)
        assert new['ABI']==old['ABI'] and new['state']==old['state'],(edge,face,foot,inside,outside,roof)
        negative+=1
    for face,offset in itertools.product((0,255),(14,24,36,58,64)):
        old=execute(448,face,203,0x54,0,False,False,offset,ingress=0x7010+len(worker))
        new=execute(448,face,203,0x54,0,False,True,offset,ingress=0x7010+len(worker))
        assert old==new
    prior=execute(448,255,203,0x54,0,False,False)
    candidate=execute(448,255,203,0x54,0,False,True)
    assert prior['x']==trace['after']['source_x']==408 and candidate['x']==440
    proof=dict(passed=True,ROM_written=False,ROM_sha256=PIN,helper_bytes=len(worker),
         fixture_link_address=hex(ARENA),original_F801_runtime_PC=hex(PC),
         positive_cases=len(positive),no_edge_exact_cases=negative,other_alignment_unchanged_cases=10,
         actual_B310_typed_probes=candidate['probes'],old_X=prior['x'],new_X=candidate['x'],
         Y_and_C40B_ABI_exact=True,source_body_exit_delta_px=12,
         projected_pipe_exit_center=452,max_cycles=max_cycles,min_fixture_SP=minsp,
         notes='Worker is an executable CPU prototype linked in isolated arena, not allocated in production RAM. No ROM, cold reset, native input/IRQ or course proof. No-edge compares all RAM2/application state and ABI; native query scratch in RAM3 is transient.',
         bindings={str(q.relative_to(ROOT)):sha(q.read_bytes())for q in (WORKER,Path(__file__),TRACE)},
         positive_summary=positive)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k!='positive_summary'},indent=2))


if __name__=='__main__':main()
