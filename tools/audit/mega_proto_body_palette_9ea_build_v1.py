"""Compile the disjoint, sparse Mega body/Proto palette source union; no native."""
from pathlib import Path
import json,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from current_mega_arsenal_prepare_v1 import sha,EXPECTED
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from check_tmnt_audio_fallback_oc import qualified
from prepare_cv3_dmc_mirror import prepare

R=Path(__file__).resolve().parents[2];B=R/'build';P='mega_proto_body_palette_9ea'
BODY='8fd3f3766486c9d6093c1ebe0cff92b6ff3a35c84829f448c5cbc32b93abbffc'
PALETTE='cb8fce744c3f95aaf11e1e52b605535dce8a301bb7a7ca5d7a73c186c79ebc62'
ORDINARY={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}

def main():
    existing='--qualify-existing'in sys.argv
    parent=B/'bill_early_cache.nes';body=B/'mm_player_prg_owner.nes';palette=B/'proto_normal_palette_ack_9ea.nes'
    assert [sha(x)for x in [parent,body,palette]]==[EXPECTED,BODY,PALETTE]
    bodyproof=B/'mm_player_prg_owner_build.json';bp=json.loads(bodyproof.read_text())
    pp=B/'proto_normal_palette_ack_9ea_build.json';p=json.loads(pp.read_text())
    assert all(sha(q)==v for q,v in p['bindings'].items())
    entry=B/(P+'_entrypoint.s');out=B/(P+'.nes');assert existing==entry.exists()and existing==out.exists()
    source=(B/'mm_player_prg_owner_entrypoint.s').read_bytes();token=b'.include "proto_palette_ack.s"'
    assert source.count(token)==1
    composed=source.replace(token,b'.include "proto_normal_palette_ack_9ea_source.s"')
    if existing:assert entry.read_bytes()==composed
    else:entry.write_bytes(composed)
    watched=[R/'src/entrypoint.s',R/'src/metasprite_engine.s',R/'src/megaman_weapons.s',R/'src/proto_palette_ack.s',R/'smb1base-mmc5-expanded.cfg',B/'smb-crossover-mmc5-expanded.nes',parent,body,palette]
    before={str(q):sha(q)for q in watched}
    def command(output,mapper=None):
        cmd=[];i=0;old=bp['build_command']
        while i<len(old):
            arg=old[i]
            if arg in ['--asm-define','-D']:
                v=old[i+1];name=v.split('=',1)[0]
                if mapper and name=='ENABLE_MMC5_EXPANDED':i+=2;continue
                if mapper and name in ['MAPPER_MMC3','MAPPER_MMC5']:v=name+'='+str(int(name=='MAPPER_'+mapper.upper()))
                cmd.extend([arg,v]);i+=2;continue
            if arg=='-C':cmd.extend([arg,str(R/('smb1base.cfg'if mapper else'smb1base-mmc5-expanded.cfg'))]);i+=2;continue
            if arg=='--ld-args':cmd.extend([arg,'--dbgfile,'+str(output.with_suffix('.dbg'))]);i+=2;continue
            if arg in ['-m','-Ln','-o']:
                cmd.extend([arg,str(output.with_suffix({'-m':'.map','-Ln':'.lbl','-o':'.nes'}[arg]))]);i+=2;continue
            cmd.append(str(entry)if arg==str(B/'mm_player_prg_owner_entrypoint.s')else arg);i+=1
        assert cmd[-1]==str(entry)
        if existing and not mapper:return cmd # Qualify the real already-emitted linked image; never edit DBG.
        run=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        output.with_suffix('.build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
        if not mapper:prepare(R,output)
        return cmd
    cmd=command(out);old=scoped_load(parent);new=scoped_load(out)
    raw=parent.read_bytes();br=body.read_bytes();pr=palette.read_bytes();nr=out.read_bytes()
    bd={i for i,(x,y)in enumerate(zip(raw,br))if x!=y};pd={i for i,(x,y)in enumerate(zip(raw,pr))if x!=y}
    assert len(raw)==len(nr)==len(br)==len(pr)and len(bd)==34 and len(pd)==24 and not bd&pd
    expected=bytearray(raw)
    for i in bd:expected[i]=br[i]
    for i in pd:expected[i]=pr[i]
    assert nr==expected and {(i-16)//8192 for i in bd}=={4}and {(i-16)//8192 for i in pd}=={66}
    qo,qn=qualified(parent),qualified(out)
    moved={str(n):[v,qn.get(n)]for n,v in qo.items()if qn.get(n)!=v and not any('LOCAL-MACRO_SYMBOL-'in x for x in n)}
    assert set(moved)=={str(('ProtoFixAndAcknowledgePalette','Restore'))},moved
    assert address(new,'ProtoFixAndAcknowledgePalette::Restore')==address(old,'ProtoFixAndAcknowledgePalette::Restore')+3
    rows=[];ordinary=[]
    for mapper in ['mmc3','mmc5']:
        fo=B/(P+'_'+mapper+'_flagoff.nes');assert not fo.exists();fcmd=command(fo,mapper)
        baseline=B/f'mm_body_adoption_{mapper}_flagoff.nes'
        assert sha(baseline)==ORDINARY[mapper]and fo.read_bytes()==baseline.read_bytes()
        rows.append(dict(mapper=mapper,passed=True,sha256=sha(fo),whole_binary_exact=True,command=fcmd))
        ordinary +=[fo,fo.with_suffix('.dbg'),fo.with_suffix('.lbl'),fo.with_suffix('.map'),fo.with_suffix('.build.log')]
    assert before=={str(q):sha(q)for q in watched}
    leaves=[B/'mm_player_prg_owner_metasprite_engine.s',B/'mm_player_prg_owner_megaman_weapons.s',B/'proto_normal_palette_ack_9ea_source.s']
    result=dict(passed=True,source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),candidate=str(out),
                exact_disjoint_union=True,changed_bytes=58,body_bytes=34,body_bank=4,palette_bytes=24,palette_bank=66,
                all_other_ROM_header_CHR_RAM_addresses_exact=True,genuine_old_label_moves=moved,
                source_overlay={str(R/'src'/name):str(leaf)for name,leaf in zip(['metasprite_engine.s','megaman_weapons.s','proto_palette_ack.s'],leaves)},
                actual_compiler_linker_debug_labels=True,command=cmd,ordinary=rows,protected_inputs_unchanged=before,
                limits='Source build only. No new native, timing margin, body visibility, DMC or frame-rate claim. Only the independently qualified31B body helper/JMP and3B palette acknowledgment are composed.',
                bindings={str(q):sha(q)for q in [Path(__file__),bodyproof,pp,*leaves,entry,parent,parent.with_suffix('.dbg'),body,body.with_suffix('.dbg'),palette,palette.with_suffix('.dbg'),out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),*ordinary]})
    receipt=B/(P+'_build.json');assert not receipt.exists();receipt.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,candidate_sha256=sha(out),proof_sha256=sha(receipt),path=str(receipt))))

if __name__=='__main__':main()
