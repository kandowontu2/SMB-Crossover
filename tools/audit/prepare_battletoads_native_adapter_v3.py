"""Source-only real BT/native boundary successor. Cold lifecycle still pending."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from check_tmnt_render_oa import load,address,location
P=R/'build/battletoads-current64-only-v1';O=R/'build/battletoads-native-adapter-v3';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def command(c,n):
    v=validate(c,J,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True)
    write(O/(n+'.json'),json.dumps(dict(command=c,validated_outputs=v,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n')
    assert z.returncode==0,(n,z.stderr)
def main():
    assert not O.exists();assert sha(P/'joint/candidate.nes')=='f6c09690b3060b960eb4fd89d8f4d81f6c45628807180791a6f84cc7685c46d8'
    shutil.copytree(P/'joint',J,ignore=shutil.ignore_patterns('*.o','candidate.nes','candidate.dbg','candidate.lbl','candidate.map'))
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg']:
            write(p,p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
    write(J/'bt/api.s',(R/'tools/audit/battletoads_native_adapter_v2.s').read_text())
    constants=(R/'inc/constants.inc').read_text().splitlines()
    names=['Sfx_PowerUpGrab','Sfx_PipeDown_Injury']
    selected=[l for l in constants if any(l.startswith(n+' ')for n in names)]
    assert len(selected)==2
    write(J/'bt/native-constants.inc','\n'.join(selected)+'\n')
    cc=R/'tools/Windows/cc65/bin'
    def assemble(n):command([str(cc/'ca65.exe'),'-g','-D','MAPPER_MMC5=1','-I',str(R),'-o',str(J/'bt'/f'{n}.o'),str(J/'bt'/f'{n}.s')],n+'-build')
    for n in['api','core','art','loader','router','preview','stream']:assemble(n)
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for flag in['-o','-Ln','-C','-m','--dbgfile','--mapfile']:
        if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
    if '--ld-args'in link:
        k=link.index('--ld-args')+1;v=link[k].split(',')
        for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
        link[k]=','.join(v)
    for n in['api','core','art','loader','router','preview','stream']:
        hit=[i for i,p in enumerate(link)if p.endswith('/bt/'+n+'.o')or p.endswith('\\bt\\'+n+'.o')]
        assert len(hit)==1,(n,hit);link[hit[0]]=str(J/'bt'/f'{n}.o')
    command(link,'initial-link')
    cache=(J/'bt/cache.bin').read_bytes();assert len(cache)==8192 and cache[0x1fe0:0x1ff0]==bytes(16)
    cookie=bytes([0xa7,33,1,117])+hashlib.sha256(cache).digest()[:12]
    (J/'bt/cookie.bin').write_bytes(cookie);(J/'bt/stream.bin').write_bytes(cache)
    assemble('loader');assemble('stream');command(link,'final-link');prepare(R,J/'candidate.nes')
    old,new=[load(x/'joint/candidate.nes')for x in[P,O]]
    diff=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
    spans=[(16+93*8192+0xdc0,16+93*8192+0xfa7),(16+0x100000+919*1024,16+0x100000+927*1024)]
    assert all(any(a<=i<b for a,b in spans)for i in diff)
    for n in['BtServiceVeneers','BtCheck','BtLoad','BtRetire','BtState','BtHostState','BtCacheServices','BtInit','BtPoseIds']:
        assert address(old,n)==address(new,n)
    q=dict(status='SOURCE_LINKED_OWN_NATIVE_BOUNDARIES_PENDING_COLD_AND_HIT_JOIN',native=False,ready=False,
        candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),changed_bytes=len(diff),
        header_current64_menu_readiness_all_foreign_bytes_exact=True,
        source_core_code_bytes=2864,source_state_bytes=117,new_global_RAM0_bytes=0,
        host_code_end=address(new,'BtUnavailable')+2,host_code_limit=0xbee0,
        implemented=['Donor integrator native import/export once','Original source fractional X/jump/gravity','Native real head/side tile probes','Native big-body contact rectangle','Exact source P0/P1 queue without universal writes','Native kernel/sourcepose geometry','Original player-punch profile18 health math','Original food+8/cap2F','Native Star/1up genuine consumer'],
        pending=['Natural ROM Fresh/Reset/cold acquisition chain','Native E2 defeat target join (event recorded/consumed only)','Cold portrait/name/status publication','P1 retirement/menu Start masks','Native firstlook/route'],
        scope='Actual private cache boundary source; no readiness/Main/cold/native qualification from this link',
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/battletoads_native_adapter_v2.s',P/'transport-controls.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'bt/api.s',J/'bt/cache.bin',J/'bt/cookie.bin',J/'bt/stream.bin']})
    write(O/'source-stage.json',json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
