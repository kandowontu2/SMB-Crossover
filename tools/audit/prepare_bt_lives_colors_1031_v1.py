"""BT-only late lives palette source repair on immutable CF67 child."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys, traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/contra-force-p1-coherent-cart-v2';Q=R/'build/bt-ready-menu-1031-v2'
O=R/'build/bt-lives-colors-source-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')
def rt(s):
    for p in [P/'joint',Q/'joint']:
        s=s.replace(str(p),str(J)).replace(p.as_posix(),J.as_posix())
    return s
def run(label,cmd):
    guard=validate(cmd,J,cwd=R)
    for x in guard['outputs']:Path(x['path']).parent.mkdir(parents=True,exist_ok=True)
    z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    save(O/(label+'.json'),dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr))
    assert z.returncode==0,(label,z.stderr)
def main():
    assert not O.exists();O.mkdir()
    try:
        stage=json.loads((P/'source-stage.json').read_text())
        assert stage['candidate']==sha(P/'joint/candidate.nes')=='fbbc7b892e22f5bf808e74a04cbe9f2220f245dbd3e097994775a78d4a27fa08'
        for n,h in stage['bindings'].items():assert sha(n)==h,n
        shutil.copytree(P/'joint',J)
        # The coherent CF child reuses root's real BT object producers.
        # Copy their exact source inputs, rather than inheriting stale aliases.
        for n in ['api.s','loader.s','stream.s','native-constants.inc']:
            src=Q/'joint/bt'/n
            if src.is_file():shutil.copy2(src,J/'bt'/n)
        for p in J.rglob('*'):
            if p.suffix.lower()in['.s','.inc','.cfg']:
                s=p.read_text(encoding='utf-8');t=rt(s)
                if s!=t:write(p,t)
        p=J/'bt/api.s';s=p.read_text(encoding='utf-8')
        old='''BtStatusName:
 cmp #0
 bne BtStatusDone
 php'''
        new='''BtStatusName:
 cmp #0
 beq BtStatusHeader
 cmp #1
 bne BtStatusDone
 cpy #30
 bne BtStatusDone
 ; Genuine WriteGameText A1/Y30 is after the complete native lives packet.
 ; Reapply only own P0/P1 body shades before that packet reaches normal NMI.
 sty VRAM_Buffer1_Offset
 php
 pha
 txa
 pha
 tya
 pha
 jsr BtColors
 pla
 tay
 pla
 tax
 pla
 plp
 rts
BtStatusHeader:
 php'''
        assert s.count(old)==1;write(p,s.replace(old,new,1))
        cmds={}
        for n in ['api','loader','stream']:
            cmds[n]=[rt(x)for x in json.loads((Q/(n+'-build.json')).read_text())['command']]
            run(n+'-build',cmds[n])
        cmd=json.loads((P/'candidate-link.json').read_text())['command']
        cmd=[rt(x)if x.startswith(('-','C:'))and not Path(x).suffix.lower()=='.o' else x for x in cmd]
        # Reuse every genuine current CF/FF/other object; replace ONLY own3.
        for i,x in enumerate(cmd):
            if Path(x).suffix.lower()=='.o' and Path(x).parent.name=='bt' and Path(x).stem in cmds:
                cmd[i]=str(J/'bt'/Path(x).name)
        cfg=J/'candidate.cfg';cmd[cmd.index('-C')+1]=str(cfg)
        # All direct sideoutputs in the copied config are private by rt.
        run('initial-link',cmd)
        cache_paths=[Path(x['path'])for x in validate(cmd,J,cwd=R)['outputs']if x['kind']=='MEMORY file'and 'cache.bin'in x['path']]
        assert len(cache_paths)==1
        cache=cache_paths[0].read_bytes();assert len(cache)==8192 and cache[0x1fe0:0x1ff0]==bytes(16)
        cookie=bytes([167,33,1,117])+hashlib.sha256(cache).digest()[:12]
        for n in ['cache.bin','stream.bin']:(J/'bt'/n).write_bytes(cache)
        (J/'bt/cookie.bin').write_bytes(cookie)
        for n in ['loader','stream']:run(n+'-final-build',cmds[n])
        run('final-link',cmd);prepare(R,J/'candidate.nes')
        old,new=[scoped_load(p/'candidate.nes')for p in[P/'joint',J]]
        assert old['raw'][:16]==new['raw'][:16]
        # No native/module ABI or public PC change; only append private cache code.
        for n,s in old['syms'].items():
            if n not in new['syms']or 'seg'not in s:continue
            if n.startswith('BtStatus'):continue
            assert(address(old,n),location(old,n))==(address(new,n),location(new,n)),n
        changed=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
        allowed=[(location(new,'BtCheck'),477),(16+1048576+919*1024,8192)]
        # The stream starts CHR919; derive its true emitted segment below.
        stream=next(g for g in new['segs'].values()if g['name']=='"BT_STREAM"')
        allowed[1]=(int(stream['ooffs'],0),int(stream['size'],0))
        assert all(any(a<=i<a+n for a,n in allowed)for i in changed),[i for i in changed if not any(a<=i<a+n for a,n in allowed)][:20]
        paths=[Path(__file__),P/'source-stage.json',P/'candidate-link.json',Q/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',cfg,
            *[J/'bt'/n for n in ['api.s','api.o','api.dep','loader.s','loader.o','loader.dep','stream.s','stream.o','stream.dep','cache.bin','cookie.bin']],*O.glob('*-build.json'),O/'initial-link.json',O/'final-link.json']
        save(O/'source-stage.json',dict(source=True,native=False,installed=False,candidate=sha(J/'candidate.nes'),parent=stage['candidate'],
            root_native_negative_parent=Q.as_posix(),repair='Own typed A1/Y30 late lives colors; source/native AXYP restored after genuine BtColors.',
            BT_cookie=cookie.hex(),changed_ROM_bytes=len(changed),allowed_envelopes=allowed,
            public_PCs_preserved=True,all_other_ROM_CHR_header_exact=True,CF_pending=True,
            retained_limitation='Two-player native CheckPlayerName still overwrites first5 header letters; no X/global-state trick applied.',
            bindings={str(p.resolve()):sha(p)for p in paths}))
        print(json.dumps(dict(source=True,native=False,candidate=sha(J/'candidate.nes'),changed=len(changed),cookie=cookie.hex())),flush=True)
    except Exception as e:
        save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
