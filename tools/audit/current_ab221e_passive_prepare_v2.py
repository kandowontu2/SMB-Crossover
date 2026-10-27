"""Prepare one additive timing/body observation profile; never launches Mesen."""
from pathlib import Path
import argparse,json,re,difflib
import current_mega_arsenal_prepare_v1 as parent
from check_tmnt_render_oa import address,location

R=Path(__file__).resolve().parents[2];B=R/'build'
EXPECTED='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
READIES={'proto':'5f9486f0acf32bb8d27d3f27cd52eab4a2dbfc9c1410df0ec8c86383c76cc686',
         'megaman':'fc07b2d67eac3f212996b8c64420ad9bac39df5c9ccb411f5b6e5db2dd36990b'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--kind',choices=['proto-timing','mega-body'],required=True);a=ap.parse_args()
    timing=a.kind=='proto-timing';identity='proto'if timing else'megaman'
    old=B/('current-ab221e-'+identity+'-hard-arsenal-v1');manifest=old/'prepared-not-run.json'
    assert parent.sha(manifest)==READIES[identity];ready=json.loads(manifest.read_text())
    for x in ready['bindings']:
        p=Path(x['path']);assert p.stat().st_size==x['bytes']and parent.sha(p)==x['sha256'],p
    rom=B/'mega_proto_body_palette_9ea.nes';assert parent.sha(rom)==EXPECTED
    b=parent.scoped_load(rom);raw=b['raw'];original=(old/'run.lua').read_text()
    def hook(n,delta=0,size=3):
        at=location(b,n)+delta;k=(at-16)//8192;bs=list(raw[at:at+size]);banks=[k]
        if k==127:
            off=(at-16)%8192;assert raw[16+125*8192+off:16+125*8192+off+size]==bytes(bs);banks=[125,127]
        return dict(pc=address(b,n)+delta,banks=banks,bytes=bs,symbol=n,delta=delta)
    def returns(owner,target):
        at=location(b,owner);pc=address(b,owner);n=int(b['syms'][owner]['size'],0);dest=address(b,target)
        needle=bytes([32,dest&255,dest>>8]);k=(at-16)//8192
        found=[dict(pc=pc+i+3,bank=k,callsite=pc+i,target=dest,callbytes=list(needle))for i in range(n-2)if raw[at+i:at+i+3]==needle]
        assert found,(owner,target);return found
    if timing:
        prior=B/'current-9ea-proto-arsenal-diagnostic-v2';old_observer=R/'tools/audit/current_mega_arsenal_timing_observer_v2.lua'
        observer=R/'tools/audit/current_ab221e_handoff_timing_v1.lua';text=observer.read_text();baseline=old_observer.read_text()
        arm=""" hook('InventoryGrant',function(s)
  if s['cpu.a']==C.trigger_item and trace_first==nil then
   trace_first=s['ppu.frameCount'];trace_last=trace_first+C.PPU_limit-1
   log('diagnostic-window-armed',{trigger_item=C.trigger_item,first_PPU=trace_first,last_PPU=trace_last})
  end
 end)
"""
        assert text.count(arm)==1
        reverse=text.replace(' local trace_first,trace_last=nil,nil\n','',1).replace(arm,'',1)
        reverse=reverse.replace(" local function window()local p=emu.getState()['ppu.frameCount'];return trace_first~=nil and p>=trace_first and p<=trace_last end",' local function window()return frame>=C.first and frame<=C.last end',1)
        reverse=reverse.replace('rows<=3000 and written<=2000000','rows<=10000 and written<=8000000',1)
        assert reverse==baseline,'Only journal window/trigger/budget differ; event bodies exact'
        cfg=json.loads((prior/'observer-config.json').read_text());cfg.update(ROM_sha256=EXPECTED,trigger_item=9,PPU_limit=200)
        cfg.pop('first');cfg.pop('last')
        cfg['hooks']['InventoryGrant']=json.loads((old/'config.json').read_text())['hooks']['InventoryGrant']
        out=B/'current-ab221e-proto-handoff-timing-v1'
        # Finite startup-only trigger/window model: non9 cannot arm, actual9
        # arms once, revisiting9 cannot extend the200-PPU observation interval.
        start=None;tests=[]
        for pp,item in [(90,1),(99,8),(100,9),(101,9),(299,9),(300,9)]:
            if item==9 and start is None:start=pp
            allowed=start is not None and start<=pp<=start+199
            tests.append(dict(PPU=pp,item=item,first=start,log=allowed))
        assert [x['log']for x in tests]==[False,False,True,True,True,False]
        checks=dict(reverse_normalization_to_frozen_v2_exact=True,trigger_source='Actual compiled InventoryGrant entry, incomingA9/BALANCE; no fixed frame assumptions',
                    PPU_span_maximum=200,journal_maximum_bytes=2000000,rows_maximum=3000,trigger_model=tests,
                    source_grant_witness=json.loads((old/'source-controls.json').read_text())['cases'][9]['grants'],
                    expected='Record actual corrected default-HUD queue, parser/CHR publication+cost, fullDMA, real2001 stamps. Only duplicate final3F11/3 may be absent versus old recorded packet; legal phase/cadence changes preclude whole-PPU prefix equality across ROMs.')
        assert checks['source_grant_witness']==[9]
        diff=''.join(difflib.unified_diff(baseline.splitlines(True),text.splitlines(True),fromfile=old_observer.name,tofile=observer.name))
    else:
        prior=B/'current-9ea-mega-knuckle-diagnostic-v1';observer=R/'tools/audit/current_mega_knuckle_observer_v1.lua';text=observer.read_text()
        cfg=json.loads((prior/'observer-config.json').read_text());cfg['ROM_sha256']=EXPECTED
        dr=returns('DrawAllMetasprites','DrawMetasprite');rr=returns('DrawMetasprite','RlNativeRenderDispatch')
        assert len(rr)==1 and rr[0]['pc']==0xa4f1
        cfg.update(draw_returns=dr,render_returns=rr,return_dispatch=list({(q['pc'],q['bank']):q for q in dr+rr}.values()))
        cfg['expected']=dict(bank=(location(b,'SsMegaFISTRight')-16)//8192,pc=address(b,'SsMegaFISTRight'))
        assert cfg['expected']==dict(bank=33,pc=0xd09d)and raw[location(b,'SsMegaFISTRight')]==36
        out=B/'current-ab221e-mega-knuckle-owner-v1';diff=''
        checks=dict(frozen_observer_byte_exact=True,actual_compiled_JSR_returns=dr+rr,
                    expected='Observe actual bank33/header36, body-record admission/sourceOAM and completedDMA/CHR through the original Knuckle window. No requirement that all nine body parts survive hardware eight-sprite evaluation.',
                    journal_scope='Frozen observer500row/4MB hard bound; old actual87rows/214868bytes. No extra screenshots; central original64file/2GB cap unchanged.')
    for name in list(cfg['ram']):cfg['ram'][name]=address(b,name)
    for name,h in list(cfg['hooks'].items()):
        symbol=h.get('symbol',h.get('source_symbol'));delta=h.get('delta',h.get('source_delta',0))
        assert symbol;cfg['hooks'][name]=hook(symbol,delta,len(h['bytes']))
    literal=set(re.findall(r"\br\('([^']+)'",text));direct=set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    for name in literal|direct:cfg['ram'][name]=address(b,name)
    assert all(cfg['ram'][n]==address(b,n)for n in literal|direct|set(cfg.get('fields',[])))
    assert all(n in cfg['hooks']for n in re.findall(r"\bhook\('([^']+)'",text))
    for forbidden in ['emu.write(','emu.setInput(','takeScreenshot','removeMemoryCallback']:assert forbidden not in text
    dynamic="for _,n in ipairs(C.fields)do t[n]=r(n)end"
    scanned=text.replace('local function r(n,i)','')
    if not timing:
        assert scanned.count(dynamic)==1
        scanned=scanned.replace(dynamic,'') # Exact linked-name list validated above.
    assert not re.search(r'(?<!function )\br\(\s*(?![\"\'])\w+',scanned)
    assert not out.exists();out.mkdir();parent.put(out/'observer-config.json',cfg)
    prefix='dofile([=['+observer.as_posix()+']=])('+parent.lua(cfg)+')\n'
    (out/'run.lua').write_text(prefix+original,newline='\n');assert(out/'run.lua').read_text()[len(prefix):]==original
    argv=json.loads((old/'command.json').read_text())['argv']
    argv=[str(out/'native')if v==str(old/'native')else str(out/'run.lua')if v==str(old/'run.lua')else v for v in argv]
    assert [str(old/'native')if v==str(out/'native')else str(old/'run.lua')if v==str(out/'run.lua')else v for v in argv]==json.loads((old/'command.json').read_text())['argv']
    parent.put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    parent.put(out/'source-controls.json',dict(passed=True,native_run=False,observer_only=True,kind=a.kind,checks=checks,
        all_RAM_reads_and_bases_validated=sorted(literal|direct),all_original53_reverified=True,
        original_run_suffix_config_controller_mechanics_guards_seed_caps_literal=True,all_registration_startup_static=True,
        new_emulated_or_input_writes=0,extra_RGB_files=0,actual_linked_hooks=cfg['hooks'],observation_layer_patch=diff,
        limitation='Source/compiled metadata and finite trigger model only, not Lua VM/native output or a candidate pass. Native capture requires ROOT grant.'))
    paths=[Path(__file__),observer,manifest,old/'config.json',old/'run.lua',old/'command.json',prior/'prepared-not-run.json',prior/'observer-config.json']
    if timing:paths +=[old_observer]
    paths +=[out/n for n in ['observer-config.json','run.lua','command.json','source-controls.json']]
    bindings=ready['bindings']+[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=parent.sha(p))for p in paths]
    parent.put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,ROM_sha256=EXPECTED,
        identity=identity,actual_numeric_mode=1,purpose='Passive candidate confirmation only; original native/readiness evidence unchanged.',
        bindings=bindings,caps=ready['caps'],extra_images=0,requires_new_ROOT_grant=True,
        comparison_scope='Exact same candidate/controller/mechanics, so fullCSV/result/originalPNG equality should be checked after observation; no cross-ROM PPU prefix equality is promised.'))
    assert all(parent.sha(x['path'])==x['sha256']for x in bindings)
    print(json.dumps(dict(ready=str(out/'prepared-not-run.json'),sha256=parent.sha(out/'prepared-not-run.json'),bindings=len(bindings),native_run=False)))

if __name__=='__main__':main()
