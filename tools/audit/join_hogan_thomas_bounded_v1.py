"""Compose both native-tested owners onto the current nightly as linked source."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
H=R/'build/hogan-adapter';HM=R/'build/hogan-current';T=R/'build/thomas-platform-chr'
TM=R/'build/thomas-native-render';TW=R/'build/thomas-natural-host-1031-v6'
HW=R/'build/wwf-hogan-natural-source-v15';O=R/'build/hogan-thomas-current'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(H/'candidate.nes')=='4acfe759b13a9dd7749fb24522f94d2e47267c24a367c294fff361ea6c1f6f2d'
    assert sha(T/'candidate.nes')=='5471f6333b02f786ccb6009b20ed49568772385692ceedef9062b4fb3f8e0262'
    refs={Path(__file__),H/'candidate.nes',T/'candidate.nes',H/'final-link.json',T/'final-link.json'}
    def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
    def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for x in guard['outputs']:Path(x['path']).parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr))
        assert result.returncode==0,result.stderr
    cc=R/'tools/Windows/cc65/bin'
    def asm(name,includes):run(name+'-build',[cc/'ca65.exe',O/(name+'.s'),*[x for p in includes for x in ['-I',p]],'-g','-o',O/(name+'.o'),'--create-full-dep',O/(name+'.dep')])
    # Main keeps the Thomas body/terrain admission and the current WWF/CF menu.
    entry=(TM/'entrypoint.s').read_text()+'\n.export ImposeGravitySprObj,VerticalForceDown,PlayerPhysicsSub,Sprite_Data,SprObject_SprAttrib,PlayerHeadWithinTerrain,BlankPalette\n.import WfScene,WfMenuRetire\n'
    write(O/'entrypoint.s',entry);refs.add(TM/'entrypoint.s')
    for name in ['megaman_environment.s','kirby.s','kirby_draw.s','x5_bounce.s','hot_render_gate.s','new_roster_dispatch.s','screen_render.s']:
        source=TW/'source'/name;write(O/'src'/name,source.read_text());refs.add(source)
    source=TW/'source/character_select.s'
    text=once(source.read_text(),'farcall CfRetire','farcall WfMenuRetire')
    write(O/'src/character_select.s',text);refs.add(source)
    source=HM/'src/full_roster_menu.s'
    text=once(source.read_text(),' lda #32\n sec\n rts',' lda #32\n clc\n rts')
    write(O/'src/full_roster_menu.s',text);refs.add(source)
    for name in ['cf_menu_body.inc','full_roster_menu_art.inc']:
        source=HM/'src'/name;write(O/'src'/name,source.read_text());refs.add(source)
    write(O/'src/inventory.s',(TM/'inventory.s').read_text());refs.add(TM/'inventory.s')
    command=json.loads((TM/'main-build.json').read_text())['command'][:]
    command[1:1]=['-I',str(O/'src'),'-I',str(O)]
    source=next(p for p in command if p.endswith('entrypoint.s'));command[command.index(source)]=str(O/'entrypoint.s')
    for flag,name in [('-o','main.o'),('-l','main.lst'),('--create-full-dep','main.dep')]:
        if flag in command:command[command.index(flag)+1]=str(O/name)
    fingerprint=O/'main-inputs.json'
    if fingerprint.exists():
        previous=json.loads(fingerprint.read_text())
        assert previous['command']==command and sha(O/'main.o')==previous['object_sha256']
        for p,h in previous['inputs'].items():assert sha(p)==h,p
    else:
        run('main-build',command)
        dep=(O/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
        inputs={Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',dep)if x}
        save(fingerprint,dict(command=command,object_sha256=sha(O/'main.o'),inputs={str(p):sha(p)for p in inputs}))
    # The compact WWF range classifier is3bytes shorter than Thomas's old
    # explicit27/31/33 list. Preserve the funded Thomas transport and Arthur
    # helper, the public HuResolve suffix and both new owner classifications.
    source=TW/'source/union.s';union=source.read_text();refs.add(source)
    before=''' cmp #27
 beq HuExtendedShared
 cmp #31
 beq HuExtendedShared
 cmp #33
 bne HuExtendedNotShared
HuExtendedShared:
 jmp HuExtendedBT'''
    after=''' cmp #27
 bcc HuExtendedNotShared
 cmp #34
 bcs HuExtendedNotShared
 cmp #28
 beq DK
 cmp #30
 beq Fetch
 jmp HuExtendedBT'''
    union=once(union,before,after)
    # DK was classified above, so its second test in Other is redundant.
    union=once(union,'Other:\n cmp #28\n beq DK\n cmp #24','Other:\n cmp #24')
    write(O/'union.s',union)
    cmd=json.loads((HM/'union-build.json').read_text())['command'][:]
    source=next(p for p in cmd if p.endswith('union.s'));cmd[cmd.index(source)]=str(O/'union.s')
    cmd[1:1]=['-I',str(O),'-I',str(TW/'source')]
    for flag,name in [('-o','union.o'),('--create-full-dep','union.dep'),('--create-dep','union.dep'),('-l','union.lst')]:
        if flag in cmd:cmd[cmd.index(flag)+1]=str(O/name)
    run('union-build',cmd)
    # This source-equivalent nested scene chain visits both owners. Its own
    # load predicate prevents a Thomas copy for any foreign selection.
    resident=(T/'resident.s').read_text()
    resident='.import WfScene\n'+once(resident,'ThSceneInit:\n ThFar BwScene,jsr','ThSceneInit:\n ThFar WfScene,jsr')
    write(O/'th-resident.s',resident);refs.add(T/'resident.s')
    for leaf in ['cookie.bin','native-background-colors.bin']:(O/leaf).write_bytes((T/leaf).read_bytes())
    write(O/'th-carrier.s',(T/'carrier.s').read_text());(O/'carrier.chr').write_bytes((T/'carrier.chr').read_bytes())
    asm('th-resident',[O,TW/'source']);asm('th-carrier',[O,TW/'source'])
    # Add only the previously granted Thomas regions to the current layout.
    cfg=(H/'candidate.cfg').read_text();tcfg=(T/'candidate.cfg').read_text()
    memories=dict(re.findall(r'\b(TH_\w+)\s*:([^;]*);',tcfg.split('SEGMENTS {',1)[0]))
    segments=dict(re.findall(r'\b(THOMAS_\w+)\s*:([^;]*);',tcfg.split('SEGMENTS {',1)[1]))
    assert len(segments)==4
    cfg,count=re.subn(r'X5_NEW_55\s*:[^;]+;',
        'X5_NEW_55:start=$c000,size=$133a,type=ro,file=%O,fill=yes,fillval=$ff,bank=$55;\n'+
        'TH_RES_LOAD:'+memories['TH_RES_LOAD']+';\nTH_55_POST:'+memories['TH_55_POST']+';',cfg)
    assert count==1
    cfg=once(cfg,'ROGUE_AUDIO_PAGES_1: load=X5_NEW_55','ROGUE_AUDIO_PAGES_1: load=TH_55_POST')
    cfg,count=re.subn(r'CD_CHR_MEM\s*:[^;]+;',
        'CD_CHR_MEM:start=$67000,size=$3800,type=ro,file=%O,fill=yes,fillval=0;\n'+
        'TH_CHR_MEM:'+memories['TH_CHR_MEM']+';\nCD_CHR_POST:'+re.search(r'\bCD_CHR_POST\s*:([^;]*);',tcfg)[1]+';',cfg)
    assert count==1
    cfg=once(cfg,'MEMORY {','MEMORY {\n'+''.join(n+':'+memories[n]+';\n'for n in ['TH_RES_RUN','TH_KERNEL_MEM','TH_STATE_MEM']))
    cfg=once(cfg,'SEGMENTS {','SEGMENTS {\n'+''.join(n+':'+s+';\n'for n,s in segments.items()))
    outputs={};counter=0
    def redirect(m):
        nonlocal counter
        if m[1]in['','%O']:return m[0]
        counter+=1;target=O/'sideoutputs'/(f'{counter:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=target
        return 'file="'+target.as_posix()+'"'
    write(O/'candidate.cfg',re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,cfg))
    link=json.loads((H/'final-link.json').read_text())['command'][:]
    for old,new in [(HM/'main.o',O/'main.o'),(HM/'union.o',O/'union.o')]:link[link.index(str(old))]=str(new)
    th_link=json.loads((T/'final-link.json').read_text())['command']
    own=[p for p in th_link if p.endswith('.o')and 'thomas-'in p and Path(p).name not in ['main.o','union.o','dmc-clones.o','mirror.o','bt-api.o','bt-loader.o','bt-stream.o']]
    assert len(own)==10
    own=[str(O/'th-resident.o')if p==str(T/'resident.o')else str(O/'th-carrier.o')if p==str(T/'carrier.o')else p for p in own]
    link+=own
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
        if flag in link:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    def linked(tag):
        run(tag+'-link',link);path=O/'candidate.dbg';data=path.read_bytes();keep={'version','info','file','lib','mod','seg','scope','sym'}
        path.write_bytes(b''.join(s for s in data.splitlines(keepends=True)if s.split(b'\t',1)[0].decode('ascii')in keep))
        save(O/(tag+'-debug-format.json'),dict(full_bytes=len(data),full_sha256=hashlib.sha256(data).hexdigest(),compact_bytes=path.stat().st_size,compact_sha256=sha(path)))
    linked('provisional')
    def image(name):return next(p for n,p in outputs.items()if n.endswith(name)).read_bytes()
    kernel,state=image('kernel.bin'),image('state.bin')
    assert len(kernel)==len(state)==8192
    (O/'cookie.bin').write_bytes(bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12])
    (O/'carrier.chr').write_bytes(kernel[:6144]+state[0x1000:0x1800]+(T/'carrier.chr').read_bytes()[8192:])
    asm('th-resident',[O,TW/'source']);asm('th-carrier',[O,TW/'source'])
    images=[image(n)for n in ['final-a1.bin','final-c2.bin','final-a3.bin']]
    template=b''.join(images);(O/'wf-template.bin').write_bytes(template)
    art=(HW/'joint/hogan-body.chr').read_bytes()
    (O/'wf-cookie.bin').write_bytes(bytes([167,29,0,1])+hashlib.sha256(template+art).digest()[:12])
    for name in ['owner','expected','stream']:
        text=(H/(name+'.s')).read_text()
        text=text.replace((H/'cookie.bin').as_posix(),(O/'wf-cookie.bin').as_posix()).replace((H/'template.bin').as_posix(),(O/'wf-template.bin').as_posix())
        write(O/('wf-'+name+'.s'),text)
        cmd=json.loads((H/(name+'-build.json')).read_text())['command'][:]
        source=next(p for p in cmd if p.endswith('.s'));cmd[cmd.index(source)]=str(O/('wf-'+name+'.s'))
        for flag,leaf in [('-o','wf-'+name+'.o'),('-l','wf-'+name+'.lst'),('--create-full-dep','wf-'+name+'.dep'),('--create-dep','wf-'+name+'.dep')]:
            if flag in cmd:cmd[cmd.index(flag)+1]=str(O/leaf)
        run('wf-'+name+'-build',cmd);link[link.index(str(H/(name+'.o')))]=str(O/('wf-'+name+'.o'))
    linked('final');prepare(R,O/'candidate.nes')
    assert kernel==image('kernel.bin')and state==image('state.bin')
    assert images==[image(n)for n in ['final-a1.bin','final-c2.bin','final-a3.bin']]
    old,new=scoped_load(H/'candidate.nes'),scoped_load(O/'candidate.nes')
    old_abi,new_abi=native_abi(old),native_abi(new);assert old_abi==new_abi,'Rebuild CF if its true native ABI changes'
    # CHR is byte-identical outside the two explicitly rebuilt cache grants.
    raw=new['raw'];base=old['raw'];allowed=[(426,442),(629,653)]
    assert all(a==z or any(1048592+lo*1024<=i<1048592+hi*1024 for lo,hi in allowed)for i,(a,z)in enumerate(zip(base,raw))if i>=1048592)
    assert address(new,'ThAllKernelEnd')-0xa000<=6144 and address(new,'ThAllResidentEnd')<=0xb900
    for n in ['GameLoop','MenuResolveCharacter','InitScreen','FmPending','HuEntryBase','BtRouter','FwNativeDrawAll']:
        assert address(old,n)==address(new,n),n
    th_bundle=scoped_load(T/'candidate.nes')
    for n in ['GmOnlyCommon','HuResolve']:
        assert address(new,n)==address(th_bundle,n),'Use the actual funded Thomas private-entry layout: '+n
    dep=(O/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs|={Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',dep)if x}
    refs|={Path(p)for p in link if p.endswith('.o')};refs|={p for p in O.rglob('*')if p.is_file()}
    save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),
        Hogan_parent=sha(H/'candidate.nes'),Thomas_parent=sha(T/'candidate.nes'),private_playable=76,
        native_CF_imports_exact=len(new_abi),both_cache_images_rebuilt_from_actual_link=True,
        limits=['Needs exact combined-ROM menu/cache-transition/native gameplay qualification before nightly delivery','No full1-1/all-powerup/original-audio completion claim'],
        bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(candidate=sha(O/'candidate.nes'),private_playable=76,CF_native_imports_exact=len(new_abi))))


if __name__=='__main__':main()
