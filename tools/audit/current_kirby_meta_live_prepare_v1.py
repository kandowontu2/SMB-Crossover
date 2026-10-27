"""Add only bounded passive live rendering to the four frozen bdf9 units."""
from pathlib import Path
import argparse,copy,hashlib,json,re
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua

ROOT=Path(__file__).resolve().parents[2]
CURRENT='bdf9ca2bfe69ee93ca85f1b5e5319e474d9f01aa641c79a58cd9bd602253c40e'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--unit',choices=['basics','copies-low','copies-high','meta'],required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();assert out.is_relative_to(ROOT/'build')and not out.exists()
    key={'basics':'kirby-hard-basics','copies-low':'kirby-hard-copies-low','copies-high':'kirby-hard-copies-high','meta':'meta-hard-earned'}[a.unit]
    old=ROOT/'build'/('current-bdf9-'+key+'-v2');oldready=old/'prepared-not-run.json';parent=json.loads(oldready.read_text());assert parent['ROM_sha256']==CURRENT
    for q in parent['bindings']:assert sha(Path(q['path']))==q['sha256'],q['path']
    original=ROOT/'tools/audit/current_kirby_meta_earned_v1.lua';helper=ROOT/'tools/audit/current_kirby_meta_live_v1.lua';fixture=ROOT/'tools/audit/current_kirby_meta_live_fixture_v1.lua';codec=ROOT/'tools/audit/final_inventory_compact_capture_v1.lua'
    text=original.read_text();extra=helper.read_text();marker='-- All callback registration is startup-static. No callback adds/removes callbacks.';assert text.count(marker)==1
    assert not re.search(r'emu\.(?:write\w*|setInput|setState|loadSavestate|reset)\s*\(',extra)and'removeMemoryCallback'not in extra
    combined=text.replace(marker,extra+'\n'+marker);assert combined.replace(extra+'\n','',1)==text
    if fixture.exists():assert fixture.read_text()==combined,'Do not mutate an already prepared additive fixture'
    else:fixture.write_text(combined,newline='\n')
    rom=ROOT/'build/cv3-life-watch-bdf9-production.nes';assert sha(rom)==CURRENT;b=scoped_load(rom);raw=b['raw'];cfg=json.loads((old/'config.json').read_text());assert cfg['ROM_sha256']==CURRENT
    def hook(n,delta=0):
        at=location(b,n)+delta;return dict(pc=address(b,n)+delta,banks=[(at-16)//8192],bytes=list(raw[at:at+3]),source_symbol=n,source_delta=delta)
    body='DrawAllMetasprites::DoneDrawingPlayer';shot='KbDrawShots::ShotReady';shotret='KbDrawShots::Next'
    for n,dest,delta in [(body,'DrawMetasprite',-3),(shot,'KbDrawShots::Draw',0)]:
        at=location(b,n)+delta;target=address(b,dest);assert raw[at:at+3]==bytes([32,target&255,target>>8])
    assert address(b,shotret)==address(b,shot)+3
    newhooks=dict(LiveBodyCall=hook(body,-3),LiveBodyReturn=hook(body),LiveShotCall=hook(shot),LiveShotReturn=hook(shotret),LiveRenderer=hook('MetaspriteRenderLoop'))
    assert not set(newhooks)&cfg['hooks'].keys();cfg['hooks'].update(newhooks)
    names=set(re.findall(r"\br\('([A-Za-z_][A-Za-z_0-9]*)'",extra));newram={}
    for name in names:
        value=address(b,name);assert value<0x2000 or 0x5c00<=value<0x8000
        if name in cfg['ram']:assert cfg['ram'][name]==value
        else:newram[name]=value;cfg['ram'][name]=value
    art=(location(b,'KbArtStart')-16)//8192
    cfg['render_diagnostic']=dict(codec=codec.as_posix(),art_bank=art,outline_buffer=address(b,'OutlinePoseBuffer'),caps=dict(container_bytes=134217728,container_records=3000,journal_bytes=67108864,journal_rows=20000,unmatched_scoped_DMAs=32,captures_per_DMA=8,extra_native_PNGs=0))
    restored=copy.deepcopy(cfg);restored.pop('render_diagnostic')
    for k in newhooks:restored['hooks'].pop(k)
    for k in newram:restored['ram'].pop(k)
    assert restored==json.loads((old/'config.json').read_text()),'All original mechanics/guards/seeds/controller/tables literal'
    source=ROOT/'build/current-ab221e-kirby-meta-live-source-v1.json';z=json.loads(source.read_text());assert z['passed']and not z['native_run']and z['actual_source_CPU_ROM_sha256']=='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
    for p,h in z['bindings'].items():assert sha(Path(p))==h
    # Parent CPU evidence is not renamed current; prove the exact relevant
    # source owner spans on both actual ROMs instead.
    oldrom=ROOT/'build/mega_proto_body_palette_9ea.nes';before=scoped_load(oldrom);owners={}
    for n in ['DrawAllMetasprites','DrawMetasprite','MetaspriteRenderLoop','KbDrawShots','KbSetPose','MkSetPose','PlayerRemoveOutlines']:
        count=int(b['syms'][n]['size'],0);prior=int(before['syms'][n]['size'],0);assert count==prior and address(b,n)==address(before,n)
        actual=raw[location(b,n):location(b,n)+count];assert actual==before['raw'][location(before,n):location(before,n)+count]
        owners[n]=dict(bytes=count,pc=address(b,n),bank=(location(b,n)-16)//8192,sha256=hashlib.sha256(actual).hexdigest())
    out.mkdir(parents=True);put(out/'config.json',cfg)
    (out/'run.lua').write_text('CURRENT_KIRBY_META_EARNED='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    command=json.loads((old/'command.json').read_text());changes={str(old/'run.lua'):str(out/'run.lua'),str(old/'native'):str(out/'native')};assert all(command['argv'].count(k)==1 for k in changes);command['argv']=[changes.get(q,q)for q in command['argv']];put(out/'command.json',command)
    delta=dict(passed=True,native_run=False,Lua_VM_executed=False,original_fixture_sha256=sha(original),helper_sha256=sha(helper),new_fixture_sha256=sha(fixture),reverse_removal_exact=True,original_config_reverse_exact=True,actual_new_hooks=newhooks,actual_added_RAM=newram,current_unchanged_compiled_owners=owners,parent_source_controls=str(source),parent_source_controls_sha256=sha(source),source_CPU_ROM_sha256=z['actual_source_CPU_ROM_sha256'],actual_native_target_sha256=CURRENT,original_controller_seed_mechanics_guard_cap_unchanged=True,limits='Passive capture selection is content linkage, not unique construction ownership, sprite opacity or art-fidelity proof. Original screenshots untouched; native rerun must preserve every guard and failed originals.')
    put(out/'passive-delta.json',delta)
    files=[Path(q['path'])for q in parent['bindings']]+[oldready,helper,fixture,codec,Path(__file__),ROOT/'tools/audit/current_kirby_meta_live_source_v1.py',ROOT/'tools/audit/final_inventory_compact_capture_v1.py',source]+[out/n for n in ['config.json','run.lua','command.json','passive-delta.json']]
    files=list(dict.fromkeys(files));ready=copy.deepcopy(parent);ready.update(status='PASSIVE_LIVE_RENDER_PREPARED_DO_NOT_RUN',native_run=False,passed=False,parent_ready=str(oldready),parent_ready_sha256=sha(oldready),passive_delta=delta,additional_caps=cfg['render_diagnostic']['caps'],same_original_PNGs=True,no_input_or_state_writes_in_additive_module=True,bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in files])
    put(out/'prepared-not-run.json',ready);assert all(sha(Path(q['path']))==q['sha256']for q in ready['bindings'])
    print(json.dumps(dict(prepared=True,native_run=False,unit=a.unit,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(files))))

if __name__=='__main__':main()
