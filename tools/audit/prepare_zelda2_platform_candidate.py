"""Prepare original Zelda II body projection and native Fairy platform depth."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load,address,location

ROOT=Path(__file__).resolve().parents[2]


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['parent','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False);source=out/'source';(source/'src').mkdir(parents=True)
    shutil.copy2(ROOT/'smb1base-mmc5-expanded.cfg',source)
    old=load(a.parent)
    span=address(old,'ProcMoveRedPTroopa')-address(old,'PositionPlayerOnVPlat')
    assert span==32,span
    for name in ['little_mac_terrain.s','samus.s','object.s','entrypoint.s','collision.s','ryu_source_body.s','zelda2_native_motion.inc']:
        text=(ROOT/'src'/name).read_text()
        if name=='little_mac_terrain.s':
            text=once(text,'.proc LmBoundingBoxGate\n','.proc Z2LegacyBoundingBoxGate\n')
        elif name=='samus.s':
            start=text.index('.proc SamusAfterBGCollisionBridge\n')
            end=text.index('.endproc',start)
            old_body=text[start:end]
            text=text[:start]+'''.proc SamusAfterBGCollisionBridge
.if ::ENABLE_MMC5_EXPANDED
  farcall Z2PostBGBodyBridge
  rts
  .res 20,$ea
  .assert *-SamusAfterBGCollisionBridge=39,lderror,"Original post-BG bridge span"
.else
'''+old_body.split('\n',1)[1]+'.endif\n'+text[end:]
        elif name=='object.s':
            start=text.index('PositionPlayerOnVPlat:\n')
            end=text.index('\n\n;--------------------------------',start)
            old_body=text[start:end]
            text=text[:start]+'''PositionPlayerOnVPlat:
.if ::ENABLE_MMC5_EXPANDED
  lda Enemy_Y_Position,x ; Keep the small-platform BIT skip's original2bytes.
  farcall Z2PositionOnPlatform
ExPlPos:rts
  .res 11,$ea
  .assert *-PositionPlayerOnVPlat=32,lderror,"Original native platform position span"
.else
'''+old_body.split('\n',1)[1]+'.endif\n'+text[end:]
        elif name=='entrypoint.s':
            text=once(text,'.include "zelda2_link_terrain.s"','.include "zelda2_link_terrain.s"\n.include "zelda2_link_platform.s"')
        elif name=='collision.s':
            start=text.index('SmallPlatformCollision:\n')
            end=text.index('\n;--------------------------------',start)
            old_small=text[start:end]
            size=address(old,'ProcSPlatCollisions')-address(old,'SmallPlatformCollision')
            assert size>25
            text=text[:start]+'''SmallPlatformCollision:
.if ::ENABLE_MMC5_EXPANDED
  farcall Z2SmallPlatformCollision
  rts
  .res '''+str(size-19)+''',$ea
  .assert *-SmallPlatformCollision='''+str(size)+''',lderror,"Native small-platform collision span"
.else
'''+old_small.split('\n',1)[1]+'.endif\n'+text[end:]
            small_body=old_small.split('\n',1)[1].replace('bcs ProcSPlatCollisions','jcs ProcSPlatCollisions')
            assert small_body.count('jsr CrossoverLiftSecondY')==2
            small_body=small_body.replace('jsr CrossoverLiftSecondY','farcall CrossoverLiftSecondY')
            (source/'src/zelda2_small_platform_native.inc').write_text(
                '.pushseg\n.segment "Z2_COLD"\n.proc Z2NativeSmallPlatformCollision\n'+small_body+'.endproc\n.popseg\n')
        elif name=='ryu_source_body.s':
            text=once(text,'.proc RyuSourceBodyPlatformPrepare\n','.proc Z2LegacyPlatformPrepare\n')
            text=once(text,'.proc RyuSourceBodyPlatformFinish\n','.proc Z2LegacyPlatformFinish\n')
        elif name=='zelda2_native_motion.inc':
            text=once(text,'L94F8:\n lda Player_Y_Position\n and #$F0\n sta Player_Y_Position',
                      'L94F8:\n jsr Z2PlatformGroundY\n nop\n nop\n nop')
        (source/'src'/name).write_text(text)
    shutil.copy2(ROOT/'src/little_mac.s',source/'src')
    shutil.copy2(ROOT/'tools/audit/zelda2_link_platform.candidate.s',source/'src/zelda2_link_platform.s')
    rom=out/'candidate.nes'
    with(out/'host-build.log').open('w')as log:
        result=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                               '--source-overlay',str(source),'--output',str(rom)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    assert result.returncode==0,(out/'host-build.log').read_text()[-4000:]
    new=load(rom);assert old['raw'][16+1048576:]==new['raw'][16+1048576:]
    for n,s in old['syms'].items():
        if 'seg'in s and address(old,n)<0x8000:assert address(old,n)==address(new,n),n
    for n in ['ProcMoveRedPTroopa','RunSmallPlatform','RunLargePlatform','SamusAfterBGCollisionBridge','Z2TerrainHead']:
        assert address(old,n)==address(new,n),n
    changes=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
    proof=dict(compiled=True,adopted=False,goal_complete=False,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
               parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),existing_RAM_and_CHR_exact=True,
               changed_PRG_banks=sorted(set((i-16)//8192 for i in changes)),
               source={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest()for p in source.rglob('*')if p.is_file()},
               scope='Private original E975 standing/crouched body boxes and Fairy26px native platform position. Existing platform actors, overlap, movement and carry routines retained. Native platform body shape/viewport edge clipping and all gameplay qualification pending; no adoption.')
    (out/'build-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
