"""Genuine private DK component link on ac126, without admitting it to the menu."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT/'build/pit-retold-host-v3'
OUT = ROOT/'build/donkey-kong-component-v1'
sys.path[:0] = [str(ROOT/'tools/audit'),str(ROOT/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not (OUT/'handoff.json').exists(), 'Frozen units need a successor'
    OUT.mkdir(exist_ok=True)
    old = scoped_load(PARENT/'candidate.nes')
    assert sha(PARENT/'candidate.nes') == 'ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2'
    closure = json.loads((PARENT/'closure.json').read_text())
    for p,h in closure['actual_dependencies'].items():
        assert sha(p) == h, p
    asset = ROOT/'build/dk-playable-assets-v3/handoff.json'
    assert sha(asset) == '1404a444e3d41f4bb902ca53274eafedfe6fa3e4ce79d70b94aac709a079d2e8'
    for row in json.loads(asset.read_text())['outputs']:
        assert sha(row['path']) == row['sha256']
    code = (PARENT/'entrypoint.s').read_text()
    code += '\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n'
    for n in ['donkey_kong_core.s','donkey_kong_render.s']:
        code += '.include "src/'+n+'"\n'
    code += '.include "build/dk-playable-assets-v3/dk-art.inc"\n'
    code += '.pushseg\n.segment "DONKEY_KONG_CHR"\n.incbin "build/dk-playable-assets-v3/dk.chr"\n.popseg\n.endif\n'
    (OUT/'entrypoint.s').write_text(code)
    cfg = (PARENT/'smb1base-mmc5-expanded.cfg').read_text()
    assert cfg.count('}\nSYMBOLS {') == 1
    score_line = '    SCORE_POPUP_COLD: load=XG_SOPHIA_A_TAIL_MEM, type=ro, optional=yes, start=$bfc0;'
    assert cfg.count(score_line) == 1
    cfg = cfg.replace(score_line,
        '    DONKEY_KONG_CORE:load=XG_SOPHIA_A_TAIL_MEM,type=ro,start=$b9fd,optional=yes;\n'+score_line)
    cfg = cfg.replace('}\nSYMBOLS {',
        '    DONKEY_KONG_ART:load=PRGC_00,type=ro,start=$db13,optional=yes;\n'
        '    DONKEY_KONG_CHR:load=TMNT_CHR_TAIL,type=ro,start=$cd000,optional=yes;\n}\nSYMBOLS {')
    (OUT/'smb1base-mmc5-expanded.cfg').write_text(cfg)
    raw = old['raw']
    leases = [(36,0x19fd,0x1fc0),(12,0x1b13,0x2000)]
    for bank,lo,hi in leases:
        assert raw[16+bank*8192+lo:16+bank*8192+hi] == b'\xff'*(hi-lo)
    assert raw[1048592+820*1024:1048592+824*1024] == bytes(4096)
    new_sources = [ROOT/'src'/n for n in ['donkey_kong_state.inc','donkey_kong_core.s','donkey_kong_render.s']]
    before = {str(p.resolve()):sha(p) for p in new_sources+[Path(__file__),asset,
        asset.parent/'dk-art.inc',asset.parent/'dk.chr',OUT/'entrypoint.s',OUT/'smb1base-mmc5-expanded.cfg']}
    command = closure['commands'][0][:]
    command[command.index('-o')+1] = str(OUT/'main.o')
    command[command.index('--create-full-dep')+1] = str(OUT/'main.d')
    command[-1] = str(OUT/'entrypoint.s')
    run = subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (OUT/'assemble.log').write_text(run.stdout+run.stderr)
    assert not run.returncode, run.stderr
    cc = ROOT/'tools/Windows/cc65/bin'
    dump = subprocess.run([str(cc/'od65.exe'),'--dump-segments',str(OUT/'main.o')],
        capture_output=True,text=True,check=True).stdout
    (OUT/'size.txt').write_text(dump)
    sizes = {name:int(size) for name,size in re.findall(r'Name:\s+"(DONKEY_KONG_\w+)"\s+Flags:\s+\d+\s+Size:\s+(\d+)',dump)}
    assert sizes['DONKEY_KONG_CORE'] <= 1475 and sizes['DONKEY_KONG_ART'] <= 1261, sizes
    assert sizes['DONKEY_KONG_CHR'] == 4096
    link = closure['commands'][3][:]
    for i,value in enumerate(link):
        for a,b in [(PARENT/'smb1base-mmc5-expanded.cfg',OUT/'smb1base-mmc5-expanded.cfg'),
                    (PARENT/'main-independent.o',OUT/'main.o'),
                    (PARENT/'independent.nes',OUT/'candidate.nes'),
                    (PARENT/'independent.dbg',OUT/'candidate.dbg'),
                    (PARENT/'independent.lbl',OUT/'candidate.lbl')]:
            value=value.replace(str(a),str(b))
        link[i]=value
    link += ['-m',str(OUT/'candidate.map')]
    run = subprocess.run(link,cwd=ROOT,capture_output=True,text=True)
    (OUT/'link.log').write_text(run.stdout+run.stderr)
    assert not run.returncode, run.stderr
    from prepare_cv3_dmc_mirror import prepare
    prepare(ROOT,OUT/'candidate.nes')
    current = scoped_load(OUT/'candidate.nes')
    changes = [i for i,(a,b) in enumerate(zip(raw,current['raw'])) if a!=b]
    allowed = [(16+bank*8192+lo,16+bank*8192+hi) for bank,lo,hi in leases]
    allowed += [(1048592+820*1024,1048592+824*1024)]
    assert len(raw)==len(current['raw']) and all(any(lo<=i<hi for lo,hi in allowed)for i in changes)
    # Source definitions generate every new PC; no binary patch or fake alias.
    dependencies = dict(before)
    for word in re.split(r'(?<!\\)\s+',(OUT/'main.d').read_text().split(':\t',1)[1].strip().removesuffix(':')):
        p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else ROOT/p).resolve()
        h=sha(p);expected=before.get(str(p),closure['actual_dependencies'].get(str(p)))
        assert expected == h, ('Unbound or changing actual assembly input',str(p))
        dependencies[str(p)] = h
    for p in link:
        if p.endswith('.o'):
            dependencies[p]=sha(p)
    result = dict(status='PRIVATE_DK_COMPONENT_LINKED_NOT_ADMITTED', source_CPU_only=True,native_run=False,
        parent=sha(PARENT/'candidate.nes'),candidate=sha(OUT/'candidate.nes'),
        sizes=sizes,changes=len(changes),actual_dependencies=dependencies,commands=[command,link],
        conditional_leases=dict(core='A36B9FD..<BFC0',art='C12DB13..<E000',CHR=[820,823]),
        admission=False,
        limits='Actual compiled movement/state/throw/barrel/render/palette leaves only. Shared menu, full42px terrain/hurtbox, native combat/block transactions, source audio, scenes, wholeMain/interrupt/PPU/1-1 and earned-item validation remain open. Unchanged old bytes do not prove arbitrary old pointer consumers cannot read a proposed tail.')
    (OUT/'build-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['commands','actual_dependencies']}))


if __name__ == '__main__':
    main()
