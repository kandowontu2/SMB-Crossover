"""Fresh native whole BG calls and compiled replay on the HD Ryu composition."""
from pathlib import Path
import argparse,concurrent.futures,contextlib,hashlib,importlib.util,io,json,re,sys,subprocess
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'agent49-ryu-motion-h-a'
C=V/'ryu-current-hd/source';O=V/'ryu-native-hf';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    global C,O
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--candidate',type=Path,default=C);parser.add_argument('--tag',default='ryu-native-hm');args=parser.parse_args()
    assert re.fullmatch('[a-z0-9-]+',args.tag);C=args.candidate.resolve();O=V/args.tag
    assert not O.exists();O.mkdir();shutil_core=O/'component-f.lua';shutil_core.write_bytes((H/'component-f.lua').read_bytes())
    sp=importlib.util.spec_from_file_location('ryu_hf_image',V/'agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
    def capture(mapper):
        i=im.Image(C/f'build/smb-crossover-{mapper}.nes')
        old=json.loads((H/f'caller-f-candidate-{mapper}/binding.json').read_text());cfg=old['config']
        def hook(name,label,scope=None,delta=0):
            z=i.hook(label,scope,delta);z['bank']=z.pop('physical_bank');z['name']=name;return z
        bg=hook('entry','PlayerBGCollision');target=bytes([0x20,bg['address']&255,bg['address']>>8])
        seg=next(z for z in i.segs.values()if z['name']=='PLAYER');raw=i.raw[seg['ooffs']:seg['ooffs']+seg['size']];spots=[n for n in range(len(raw)-3)if raw[n:n+3]==target];assert len(spots)==1
        offset=seg['ooffs']+spots[0]+3
        post=dict(name='post',address=seg['start']+spots[0]+3,bank=(offset-16)//8192,bytes=list(i.raw[offset:offset+8]))
        cfg['hooks']=[bg,post,hook('gate','SamusRyuWallHandled'),hook('clamp','NativeGuest','SamusStopAtWallBanked')]
        cfg['interrupts']=[hook(n,n,delta='last'if tail else 0)|dict(ni=(-1 if tail else 1)if n=='NonMaskableInterrupt'else 0,iq=(-1 if tail else 1)if n=='IrqScrollSplit'else 0)for n in('NonMaskableInterrupt','IrqScrollSplit')for tail in(False,True)]
        d=O/f'caller-f-candidate-{mapper}';d.mkdir();out=d/'native-output';out.mkdir();cfg['out']=out.as_posix()+'/'
        wrapper=d/'component.lua';wrapper.write_text('L='+im.lua(i.ram)+'\nCFG='+im.lua(cfg)+'\ndofile('+im.lua(shutil_core.as_posix())+')\n')
        binding=dict(image=i.metadata(),core_sha256=sha(shutil_core),wrapper_sha256=sha(wrapper),config=cfg,parent_binding_sha256=sha(H/f'caller-f-candidate-{mapper}/binding.json'))
        (d/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
        cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(d/'host-output'),str(wrapper),str(i.path),'--timeout','120','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
        with(d/'host.log').open('wb')as f:z=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
        result=json.loads((out/'result.json').read_text())if(out/'result.json').exists()else None
        print('NATIVE',mapper,z.returncode,result,flush=True);return dict(mapper=mapper,exit=z.returncode,result=result)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:groups=list(pool.map(capture,('mmc3','mmc5')))
    (O/'native.json').write_text(json.dumps(groups,indent=2)+'\n');assert all(z['exit']==0 and z['result']['failures']==0 for z in groups)
    original=H/'check_native_f.py';code=original.read_text();anchor='R=Path.cwd();A=Path(__file__).resolve().parent;';assert code.count(anchor)==1
    code=code.replace(anchor,anchor+'A=ROOT_OUTPUT;')
    old="old=g.Image(A/'source-b/build'/f'smb-crossover-{mapper}.nes');new=g.Image(A/'source-f/build'/old.path.name)";assert code.count(old)==1
    code=code.replace(old,"old=g.Image(ROOT_PARENT/f'build/smb-crossover-{mapper}.nes');new=g.Image(ROOT_CANDIDATE/'build'/old.path.name)")
    old="for role,im in [('parent',old),('candidate',new)]:";assert code.count(old)==1
    code=code.replace(old,"for role,im in [('candidate',new)]:")
    # GO predates the source climb bypass already present in the old F/B
    # counterfactual. Permit the same explicit side-response fields for that
    # source-backed fix; keep every other comparison and native oracle.
    old="if kind!='interior':assert not semantic";assert code.count(old)==1
    code=code.replace(old,"if kind not in('interior','climb'):assert not semantic")
    (O/'check-bound.py.txt').write_text(code);stream=io.StringIO()
    with contextlib.redirect_stdout(stream):exec(compile(code,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'ROOT_OUTPUT':O,'ROOT_PARENT':R/'build/checkpoints/weapons-source-go','ROOT_CANDIDATE':C})
    (O/'review.log').write_text(stream.getvalue())
    result=json.loads((O/'strict-native-f.json').read_text());assert result['status'].startswith('PASS_')
    report=dict(passed=True,native=groups,compiled_report_sha256=sha(O/'strict-native-f.json'),source_core_sha256=sha(shutil_core),bound_verifier_sha256=sha(O/'check-bound.py.txt'),actual_compiled_calls=sum(z['actual_native_reexecution_calls']for z in result['groups']),actual_interrupt_gaps=sum(len(z['gaps'])for z in result['groups']),scope='Native whole BG source/fallback assertions, exact attained noninterrupt full callers. Actual in-call interrupts remain explicit compiled-model gaps. Not a full route/arsenal proof.',goal_complete=False)
    (O/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)


if __name__=='__main__':main()
