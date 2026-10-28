"""Assemble the independent Mac roster component; no link/install/native run."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R=Path(__file__).resolve().parents[1];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    manifest=R/'chr/characters/mac-roster-manifest.json'
    assets=json.loads(manifest.read_text())
    for p,h in assets['files'].items():assert sha(R/p)==h
    for q in assets['sources'].values():assert sha(R/'chr/characters'/q['file'])==q['sha256']
    assert assets['CHR_bytes']==40960 and assets['maximum_body_parts']<=10
    assert assets['body_pages'][1]<704 and assets['original_star_page_exact']
    assert assets['all_cells_roundtrip_exact'] and assets['left_facing_raster_mirror_exact']
    wrapper=B/'mac_roster_compile.s'
    text='.include "entrypoint.s"\n.include "mac_roster.s"\n'
    assert not wrapper.exists()or wrapper.read_text()==text
    wrapper.write_text(text,newline='\n')
    parent=B/'bill_capsule_hud44204_build.json'
    old=json.loads(parent.read_text())['command']
    defs=[old[i+1]for i,v in enumerate(old)if v=='--asm-define']
    obj=B/'mac_roster_component.o'
    command=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g',
             '-I',str(R/'src'),'-I',str(R),'-o',str(obj)]
    for d in defs:command+=['-D',d]
    command.append(str(wrapper))
    inputs=[Path(__file__),parent,wrapper,R/'src/entrypoint.s',R/'src/mac_roster.s',
        R/'src/mac_roster_state.inc',R/'src/mac_roster_data.inc',manifest,
        R/'chr/characters/mac-roster.chr',R/'tools/Windows/cc65/bin/ca65.exe',
        R/'tools/Windows/cc65/bin/od65.exe']
    before={str(p):sha(p)for p in inputs}
    result=subprocess.run(command,cwd=R,capture_output=True,text=True)
    (B/'mac_roster_compile.log').write_text(result.stdout+result.stderr,newline='\n')
    assert result.returncode==0,result.stdout+result.stderr
    dump=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments',str(obj)],
        capture_output=True,text=True,check=True).stdout
    segments={name:int(size)for name,size in re.findall(r'Name:\s+"(MAC_ROSTER_\w+)"\s+Flags:\s+\d+\s+Size:\s+(\d+)',dump)}
    assert set(segments)=={'MAC_ROSTER_CORE','MAC_ROSTER_ART','MAC_ROSTER_CHR'}
    assert segments['MAC_ROSTER_CORE']<=0x1cf0 and segments['MAC_ROSTER_ART']<=0x1d40
    assert segments['MAC_ROSTER_CHR']==40960
    assert all(sha(p)==h for p,h in before.items()),'Source changed during component assembly'
    proof=dict(passed=True,source_only=True,unlinked=True,native_run=False,
        no_shared_menu_entrypoint_cfg_or_old_Mac_edits=True,
        actual_emitted_segments=segments,reserved_proposed_placements={
         'MAC_ROSTER_CORE':dict(physical_bank=95,start=0xa310,end_exclusive=0xa310+segments['MAC_ROSTER_CORE']),
         'MAC_ROSTER_ART':dict(physical_bank=94,start=0xc2c0,end_exclusive=0xc2c0+segments['MAC_ROSTER_ART']),
         'MAC_ROSTER_CHR':dict(physical_pages=[668,707],replace_old_LM_CHR_only_at_root_integration=True)},
        assembly_command=command,source_bindings=before,object_sha256=sha(obj),
        asset_manifest_sha256=sha(manifest),
        qualification='Actual ca65 emitted-size/syntax plus asset source/roundtrip/facing tests. Not linked publicPC, complete runtime caller, IRQ, palette deadline, gameplay or performance qualification.',
        independent_root_integration_required=True)
    out=B/'mac_roster_component.json';out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(proof=str(out),sha256=sha(out),segments=segments,native_run=False)))

if __name__=='__main__':main()
