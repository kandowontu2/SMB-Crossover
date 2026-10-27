"""One flat sparse Bass working draft; no source tree copy or native launch.

Only current changed files and their two include parents are overlaid in the
existing build directory. The installed ROM/source/config are never written.
This first draft is intentionally incomplete until the ceiling body is added.
"""
from pathlib import Path
import configparser
import difflib
import hashlib
import json
import re
import subprocess
import sys

from check_tmnt_render_oa import location
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=Path(__file__).resolve().parents[2]
BUILD=R/'build'
P=R/'tools/audit/proposals'
BASE=BUILD/'smb-crossover-mmc5-expanded.nes'
EXPECTED='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n')

ADDER='''  ldy #6
  cmp #CHARACTER_SCROOGE
  beq Scrooge
  cmp #CHARACTER_LUIGI
  jeq Luigi
  cmp #CHARACTER_PIT
  beq Medium
  cmp #CHARACTER_BASS
  jeq BassTerrainAdder
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny
  sec
  rts
Medium:
  ldy #3
Crouch:
  lda RgCrouch
  beq Yes
Short:
  ldy #8
Yes:
  sec
  rts
Luigi:
  clc
  rts
Scrooge:
  ldy #10
  sec
  rts
  .res 57-(*-::KbLegacyExpandedCollisionAdder),$ea
  .assert *-KbLegacyExpandedCollisionAdder=57,error,"Original adder span"
'''
BOX='''  cmp #CHARACTER_SCROOGE
  beq Scrooge
  cmp #CHARACTER_LUIGI
  beq Done
  ldy #15
  cmp #CHARACTER_PIT
  beq Medium
  cmp #CHARACTER_BASS
  jeq BassTerrainBox
  cmp #CHARACTER_SOPHIA
  beq Medium
  lda GuestHurtTicks
  beq Crouch
  iny
  rts
Medium:
  ldy #12
Crouch:
  lda RgCrouch
  beq Done
Short:
  ldy #17
Done:
  rts
Scrooge:
  ldy #19
  lda RgCrouch
  beq Done
  iny
  rts
  .res 55-(*-::KbLegacyExpandedCollisionBox),$ea
  .assert *-KbLegacyExpandedCollisionBox=55,error,"Original box span"
'''


