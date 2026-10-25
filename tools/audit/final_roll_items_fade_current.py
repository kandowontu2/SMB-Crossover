"""Compose frozen Roll fade onto qualified Mike9e0e; no install/native launch."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
PARENT='9e0e5ed5d4957aac9baa040ea76616ee4a88233312700b78a8c55250c19f42d3'
HISTORICAL='c32b70ed95f3a4031e9e8ff5696c9bd8f310bf11443748aa6377482d40b41f47'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ledger(root):return{f.relative_to(root).as_posix():sha(f)for f in sorted(root.rglob('*'))if f.is_file()}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['mike','roll-private','calm-packet','parser-root','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    assert sha(a.mike/'candidate.nes')==PARENT and sha(a.roll_private/'candidate.nes')==HISTORICAL
    comp=json.loads((a.mike/'composition.json').read_text(encoding='utf-8'));changes=json.loads((a.mike/'ready-v1/changed-source-files.json').read_text(encoding='utf-8'))
    assert comp['candidate_ROM_sha256']==PARENT and len(changes)==4
    base=a.output/'parent-source';shutil.copytree(a.mike/'baseline-source',base)
    for name,entry in changes.items():
        src=a.mike/'ready-v1/source'/name;dst=base/name
        assert sha(src)==entry['after_sha256']
        assert(sha(dst)if dst.exists()else None)==entry['before_sha256']
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    deps=[ROOT/'build_options.ini',ROOT/'smb1base.cfg',ROOT/'tools/build_mmc5_expanded.py',ROOT/'tools/prepare_cv3_dmc_mirror.py']
    for folder in ['inc','audio','chr']:deps+=sorted(f for f in(ROOT/folder).rglob('*')if f.is_file())
    assets={str(f):sha(f)for f in deps}
    def build(overlay,out,flag=None):
        cmd=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(ROOT),'--source-overlay',str(overlay),'--output',str(out)]
        if flag:cmd+=['--flag-off',flag]
        r=subprocess.run(cmd,capture_output=True,text=True);out.with_suffix('.driver.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
    oldrom=a.output/'baseline/candidate.nes';oldrom.parent.mkdir();build(base,oldrom);assert sha(oldrom)==PARENT
    overlay=a.output/'overlay';shutil.copytree(base,overlay)
    rollfiles=['roll.s','roll_render.s','roll_drop_fade.s']
    oldsource=a.roll_private/'baseline';historical_proof=json.loads((a.roll_private/'proof.json').read_text(encoding='utf-8'))
    assert historical_proof['all_other_ROM_bytes_identical']and historical_proof['RAM_CHR_art_identical']
    oldroll=a.roll_private.parent/'drop-single-owner-input4c70-v1/src'
    for name in rollfiles:
        src=a.roll_private/'overlay/src'/name;dst=overlay/'src'/name
        if name!='roll_drop_fade.s':assert sha(dst)==sha(oldroll/name),'Current Roll source drift: '+name
        else:assert not dst.exists()
        shutil.copy2(src,dst)
    newrom=a.output/'candidate.nes';build(overlay,newrom)
    assert assets=={f:sha(Path(f))for f in assets},'Nonproduction build assets changed during composition'
    old,new=map(scoped_load,[oldrom,newrom]);at=location(new,'RlDropVisibleKind');size=int(new['syms']['RlDropVisibleKind']['size'],0);call=location(old,'RlDraw::Drops')+3
    assert size==33 and old['raw'][at:at+size]==b'\xff'*size
    want=bytearray(old['raw']);want[call:call+3]=new['raw'][call:call+3];want[at:at+size]=new['raw'][at:at+size];assert bytes(want)==new['raw']
    assert new['raw'][call:call+3]==bytes([0x20,address(new,'RlDropVisibleKind')&255,address(new,'RlDropVisibleKind')>>8])
    moved={n:[address(old,n),address(new,n)if n in new['syms']else None]for n in old['syms']if n not in new['syms']or address(old,n)!=address(new,n)};assert not moved,moved
    delta={bank:sum(x!=y for x,y in zip(old['raw'][16+bank*8192:16+(bank+1)*8192],new['raw'][16+bank*8192:16+(bank+1)*8192]))for bank in range(128)};delta={str(k):v for k,v in delta.items()if v};assert set(delta)=={'119'}
    oldledger,newledger=ledger(base),ledger(overlay);changed=[n for n in sorted(set(oldledger)|set(newledger))if oldledger.get(n)!=newledger.get(n)];assert changed==['src/roll.s','src/roll_drop_fade.s','src/roll_render.s']
    ordinary={}
    for flag in ['mmc3','mmc5']:
        out=a.output/('candidate-'+flag+'.nes');build(overlay,out,flag);assert sha(out)==comp['ordinary_target_hashes'][flag];ordinary[flag]=sha(out)
    assert assets=={f:sha(Path(f))for f in assets}
    (a.output/'parent-source-ledger.json').write_text(json.dumps(oldledger,indent=2)+'\n',encoding='utf-8');(a.output/'candidate-source-ledger.json').write_text(json.dumps(newledger,indent=2)+'\n',encoding='utf-8')
    shutil.copy2(a.roll_private/'sourcepatch.patch',a.output/'sourcepatch.patch')
    result=dict(passed=True,native_passed=False,goal_complete=False,base_sha256=PARENT,candidate_sha256=sha(newrom),historical_candidate_sha256=HISTORICAL,historical_build_proof_sha256=sha(a.roll_private/'proof.json'),qualified_Mike_composition_sha256=sha(a.mike/'composition.json'),Mike_ready_qualification_sha256=sha(a.mike/'ready-v1/qualification.json'),changed_source=changed,replaced_call=historical_proof['replaced_call'],new_helper=historical_proof['new_helper'],changed_PRG_bytes=delta,all_old_symbol_addresses_identical=True,old_symbols_checked=len(old['syms']),all_other_ROM_bytes_identical=True,RAM_CHR_art_identical=True,ordinary_flag_off_hashes=ordinary,parent_source_ledger_sha256=sha(a.output/'parent-source-ledger.json'),candidate_source_ledger_sha256=sha(a.output/'candidate-source-ledger.json'),build_dependencies=assets,tool_sha256=sha(Path(__file__)))
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    # Freeze the exact previously run calm controller. Rebind only numeric
    # configurations, current ROM hashes, source ledgers and verified opcodes.
    calm=json.loads((a.calm_packet/'preparation.json').read_text(encoding='utf-8'));fixture=a.calm_packet/'fixture.lua';assert sha(fixture)==calm['fixture_sha256']
    packet=a.output/'native-preparation';packet.mkdir();shutil.copy2(fixture,packet/'fixture.lua')
    sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(fixture.read_text(encoding='utf-8'))
    profiles=[]
    for role,bundle,source,rom,expected in [('baseline',old,base,oldrom,PARENT),('candidate',new,overlay,newrom,sha(newrom))]:
        folder=packet/role;folder.mkdir();shutil.copytree(source/'src',folder/'src')
        for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(rom.with_suffix(ext),folder/('candidate'+ext))
        (folder/'source-ledger.json').write_text(json.dumps(ledger(folder/'src'),indent=2)+'\n',encoding='utf-8')
        for mode in [0,1]:
            previous=next(x for x in calm['profiles']if x['role']==role and x['mode_value']==mode)
            c=json.loads((Path(previous['script']).parent/'config.json').read_text(encoding='utf-8'))
            assert all(address(bundle,n)==v for n,v in c['ram'].items())
            for name,h in c['hooks'].items():
                if name in ['DropAdmission','DropAdmissionResult']:offset=location(bundle,'RlDraw')+h['address']-address(bundle,'RlDraw')
                elif name=='DropIncrement':offset=location(bundle,'InventoryUpdateDrops')+h['address']-address(bundle,'InventoryUpdateDrops')
                elif name in ['finish','NmiReturn']:
                    proc='GameLoop'if name=='finish'else'NonMaskableInterrupt';offset=location(bundle,proc)+h['address']-address(bundle,proc)
                else:
                    assert address(bundle,name)==h['address'];offset=location(bundle,name)
                assert(offset-16)//8192==h['physical_bank']
                assert list(bundle['raw'][offset:offset+len(h['bytes'])])==h['bytes'],'Controller hook drift: '+name
            c['ROM_sha256']=expected
            dest=packet/(role+'-'+('hard'if mode else'easy'));dest.mkdir();script=dest/'run.lua';script.write_text('OUTPUT=assert(OUTPUT)\nFINAL_ROLL_ITEMS='+lua(c)+'\n'+fixture.read_text(encoding='utf-8'),encoding='utf-8');ast.parse(script.read_text(encoding='utf-8'))
            (dest/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8');profiles.append(dict(role=role,mode_value=mode,script=str(script),script_sha256=sha(script),config_sha256=sha(dest/'config.json'),ROM_sha256=expected,source_ledger_sha256=sha(folder/'source-ledger.json')))
    dependencies={str(f.relative_to(ROOT)).replace('\\','/'):sha(f)for f in [Path(__file__),ROOT/'tools/audit/final_roll_items_prepare.py',ROOT/'tools/audit/final_roll_items_fade_native_run.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py']}
    prep=dict(prepared=True,native_passed=False,goal_complete=False,baseline=PARENT,candidate=sha(newrom),component='current-Mike-parent-calm-fade-idle',parent_historical_preparation_sha256=sha(a.calm_packet/'preparation.json'),fixture_sha256=sha(fixture),controller_text_exact=True,build_proof_sha256=sha(a.output/'proof.json'),dependencies=dependencies,profiles=profiles,scope='Exact unchanged frozen calm controller, freshly bound to qualified Mike9e0e and composed Roll candidate; numeric modes, actual earned orb/controller jump/pickup/expiry and idle cost, PPU/DMA/SMC/bank/stack/CHR guards. Historical9bac/c32b full-pool controls are not current qualifications.')
    (packet/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,candidate_sha256=sha(newrom),build_proof_sha256=sha(a.output/'proof.json'),native_preparation_sha256=sha(packet/'preparation.json'),old_symbols_checked=result['old_symbols_checked'],changed_PRG_bytes=delta)))
if __name__=='__main__':main()
