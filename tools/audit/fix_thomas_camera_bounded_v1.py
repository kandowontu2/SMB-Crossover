"""Separate the omitted Kung Fu corridor bounds from SMB's real camera/world."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/thomas-natural-host-1031-v6';O=R/'build/thomas-adapter'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='3fe8683284193f311aecde19290ad507f80283cf12c82ce27efea3b64c995527'
    def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)
    boundary=(P/'source/boundary.s').read_text()
    boundary='.import Player_X_Scroll,ThomasOriginal_811D\n'+boundary
    boundary=once(boundary,' jsr ThomasHostImportX\n tsx',''' jsr ThomasHostImportX
 ; SMB owns the terrain/camera/end point. The omitted Kung Fu corridor's
 ; remaining-distance accumulator otherwise reaches its old144px limit
 ; after48px because host worldX replaced the donor worldX at import.
 ; Rebase that level-owned input at its genuine interior cold anchor.
 ; Keep the donor actor instructions, speed, jump table and attacks intact.
 lda ThomasOriginal_811D
 sta ThomasState+$64
 tsx''')
    boundary=once(boundary,' sta Player_X_Speed\n lda Player_Y_Position',' sta Player_X_Speed\n sta Player_X_Scroll       ; actual signed pixel displacement for native ScrollHandler\n lda Player_Y_Position')
    cache=(P/'source/cache.s').read_text()
    cache='.import Player_Pos_ForScroll\n'+cache
    cache=once(cache,' jsr ThEnsure\n bcc ThNaturalMoveDone\n lda Player_Y_Speed',''' jsr ThEnsure
 bcc ThNaturalMoveDone
 ; Raw10 bypasses the generic13..27 pre-step camera publisher.
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
 lda Player_Y_Speed''')
    for name,text in [('boundary',boundary),('cache',cache)]:
        (O/(name+'.s')).write_text(text,encoding='utf-8',newline='\n')
    cc=R/'tools/Windows/cc65/bin'
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for q in guard['outputs']:Path(q['path']).parent.mkdir(parents=True,exist_ok=True)
        q=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=q.returncode,stderr=q.stderr))
        assert q.returncode==0,q.stderr
    def asm(name):
        run(name+'-build',[cc/'ca65.exe',O/(name+'.s'),'-I',O,'-I',P/'source','-g','-o',O/(name+'.o'),'--create-full-dep',O/(name+'.dep')])
    asm('boundary');asm('cache')
    cfg=(P/'candidate.cfg').read_text();count=0;outputs={}
    def redirect(m):
        nonlocal count
        if m[1]in['','%O']:return m[0]
        count+=1;p=O/'sideoutputs'/(f'{count:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=p
        return 'file="'+p.as_posix()+'"'
    cfg=re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,cfg);(O/'candidate.cfg').write_text(cfg)
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for n in ['boundary','cache']:link[link.index(str(P/(n+'.o')))]=str(O/(n+'.o'))
    for flag,name in [('-C','candidate.cfg'),('-Ln','candidate.lbl'),('-o','candidate.nes'),('-m','candidate.map')]:
        if flag in link:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    run('provisional-link',link)
    kernel=outputs['kernel.bin'].read_bytes();state=outputs['state.bin'].read_bytes()
    b=scoped_load(O/'candidate.nes');assert address(b,'ThAllKernelEnd')-0xa000<=6144
    assert len(kernel)==len(state)==8192
    cookie=bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12]
    (O/'cookie.bin').write_bytes(cookie)
    oldbody=P/'source/carrier.chr'
    oldcarrier=oldbody.read_bytes();assert len(oldcarrier)==16384
    # Keep the actual parent's complete art/padding tail, without recovering
    # another historical copy of the identical body input.
    body=oldcarrier[8192:];carrier=kernel[:6144]+state[0x1000:0x1800]+body
    assert len(carrier)<=16384
    (O/'carrier.chr').write_bytes(carrier+bytes(16384-len(carrier)))
    for name in ['resident','carrier']:
        (O/(name+'.s')).write_text((P/'source'/(name+'.s')).read_text())
        asm(name);link[link.index(str(P/(name+'.o')))]=str(O/(name+'.o'))
    run('final-link',link)
    assert outputs['kernel.bin'].read_bytes()==kernel and outputs['state.bin'].read_bytes()==state
    old,new=scoped_load(P/'candidate.nes'),scoped_load(O/'candidate.nes')
    for n in ['GameLoop','X5OwnMovement','ThServiceVeneers','ThLoad','ThCheckCode','ThGmHeadWithinOwn','ThArExtended','BwServiceVeneers','BtServiceVeneers']:
        assert address(old,n)==address(new,n),n
    # The original actor is the SAME linked object; only the host boundary and
    # cache changed. Its constants are authentic source, not invented speeds.
    at=address(new,'ThomasOriginal_811D')-0xa000;assert kernel[at]==192
    assert old['raw'][16+127*8192:16+128*8192]==new['raw'][16+127*8192:16+128*8192]
    chrbase=1048592
    assert old['raw'][chrbase:chrbase+426*1024]==new['raw'][chrbase:chrbase+426*1024]
    assert old['raw'][chrbase+442*1024:]==new['raw'][chrbase+442*1024:]
    assert new['raw'][chrbase+426*1024:chrbase+442*1024]==(O/'carrier.chr').read_bytes()
    at=location(new,'ThCookie');assert new['raw'][at:at+16]==cookie
    refs={Path(__file__),P/'source-stage.json',P/'source/boundary.s',P/'source/cache.s',P/'final-link.json',P/'component.o',oldbody}
    refs|={Path(p)for p in link if p.endswith('.o')}
    refs|={p for p in O.rglob('*')if p.is_file()}
    q=dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),
           kernel_bytes=address(new,'ThAllKernelEnd')-0xa000,resident_bytes=address(new,'ThAllResidentEnd')-0xb33a,
           donor_actor_object_unchanged=True,adaptation='Native pre-step scroll position plus actual pixel displacement; omitted donor corridor distance rebased to its genuine interior cold anchor. SMB owns terrain, stage bounds and end lock.',
           limits=['Source link only; natural Main, reference actor and native validation pending','Original27px jump retained; pipe feasibility unresolved','Private Thomas parent, not composed into the installed74-character cartridge'],
           bindings={str(p.resolve()):sha(p)for p in refs})
    save(O/'source-stage.json',q)
    print(json.dumps({k:q[k]for k in ['passed','candidate','kernel_bytes','resident_bytes']}))


if __name__=='__main__':main()
