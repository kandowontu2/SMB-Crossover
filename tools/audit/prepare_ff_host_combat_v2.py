"""Private successor: guard the typed fresh constructor before source state.

Only FF_HOST_COMBAT changes; original source kernel/art/CHR and v1 immutable.
This remains a virtual source-linked RAM3 image, without any resource grant.
"""
from pathlib import Path
import difflib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_ram3_kernel_v1 import sha,write
from finalize_ff_current_component_v3 import dependencies
P=R/'build/final-fantasy-host-combat-v1'
O=R/'build/final-fantasy-host-combat-v2'

def main():
    assert not O.exists()
    old=json.loads((P/'build-proof.json').read_text())
    for p,h in old['bindings'].items():assert sha(p)==h,p
    negative=R/'build/final-fantasy-host-combat-controls-v1/controls.json'
    n=json.loads(negative.read_text())
    assert 'foreign FfReady mutation'in n['failures']['fresh_foreign']['error']
    O.mkdir()
    src=(P/'combat.s').read_text()
    before='FfHostFresh:\n lda #0\n sta FfReady\n jmp FfEnsure\n'
    after=('FfHostFresh:\n ; Public own-only constructor. A/N/Z/C are volatile; X/Y and\n'
           ' ; source fields remain unchanged for foreign owners. Owned Ensure\n'
           ' ; initializes phase state and preserves selected menu class.\n'
           ' lda SelectedCharacter\n cmp #22\n bne FfHostFreshDone\n'
           ' lda #0\n sta FfReady\n jmp FfEnsure\nFfHostFreshDone:\n rts\n')
    assert src.count(before)==1
    new=src.replace(before,after)
    write(O/'combat.s',new)
    write(O/'source.patch',''.join(difflib.unified_diff(src.splitlines(True),new.splitlines(True),fromfile='v1/combat.s',tofile='v2/combat.s')))
    for name in ['component.s','publisher.s','host-definitions.s','ff-host-health.inc']:
        (O/name).write_bytes((P/name).read_bytes())
    cfg=(P/'kernel.cfg').read_text().replace(P.as_posix(),O.as_posix())
    assert P.as_posix()not in cfg
    write(O/'kernel.cfg',cfg)
    ca=R/'tools/Windows/cc65/bin/ca65.exe';names=['component','publisher','host-definitions','combat']
    commands=[[str(ca),'-g','--cpu','6502x','-I',str(O),'-I',str(R/'src'),'--bin-include-dir',str(R),
               '--create-full-dep',str(O/(name+'.d')),'-o',str(O/(name+'.o')),str(O/(name+'.s'))]for name in names]
    commands += [[str(ca.with_name('ld65.exe')),'-C',str(O/'kernel.cfg'),'--dbgfile',str(O/'kernel.dbg'),
                  '-Ln',str(O/'kernel.lbl'),'-m',str(O/'kernel.map'),'-o',str(O/'unused-output.bin'),*[str(O/(name+'.o'))for name in names]]]
    logs=[]
    for command in commands:
        q=subprocess.run(command,cwd=R,capture_output=True,text=True)
        logs.append(dict(command=command,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr))
        write(O/'compile-log.json',json.dumps(logs,indent=2)+'\n');assert q.returncode==0,q.stderr
    a,z=(P/'ram3.bin').read_bytes(),(O/'ram3.bin').read_bytes()
    changes=[i for i,(v,w)in enumerate(zip(a,z))if v!=w]
    assert all(0x1700<=i<0x1fe0 for i in changes)
    assert (O/'art.bin').read_bytes()==(P/'art.bin').read_bytes()
    assert (O/'art.chr').read_bytes()==(P/'art.chr').read_bytes()
    from ff_host_combat_controls_v1 import bundle
    from check_tmnt_render_oa import address
    b=bundle(O);size=address(b,'FfHostCombatEnd')-address(b,'FfHostCombatBegin')
    bindings={**old['bindings'],str((P/'build-proof.json').resolve()):sha(P/'build-proof.json'),
              str(negative.resolve()):sha(negative),str(Path(__file__).resolve()):sha(__file__)}
    for name in names:
        for p in dependencies(O/(name+'.d')):bindings[str(p.resolve())]=sha(p)
    bindings.update({str(p.resolve()):sha(p)for p in O.iterdir()if p.is_file()})
    proof=dict(passed=True,status='PRIVATE_RAM3_SUCCESSOR_CPU_PENDING',native=False,host_Main=False,
               image_sha256=sha(O/'ram3.bin'),host_combat_bytes=size,source_CORE_ART_CHR_unchanged=True,
               state_bytes_added=0,resource_grant=False,changed_offsets=changes,
               Fresh_ABI='Selected22: genuine FfEnsure reset, selected class retained; A/X/Y/N/Z/C volatile on owned path. Foreign: no source/native application state writes; X/Y retained, A/N/Z/C volatile. V/D/I preserved by the source operations.',
               bindings=bindings)
    write(O/'build-proof.json',json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['image_sha256','host_combat_bytes','state_bytes_added']}))
if __name__=='__main__':main()
