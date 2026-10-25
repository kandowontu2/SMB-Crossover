"""Recheck Mac's authentic pixels, hulls and native interactions after MV merge."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/player-guide-agent/little-mac-private/adoption-packet'
O=R/'build/verification/mac-adoption-mw'
P=O/'mac-final.nes'

def main():
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    shutil.copyfile(D/'composed-poses.json',O/'composed-poses.json')
    (O/'art').mkdir(exist_ok=True)
    shutil.copyfile(D.parent/'art/manifest.json',O/'art/manifest.json')
    text=(D/'tests/check_art.py').read_text()
    text=text.replace('D=Path(__file__).resolve().parent;R=D.parents[2]',f'D=Path({str(O)!r});R=Path({str(R)!r})')
    text=text.replace("P=D/'mac.nes'",f'P=Path({str(P)!r})')
    text=text.replace("D/'source/src/little_mac_state.inc'","R/'src/little_mac_state.inc'")
    (O/'check_art.py').write_text(text)
    text=(D/'tests/check_components.py').read_text()
    text=text.replace('checks=0','checks=0',1)
    (O/'check_components.py').write_text(text)
    exec(compile(text,str(O/'check_components.py'),'exec'),{'__file__':str(O/'check_components.py'),'__name__':'root_mac'})
    raw=P.read_bytes();private=(D/'little-mac-mr-private.nes').read_bytes()
    assert raw[16+94*8192:16+95*8192]==private[16+94*8192:16+95*8192]
    asset=(R/'chr/characters/little-mac.chr').read_bytes()
    assert raw[16+1048576+668*1024:16+1048576+668*1024+len(asset)]==asset
    (O/'native-bank-and-CHR-proof.json').write_text(json.dumps(dict(passed=True,sha256=hashlib.sha256(raw).hexdigest(),art94_exact_private=True,CHR668_to707_exact_asset=True),indent=2)+'\n')
    s=importlib.util.spec_from_file_location('mw_runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(s);s.loader.exec_module(runner)
    folder=O/'native-features';folder.mkdir(exist_ok=True)
    for name in ('native_mac.lua','native_features.lua'):shutil.copyfile(D/'tests'/name,folder/name)
    source=folder/'native_features.lua';text=source.read_text();old='dofile([['+(D.parent/'native_mac.lua').as_posix()+']])'
    assert text.count(old)==1;text=text.replace(old,"dofile(TEST_DIR..'native_mac.lua')");source.write_text(text)
    runner.ROOT=folder;code=runner.run(source,P,timeout=45)
    (O/'native-results.json').write_text(json.dumps(dict(mac=code),indent=2)+'\n');assert code==0
    print('PASS Mac source art, quantities, hulls, page edges and native features after composition')

if __name__=='__main__':main()
