"""Freeze two numeric-mode Roll lifecycles. Source-only: never launches Mesen."""
from pathlib import Path
import argparse,hashlib,json,re,shutil
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

ROOT=Path(__file__).resolve().parents[2]
TARGET='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def lua(v):
    if isinstance(v,bool):return 'true'if v else'false'
    if isinstance(v,str):return json.dumps(v)
    if isinstance(v,list):return '{'+','.join(lua(x)for x in v)+'}'
    if isinstance(v,dict):return '{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
    if v is None:return 'nil'
    assert isinstance(v,(int,float));return str(v)


def plan():
    steps=[]
    def add(action,name,**v):steps.append(dict(action=action,name=name,**v))
    def damage(count,hp):add('damage',f'earn-hp{hp}-through-{count}-real-contacts',contacts=count,hp=hp)
    def charge(count):add('charge',f'deplete-energy-with-{count}-actual-charges',count=count)
    def block(kind,name):add('block',name,type=kind,tile={0:193,1:193,2:87,3:89}[kind])
    def cap(kind,meter,hp,energy,name):add('capsule',name,kind=kind,meter=meter,hp=hp,energy=energy)
    damage(1,24);charge(7);add('refuse','zero-energy-free-buster-charge-refusal',energy=0)
    block(0,'actual-head-mushroom-restores-both-from24-and0')
    damage(4,12);charge(5);block(1,'actual-head-flower-restores-both-from12-and8')
    block(1,'full-meter-flower-still-consumed')
    damage(1,24)
    for hp,name in [(26,'add2'),(28,'reach28'),(28,'full-still-consumed')]:cap(1,128,hp,28,'small-health-'+name)
    damage(3,16)
    for hp,name in [(26,'add10'),(28,'cap28'),(28,'full-still-consumed')]:cap(2,128,hp,28,'large-health-'+name)
    charge(1)
    for energy,name in [(26,'add2'),(28,'reach28'),(28,'full-still-consumed')]:cap(1,0,28,energy,'small-energy-'+name)
    charge(5)
    for energy,name in [(18,'add10'),(28,'reach28'),(28,'full-still-consumed')]:cap(2,0,28,energy,'large-energy-'+name)
    charge(7);cap(1,0,28,2,'small-energy-real-acquisition-earns2')
    add('refuse','two-energy-free-buster-charge-refusal',energy=2)
    block(1,'flower-restores-energy-after-insufficient-charge')
    add('expiry','earned-uncollected-capsule-native420-update-expiry',kind=1,meter=128)
    block(2,'actual-head-star-native-delivery')
    add('star','real-star-body-contact-and-natural-expiry')
    damage(1,24);block(3,'actual-head-oneup-one-life-no-resource-change')
    damage(5,4)
    add('hold','earned-uncollected-actor-before-death',kind=1,meter=0)
    add('death','real-lethal-contact-live-shot-drop-death-respawn-cleanup')
    assert len(steps)==36
    return steps


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True,help='Explicit frozen input root containing candidate.*,src, binding.json and reference/chr assets.')
    p.add_argument('--expected-sha256',default=TARGET)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();rom=a.input/'candidate.nes';assert sha(rom)==a.expected_sha256
    a.output.mkdir(parents=True,exist_ok=False);frozen=a.output/'frozen-current';frozen.mkdir()
    shutil.copytree(a.input/'src',frozen/'src')
    for n in ['reference','chr']:shutil.copytree(a.input/n,frozen/n)
    for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.input/('candidate'+ext),frozen/('candidate'+ext))
    fixture=ROOT/'tools/audit/final_roll_items_native.lua'
    for pth in [fixture,Path(__file__)]:shutil.copy2(pth,frozen/pth.name)
    ledger={str(f.relative_to(frozen)).replace('\\','/'):sha(f)for f in sorted((frozen/'src').rglob('*'))if f.is_file()}
    (frozen/'source-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
    b=scoped_load(frozen/'candidate.nes');raw=b['raw'];meta=json.loads((frozen/'reference/roll-mobile/art.json').read_text(encoding='utf-8'))
    assert sha(frozen/'reference/new-roster-art/rollsheet_mobile1.png')==meta['source_sha256']
    packed=(frozen/'chr/characters/roll.chr').read_bytes();assert hashlib.sha256(packed).hexdigest()==meta['CHR_sha256']
    assert sha(frozen/'chr/characters/special-weapons-mmc5.chr')==meta['capsule_source_sha256']
    prg_size=(raw[4]+((raw[9]&15)<<8))*16384 if raw[7]&12==8 else raw[4]*16384
    chr_start=16+(512 if raw[6]&4 else 0)+prg_size
    for i,bank in enumerate(meta['pool_chr']):assert raw[chr_start+bank*1024:chr_start+bank*1024+4096]==packed[i*4096:(i+1)*4096]
    linked=0
    for key,parts in meta['records'].items():
        frame,outline,face=key.split('-');at=location(b,f'RlP{frame}O{outline}D{face}')
        assert raw[at:at+1+len(parts)*4]==bytes([len(parts)*4]+[v for part in parts for v in part]);linked+=1
    for face,records in [(1,meta['shot_records']),(2,meta['shot_left_records'])]:
        for i,parts in enumerate(records):
            at=location(b,'RlShot'+str(i)+('Left'if face==2 else''))
            assert raw[at:at+1+len(parts)*4]==bytes([len(parts)*4]+[v for part in parts for v in part]);linked+=1
    hooks=['GameLoop','NonMaskableInterrupt','IrqScrollSplit','RosterOamReady','RlPrepare','RlCollect',
           'MarioSourcePowerupCollision','RlInjury','RlWeapons','RlWeapons::Spawn','ShellOrBlockDefeat','RlDropDispatch','RlRefillDispatch','RlDeathStart','RlDrawRecord']
    hook_data={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(raw[location(b,n):location(b,n)+3]))for n in hooks}
    for key,n in [('finish','GameLoop'),('NmiReturn','NonMaskableInterrupt')]:
        delta=int(b['syms'][n]['size'],0)-1;at=location(b,n)+delta;assert raw[at]in (96,64)
        hook_data[key]=dict(address=address(b,n)+delta,physical_bank=(at-16)//8192,bytes=[raw[at]])
    at=location(b,'IrqScrollSplit');size=int(b['syms']['IrqScrollSplit']['size'],0)
    irq=[address(b,'IrqScrollSplit')+i for i in range(size-2)if raw[at+i:at+i+3]==b'\x8d\x05\x20'];assert irq
    text=fixture.read_text(encoding='utf-8');used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))
    dot_symbols=set(re.findall(r'\bL\.([A-Za-z_][A-Za-z_0-9]*)',text));used|=dot_symbols
    ram={n:address(b,n)for n in used if n in b['syms']}
    assert not set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",text))-set(ram)
    assert not dot_symbols-set(ram)
    common=dict(ROM_sha256=a.expected_sha256,ram=ram,hooks=hook_data,irq_scroll_stores=irq,plan=plan(),powerup_sfx=address(b,'Sfx_PowerUpGrab'),coin_sfx=address(b,'Sfx_CoinGrab'),expiry_art_pointer=address(b,'RlShot1'),
                art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},
                smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
    profiles=[]
    for mode in (0,1):
        name='hard'if mode else'easy';folder=a.output/('roll-'+name+'-prepared-v1');folder.mkdir()
        config=dict(common,mode_value=mode,hard=bool(mode));rendered=lua(config)
        assert '["hard"]='+('true'if mode else'false')in rendered and '["mode_value"]='+str(mode)in rendered
        script=folder/'run.lua';script.write_text('OUTPUT=assert(OUTPUT)\nFINAL_ROLL_ITEMS='+rendered+'\n'+text,encoding='utf-8')
        (folder/'config.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
        profiles.append(dict(mode=name,mode_value=mode,script=str(script),script_sha256=sha(script),status='prepared_not_run',passed=False,steps=36))
    result=dict(status='source_cpu_preparation_only',native_passed=False,goal_complete=False,ROM_sha256=a.expected_sha256,input_binding_sha256=sha(a.input/'binding.json'),source_ledger_sha256=sha(frozen/'source-ledger.json'),fixture_sha256=sha(fixture),preparer_sha256=sha(Path(__file__)),profiles=profiles,
                linked_asset_records=linked,embedded_chr_pages=6,asset_bindings={str(f.relative_to(frozen)).replace('\\','/'):sha(f)for n in ['reference','chr']for f in sorted((frozen/n).rglob('*'))if f.is_file()},
                expected_per_profile=dict(steps=36,planned_physical_food=4,planned_physical_capsules=13,planned_star=1,planned_oneup=1,planned_desired_drop_actors=15,ordinary_nonlethal_injuries=15,actual_charge_attacks=25,real_lethal_injuries=1,committed_hud_values=36),
                scope='No Mesen. Both numeric modes prepared for real cold menu, staged flat world/blocks/default-health NPCs, genuine head/reveal/rise/controller contact, actual injury/charge depletion, natural source RNG/drop actor search/expiry, star/1up/death/respawn. No resource/RNG/counter/outcome writes, no item clones or mature placement. Timings and assertions remain unqualified until native run.',
                reference_limit='Pinned mobile sprites and source-derived imported energy art; no executable mobile gameplay source. Production behavior is an explicit SMB adaptation, not mobile timing/audio parity.')
    (a.output/'preparation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],profiles=2,ROM_sha256=a.expected_sha256,linked_asset_records=linked,preparation_sha256=sha(a.output/'preparation.json'))))


if __name__=='__main__':main()
