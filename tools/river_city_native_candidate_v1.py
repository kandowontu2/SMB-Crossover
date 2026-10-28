"""Expose Alex/Ryan only in an independent palette-qualified test cartridge.

No shared source/menu/canonical mutation. Uses the exact root33d2 sparse
preimages and the separately qualified RCR renderer. Menu thumbnail artwork
is still a placeholder; this is native discovery, not a release candidate.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools/reference'))
from build_roster_expansion_menu import navigation


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent=R/'build/river-city-palette-runtime-v3-overlay'
    overlay=R/'build/river-city-native-v1-overlay'
    assert not (overlay/'build-proof.json').exists(), 'Never overwrite a frozen test candidate'
    overlay.mkdir(exist_ok=True)
    (overlay/'src').mkdir(exist_ok=True)
    assert sha(R/'build/river-city-palette-private-v3.nes')=='d83fe8ac8aec86b2f5835bab7a7e7dcd32f68d1f83287a1a5dbb4212e59e825b'
    for name in json.loads((parent/'snapshot.json').read_text())['preimages']+['src/river_city.s']:
        p=overlay/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes((parent/name).read_bytes())
    menu=(R/'src/roster_expansion_menu.inc').read_text()
    def get(name):return list(map(int,re.search(name+r':\n \.byte ([^\n]+)',menu)[1].split(',')))
    present=get('X5MenuPresent');characters=get('X5MenuCharacters')
    assert len(present)==28 and present[20]==0 and characters[20]==0
    present[20]=1;characters[20]=21
    edges=navigation([i for i,v in enumerate(present)if v])
    tables={'X5MenuPresent':present,'X5MenuCharacters':characters}
    for direction in ('left','right','up','down'):
        tables['X5Menu'+direction.title()]=[edges[i][direction]if i in edges else 0 for i in range(28)]
    for label,values in tables.items():
        menu,n=re.subn(label+r':\n \.byte [^\n]+',label+':\n .byte '+','.join(map(str,values)),menu)
        assert n==1
    (overlay/'src/roster_expansion_menu.inc').write_text(menu,newline='\n')
    dispatch=(overlay/'src/new_roster_dispatch.s').read_text()
    begin=dispatch.index('.proc NrMenuToggle\n');end=dispatch.index('.endproc',begin)
    body=dispatch[begin:end]
    token=' cmp #CHARACTER_ICE_CLIMBERS\n'
    assert body.count(token)==1
    body=body.replace(token,' cmp #CHARACTER_RIVER_CITY\n beq City\n'+token)
    token='No:clc\n rts\n'
    assert body.count(token)==1
    body=body.replace(token,'City:\n lda RcVariant\n eor #1\n sta RcVariant\n lda #0\n sta RcPalette\n sec\n rts\n'+token)
    dispatch=dispatch[:begin]+body+dispatch[end:]
    (overlay/'src/new_roster_dispatch.s').write_text(dispatch,newline='\n')
    linked=R/'build/river-city-native-v1-linked.nes'
    command=['python','-B','tools/build_mmc5_expanded.py','--source-overlay',str(overlay),'--output',str(linked)]
    result=subprocess.run(command,cwd=R,capture_output=True,text=True)
    (overlay/'build.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    raw=bytearray(linked.read_bytes());at=16+1048576+677*1024
    assert raw[at:at+3072]==bytes(3072)
    raw[at:at+3072]=(R/'chr/characters/river-city-shared-palette.chr').read_bytes()[8192:]
    output=R/'build/river-city-native-v1.nes';assert not output.exists();output.write_bytes(raw)
    for ext in ('.dbg','.lbl','.map'):shutil.copyfile(linked.with_suffix(ext),output.with_suffix(ext))
    files=[Path(__file__),output,output.with_suffix('.dbg'),output.with_suffix('.lbl'),
           R/'src/river_city_shared_palette_art.inc',R/'src/river_city_shared_palette_render.inc',
           R/'chr/characters/river-city-shared-palette.chr']+[p for p in overlay.rglob('*')if p.is_file()]
    proof=dict(status='Independent native-discovery cartridge, not release or shared adoption',native_run=False,
               ROM_sha256=sha(output),command=command,menu_slot=20,raw_identity=21,variants=['Alex','Ryan'],
               limits=['Thumbnail silhouette placeholder; real colored portrait still requires native review.',
                       'Extra3KBCHR uses explicit padding patch; shared incbin split unimplemented.',
                       'No source combat/physics/actor/full frame claim from building.'],
               bindings=[dict(path=str(p),sha256=sha(p))for p in files])
    (overlay/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(ROM_sha256=sha(output),native_run=False)))


if __name__=='__main__':main()
