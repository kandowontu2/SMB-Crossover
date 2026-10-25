"""Fresh GF Arm/Rush source-rule witnesses and exact compiled caller replay."""
from pathlib import Path
import concurrent.futures,contextlib,hashlib,importlib.util,io,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
C=V/'weapons-current-gf/source';O=V/'weapons-mechanics-gi'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())


def main():
    assert not O.exists();O.mkdir()
    module=V/'agent49g-samus-crouch-fix-proposal-b/image.py'
    sp=importlib.util.spec_from_file_location('weapon_gi_image',module);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
    tasks=[]
    armcases=[dict(name='throw-full-right',kind='throw',stock=112,face=1),dict(name='throw-last8-left',kind='throw',stock=8,face=2),dict(name='switch-cancel',kind='cancel',stock=112),dict(name='real-damage-cancel',kind='damage',stock=112),dict(name='reject-lift7',kind='none',stock=7),dict(name='reject-lift0',kind='none',stock=0),dict(name='Star-free0',kind='throw',stock=0,star=True),dict(name='Star-expiry-reject-throw',kind='expire',stock=0,star=True)]
    cases=['gate0','gate3','gate4','gate8','gateStar0','bounce4','bounce8','bounce12','bounceStar0','active4','activeStar0','burst4','spent4','StarFire0','expireStar0']
    for mapper in ('mmc3','mmc5'):
        image=im.Image(C/f'build/smb-crossover-{mapper}.nes')
        isr={n:image.hook(label,delta=d)for n,label,d in [('NMI','NonMaskableInterrupt',0),('NMIEnd','NonMaskableInterrupt','last'),('IRQ','IrqScrollSplit',0),('IRQEnd','IrqScrollSplit','last')]}
        for character in (1,9):
            hooks={n:image.hook(label,scope)for n,label,scope in [('MegaAttack','MegaAttack','SpecialWeapons'),('GrabBrick','GrabBrick','SpecialWeapons')]}
            hooks['ArmThrow']=image.hook('MegaManSuperArmThrow');hooks.update(isr)
            tasks.append(dict(tag=f'arm-{mapper}-{character}',mapper=mapper,character=character,family='arm',config=dict(character=character,cases=armcases,observeSelected=1,hooks=hooks)))
        for case in cases:
            h=V/'agent49-rush-h-a';old=h/f'C-{mapper}-{case}-f/binding.json'
            if not old.exists():old=h/f'C-{mapper}-{case}-e/binding.json'
            cfg=read(old)['config'];cfg['hooks']={'MegaAttack':image.hook('MegaAttack','SpecialWeapons')}
            cfg['hooks'].update({n:image.hook(n)for n in ('MegaManRushAttack','MegaManRushBounce','MegaManRushBusterSpawn')});cfg['hooks'].update(isr)
            tasks.append(dict(tag=f'rush-{mapper}-{case}',mapper=mapper,family='rush',config=cfg,parent_binding_sha256=sha(old)))

    def native(t):
        dest=O/t['tag'];dest.mkdir();out=dest/'native-output';out.mkdir()
        h=V/('agent49-super-arm-h-a'if t['family']=='arm'else'agent49-rush-h-a')
        cfg=t['config'];cfg['out']=out.as_posix()+'/'
        caller=h/('caller_m.lua'if t['family']=='arm'else'caller_e.lua');core=h/'witness_f.lua'
        wrapper=dest/'component.lua'
        wrapper.write_text('CFG='+im.lua(cfg)+'\ndofile('+im.lua((R/'tests/menu-bootstrap.lua').as_posix())+')\ndofile('+im.lua(caller.as_posix())+')\ndofile('+im.lua(core.as_posix())+')\n')
        rom=C/f'build/smb-crossover-{t["mapper"]}.nes'
        binding=dict(t,image='candidate',ROM_sha256=sha(rom),core_sha256=sha(core),caller_sha256=sha(caller),wrapper_sha256=sha(wrapper),scope='Authored component arena with real mature-pickup, Select/B and real native contacts. No ordinary route claim.')
        (dest/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
        cmd=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(dest/'host-output'),str(wrapper),str(rom),'--timeout','180']
        with(dest/'host.log').open('wb')as f:z=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
        result=dict(tag=t['tag'],mapper=t['mapper'],family=t['family'],exit=z.returncode,ROM_sha256=sha(rom),binding_sha256=sha(dest/'binding.json'))
        print('NATIVE',t['tag'],z.returncode,flush=True);return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(native,tasks))
    (O/'native.json').write_text(json.dumps(results,indent=2)+'\n')
    assert all(z['exit']==0 for z in results),'Retain native failures before caller review'
    # Keep oracle and execution comparisons byte-literal; rebind folders only.
    for z in results:
        h=V/('agent49-super-arm-h-a'if z['family']=='arm'else'agent49-rush-h-a')
        original=h/('review_callers_j.py'if z['family']=='arm'else'review_h.py')
        code=original.read_text();anchor='H=Path(__file__).resolve().parent;R=H.parents[2]';assert code.count(anchor)==1
        code=code.replace(anchor,anchor+'\nH=ROOT_NATIVE')
        if z['family']=='arm':
            old='rom=(H/\'source-b/build\'if binding[\'image\']==\'candidate\'else R/\'build/checkpoints/roster-audit-v49-samus-audio-scan-h\')/f"smb-crossover-{binding[\'mapper\']}.nes"'
        else:old='rom=H/f"source-c/build/smb-crossover-{binding[\'mapper\']}.nes"'
        assert code.count(old)==1,old
        code=code.replace(old,'rom=ROOT_SOURCE/f"build/smb-crossover-{binding[\'mapper\']}.nes"')
        if not(O/(z['family']+'-review-bound.py.txt')).exists():(O/(z['family']+'-review-bound.py.txt')).write_text(code)
        previous=sys.argv;sys.argv=[str(original),'--tag',z['tag'],'--suffix',z['tag']];stream=io.StringIO()
        try:
            with contextlib.redirect_stdout(stream):exec(compile(code,str(original),'exec'),{'__name__':'__main__','__file__':str(original),'ROOT_NATIVE':O,'ROOT_SOURCE':C})
        finally:sys.argv=previous;(O/(z['tag']+'-review.log')).write_text(stream.getvalue())
        review=read(O/f'caller-review-{z["tag"]}.json');assert review['status'].startswith('PASS_')
        z['exact_native_callers']=len(review['calls']);z['caller_review_sha256']=sha(O/f'caller-review-{z["tag"]}.json')
        print('CALLERS',z['tag'],len(review['calls']),flush=True)
    (O/'summary.json').write_text(json.dumps(dict(passed=True,cases=results,total_exact_callers=sum(z['exact_native_callers']for z in results),candidate_build_sha256=sha(C.parent/'build.json'),script_sha256=sha(__file__),goal_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
