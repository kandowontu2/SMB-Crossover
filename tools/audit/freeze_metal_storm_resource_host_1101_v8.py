"""Compact ungranted bank/loader proposal; exclude compiled payload/ROM trees."""
from pathlib import Path
import hashlib,json,zipfile
import prepare_metal_storm_resource_host_1101_v8 as P
ROOT=P.ROOT;OUT=P.OUT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    a=json.loads((OUT/'assembly.json').read_text());c=json.loads((OUT/'CPU-controls.json').read_text());o=json.loads((OUT/'ownership.json').read_text())
    assert a['passed']and c['passed']and o['passed']and not any(q['granted']for q in[a,c,o])
    for q in[a,c,o]:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    code=[ROOT/'tools/audit/audit_metal_storm_resource_host_1101_v8.py',Path(P.__file__),ROOT/'tools/audit/check_metal_storm_resource_host_1101_v8.py',Path(__file__),P.REF,P.REF.with_suffix('.md')]
    items={p.relative_to(ROOT).as_posix():p.read_bytes()for p in code}
    for n in['renderer-adapted.inc','renderer.s','loader.s','symbols.s','resource.cfg']:items['source/'+n]=(OUT/n).read_bytes()
    items['assets/body-packed.chr']=(OUT/'body-packed.chr').read_bytes()
    for n in['ownership.json','native-witness.json','CPU-controls.json']:items['proof/'+n]=(OUT/n).read_bytes()
    summary={k:v for k,v in a.items()if k not in['labels','commands']};items['proof/assembly-summary.json']=(json.dumps(summary,indent=2)+'\n').encode()
    external=dict(v7_packet=(P.V7/'source-proof.zip').relative_to(ROOT).as_posix(),v7_sha256=sha(P.V7/'source-proof.zip'),v7_lab='Read-only exact includes/actor wrapper used by recipe, no recursive source or compiled-tree copy.',baseline_ROM_sha256=o['ROM_sha256'],baseline_debug_sha256=o['debug_sha256'],resource_granted=False,mutable_O_inputs_not_current=True,scope='Current O/Downloads can advance independently. Serialized exact baseline ownership/helper witnesses remain the tested inputs. No baseline ROM, PRG snapshot or debug copy is included.')
    items['external-inputs.json']=(json.dumps(external,indent=2)+'\n').encode();manifest={n:dict(bytes=len(d),sha256=hashlib.sha256(d).hexdigest())for n,d in items.items()};items['manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    path=OUT/'source-proof.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in sorted(items.items()):
            assert not name.endswith(('.nes','.fds','.bin','.o','.dbg','.lbl'))
            info=zipfile.ZipInfo(name,(2026,11,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(path)as z:
        assert z.testzip()is None
        for name,q in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==q['sha256']
    result=dict(passed=True,granted=False,native=False,installed=False,menu_admitted=False,complete=False,archive=path.relative_to(ROOT).as_posix(),archive_sha256=sha(path),archive_bytes=path.stat().st_size,members=len(items),source_paths=[p.relative_to(ROOT).as_posix()for p in code],actor_bytes=a['actor_bytes'],renderer_bytes=a['renderer_bytes'],ROM_fragment_bytes=a['total_ROM_fragment_bytes'],PRG_proposals=a['ROM_fragments'],external_inputs=external,remaining=['Whole-current low/CV3-page and indirect writer closure; final physical grant and host config composition','Original simultaneous world/player palette coexistence','Typed service/constructor/life/scene/audio/combat routes and actual Main/ISR/SMC/menu/gameplay qualification'],scope='Concrete compiled/tested ROM-only scatter loader, paired readback/authentication, packed original art and native world CHR-window correction. No allocation or native admission.')
    (OUT/'source-stage.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
