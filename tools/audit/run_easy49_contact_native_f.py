"""Adapt existing real-contact arenas to source-backed Easy swim eligibility."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,sys
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-easy-contact-private-d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--mapper',choices=['mmc3','mmc5'],required=True);p.add_argument('--tag',required=True);a=p.parse_args();sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('contact_f_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    review=json.loads((H/'build-review-f.json').read_text());assert review['status']=='PASS_PRIVATE_SOURCE_STOMP_BUILD_ONLY'
    assert all(sha(H/'source'/n)==v for n,v in review['all_source_hashes'].items())
    im=mod.Image(H/('source/build/smb-crossover-'+a.mapper+'.nes'));out=H/'native'/a.tag;out.mkdir(parents=True,exist_ok=False)
    cases=[]
    for char,variant in [(0,0),(1,0),(2,0),(3,0),(3,1),(4,0),(5,0),(8,0),(9,0)]:
        for mode in [0,1]:
            for water in [False,True]:
                for enemy in [6,7,10,20]:
                    if mode==0 and char<=5:stomp=enemy not in [7,10]
                    else:stomp=not water and(mode==0 or char in [0,8])
                    cases.append(dict(character=char,variant=variant,power=1,stale=False,mode=mode,water=water,enemy=enemy,stomp=stomp))
    cfg=dict(cases=cases,ram=im.ram,out=out.as_posix()+'/',hooks={n:im.hook(n)for n in ['HandlePECollisions','EnemyStomped','ForceInjury']},ROM_sha256=sha(im.path))
    text=(R/'tests/guest-ordinary-contact.lua').read_text();start=text.index('local current, bodies, stomps, injuries');text=text[start:]
    text="local C=assert(SOURCE_CONTACT);local frame,index,age=0,0,0;local cases=C.cases\n"+text
    text=text.replace("w('AreaType',1);w('StompTimer'", "w('CrossoverBehaviorVersion',current.mode);w('GuestLegacyHurt',0);w('AreaType',current.water and 0 or 1);w('SwimmingFlag',current.water and 1 or 0);w('StompTimer'")
    text=text.replace("w('Enemy_ID',6)","w('Enemy_ID',current.enemy)")
    text=text.replace("w('Enemy_Y_Position',184)","w('Enemy_Y_Position',(current.enemy==7 or current.enemy==10)and 168 or 184)")
    text=text.replace("local tag=string.format('character", "local tag=string.format('character")
    text=text.replace("tostring(current.stale))\n", "tostring(current.stale))..' enemy'..current.enemy..' mode'..current.mode..' water'..tostring(current.water)\n")
    text=text.replace("emu.setInput({start=frame==200},0)","emu.setInput({start=frame==60 or frame==200},0)")
    a0=text.index(' if current.character==0 or current.character==8 then\n',text.index("print(string.format('CONTACT"))
    a1=text.index(" print('PASS source ordinary body contact",a0)
    text=text[:a0]+''' if current.stomp then
  assert(stomps>0 and injuries==0,'Source/native descending stomp eligibility '..tag..' enemy'..current.enemy..' mode'..current.mode..' water'..tostring(current.water))
  assert(r('PlayerStatus')==current.power,'Stomp retains current tier')
 else
  assert(stomps==0 and injuries>0,'Non-stompable enemy or retainedHard/water restriction '..tag..' enemy'..current.enemy..' mode'..current.mode..' water'..tostring(current.water))
 end
'''+text[a1:]
    text=text.replace("else print('PASS all'..#cases..' ordinary contact arenas, source injury and stale stomp timers');emu.stop(0) end",'''else
  local f=assert(io.open(C.out..'result.json','w'));f:write('{"status":"PASS_NATIVE_SOURCE_STOMP_ELIGIBILITY","cases":'..#cases..',"frames":'..frame..',"route_proof":false}');f:close()
  print('PASS all'..#cases..' source/native eligibility arenas');emu.stop(0)
 end''')
    # Guard every actual collision hook by physical bank and eight compiled bytes.
    guard='''local rawAdd=emu.addMemoryCallback
emu.addMemoryCallback=function(fn,kind,first,last,...)
 if kind==emu.callbackType.exec then
  local h;for _,v in pairs(C.hooks)do if v.address==first then h=v end end
  assert(h,'Bound actual contact hook')
  local original=fn;fn=function(...)
   local p=emu.convertAddress(first)
   if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
   for i,v in ipairs(h.bytes)do assert(emu.read(first+i-1,emu.memType.nesDebug)==v,'Actual8byte collision hook')end
   return original(...)
  end
 end
 return rawAdd(fn,kind,first,last,...)
end
'''
    text=text.replace('local current, bodies, stomps, injuries',guard+'local current, bodies, stomps, injuries',1)
    core=out/'native-core.lua';core.write_text(text)
    wrapper=out/('source-contact-'+a.tag+'.lua');wrapper.write_text('SOURCE_CONTACT='+mod.lua(cfg)+'\n'+''.join('L['+mod.lua(n)+']='+str(h['address'])+'\n'for n,h in cfg['hooks'].items())+'dofile('+mod.lua(core.as_posix())+')\n')
    (out/'binding.json').write_text(json.dumps(cfg,indent=2)+'\n')
    sys.path.insert(0,str(R/'tools'));import run_mesen
    rc=run_mesen.run(wrapper,im.path,timeout=120,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    shutil.copyfile(R/'build/verification'/f'{im.path.stem}-{wrapper.stem}.log',out/'native.log')
    result=out/'result.json';(out/'host-report.json').write_text(json.dumps(dict(exit=rc,result=json.loads(result.read_text())if result.exists()else None,binding_sha256=sha(out/'binding.json'),core_sha256=sha(core),launcher_sha256=sha(__file__),route_proof=False),indent=2)+'\n');return rc
if __name__=='__main__':raise SystemExit(main())
