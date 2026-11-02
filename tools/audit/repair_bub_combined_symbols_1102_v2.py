"""Use the exact native-passed DBG; preserve the failed combined packet."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
O=R/'build/bub-menu-candidate-1102-v2'
PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'
VALID='a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'
MODES=['bub-cold','bob-cold','bt-start','cf-start','ex-regression','sh-regression']

def exact(path,data):
    if path.exists():assert path.read_bytes()==data,path
    else:path.write_bytes(data)

def metadata_edges(path):
    records={}
    for line in path.read_text().splitlines():
        if '\t'not in line:continue
        kind,data=line.split('\t',1)
        row=dict(f.split('=',1)for f in data.split(',')if'='in f)
        if kind in['seg','sym','scope','csym','type','mod','file','line','span']:
            assert 'id'in row
            assert row['id']not in records.setdefault(kind,{})
            records[kind][row['id']]=row
    # Check every explicitly referenced segment/scope/parent/type/size edge.
    # The passed compact package intentionally contains no source graph.
    for kind,rows in records.items():
        for row in rows.values():
            for field,target in [('seg','seg'),('scope','scope'),('parent','scope'),('type','type')]:
                if field in row and row[field].isdigit():assert row[field]in records.get(target,{}),(kind,field,row)
            for field in['def','ref']:
                if field in row:
                    for item in row[field].split('+'):assert item in records.get('line',{}),(kind,field,row)
    assert len(records['seg'])==12 and len(records['sym'])==71
    assert not records.get('scope') and not records.get('line')
    for row in records['seg'].values():
        assert 'addrsize'in row
        if row['type']=='ro':assert 'oname'in row and'ooffs'in row
    return dict(segments=12,symbols=71,source_scopes=0,dangling_edges=0,
        constant_symbols=sum(s.get('type')=='equ'for s in records['sym'].values()))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--modes',default='bub-cold,bob-cold');a=ap.parse_args()
    modes=a.modes.split(',');assert set(modes)<=set(MODES)
    old=O/'native-combined-bub-cold';capture=old/'capture'
    binding=capture/'binding.json';terminal=json.loads(binding.read_text())
    log=capture/'combined-controller.log'
    assert terminal['exit_code']==3221226505 and terminal['ROM_sha256']==PIN
    assert 'DbgImporter'in log.read_text(errors='replace') and "key '2'"in log.read_text(errors='replace')
    assert not(capture/'result.json').exists()
    source=O/'candidate.dbg';assert sha(source)==VALID;edges=metadata_edges(source)
    native=json.loads((O/'native-menu3/capture/binding.json').read_text())
    assert native['exit_code']==0 and json.loads((O/'native-menu3/capture/result.json').read_text())['passed']
    rom=O/'combined2.nes';assert sha(O/'combined.nes')==PIN
    exact(rom,(O/'combined.nes').read_bytes());exact(rom.with_suffix('.dbg'),source.read_bytes())
    exact(rom.with_suffix('.lbl'),(O/'combined.lbl').read_bytes())
    receipt=O/'combined-metadata-repair-v2.json'
    q=dict(passed=True,metadata_only=True,ROM_changed=False,ROM_SHA256=PIN,native=False,installed=False,
        negative_packet=old.relative_to(R).as_posix(),negative_scope='Mesen DBG constants/address importer failed before Lua or gameplay',
        replacement='Byte-for-byte native-menu3-passed DBG; no added or re-encoded symbol/segment records. Unchanged extended VICE labels; every packet has explicit L globals.',
        valid_DBG_SHA256=VALID,metadata_edges=edges,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),O/'combined.nes',O/'combined.dbg',O/'combined.lbl',O/'combined.json',source,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),binding,log,O/'native-menu3/capture/binding.json',O/'native-menu3/capture/result.json']})
    exact(receipt,(json.dumps(q,indent=2)+'\n').encode())
    outputs=[]
    for mode in modes:
        previous=O/('native-combined-'+mode);ready=json.loads((previous/'ready.json').read_text())
        for path,digest in ready['bindings'].items():assert sha(path)==digest,path
        # Explicit prefixes carry all extra control/observer globals. Metadata
        # content itself stays identical to the already-passed71-symbol input.
        controller=(previous/'controller.lua').read_text();assert 'L['in controller
        output=O/('native-combined2-'+mode)
        refs={Path(__file__),receipt,O/'combined.json',previous/'ready.json',previous/'controller.lua'}
        prepare(output,rom,controller,refs,expected=PIN,timeout=ready['timeout'],
            scope='Metadata-only successor, identical00971ROM. '+ready['scope'],allow_interactive=True)
        outputs.append(output.relative_to(R).as_posix())
    own=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(prepared=outputs,ROM_changed=False,ROM_SHA256=PIN,DBG_SHA256=VALID,
        bytes=sum(p.stat().st_size for p in own),files=len(own))))

if __name__=='__main__':main()
