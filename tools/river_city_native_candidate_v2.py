"""Private RCR pipe-contact successor; preserve all frozen v1 files."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parent=R/'build/river-city-native-v1-overlay'
    proof=json.loads((parent/'build-proof.json').read_text())
    for row in proof['bindings']:
        assert sha(row['path'])==row['sha256'],row['path']
    overlay=R/'build/river-city-native-v2-overlay'
    assert not overlay.exists()
    overlay.mkdir()
    for p in parent.rglob('*'):
        if p.is_file()and p.suffix in ('.s','.inc','.cfg'):
            d=overlay/p.relative_to(parent);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
    core=(R/'src/river_city_core.s').read_text()
    token=' jsr RcIntegrate\n'
    assert core.count(token)==1
    core=core.replace(token,' lda Player_Y_Position\n sta RcTerrainOldY\n jsr RcIntegrate\n jsr RcTerrainWallPrepass\n')
    (overlay/'src/river_city_core.s').write_text(core,newline='\n')
    wrapper=(overlay/'src/river_city.s').read_text()
    wrapper=wrapper.replace('.include "river_city_core.s"','.include "river_city_core.s"\n.include "river_city_wall_prepass.s"')
    (overlay/'src/river_city.s').write_text(wrapper,newline='\n')
    linked=R/'build/river-city-native-v2-linked.nes'
    command=['python','-B','tools/build_mmc5_expanded.py','--source-overlay',str(overlay),'--output',str(linked)]
    result=subprocess.run(command,cwd=R,capture_output=True,text=True)
    (overlay/'build.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    raw=bytearray(linked.read_bytes());at=16+1048576+677*1024
    assert raw[at:at+3072]==bytes(3072)
    raw[at:at+3072]=(R/'chr/characters/river-city-shared-palette.chr').read_bytes()[8192:]
    output=R/'build/river-city-native-v2.nes';assert not output.exists();output.write_bytes(raw)
    for ext in ('.dbg','.lbl','.map'):shutil.copyfile(linked.with_suffix(ext),output.with_suffix(ext))
    files=[Path(__file__),R/'src/river_city_wall_prepass.s',output,output.with_suffix('.dbg'),output.with_suffix('.lbl')]
    files += [p for p in overlay.rglob('*')if p.is_file()]
    (overlay/'build-proof.json').write_text(json.dumps(dict(ROM_sha256=sha(output),native_run=False,
        parent_ROM_sha256=proof['ROM_sha256'],command=command,
        bindings=[dict(path=str(p),sha256=sha(p))for p in files]),indent=2)+'\n')
    print(json.dumps(dict(ROM_sha256=sha(output),native_run=False)))
if __name__=='__main__':main()
