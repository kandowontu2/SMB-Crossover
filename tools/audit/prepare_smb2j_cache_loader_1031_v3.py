"""Source-link a private64KiB-WRAM campaign-data loader, without2J admission."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

P = R/'build/smb2j-campaign-menu-source-1031-v7'
D = R/'build/smb2j-campaign-data-1031-v2'
O = R/'build/smb2j-cache-loader-source-1031-v3'
J = O/'joint'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,t):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(t,encoding='utf-8',newline='\n')


def save(p,q):
    write(p,json.dumps(q,indent=2)+'\n')


def once(s,a,z):
    assert s.count(a)==1,a
    return s.replace(a,z)


def main():
    assert not O.exists()
    O.mkdir()
    parent=P/'joint/candidate.nes'
    assert sha(parent)=='5995749b2efe82343f58899358a663bd050219d3857bbdbc7e01bb38c7e540ba'
    bindings={}
    for p in [P/'source-stage.json',D/'data-stage.json']:
        q=json.loads(p.read_text())
        assert q['passed']
        for n,h in q['bindings'].items():
            assert sha(n)==h,n
            bindings[n]=h
    old=scoped_load(parent)
    before=parent.read_bytes()
    # Proven declared Proto art tail and untouched owner-tail carriers.
    fill=location(old,'ProtoArtEnd')
    assert address(old,'ProtoArtEnd')==0xc738
    assert before[fill:16+65*8192+0x1108]==bytes([255])*2512
    carrier_ranges=[(442,460),(563,571)]
    for a,z in carrier_ranges:
        assert before[1048592+a*1024:1048592+z*1024]==bytes((z-a)*1024)
    main_cmd=json.loads((P/'candidate-main-build.json').read_text())['command']
    link_cmd=json.loads((P/'candidate-link.json').read_text())['command']
    old_main=Path(main_cmd[main_cmd.index('-o')+1])
    entry=next(Path(x)for x in main_cmd if x.endswith('.s'))
    loader=R/'tools/reference/smb2j_cache_loader_1031_v2.inc'
    decoder=R/'tools/reference/smb2j_cache_decoder_1031_v1.inc'
    frontend=R/'tools/reference/smb2j_campaign_menu_1031_v7.inc'
    proto=R/'src/protoman.s'
    for p in [Path(__file__),loader,decoder,frontend,proto,P/'candidate-main-build.json',P/'candidate-link.json']:
        bindings[str(p.resolve())]=sha(p)
    text=once(entry.read_text(),'nes2wram $8000','nes2wram $10000 ; Private exclusive campaign RAM4; no save yet.')
    write(J/'entrypoint.s',text)
    for n in ['character_select.s','cf_menu_body.inc','smb2j_campaign_dispatch_1031_v1.inc']:
        old_text=(P/'joint/src'/n).read_text()
        if n=='smb2j_campaign_dispatch_1031_v1.inc':
            old_text=once(old_text,' and #2',' and #4')
            old_text=once(old_text,' and #$fd',' and #$fb')
        write(J/'src'/n,old_text)
    # Keep the already consumed include identity while changing only its private
    # source body. Original named game/roster PCs remain fixed.
    write(J/'src/smb2j_campaign_menu_1031_v5.inc',frontend.read_text())
    write(J/'src/protoman.s',once(proto.read_text(),'.res $1108-(*-ProtoArtBegin), $ff',
             '.include "smb2j_cache_loader_1031_v2.inc"\n.res $1108-(*-ProtoArtBegin), $ff'))
    write(J/'src/smb2j_cache_loader_1031_v2.inc',loader.read_text())
    write(J/'src/smb2j_cache_decoder_1031_v1.inc',decoder.read_text())
    data=json.loads((D/'data-stage.json').read_text())
    profiles=data['profiles']
    table=''
    for label,values in [
        ('J2LoadPage',[442+p['carrier_offset']//1024 for p in profiles]),
        ('J2LoadHigh',[(p['carrier_offset']%1024)>>8 for p in profiles]),
        ('J2LoadLow',[p['carrier_offset']%256 for p in profiles]),
    ]:
        assert all((values[i]&255)+7<256 for i in range(4)) if label=='J2LoadPage' else True
        table+=label+':.byte '+','.join(str(x&255)for x in values)+'\n'
    cookies=[]
    for i,p in enumerate(profiles):
        cookies+=list(bytes([167,74,50,i])+bytes.fromhex(p['cache_sha256'])[:12])
        first=442+p['carrier_offset']//1024
        assert first+8<=460 and p['carrier_offset']%1024+p['packed_bytes']<8192
    table+='J2CacheCookies:.byte '+','.join(str(v)for v in cookies)+'\n'
    write(J/'src/smb2j_cache_tables.inc',table)
    write(J/'carrier.s','.segment "J2_LEVEL_CARRIER"\n.incbin "'+(D/'campaign-data.bin').as_posix()+'"\n.segment "J2_WORLD_CHR"\n.incbin "'+(D/'original-world-art.chr').as_posix()+'"\n')
    cfg=(P/'joint/candidate.cfg').read_text()
    cfg=once(cfg,'CD_CHR_MEM: start=$67000,size=$c000,type=ro,fill=yes,file=%O,fillval=$00;',
        'CD_CHR_MEM:start=$67000,size=$7800,type=ro,fill=yes,file=%O,fillval=$00;\nJ2_DATA_MEM:start=$6e800,size=$4800,type=ro,fill=yes,file=%O,fillval=$00;')
    cfg=once(cfg,'M3_CHR_MEM: start=$83000,size=$14000,type=ro,fill=yes,file=%O,fillval=$00;',
        'M3_CHR_MEM:start=$83000,size=$9c00,type=ro,fill=yes,file=%O,fillval=$00;\nJ2_ART_MEM:start=$8cc00,size=$2000,type=ro,fill=yes,file=%O,fillval=$00;\nJ2_M3_POST:start=$8ec00,size=$8400,type=ro,fill=yes,file=%O,fillval=$00;')
    cfg=once(cfg,'SEGMENTS {','SEGMENTS {\nJ2_LEVEL_CARRIER:load=J2_DATA_MEM,type=ro;\nJ2_WORLD_CHR:load=J2_ART_MEM,type=ro;')
    counter=0
    def redirect(m):
        nonlocal counter
        if m[1] in ['', '%O']:return m[0]
        path=J/'sideoutputs'/(f'{counter:03d}-'+Path(m[1]).name)
        counter+=1
        return 'file="'+path.as_posix()+'"'
    write(J/'candidate.cfg',re.sub(r'file\s*=\s*"([^"]*)"',redirect,cfg))
    def run(name,cmd):
        guard=validate(cmd,O,cwd=R)
        for out in guard['outputs']:Path(out['path']).parent.mkdir(parents=True,exist_ok=True)
        p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,output_guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        assert p.returncode==0,p.stderr
    cmd=[str(J/'entrypoint.s')if x.endswith('.s')else x for x in main_cmd]
    cmd[1:1]=['-I',str(J),'-I',str(J/'src')]
    cmd[cmd.index('-o')+1]=str(J/'main.o')
    cmd[cmd.index('--create-full-dep')+1]=str(J/'main.dep')
    run('main-build',cmd)
    run('carrier-build',[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g',str(J/'carrier.s'),'-o',str(J/'carrier.o')])
    cmd=[str(J/'main.o')if Path(x)==old_main else x for x in link_cmd]
    for flag,p in [('-C',J/'candidate.cfg'),('-o',J/'candidate.nes'),('-Ln',J/'candidate.lbl'),('-m',J/'candidate.map')]:
        cmd[cmd.index(flag)+1]=str(p)
    cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg')
    cmd.append(str(J/'carrier.o'))
    run('final-link',cmd)
    prepare(R,J/'candidate.nes')
    new=scoped_load(J/'candidate.nes')
    after=(J/'candidate.nes').read_bytes()
    assert len(after)==len(before) and before[10]==9 and after[10]==10
    assert before[:10]==after[:10] and before[11:16]==after[11:16]
    assert address(new,'J2CacheResidentStart')==0xc738 and address(new,'J2CacheResidentEnd')<=0xd108
    stable=0
    for n,sym in old['syms'].items():
        if n.split('::')[-1].startswith(('J2','LOCAL-MACRO_SYMBOL-')) or sym.get('type')!='lab' or 'seg'not in sym or n not in new['syms']:continue
        assert address(old,n)==address(new,n),n
        if 'ooffs'in old['segs'][sym['seg']]:assert location(old,n)==location(new,n),n
        stable+=1
    hook=location(old,'CrossoverMenuInput::FmStartReady')
    expected=bytearray(before[hook:hook+18]);target=address(new,'J2OpenCampaign')
    expected[4]=target&255;expected[9]=target>>8
    assert after[hook:hook+18]==expected
    regions=[(hook,hook+18),(location(old,'J2SelectionReset'),location(old,'J2SelectionReset')+25),(10,11),(fill,location(new,'J2CacheResidentEnd')),
             (location(new,'J2MenuStart'),location(new,'J2MenuEnd'))]
    regions += [(1048592+a*1024,1048592+z*1024)for a,z in carrier_ranges]
    diff=[i for i,(a,z)in enumerate(zip(before,after))if a!=z]
    assert all(any(a<=i<z for a,z in regions)for i in diff),[hex(i)for i in diff if not any(a<=i<z for a,z in regions)][:10]
    # Bind the actual new complete include closure as well as exact consumed
    # original objects. No old whole-main/object overlay or binary patch.
    dep=(J/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs=[Path(p.replace('\\ ',' '))for p in re.split(r'(?<!\\)\s+',dep)if p]
    refs += [Path(p)for p in cmd if p.endswith('.o')]
    refs += [p for p in J.rglob('*')if p.is_file()]+list(O.glob('*.json'))
    for p in refs:bindings[str(p.resolve())]=sha(p)
    save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,
        source_component_only=True,SMB2J_campaign_still_declined=True,candidate=sha(J/'candidate.nes'),
        parent=sha(parent),new_private_header_WRAM_KiB=64,exclusive_cache_physical_bank=4,
        root_private_grant=dict(data_CHR_pages=[442,460],art_CHR_pages=[563,571],
            resident_physical_bank=65,resident_C_view=[0xc738,0xd108],new_global_or_ZP_bytes=0),
        actual_resident_bytes=address(new,'J2CacheResidentEnd')-0xc738,
        matched_old_nonJ2_label_PCs=stable,exact_allowed_regions=regions,changed_ROM_bytes=len(diff),
        menu_probe='Private2J confirm forces blank, loads worlds1-4 donor data intoRAM4, then returns to choice screen. No2J gameplay admission.',
        source_data_stage=sha(D/'data-stage.json'),bindings=bindings))
    print(json.dumps(dict(source=True,native=False,installed=False,candidate=sha(J/'candidate.nes'),resident_bytes=address(new,'J2CacheResidentEnd')-0xc738)))


if __name__=='__main__':main()
