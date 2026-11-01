"""Compile the actual compact decoder and exercise every donor pose/facing."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_wwf_roster_package_bounded_v1 import decode
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
from private_build_outputs_v1 import validate
J=R/'build/ready76-menu-fixed-v5';P=R/'build/wwf-roster-package-1101-v1';O=R/'build/wwf-roster-decoder-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    assert not(O/'source-controls.json').exists();O.mkdir(exist_ok=True)
    package=json.loads((P/'source-package.json').read_text())
    for p,h in package['bindings'].items():assert sha(p)==h,p
    b=scoped_load(J/'candidate.nes');symbols=['WfState','WfHoganMetadata','WfPoseIndex','WfPoseWidth','WfPosePage','WfCellCount','WfRenderBuffer','WfRenderFace','WfCellOffset','R0','R1','R2','R3']
    template=R/'tools/reference/wwf_roster_pose_decoder_v1.s'
    world=R/'build/wwf-hogan-natural-source-v15/joint/world.s'
    declarations=world.read_text().split('.segment "WF_RUNTIME_STATE"\n',1)[1].split('.segment "WF_WORLD_CALLBACKS"',1)[0]
    assert declarations.count('WfRenderBuffer:.res 64')==1
    declarations=declarations.replace('WfRenderBuffer:.res 64','WfRenderBuffer:.res 69',1)
    state_names=re.findall(r'^(\w+):\.res',declarations,re.M)
    (O/'runtime-state.s').write_text('.segment "WF_RUNTIME_STATE"\n.export '+','.join(state_names)+'\n'+declarations)
    fixed=[n for n in symbols if n not in state_names]
    (O/'decoder.s').write_text('\n'.join(f'{n}=${address(b,n):04x}'for n in fixed)+'\n.import '+','.join(n for n in symbols if n in state_names)+'\n'+template.read_text())
    (O/'decoder.cfg').write_text('MEMORY { CODE:start=$a000,size=$2000,type=ro,file=%O; STATE:start=$dd2a,size=$53,type=rw,file=""; }\nSEGMENTS { WF_ROSTER_DECODER:load=CODE,type=ro; WF_RUNTIME_STATE:load=STATE,type=bss; }\n')
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    run('assemble',[R/'tools/Windows/cc65/bin/ca65.exe',O/'decoder.s','-o',O/'decoder.o','-l',O/'decoder.lst'])
    run('state-assemble',[R/'tools/Windows/cc65/bin/ca65.exe',O/'runtime-state.s','-o',O/'runtime-state.o'])
    run('link',[R/'tools/Windows/cc65/bin/ld65.exe','-C',O/'decoder.cfg',O/'decoder.o',O/'runtime-state.o','-o',O/'decoder.bin','-Ln',O/'decoder.lbl'])
    labels={name:int(value,16)for value,name in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/'decoder.lbl').read_text())}
    fields={n:labels[n]if n in state_names else address(b,n)for n in symbols}
    assert fields['WfRenderBuffer']==address(b,'WfRenderBuffer')
    assert fields['WfPosePage']==address(b,'WfPosePage')+5
    assert address(b,'WfOwnerCookie')-(0xdfd6+5)==5
    code=(O/'decoder.bin').read_bytes();blob=(P/'metadata-and-cookie-slots.bin').read_bytes();roster=json.loads((P/'roster.json').read_text())
    cases=clamps=0;costs=[]
    for row in roster['variants']:
        meta=blob[row['package_offset']:row['cookie_offset']]
        memory=[0]*65536;memory[0xa000:0xa000+len(code)]=code
        at=fields['WfHoganMetadata'];memory[at:at+1687]=meta+bytes(1687-len(meta))
        for group in range(meta[0]+1):
            actual_group=group if group<meta[0]else 0
            start=meta[2+2*actual_group];end=meta[4+2*actual_group]if actual_group+1<meta[0]else meta[1]
            for frame in range(end-start+1):
                actual_frame=frame if frame<end-start else 0
                for face in[0,1]:
                    memory[fields['WfState']+0x32]=group;memory[fields['WfState']+0x34]=frame;memory[fields['WfState']+0x3a]=face
                    cpu=NesMPU(memory=memory,pc=0xa000);cpu.sp=224;cpu.stPushWord(0x5aff)
                    for step in range(10000):
                        if cpu.pc==0x5b00:break
                        assert memory[cpu.pc]!=0,('Actual decoder BRK',hex(cpu.pc));cpu.step()
                    else:raise AssertionError('Decoder instruction bound')
                    assert cpu.sp==224
                    width,cells=decode(meta,actual_group,actual_frame);want=[4*len(cells)]
                    for tile,role,x,y,page in cells:want.extend([tile,role|(64 if face else 0),y&255,(width-x if face else x)&255])
                    got=memory[fields['WfRenderBuffer']:fields['WfRenderBuffer']+len(want)]
                    assert got==want,(row['name'],group,frame,face)
                    assert memory[fields['WfPosePage']]==cells[0][4]and memory[fields['WfPoseWidth']]==width
                    costs.append(cpu.processorCycles);cases+=1;clamps+=group!=actual_group or frame!=actual_frame
    assert cases>390
    result=dict(passed=True,source_CPU=True,native=False,ROM_parent=sha(J/'candidate.nes'),decoder_bytes=len(code),pose_buffer_bytes=69,private_layout_growth=5,private_fields=fields,legal_pose_facing_cases=390,cases_with_clamps=cases,clamped_cases=clamps,CPU_cycles=[min(costs),max(costs)],
                scope='Actual assembled6502 compact decoder on all195 original poses, both facings, plus legal group/frame fallback cases. Exact output packet, width, bank page and stack return. No host ROM integration or native-playable claim.',
                bindings={str(p.resolve()):sha(p)for p in[Path(__file__),template,world,P/'source-package.json',P/'metadata-and-cookie-slots.bin',J/'candidate.nes',J/'candidate.dbg',*[p for p in O.iterdir()if p.is_file()]]})
    save(O/'source-controls.json',result);print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
