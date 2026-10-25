"""Compose reviewed Arm/Rush/Land changes onto the actual GA source privately."""
from pathlib import Path
import argparse, configparser, hashlib, importlib.util, json, re, shutil, subprocess

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/weapons-current-ge'
C=O/'source'
L=R/'build/verification/root49-components-land-l-ia/source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    global O,C
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag',default='weapons-current-gf')
    args=parser.parse_args();assert re.fullmatch('[a-z0-9-]+',args.tag)
    O=R/'build/verification'/args.tag;C=O/'source'
    parent=R/'build/checkpoints/rygar-world-palette-ga/manifest.json'
    p=json.loads(parent.read_text())
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in p['ROMs'].items())
    assert not O.exists()
    C.mkdir(parents=True)
    seed=json.loads((R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json').read_text())
    names=set(seed['source_hashes'])|{q.relative_to(R).as_posix()for q in(R/'src').rglob('*')if q.is_file()}
    before={n:sha(R/n)for n in names}
    for n in names:
        dst=C/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,dst)
    for n in seed['generated11']:
        dst=C/'build/generated'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/'build/generated'/n,dst)
    for n in ('megaman_super_arm.s','megaman_rush.s','megaman_rush_land.s','megaman_audio.s'):
        shutil.copyfile(L/'src'/n,C/'src'/n)
    entry=C/'src/entrypoint.s'
    with entry.open('a')as f:
        f.write('\n.if ::ENABLE_CROSSOVER\n.include "megaman_super_arm.s"\n.include "megaman_rush.s"\n.include "megaman_rush_land.s"\n.endif\n')
    q=C/'src/guest_audio.s';s=q.read_text();old='  sta BassAudioInit\n';assert s.count(old)==1
    q.write_text(s.replace(old,'  jsr MegaManRushLandCharacterReset\n'))
    q=C/'src/special_weapons.s';s=q.read_text();t=(L/'src/special_weapons.s').read_text()
    def replace_span(start,end,replacement):
        nonlocal s
        assert s.count('\n'+start)==1 and s.count('\n'+end)==1,(start,end)
        a=s.index('\n'+start)+1;b=s.index('\n'+end,a)+1
        s=s[:a]+replacement+s[b:]
    start='  jsr Count\n  lda SsSelected\n  cmp #1\n'
    assert s.count(start)==1
    s=s.replace(start,'  jsr Count\n  lda SsSelected\n  cmp #8\n  jeq Rush\n  lda SsSelected\n  cmp #1\n')
    replace_span('  tax\n  dex\n  stx RgSlot\n  lda #0\n  sta SsHeld\n','Ordinary:\n',t[t.index('ArmThrowSpan:\n'):t.index('Ordinary:\n')])
    replace_span('Rush:\n','ShootPose:\n',t[t.index('Rush:\n'):t.index('ShootPose:\n')])
    replace_span('  lda #8\n  ldy #12\n  farcall InventorySpend\n','  lda #$55\n  sta MmVY+1\n',t[t.index('RushBounceSpan:\n'):t.index('  lda #$55\n  sta MmVY+1\n',t.index('RushBounceSpan:\n'))])
    replace_span('  lda #1\n  ldy #8\n  farcall InventorySpend\n','  ldy #0\n  lda #0\n  sta (M0),y\n',t[t.index('ArmLiftCheckSpan:\n'):t.index('  ldy #0\n  lda #0\n  sta (M0),y\n',t.index('ArmLiftCheckSpan:\n'))])
    q.write_text(s)
    prep=dict(parent_manifest_sha256=sha(parent),parent_ROMs=p['ROMs'],parent_source_hashes=before,
              private_L_build_sha256=sha(L.parent/'build-review-ic.json'),
              modified_files={q.relative_to(C).as_posix():sha(q)for q in(C/'src').rglob('*')if q.is_file()and(not(R/q.relative_to(C)).exists()or sha(q)!=sha(R/q.relative_to(C)))},
              scope='Additive GA plus Arm payment, Rush mechanics, Land sound and native MM audio closure optimization; no unrelated older L files copied.',installed=False,goal_complete=False)
    (O/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('weapon_ge_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py')
    im=importlib.util.module_from_spec(spec);spec.loader.exec_module(im)
    cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(C/'build_options.ini')
    options={n:v for section in cfg.values()for n,v in section.items()};builds=[]
    for mapper,baseline in [('mmc3',False),('mmc5',False),('mmc3',True),('mmc5',True)]:
        stem=f'smb-crossover-{mapper}'+('-baseline'if baseline else'')
        obj=C/'build/objects'/stem;obj.mkdir(parents=True)
        for n in ('main.c','entrypoint.s'):shutil.copyfile(C/'src'/n,obj/n)
        opts=dict(options,MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')),ENABLE_CROSSOVER=str(int(not baseline)))
        cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C','smb1base.cfg','--ld-args',f'--dbgfile,build/{stem}.dbg','--include-dir','.','--asm-include-dir','.','--asm-include-dir','src','--bin-include-dir','.','-m',f'build/{stem}.map','-Ln',f'build/{stem}.lbl','-o',f'build/{stem}.nes']
        for k,v in opts.items():cmd+=['--asm-define',f'{k}={v}','-D',f'{k}={v}']
        cmd += [str(obj/'main.c'),str(obj/'entrypoint.s')]
        with(O/(stem+'.log')).open('wb')as f:z=subprocess.run(cmd,cwd=C,stdout=f,stderr=subprocess.STDOUT)
        assert z.returncode==0,stem
        original=R/f'build/{stem}.nes';candidate=C/f'build/{stem}.nes'
        a,b=original.read_bytes(),candidate.read_bytes();layout={}
        if baseline:assert a==b
        else:
            old,new=im.Image(original),im.Image(candidate)
            assert all(new.ram[n]==v for n,v in old.ram.items())
            def globals(image):return {z['name']:z for z in image.data['sym']if z.get('scope')==1 and 'seg'in z and 'val'in z}
            og,ng=globals(old),globals(new)
            changed=[n for n,z in og.items()if n not in ng or z['val']!=ng[n]['val']]
            assert changed==['DPCM_BANK0'],changed
            assert old.segs[og['DPCM_BANK0']['seg']]['size']==new.segs[ng['DPCM_BANK0']['seg']]['size']==0
            assert a[:16]==b[:16] and a[16+512*1024:]==b[16+512*1024:]
            os={z['name']:z for z in old.segs.values()};ns={z['name']:z for z in new.segs.values()}
            layout=dict(old_RAM_and_nonempty_global_PC_unchanged=True,new_aliases=sorted(set(new.ram)-set(old.ram)),header_and_CHR_unchanged=True,segment_growth={n:ns[n]['size']-os.get(n,{'size':0})['size']for n in ns if ns[n]['size']!=os.get(n,{'size':0})['size']},special_roster_free=8192-ns['SPECIAL_ROSTER']['size'])
        builds.append(dict(stem=stem,ROM_sha256=sha(candidate),layout=layout))
        print(stem,'PASS',layout,flush=True)
    assert before=={n:sha(R/n)for n in names}
    (O/'build.json').write_text(json.dumps(dict(passed=True,builds=builds,installed=False,goal_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
