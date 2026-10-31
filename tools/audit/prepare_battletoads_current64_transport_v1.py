"""Private real-source A79 compaction/raw33 proposal; no menu unlock."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/battletoads-current64-host-v1';O=R/'build/battletoads-current64-transport-v1';J=O/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def command(c,name):
    proof=validate(c,J,cwd=R)
    z=subprocess.run(c,cwd=R,text=True,capture_output=True)
    write(O/(name+'.json'),json.dumps(dict(command=c,validated_outputs=proof,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n')
    assert z.returncode==0,(name,z.stderr)
def main():
    assert not O.exists()
    assert sha(P/'joint/candidate.nes')=='e4adafff0eb89bde3ea9381ec700901734cfcc77d38f178c320c0cf5895f255c'
    b=load(P/'joint/candidate.nes')
    actual=R/'build/benj-menu-unlocked-1030-v3/joint/union.s'
    s=actual.read_text();assert s==(P/'joint/union.s').read_text()
    targets=re.findall(r'<([A-Za-z0-9_]+)',s[s.index('HuLo:'):s.index('HuHi:')]);assert len(targets)==144
    groups={};indices=[]
    for t in targets:
        pair=(address(b,t)>>8,((location(b,t)-16)//8192)|128)
        if pair not in groups:groups[pair]=[t]
        elif t not in groups[pair]:groups[pair].append(t)
        indices.append(list(groups).index(pair))
    reps=[members[0]for members in groups.values()]
    assert len(reps)==46,'Recompute capacity on a genuinely changed source base'
    shutil.copytree(P/'joint',J,ignore=shutil.ignore_patterns('*.o','candidate.nes','candidate.dbg','candidate.lbl','candidate.map'))
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg']:
            write(p,p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
    s=s.replace('.import S2ServiceVeneers,S2BoundaryLateUI','.import S2ServiceVeneers,S2BoundaryLateUI\n.import BtServiceVeneers',1)
    marker=' cmp #32\n jeq HuExtendedArthur\n';assert s.count(marker)==1
    s=s.replace(marker,marker+' cmp #33\n jeq HuExtendedBT\n',1)
    marker=' lda HuHi,y\n sta FarcallJmpTarget_SMC+2\n lda HuBank,y'
    assert s.count(marker)==1
    s=s.replace(marker,' lda HuPairIndex,y\n tay\n lda HuPairHi,y\n sta FarcallJmpTarget_SMC+2\n lda HuPairBank,y',1)
    a=s.index('HuLo:');z=s.index('.export HuResolve',a)
    text='HuLo:\n .byte '+','.join('<'+t for t in targets)+'\n'
    text+='HuPairIndex:\n .byte '+','.join(map(str,indices))+'\n'
    text+='HuPairHi:\n .byte '+','.join('>'+t for t in reps)+'\n'
    text+='HuPairBank:\n .byte '+','.join('.lobyte(.bank('+t+')|$80)'for t in reps)+'\n'
    # Every original target remains a genuine linked expression. The grouping
    # may be regenerated after Benj or any later producer changes its values.
    for i,t in enumerate(targets):
        rep=reps[indices[i]]
        text+=f'.assert >{t} = >{rep},lderror,"Pair high member{i}"\n'
        text+=f'.assert .bank({t})=.bank({rep}),lderror,"Pair bank member{i}"\n'
    text+='''HuExtendedBT:
 lda #>BtServiceVeneers
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BtServiceVeneers)|$80)
 sta NextBank_SMC+1
 cpy #36
 bcc Valid
 ldy #36
Valid:
 tya
 sta FarcallJmpTarget_SMC+1
 asl
 clc
 adc FarcallJmpTarget_SMC+1
 clc
 adc #<BtServiceVeneers
 sta FarcallJmpTarget_SMC+1
 jmp HuCommon::Restore
.assert .lobyte(BtServiceVeneers)+108<256,lderror,"BT full row remains on one page"
'''
    resolve=address(b,'HuResolve');text+=f'.assert *<=${resolve:04x},lderror,"Private table compaction must fund BT without shifting public suffix"\n.res ${resolve-0xb5e0:04x}-(*-HuStart),$ea\n'
    s=s[:a]+text+s[z:];write(J/'union.s',s)
    recipe=json.loads((R/'build/benj-menu-unlocked-1030-v3/union-build.json').read_text())['command'][:]
    assert recipe[-1].endswith('union.s')
    recipe[-1]=str(J/'union.s');recipe[recipe.index('-o')+1]=str(J/'bt-union.o')
    # Copied relative includes stay source-owned in this private tree. Other
    # frozen include roots are read-only and part of the exact prior recipe.
    recipe[1:1]=['-I',str(J),'-I',str(J/'src')]
    command(recipe,'union-build')
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for flag in['-o','-Ln','-C','-m','--dbgfile','--mapfile']:
        if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
    if '--ld-args'in link:
        k=link.index('--ld-args')+1;v=link[k].split(',')
        for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
        link[k]=','.join(v)
    old=str(R/'build/benj-menu-unlocked-1030-v3/joint/consumer-18.o')
    assert link.count(old)==1;link[link.index(old)]=str(J/'bt-union.o')
    command(link,'final-link');prepare(R,J/'candidate.nes')
    new=load(J/'candidate.nes');oldraw=b['raw'];newraw=new['raw']
    diffs=[i for i,(a,z)in enumerate(zip(oldraw,newraw))if a!=z]
    first=16+79*8192+0x15e0;last=16+80*8192
    assert all(first<=i<last for i in diffs)
    exports=re.findall(r'^\.export\s+([^\n]+)',actual.read_text(),re.M)
    exports=[x.strip()for row in exports for x in row.split(',')]
    assert all(address(b,t)==address(new,t)and location(b,t)==location(new,t)for t in exports)
    for i in range(36):
        p=location(b,'HuEntryBase')+i*16
        assert oldraw[p:p+11]==newraw[p:p+11]
    # The only input object changed is the genuine union producer. Its export
    # set contains no table/helper internals, preventing source-link consumers.
    cc=R/'tools/Windows/cc65/bin/od65.exe'
    object_proofs={}
    for name,p in [('old',Path(old)),('new',J/'bt-union.o')]:
        z=subprocess.run([str(cc),'--dump-exports',str(p)],cwd=R,text=True,capture_output=True,check=True)
        write(O/(name+'-exports.txt'),z.stdout);object_proofs[name]=sha(p)
    q=dict(status='SOURCE_LINKED_PRIVATE_TRANSPORT_PROPOSAL_NOT_UNLOCKED',native=False,
        candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),changed_bytes=len(diffs),
        changed_extent='Only existing owned A79 B5E0..<C000',target_members=144,pair_groups=len(groups),
        old_table_bytes=432,new_table_bytes=288+2*len(groups),fetch_growth=4,raw33_growth=41,
        public_prefix_pad_bytes=resolve-address(new,'HuExtendedBT')-34,
        all_public_exports_and_36_original_11B_entry_prologues_exact=True,
        menu_64_readiness_unchanged=True,foreign_rare_fetch_CPU_delta=11,
        later_Benj_composition='Regenerate groups from actual final DBG/source targets; every144 member has linked high/bank assertions',
        groups=[dict(high=pair[0],rawbank=pair[1],representative=members[0],members=members)for pair,members in groups.items()],
        targets=targets,index=indices,object_proofs=object_proofs,
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'source-stage.json',actual,R/'build/benj-menu-unlocked-1030-v3/union-build.json',J/'union.s',J/'private.cfg',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'bt-union.o']})
    write(O/'proposal.json',json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['groups','targets','index','object_proofs','bindings']}))
if __name__=='__main__':main()
