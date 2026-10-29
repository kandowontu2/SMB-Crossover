"""Rebuild pinned SMB3 PRG; carry local-ROM CHR through without a PCX claim."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

from acquire_nesasm_source_v1 import ROOT, bind

SOURCE = ROOT/'build/source-acquisition/dk-bowser-2026-10-29'
OUT = ROOT/'build/smb3-original-source-match-v1'
ROM = Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes')


def main():
    assert not (OUT/'proof.json').exists(), 'Keep the source-match proof immutable'
    acquisition = SOURCE/'acquisition.json'
    repositories = json.loads(acquisition.read_text())['repositories']
    source = next(r for r in repositories if r['repository']=='https://github.com/captainsouthbird/smb3')
    assert source['commit']=='09b1bd81a788de8ceec664a34094e84ddb463117'
    closure_path=SOURCE/'smb3/assembly-closure-v1.json'
    closure=json.loads(closure_path.read_text())
    assert closure['commit']==source['commit'] and closure['source_files']==727
    for row in closure['files']:
        assert bind(row['path'])['sha256']==row['sha256']
    tool_proof = ROOT/'build/nesasm-local-v1/proof.json'
    compiler = json.loads(tool_proof.read_text())['executable']
    assert bind(compiler['path'])['sha256']==compiler['sha256']
    original = ROM.read_bytes()
    assert hashlib.sha256(original).hexdigest()=='1ddc4b429490e298c05fa70389034107c0cb50f671c7c1baaa3f228224afc2e9'
    assert original[:4]==b'NES\x1a' and original[4:6]==bytes([16,16]) and not original[6]&4
    assert len(original)==16+262144+131072
    OUT.mkdir(exist_ok=True)
    copied = []
    for row in closure['files']:
        relative = Path(row['source_path'])
        if relative.suffix.lower() not in ['.asm','.inc']:
            continue
        destination = OUT/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        data = Path(row['path']).read_bytes()
        if relative.name.lower()=='smb3.asm':
            text = data.decode('utf-8')
            lines = re.findall(r'^\s*\.incchr\s+"CHR/chr\d{3}\.pcx"[^\r\n]*', text, re.M)
            assert len(lines)==128
            text = re.sub(r'^\s*\.incchr\s+"CHR/chr\d{3}\.pcx"[^\r\n]*', '', text, flags=re.M)
            text += '\n; Local original ROM CHR, unchanged; no independent PCX conversion claim.\n\t.incbin "original-graphics.chr"\n'
            data = text.encode('utf-8')
        destination.write_bytes(data)
        copied.append(bind(destination))
    assert (OUT/'smb3.asm').exists() and len(copied)>=33
    (OUT/'original-graphics.chr').write_bytes(original[16+262144:])
    command = [compiler['path'],'smb3.asm','-l','3']
    assembled = subprocess.run(command,cwd=OUT,capture_output=True,text=True)
    (OUT/'assemble.log').write_text(assembled.stdout+assembled.stderr)
    assert not assembled.returncode and (OUT/'smb3.nes').is_file(), assembled.stdout[-4000:]+assembled.stderr[-1000:]
    rebuilt = (OUT/'smb3.nes').read_bytes()
    assert len(rebuilt)==len(original), (len(rebuilt),len(original))
    prg_equal = rebuilt[16:16+262144]==original[16:16+262144]
    assert prg_equal, 'Pinned original PRG source failed byte-exact comparison'
    assert rebuilt[16+262144:]==original[16+262144:]
    result = dict(status='Original SMB3 PRG assembled byte-exactly; local original CHR carried through',
        repository=source['repository'],commit=source['commit'],tool=bind(__file__),
        acquisition=bind(acquisition),assembly_closure=bind(closure_path),compiler_proof=bind(tool_proof),compiler=compiler,
        original=bind(ROM),rebuilt=bind(OUT/'smb3.nes'),command=command,
        original_PRG_bytes=262144,original_PRG_exact=prg_equal,
        original_PRG_sha256=hashlib.sha256(original[16:16+262144]).hexdigest(),
        original_CHR_bytes=131072,original_CHR_passthrough_exact=True,
        independent_PCX_source_conversion=False,
        only_source_edit='Replace 128 graphics-only .incchr directives with unchanged local-ROM CHR .incbin; all PRG assembly text unchanged.',
        header_differences=[dict(offset=i,original=a,rebuilt=b) for i,(a,b) in enumerate(zip(original[:16],rebuilt[:16])) if a!=b],
        generated_assembly=copied,assembly_log=bind(OUT/'assemble.log'),
        source_credit='Southbird, https://www.sonicepoch.com/sm3mix/',
        Bowser_player_implementation=False)
    for name in ['smb3.lst','smb3.fns']:
        path=OUT/name
        if path.is_file(): result[name]=bind(path)
    (OUT/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(proof=bind(OUT/'proof.json'),PRG_exact=prg_equal,header_differences=result['header_differences'])))


if __name__=='__main__':
    main()
