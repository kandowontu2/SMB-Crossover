"""Use exactly four old capsule padding bytes for typed raw32/33 ingress."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/battletoads-current64-transport-v1';O=R/'build/battletoads-current64-only-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def command(c,n):
    v=validate(c,J,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True)
    write(O/(n+'.json'),json.dumps(dict(command=c,validated_outputs=v,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n')
    assert z.returncode==0,(n,z.stderr)
def main():
    assert not O.exists();assert json.loads((P/'proposal.json').read_text())['candidate']==sha(P/'joint/candidate.nes')
    shutil.copytree(P/'joint',J,ignore=shutil.ignore_patterns('*.o','candidate.nes','candidate.dbg','candidate.lbl','candidate.map'))
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg']:
            write(p,p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
    p=J/'src/new_roster_dispatch.s';s=p.read_text()
    a=' cmp #32\n beq GmOnlyRare\n';assert s.count(a)==1;s=s.replace(a,' cmp #32\n bcs GmOnlyHigh\n')
    a='::GmOnlyRare:\n jmp HuOnlyRare';assert s.count(a)==1
    s=s.replace(a,'::GmOnlyHigh:\n cmp #34\n bcs GmOnlyLegacy\n'+a)
    a='GmExtraNrWeapons,51,0';assert s.count(a)==1;s=s.replace(a,'GmExtraNrWeapons,55,0')
    lo=s.index('::GmOnlyCommon:');hi=s.index('GmNrRoute NrPortrait',lo)
    s=s[:lo]+s[lo:hi].replace('beq GmOnlyRare','beq GmOnlyHigh')+s[hi:];write(p,s)
    recipe=json.loads((R/'build/benj-menu-unlocked-1030-v3/main-build.json').read_text())['command'][:]
    assert recipe[-1].endswith('entrypoint.s');recipe[-1]=str(J/'entrypoint.s')
    recipe[recipe.index('-o')+1]=str(J/'bt-main.o');recipe[1:1]=['-I',str(J),'-I',str(J/'src')]
    # Dependency outputs in the old command must not retain frozen paths.
    for flag in['--create-dep','--create-full-dep','-l','--listing']:
        if flag in recipe:recipe[recipe.index(flag)+1]=str(J/Path(recipe[recipe.index(flag)+1]).name)
    command(recipe,'main-build')
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for flag in['-o','-Ln','-C','-m','--dbgfile','--mapfile']:
        if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
    if '--ld-args'in link:
        k=link.index('--ld-args')+1;v=link[k].split(',')
        for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
        link[k]=','.join(v)
    old=str(R/'build/benj-menu-unlocked-1030-v3/joint/main.o')
    assert link.count(old)==1;link[link.index(old)]=str(J/'bt-main.o')
    command(link,'final-link');prepare(R,J/'candidate.nes')
    a,b=[load(x/'joint/candidate.nes')for x in[P,O]]
    raw=a['raw'];new=b['raw'];diff=[i for i,(x,y)in enumerate(zip(raw,new))if x!=y]
    allowed=[(location(a,'NrPortrait'),location(a,'NrPortrait')+97),(location(a,'NrWeapons'),location(a,'NrWeapons')+97)]
    assert all(any(lo<=i<hi for lo,hi in allowed)for i in diff),[(hex(i),i//8192)for i in diff[:30]]
    for n in['NrMovement','NrGraphics','NrDraw','NrPortrait','NrWeapons','NrInjury','NrLegacyInjuryStatus','NrDeathStart','NrDeath','NrVisible','NrHead','NrBody','NrAdder','NrBox','NrSide']:
        assert address(a,n)==address(b,n)and location(a,n)==location(b,n)
    # Sole main object's assembly resolves every branch to moved internal Rare.
    q=dict(status='PRIVATE_EXACT_CAPSULE_RAW33_PROPOSAL_NOT_UNLOCKED',candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),
        changed_bytes=len(diff),only_extents='Original NrPortrait/NrWeapons 97B capsules, public starts/ends unchanged',
        oldRare=address(a,'GmOnlyRare'),newRare=address(b,'GmOnlyRare'),
        four_padding_bytes_consumed=True,global_RAM_new_bytes=0,menu_readiness_64_unchanged=True,native=False,
        source_internal_relocation='GmOnlyRare not exported; all actual branch consumers source-reassembled in sole main object; new high guard accepts32/33 and rejects34..255',
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'proposal.json',J/'src/new_roster_dispatch.s',J/'bt-main.o',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg']})
    write(O/'proposal.json',json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
