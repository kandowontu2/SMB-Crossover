"""Controller-only current family launch, physical bridge observer and stairs."""
import argparse,json,re,sys
from pathlib import Path
import measure_bub_landing_1102_v21 as V
import audit_bub_menu_frontend_1102_v1 as F
from inventory_playable_menu_1101_v3 import menu_name
from prepare_selected_native_packet_v1 import prepare,sha
from observe_chip_committed_write import lua

O=V.O;R=V.R;B=V.B;M=F.M

def convert(table):
    if not hasattr(table,'items'):return table
    values={k:convert(v)for k,v in table.items()}
    if values and all(isinstance(k,int)for k in values)and set(values)==set(range(1,len(values)+1)):
        return[values[k]for k in range(1,len(values)+1)]
    return values

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args();identity=int(args.identity=='bob')
    source=O/'native-event-bub-full11-wide/controller.lua';text=source.read_text()
    old,new,q,route=V.bundle();manifest=O/'landing-v21-proposal.json';proposal=json.loads(manifest.read_text());pin=proposal['expected_candidate_sha256']
    rom=O/'combined-landing.nes';assert sha(rom)==pin and rom.read_bytes()==new['raw']
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    runtime=LuaRuntime()
    # Decode only the frozen literal metadata; no emulator code is executed.
    configline=next(s for s in text.splitlines()if s.startswith('local BUB_NATIVE_OBSERVER_CONFIG='))
    cfg=convert(runtime.execute(configline+'\nreturn BUB_NATIVE_OBSERVER_CONFIG'))
    cfg.update(ROM_sha256=pin,identity=identity,cookie=list(bytes.fromhex(q['cookie'])))
    cfg['ram']['Player_Y_Speed']=142
    image=(O/'landing-v21-image.bin').read_bytes()
    for name,h in cfg['hooks'].items():
        if h['memory']=='nesWorkRam':
            pc=q['labels'].get(name,h['pc']);h.update(pc=pc,physical=3*8192+pc-0xa000,bytes=list(image[pc-0xa000:pc-0xa000+4]))
        else:
            at=16+h['physical'];assert new['raw'][at:at+len(h['bytes'])]==bytes(h['bytes']),name
    text=text.replace(configline,'local BUB_NATIVE_OBSERVER_CONFIG='+lua(cfg))
    # A strict transport check belongs at the actual bridge's physical return,
    # before native collisions legitimately adjust the authoritative position.
    needle=" local eventCallbacks=0";assert text.count(needle)==1
    text=text.replace(needle,needle+'\n local coordinateSamples,postCollisionDifferences=0,0')
    original="  check(x==((wx()-camera()+16)&255)and y==((r('Player_Y_Position')+16)&255),'source/native coordinate transport',{native_anchor_y=r('Player_Y_Position'),source_sprite_y=y,source_x=x,world_x=wx(),camera=camera()})"
    assert text.count(original)==1
    text=text.replace(original,"  if x~=((wx()-camera()+16)&255)or y~=((r('Player_Y_Position')+16)&255)then postCollisionDifferences=postCollisionDifferences+1 end")
    needle="  perfStack[#perfStack]=nil";assert text.count(needle)==1
    check="""  if q.name=='BbNativeIn'or q.name=='BbNativeOut'then
   coordinateSamples=coordinateSamples+1
   local oy=C.identity==1 and 8 or 0
   check(state(0x103+oy)==((wx()-camera()+16)&255)and state(0x100+oy)==((r('Player_Y_Position')+16)&255),'source/native coordinate transport at actual bridge return',{entry=q.name,world_x=wx(),camera=camera(),source_x=state(0x103+oy),source_y=state(0x100+oy),native_anchor_y=r('Player_Y_Position')})
  end
"""
    text=text.replace(needle,check+needle)
    needle='source_native_event_callbacks=eventCallbacks,';assert text.count(needle)==1
    text=text.replace(needle,'coordinate_samples=coordinateSamples,post_native_collision_cache_differences=postCollisionDifferences,'+needle)
    # Minimal real menu input path to the delivered existing Gimmick family.
    m=M.fresh(new);M.put(m,CrossoverMenuIndex=0);F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
    plans=[]
    def action(key=None,kind='observe'):
        if key:
            bits={'right':1,'down':4,'select':32,'a':128}
            M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=bits[key],SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput')
        name,cells=menu_name(m)
        plans.append(dict(keys=[key]if key else[],slot=M.get(m,'CrossoverMenuIndex'),variant=0,tag=name,state=2,kind=kind,wait=40,raw=M.get(m,'SelectedCharacter'),name=cells,bob=identity))
    action()
    for _ in range(3):action('down')
    action('right');assert M.get(m,'CrossoverMenuIndex')==25 and menu_name(m)[0]=='MR GIMMICK'
    for _ in range(identity+1):action('select')
    assert menu_name(m)[0]==args.identity.upper()and M.get(m,'SelectedCharacter')==39
    selected=dict(plans[-1]);M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=128,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput')
    assert M.get(m,'CrossoverMenuState')==0
    plans.append(dict(selected,keys=['a'],kind='launch',tag='confirm-selected-'+args.identity))
    plan=dict(mode='landing-'+args.identity+'-full11',steps=plans,maxFrames=40000,launch=dict(raw=39,groups=M.get(m,'FmGroups'),bob=identity,requiresRestore=False),restore=[26,48,39])
    text,n=re.subn(r'(?m)^local Q=\{[^\n]*\}$','local Q='+lua(plan),text);assert n==1
    obsolete="  for _,cell in ipairs({{676,245},{677,246},{708,247},{709,248}})do assert(ppu(0x2000+cell[1])==cell[2],'Actual same-span NT copy/icon survives rebuild')end"
    assert text.count(obsolete)==1;text=text.replace(obsolete,'')
    # Reuse the already-proven bodyfoot step/gap request in approach as well as
    # finalmarch; stop it32px before an earnedbubble setup begins.
    needle=" if full_part=='approach'then\n  full_pad={right=true}\n  if grounded and x>=obstacle.left-obstacle.lead then"
    replacement=""" if full_part=='approach'then
  full_pad={right=true}
  if grounded and x<obstacle.left-obstacle.lead-32 then
   local need=not full_solid(x+12,y+32)or full_solid(x+20,y+31)
   if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then
    full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3
   else full_ground_pulse=0 end
  else full_ground_pulse=0 end
  if grounded and x>=obstacle.left-obstacle.lead then"""
    assert text.count(needle)==1;text=text.replace(needle,replacement)
    oldcondition='if need then full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3 else full_ground_pulse=0 end'
    assert text.count(oldcondition)==1;text=text.replace(oldcondition,'if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3 else full_ground_pulse=0 end')
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    assert runtime.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/('native-landing-'+args.identity+'-full11')
    prepare(target,rom,text,[Path(__file__),source,manifest,O/'landing-v21-CPU.json',O/'landing-v21-transport-CPU.json',O/'stair-route-v20-CPU.json',O/'runtime-facing-v19.json',O/'combined-landing.json'],
        expected=pin,timeout=240,allow_interactive=True,
        scope='Exactprivate source-funded native-floor landing reconciliation; actualcurrent32slot MrGimmickSelect family coldlaunch. Previous fourpipes/first2pits earnedbubblecontrols retained; ordinary43pxfreshA feet/sideprobes nowactive duringapproachandmarch. Passive transport assertion moved to actualphysicallyqualified NativeIn/Out returns; endMain nativeclamp differences counted, allactual lastdraw/OAM/CHR/RGB/headerguards retained. Requires all7authored crossings/active1-2/livesunchanged; nostatewrites/helpers/install.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,ROM_sha256=pin,identity=args.identity,Lua54_syntax=True,bindings_verified=True,path=str(target))))

if __name__=='__main__':main()
