"""Freeze bounded real-earned Roll fade fixtures; never launch an emulator."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

ROOT=Path(__file__).resolve().parents[2]
BASE='9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c'
CANDIDATE='c32b70ed95f3a4031e9e8ff5696c9bd8f310bf11443748aa6377482d40b41f47'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-input',type=Path,required=True)
    p.add_argument('--candidate-input',type=Path,required=True)
    p.add_argument('--old-preparation',type=Path,required=True)
    p.add_argument('--parser-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old=json.loads((a.old_preparation/'preparation.json').read_text(encoding='utf-8'))
    assert old['ROM_sha256']==BASE
    template=a.old_preparation/'frozen-current/final_roll_items_native.lua'
    assert sha(template)==old['fixture_sha256']
    original=template.read_text(encoding='utf-8')
    common=original[:original.index('local function complete()')]
    guards=original[original.index('-- Same committed-publication'):original.index("for _,n in ipairs({'RlHealth'")]
    guards=guards.replace("published=bytes(L.Sprite_Data,emu.memType.nesDebug)","published=bytes(L.Sprite_Data,emu.memType.nesDebug);publishedRender=completedRender;publicationSerial=publicationSerial+1;lastPublication={id=publicationSerial,ppu=ppuStamp(),render_id=publishedRender and publishedRender.id} ")
    guards=guards.replace('if q==published then dma=q end','if q==published then dma=q;dmaRender=publishedRender;lastDmaImage=q;lastDmaEpoch=publishedRender;dmaSerial=dmaSerial+1;lastDmaStamp={id=dmaSerial,ppu=ppuStamp(),publication=lastPublication,render_id=publishedRender and publishedRender.id} end')
    module=ROOT/'tools/audit/final_roll_items_fade_native.lua'
    text=common+'\n'+module.read_text(encoding='utf-8')+'\n'+guards+'\nFINAL_ROLL_FADE_INSTALL_END_FRAME(function() return dma,dmaRender end,function() dma=nil end,function(i) return physical[i] end)\n'
    sys.path.insert(0,str(a.parser_root));from luaparser import ast
    ast.parse(text)
    assert not re.search(r'(?<![A-Za-z0-9_])(True|False)(?![A-Za-z0-9_])',text)
    (a.output/'fixture.lua').write_text(text,encoding='utf-8')
    shutil.copy2(module,a.output/module.name);shutil.copy2(template,a.output/'inherited-native.lua')
    dependencies={str(q.relative_to(ROOT)).replace('\\','/'):sha(q)for q in [Path(__file__),module,ROOT/'tools/audit/final_roll_items_prepare.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/audit/final_roll_items_fade_native_run.py']}
    profiles=[]
    for role,inp,expected in [('baseline',a.baseline_input,BASE),('candidate',a.candidate_input,CANDIDATE)]:
        assert sha(inp/'candidate.nes')==expected
        frozen=a.output/role;frozen.mkdir()
        for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(inp/('candidate'+ext),frozen/('candidate'+ext))
        shutil.copytree(a.baseline_input/'src',frozen/'src')
        if role=='candidate':
            for f in (inp/'overlay/src').rglob('*'):
                if f.is_file():shutil.copy2(f,frozen/'src'/f.relative_to(inp/'overlay/src'))
        ledger={str(f.relative_to(frozen)).replace('\\','/'):sha(f)for f in sorted((frozen/'src').rglob('*'))if f.is_file()}
        (frozen/'source-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
        b=scoped_load(frozen/'candidate.nes');raw=b['raw']
        oldcfg=json.loads((Path(old['profiles'][0]['script']).parent/'config.json').read_text(encoding='utf-8'))
        used=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'\bL\.([A-Za-z_][A-Za-z_0-9]*)',text))
        ram=dict(oldcfg['ram']);ram.update({n:address(b,n)for n in used})
        hooks=dict(oldcfg['hooks'])
        def add(n,pc=None):
            at=location(b,n)if pc is None else location(b,'RlDraw')+pc-address(b,'RlDraw')
            hooks[n]=dict(address=address(b,n)if pc is None else pc,physical_bank=(at-16)//8192,bytes=list(raw[at:at+3]))
        for n in ['InventoryUpdateDrops','RlDraw','RlDraw::DropNext']:add(n)
        add('DropAdmission',0xA68F);add('DropAdmissionResult',0xA692)
        assert hooks['DropAdmission']['bytes']==([0xbd,ram['InvDropKind']&255,ram['InvDropKind']>>8]if role=='baseline'else[0x20,0xc0,0xaa])
        at=location(b,'InventoryUpdateDrops');size=int(b['syms']['InventoryUpdateDrops']['size'],0)
        op=bytes([0xfe,ram['InvDropAge']&255,ram['InvDropAge']>>8]);delta=raw[at:at+size].index(op)
        hooks['DropIncrement']=dict(address=address(b,'InventoryUpdateDrops')+delta,physical_bank=(at-16)//8192,bytes=list(op))
        arts={}
        for i in [1,4,5,6]:
            at=location(b,'RlShot'+str(i));length=raw[at]
            arts[i]=dict(pointer=address(b,'RlShot'+str(i)),parts=[list(raw[x:x+4])for x in range(at+1,at+1+length,4)])
        for mode in [0,1]:
            c=dict(oldcfg,ROM_sha256=expected,mode_value=mode,hard=bool(mode),ram=ram,hooks=hooks,role=role,art_records=arts,plan=[])
            c['art_records']={str(k):v for k,v in arts.items()}
            folder=a.output/(role+'-'+('hard'if mode else'easy'));folder.mkdir()
            script=folder/'run.lua';script.write_text('OUTPUT=assert(OUTPUT)\nFINAL_ROLL_ITEMS='+lua(c)+'\n'+text,encoding='utf-8')
            ast.parse(script.read_text(encoding='utf-8'))
            (folder/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
            profiles.append(dict(role=role,mode_value=mode,script=str(script),script_sha256=sha(script),config_sha256=sha(folder/'config.json'),ROM_sha256=expected,source_ledger_sha256=sha(frozen/'source-ledger.json')))
    z=dict(prepared=True,native_passed=False,goal_complete=False,baseline=BASE,candidate=CANDIDATE,fixture_sha256=sha(a.output/'fixture.lua'),inherited_fixture_sha256=sha(template),source_packet_sha256=sha(a.old_preparation/'preparation.json'),dependencies=dependencies,profiles=profiles,scope='Cold numeric-mode selection; staged terrain/player/default Goomba geometry, real free buster defeats, unmodified RNG, natural four-slot birth/age/fade/420 expiry, actual full-resource pickup, supplied-art OAM and committed DMA, matched empty controls and per-update/render cadence. No resource, RNG, inventory, counter, drop actor, projectile or result injection. Random pool composition can differ across ROMs; full-pool performance is matched scenario rather than identical actor epochs.')
    (a.output/'preparation.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(preparation_sha256=sha(a.output/'preparation.json'),fixture_sha256=z['fixture_sha256'],profiles=len(profiles))))

if __name__=='__main__':main()
