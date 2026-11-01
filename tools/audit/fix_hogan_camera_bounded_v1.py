"""Publish Hogan's pre-step camera position in his own granted resident code."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/hogan-current';W=R/'build/wwf-hogan-natural-source-v15';O=R/'build/hogan-adapter'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='656212fafe13f070807049cce8cc188403677a6b6cb35d68261706ac10897b56'
    source=(W/'joint/runtime.s').read_text()
    old=' jsr WfDetachRuntime\n WfFar PlayerPhysicsSub'
    assert source.count(old)==1
    source=source.replace('.import CurrentOAMOffset','.import Player_Pos_ForScroll\n.import CurrentOAMOffset',1)
    source=source.replace(old,''' jsr WfDetachRuntime
 ; Raw29 is outside the old generic13..27 camera publisher. Retain the
 ; same pre-step sample and preserve all input flags/A for native physics.
 php
 pha
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 pla
 plp
 WfFar PlayerPhysicsSub''',1)
    (O/'runtime.s').write_text(source,encoding='utf-8',newline='\n')
    cmd=json.loads((W/'runtime-build.json').read_text())['command'][:]
    for i,x in enumerate(cmd):
        if x==str(W/'joint/runtime.s'):cmd[i]=str(O/'runtime.s')
    for flag,n in [('-o','runtime.o'),('-l','runtime.lst'),('--create-dep','runtime.dep'),('--create-full-dep','runtime.dep')]:
        if flag in cmd:cmd[cmd.index(flag)+1]=str(O/n)
    def run(name,command):
        guard=validate(command,O,cwd=R)
        for x in guard['outputs']:Path(x['path']).parent.mkdir(parents=True,exist_ok=True)
        q=subprocess.run(command,cwd=R,capture_output=True,text=True)
        (O/(name+'.json')).write_text(json.dumps(dict(command=command,guard=guard,returncode=q.returncode,stderr=q.stderr),indent=2)+'\n')
        assert q.returncode==0,q.stderr
    run('runtime-build',cmd)
    cfg=(P/'candidate.cfg').read_text();counter=0
    def redirect(m):
        nonlocal counter
        if m[1]in['','%O']:return m[0]
        counter+=1
        return 'file="'+(O/'sideoutputs'/(f'{counter:03d}-'+Path(m[1]).name)).as_posix()+'"'
    cfg=re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,cfg)
    (O/'candidate.cfg').write_text(cfg,encoding='utf-8')
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    assert str(W/'joint/runtime.o')in link
    link[link.index(str(W/'joint/runtime.o'))]=str(O/'runtime.o')
    for flag,n in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
        if flag in link:link[link.index(flag)+1]=str(O/n)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    run('provisional-link',link)
    # The resident insertion moves real imported targets used by the selected
    # C2 image. Rebuild its carrier and BOTH expected-cookie consumers from
    # actual final-link images rather than retaining the old cached operands.
    images=[];cache_changes={}
    for n in ['final-a1.bin','final-c2.bin','final-a3.bin']:
        oldfiles=[p for p in(P/'sideoutputs').iterdir()if p.name.endswith(n)]
        newfiles=[p for p in(O/'sideoutputs').iterdir()if p.name.endswith(n)]
        assert len(oldfiles)==len(newfiles)==1
        oldimage=oldfiles[0].read_bytes();image=newfiles[0].read_bytes();assert len(image)==8192
        images.append(image);cache_changes[n]=sum(a!=z for a,z in zip(oldimage,image))
    template=b''.join(images);(O/'template.bin').write_bytes(template)
    art=(W/'joint/hogan-body.chr').read_bytes()
    cookie=bytes([167,29,0,1])+hashlib.sha256(template+art).digest()[:12]
    (O/'cookie.bin').write_bytes(cookie)
    for name in ['owner','expected','stream']:
        text=(W/'joint'/(name+'.s')).read_text()
        for leaf in ['cookie.bin','template.bin']:
            text=text.replace((W/'joint'/leaf).as_posix(),(O/leaf).as_posix())
        (O/(name+'.s')).write_text(text,encoding='utf-8')
        command=json.loads((W/(name+'-build.json')).read_text())['command'][:]
        command[command.index(str(W/'joint'/(name+'.s')))]=str(O/(name+'.s'))
        for flag,leaf in [('-o',name+'.o'),('-l',name+'.lst'),('--create-dep',name+'.dep'),('--create-full-dep',name+'.dep')]:
            if flag in command:command[command.index(flag)+1]=str(O/leaf)
        run(name+'-build',command)
        link[link.index(str(W/'joint'/(name+'.o')))]=str(O/(name+'.o'))
    run('final-link',link);prepare(R,O/'candidate.nes')
    for i,n in enumerate(['final-a1.bin','final-c2.bin','final-a3.bin']):
        assert next(p for p in(O/'sideoutputs').iterdir()if p.name.endswith(n)).read_bytes()==images[i]
    old,new=scoped_load(P/'candidate.nes'),scoped_load(O/'candidate.nes')
    abi=native_abi(new)
    for n in ['GameLoop','ScrollHandler','MenuResolveCharacter','InitScreen','BtRouter','FwNativeDrawAll','WfMovement']:
        assert address(old,n)==address(new,n),n
    assert old['raw'][1048592:1048592+629*1024]==new['raw'][1048592:1048592+629*1024]
    assert old['raw'][1048592+653*1024:]==new['raw'][1048592+653*1024:]
    assert new['raw'][1048592+629*1024:1048592+653*1024]==template
    for n in ['WfExpectedCookie','WfCookieC']:
        at=location(new,n);assert new['raw'][at:at+16]==cookie,n
    refs=[Path(__file__),W/'joint/runtime.s',W/'runtime-build.json',P/'source-stage.json',P/'final-link.json',P/'candidate.cfg']
    refs +=[Path(p)for p in link if p.endswith('.o')]
    refs +=[p for p in O.rglob('*')if p.is_file()]
    q=dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),
           repair='Own raw29 pre-step Player_Pos_ForScroll publication, preserving A/P and leaving native ScrollHandler once-per-Main.',
           selected_cache_rebuilt_from_actual_link=True,selected_cache_changed_bytes=cache_changes,cookie=list(cookie),all_non_WWF_cache_CHR_exact=True,native_imports_checked=len(abi),
           limits='Source link only. Recheck whole Main/native camera and investigate captured intermediate-screen scroll before installation.',
           bindings={str(p.resolve()):sha(p)for p in refs})
    (O/'source-stage.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','candidate','selected_cache_changed_bytes','native_imports_checked']}))


if __name__=='__main__':main()