def main():
    assert sha(BASE)==EXPECTED,'Explicit current3b baseline only'
    assert BUILD.is_dir()and P.is_dir(),'Reuse existing directories; no new trees'
    b=scoped_load(BASE)
    pools=[('BASS_PROFILE','X5_NEW_48',72,0xafb0,160),('BASS_HEAD_GATE','X5_NEW_59',89,0xbf70,144),
        ('BASS_CEILING','X5_NEW_4E',78,0xac00,1024),('BASS_POST','X5_NEW_47',71,0xaf00,256)]
    for _,_,bank,start,size in pools:
        at=16+bank*8192+(start&8191)
        assert b['raw'][at:at+size]==b'\xff'*size,(bank,start,size)
        for seg in b['segs'].values():
            if 'ooffs'in seg:
                pos,n=int(seg['ooffs'],0),int(seg['size'],0)
                assert not(n and pos<at+size and at<pos+n),(seg,start)
    changes={}
    original=(R/'src/kirby_legacy.s').read_text()
    text=original
    for name,body in [('KbLegacyExpandedCollisionAdder',ADDER),('KbLegacyExpandedCollisionBox',BOX)]:
        pattern=r'(?s)(\.proc '+name+r'\n).*?(\.endproc)'
        text,n=re.subn(pattern,lambda m:m[1]+body+m[2],text)
        assert n==1,name
    changes['src/kirby_legacy.s']=text
    head=(R/'src/tmnt_probe_gates.s').read_text()
    token=' jmp Z2HeadAdmission\n .res 17,$ea'
    assert head.count(token)==1
    changes['src/tmnt_probe_gates.s']=head.replace(token,' cmp #CHARACTER_BASS\n beq Bass\n jmp Z2HeadAdmission\nBass:jmp BassHeadAdmission\n .res 10,$ea')
    post=(R/'src/zelda2_link_platform.s').read_text()
    pattern=r'(?s)(\.proc Z2PostBGBodyBridge\n).*?(\.endproc)'
    post,n=re.subn(pattern,lambda m:m[1]+' jmp BassPostBGDispatch\n .res 35,$ea\n .assert *-::Z2PostBGBodyBridge=38,error,"Original post-BG span"\n'+m[2],post)
    assert n==1
    changes['src/zelda2_link_platform.s']=post
    cfg=(R/'smb1base-mmc5-expanded.cfg').read_text()
    token='    KIRBY_CORE: load=X5_NEW_48,type=ro;\n'
    assert cfg.count(token)==1
    i=cfg.index('\n}\nSYMBOLS')
    changes['smb1base-mmc5-expanded.cfg']=cfg[:i]+''.join('    '+name+': load='+load+',type=ro,start=$'+format(start,'x')+';\n'for name,load,_,start,_ in pools)+cfg[i:]
    entry=(R/'src/entrypoint.s').read_text()
    changes['src/entrypoint.s']=entry+'\n.if ::ENABLE_MMC5_EXPANDED\n.include "bass_corner_profile.inc"\n.endif\n'
    changes['src/bass_corner_profile.inc']=(P/'bass_corner_profile.inc').read_text()
    # Flat build overlay. Only the include parent of the changed leaf is
    # copied; all its other children resolve unchanged through ROOT/src.
    leaf=BUILD/'bass_corner_kirby_legacy.s';leaf.write_text(changes['src/kirby_legacy.s'])
    parent=BUILD/'bass_corner_kirby.s'
    k=(R/'src/kirby.s').read_text();token='.include "kirby_legacy.s"'
    assert k.count(token)==1
    parent.write_text(k.replace(token,'.include "'+leaf.name+'"'))
    inc=BUILD/'bass_corner_profile.inc';inc.write_text(changes['src/bass_corner_profile.inc'])
    head=BUILD/'bass_corner_tmnt_probe_gates.s';head.write_text(changes['src/tmnt_probe_gates.s'])
    tmnt=BUILD/'bass_corner_tmnt.s'
    tmnt.write_text((R/'src/tmnt.s').read_text().replace('.include "tmnt_probe_gates.s"','.include "'+head.name+'"'))
    post=BUILD/'bass_corner_zelda2_link_platform.s';post.write_text(changes['src/zelda2_link_platform.s'])
    ep=changes['src/entrypoint.s'].replace('.include "kirby.s"','.include "'+parent.name+'"').replace('.include "tmnt.s"','.include "'+tmnt.name+'"').replace('.include "zelda2_link_platform.s"','.include "'+post.name+'"')
    asm=BUILD/'bass_corner_entrypoint.s';asm.write_text(ep)
    c=BUILD/'bass_corner_main.c';c.write_bytes((R/'src/main.c').read_bytes())
    conf=BUILD/'bass_corner.cfg';conf.write_text(changes['smb1base-mmc5-expanded.cfg'])
    patch=[]
    for rel,new in changes.items():
        before=(R/rel).read_text().splitlines(True)if(R/rel).exists()else[]
        patch+=difflib.unified_diff(before,new.splitlines(True),fromfile='parent3b/'+rel,tofile='private/'+rel)
    (P/'bass_corner_source.patch').write_text(''.join(patch))
    options=configparser.ConfigParser();options.optionxform=str;options.read(R/'build_options.ini')
    definitions={k:v for s in options.values()for k,v in s.items()}
    definitions.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    output=BUILD/'bass_corner_private.nes'
    cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(conf),
        '--ld-args','--dbgfile,'+str(output.with_suffix('.dbg')),'--include-dir',str(R),
        '--asm-include-dir',str(BUILD),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),
        '--bin-include-dir',str(R),'-m',str(output.with_suffix('.map')),
        '-Ln',str(output.with_suffix('.lbl')),'-o',str(output)]
    for k,v in definitions.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
    cmd +=[str(c),str(asm)]
    result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    (BUILD/'bass_corner_build.log').write_text(result.stdout+result.stderr)
    q=dict(source_only=True,native_run=False,product_fix_complete=False,base_ROM_sha256=EXPECTED,
        scope='Source-only ceiling/profile working candidate. Finite assembled controls not completed; native forbidden.',
        source_tree_copies=0,new_directories=0,source_changed_files=list(changes),
        command=cmd,exit=result.returncode,patch_sha256=sha(P/'bass_corner_source.patch'),
        declared_pools=[dict(name=name,bank=bank,start=start,maximum_bytes=size,actual_old_FF_verified=True)for name,_,bank,start,size in pools],
        primary_source_files_written=False,installed_or_default_written=False)
    if result.returncode==0:
        sys.path.insert(0,str(R/'tools'))
        from prepare_cv3_dmc_mirror import prepare
        prepare(R,output)
        q['candidate_ROM_sha256']=sha(output)
        after=output.read_bytes()
        q['changed_banks']={bank:sum(x!=y for x,y in zip(b['raw'][16+bank*8192:16+(bank+1)*8192],after[16+bank*8192:16+(bank+1)*8192]))for bank in range(128)}
        q['changed_banks']={k:v for k,v in q['changed_banks'].items()if v}
        q['all_other_header_CHR_exact']=b['raw'][:16]==after[:16]and b['raw'][16+128*8192:]==after[16+128*8192:]
    put(BUILD/'bass_corner_working_result.json',q)
    print(json.dumps(q,indent=2))
    assert result.returncode==0,result.stdout+result.stderr


if __name__=='__main__':main()
