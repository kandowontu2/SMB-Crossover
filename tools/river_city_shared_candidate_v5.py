"""Make staged menu assets actual assembler inputs, preserving v4 negative."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    original=R/'build/river_city_shared_v4_build.py';proof=R/'build/river-city-shared-v4-overlay/build-proof.json'
    d=json.loads(proof.read_text());assert next(r['sha256']for r in d['bindings']if Path(r['path'])==original)==sha(original)
    src=original.read_text().replace('river-city-shared-v4','river-city-shared-v5')
    token="    output=R/'build/river-city-shared-v5.nes';assert not output.exists()"
    assert src.count(token)==1
    changes='''    # ca65 resolves an existing relative incbin from cwd before the binary
    # include path. Explicit staged paths make the reviewed pixels real inputs.
    for source,asset in [('src/entrypoint.s','chr/characters/packed-mmc5-roster-expanded.chr'),
                         ('src/character_select.s','chr/raw/roster-expansion-menu.bin')]:
        edit(source,lambda s,asset=asset:once(s,'.incbin "'+asset+'"',
             '.incbin "'+(out/asset).as_posix()+'"'))
'''
    src=src.replace(token,changes+token)
    token="    # Real layout, no postlink mutation; original Mac used patterns unchanged."
    assert src.count(token)==1
    src=src.replace("    assert actual[cb+668*1024:cb+677*1024]==mac[:9216]",
        "    assert actual[cb+4096:cb+8192]==packed[4096:8192], 'Actual staged menu CHR'\n"
        "    assert bytes(nt)in actual[16:cb], 'Actual staged nametable bytes'\n"
        "    assert actual[cb+668*1024:cb+677*1024]==mac[:9216]")
    generated=R/'build/river_city_shared_v5_build.py';assert not generated.exists();generated.write_text(src,newline='\n')
    negative=R/'build/river-city-shared-v4-incbin-negative.json'
    negative.write_text(json.dumps(dict(ROM_sha256=d['ROM_sha256'],native_run=False,
        reason='ca65 resolves existing cwd relative incbin before --bin-include-dir; staged menu art was not consumed. Assert actual CHR/nametable bytes in successor before native acceptance.'),indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(generated)],cwd=R,check=True)
    p=R/'build/river-city-shared-v5-overlay/build-proof.json';out=json.loads(p.read_text());out['bindings'].append(dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)))
    out['retained_incbin_negative']=dict(path=str(negative),sha256=sha(negative));p.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
