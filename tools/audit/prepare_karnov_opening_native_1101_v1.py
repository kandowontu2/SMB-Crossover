"""Controller-only Karnov opening, reusing the bounded Doki display observer."""
from pathlib import Path
import argparse,json,sys
from prepare_selected_native_packet_v1 import R,prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from observe_chip_committed_write import lua


def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    joint=R/'build/karnov-host-resource-base-1101-v1';template=R/'tools/reference/doki_native_bounded_1101_v1.lua'
    b=scoped_load(joint/'candidate.nes');expected=sha(joint/'candidate.nes')
    args=dict(sha256=expected,main_return=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1,background=list((joint/'kr-native-bg.bin').read_bytes()),chr=list(b['raw'][1048592+407*1024:1048592+412*1024]))
    t=template.read_text().replace('DOKI_ARGS','KARNOV_ARGS').replace('DOKI_NATIVE','KARNOV_NATIVE').replace('DOKI_PROGRESS','KARNOV_PROGRESS')
    t=once(t,"local plan={'up'};for i=1,P.variant do plan[#plan+1]='select'end","local plan={'left','select'}")
    t=once(t,'local vectors,sourceTicks,damage,defeats,apu=0,0,0,0,0','local vectors,sourceTicks,damage,defeats,apu,weaponTicks,maxShots,minimumSP,backgroundChecks=0,0,0,0,0,0,0,255,0')
    t=t.replace("variant=P.variant,",'').replace('source_movement=sourceTicks,','source_movement=sourceTicks,source_weapons=weaponTicks,maximum_projectiles=maxShots,minimum_observed_SP=minimumSP,background_checks=backgroundChecks,')
    t=t.replace("'Cold selection/lives, authentic CHR/palette/descriptor DMA, idle/jump/native enemy encounters and opening camera crossing. No RAM writes, full1-1/shortcut/all-powerup or 60Hz claim.'","'Cold real Select/Start, original body CHR/palette/OAM, idle/jump/landing and opening camera crossing, source shots and native ISR returns. Controller only. Combat, health, earned gear, source audio and complete1-1 remain unimplemented or unqualified; not nightly admission.'")
    start=t.index('local function capture()');end=t.index('local function sample(',start)
    t=t[:start]+'''local function capture()
 if r('SelectedCharacter')~=34 then return end
 local ptr=r('R0')+256*r('R1');local bank=r('CurrentBankC')
 if not(bank==2 and ptr>=0xd100 and ptr<0xd541 or bank==157 and ptr==L.KrColdPose+8192)then return end
 local n=peek(ptr);if n==0 then return end
 assert(n%4==0 and n<=40,'Original body packet length')
 body={};for i=1,n,4 do body[#body+1]={peek(ptr+i),peek(ptr+i+1),peek(ptr+i+2),peek(ptr+i+3)}end
 if bank==2 then poses[tostring(peek(0xc062)&31)]=true end
end
emu.addMemoryCallback(capture,emu.callbackType.exec,L.MetaspriteRenderLoop)
'''+t[end:]
    t=t.replace('physical>=796 and physical<=807','physical>=407 and physical<=411').replace('(physical-796)','(physical-407)')
    t=t.replace("r('SelectedCharacter')~=25","r('SelectedCharacter')~=34")
    start=t.index("emu.addMemoryCallback(function()if active()and raw(L.S2Movement)");end=t.index('local function route()',start)
    t=t[:start]+'''emu.addMemoryCallback(function()if active()and raw(L.KrMovement)==3 then sourceTicks=sourceTicks+1;minimumSP=math.min(minimumSP,emu.getState()['cpu.sp'])end end,emu.callbackType.exec,L.KrMovement)
emu.addMemoryCallback(function()if active()and raw(L.KrSourceWeapons)==3 then weaponTicks=weaponTicks+1 end end,emu.callbackType.exec,L.KrSourceWeapons)
emu.addMemoryCallback(function()if active()and raw(L.ShellOrBlockDefeat)==254 then defeats=defeats+1 end end,emu.callbackType.exec,L.ShellOrBlockDefeat)
'''+t[end:]
    t=once(t,"if jumped and r('S2Air')==0 then landed=true end","if jumped and r('Player_State')==0 then landed=true end\n local n=0;for i=0,8 do if peek(0xc06e+3*i)&128~=0 then n=n+1 end end;maxShots=math.max(maxShots,n)")
    start=t.index(' if updates<=40 then');end=t.index(' if updates%20==0',start)
    t=t[:start]+''' if updates<=40 then assert(x==startX,'No idle drift');pad={}
 elseif updates<=62 then pad={a=true,b=updates<46}
 elseif updates<=105 then pad={}
 elseif x<220 then pad={right=true}
 else pad={b=updates%24<4}end
'''+t[end:]
    t=once(t,"assert(r('CrossoverMenuIndex')==24 and r('S2Variant')==P.variant)","assert(r('CrossoverMenuIndex')==7 and r('SelectedCharacter')==34 and r('FmAlts')&1~=0)")
    t=once(t,"if updates>=105 and maxCamera>=257 and jumped and landed and shown.game and shown.game.visible and not lastMain then finish(vectors>100 and sourceTicks>100,'Cold original identity, displayed graphics, real jump/landing and camera crossing');return end","if updates>=240 and maxX>=220 and maxCamera>=80 and jumped and landed and maxShots>0 and shown.game and shown.game.visible and not lastMain then finish(vectors>100 and sourceTicks>100 and weaponTicks>100,'Real Karnov menu Start, original displayed body, jump/landing/source shots and opening camera crossing');return end")
    t=once(t," for _,stage in ipairs({'selected','lives','game'})do visible(stage)end",''' for _,stage in ipairs({'selected','lives','game'})do visible(stage)end
 if active()and updates>15 then
  local ctrl=r('BackgroundColorCtrl');local ix=ctrl~=0 and ctrl or r('AreaType')
  assert(emu.read(0x3f00,emu.memType.nesPpuDebug)==P.background[ix+1],'Native gameplay backdrop restored after lives');backgroundChecks=backgroundChecks+1
 end''')
    names=['R0','R1','KrColdPose','KrMovement','KrSourceWeapons','FmAlts','MetaspriteRenderLoop','BackgroundColorCtrl']
    t='KARNOV_ARGS='+lua(args)+'\n'+''.join('L['+json.dumps(n)+']='+str(address(b,n))+'\n'for n in names)+t
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(t);assert ok,error
    a.output.parent.mkdir(exist_ok=True)
    prepare(a.output,joint/'candidate.nes',t,[Path(__file__),template,joint/'terrain-assembly.json'],expected=expected,timeout=160,scope='Private Karnov cold Select/Start, authentic body display/source shot updates, idle/jump/landing and opening camera crossing. Actual ISR registers/SMC and background restoration checks. Four PNG cap, no combat/item/audio/full-stage/nightly-admission claim.')


if __name__=='__main__':main()
