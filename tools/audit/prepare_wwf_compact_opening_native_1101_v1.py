"""Check compact selection then restored original WWF lives/game display."""
from pathlib import Path
import argparse,json,sys
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_wwf_roster_package_bounded_v1 import decode
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--variant',type=int,required=True);a=ap.parse_args();assert 0<=a.variant<6
    b=scoped_load(a.joint/'candidate.nes');expected=sha(a.joint/'candidate.nes')
    template=R/'tools/reference/hogan_native_bounded_v1.lua';text=template.read_text();metadata=R/'build/wwf-roster-native-1101-v1'
    at=int.from_bytes((metadata/'wf-meta-offsets.bin').read_bytes()[2*a.variant:2*a.variant+2],'little')
    _,cells=decode((metadata/'metadata.chr').read_bytes()[at:at+1687],0,0)
    idle=[[t,r,y,x]for t,r,x,y,p in cells]
    art=R/'build/wwf-roster-package-1101-v1/body-pages.chr';body=art.read_bytes();assert len(body)==84*1024
    physical=[546+p if p<58 else 442+p-58 if p<76 else 629+p-76 for p in range(84)]
    menu=b['raw'][1048592+700*1024:1048592+704*1024]
    tiles=b['raw'][location(b,'FmPreviewTiles')+4*(18+a.variant):location(b,'FmPreviewTiles')+4*(18+a.variant)+4]
    compact=[[t,0,(i//2)*16,(i%2)*8]for i,t in enumerate(tiles)]
    point=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1
    args=dict(sha256=expected,main_return=point,idle=idle,menu_idle=compact,chr=list(body+menu),physical=physical+[700,701,702,703],variant=a.variant,frontend_only=True)
    changes=[("local pad={}","for i=1,P.variant do plan[#plan+1]='select' end\nlocal pad={}"),
             ("if active()or lastMain or#isrs>0 then","if true then"),
             ("if#isrs>0 then local q=table.remove(isrs);local s=emu.getState()","local s=emu.getState();local q=isrs[#isrs]\n  if q and q.kind==kind and q.sp==s['cpu.sp']then table.remove(isrs)"),
             ("if active()then local sp=emu.getState()['cpu.sp']","if phase~='title'then local sp=emu.getState()['cpu.sp']"),
             ("local minSP=255","local minSP=255\nlocal artIndex={} for i,p in ipairs(P.physical)do artIndex[p]=i-1 end"),
             ("physical>=546 and physical<563","artIndex[physical]~=nil"),
             ("(physical-546)*1024","artIndex[physical]*1024"),
             ("size<=64","size<=68"),
             ("r('FmGroups')&7~=0","r('FmGroups')&7~=P.variant"),
             ("sample(page,P.idle,'selected')","sample(page,P.menu_idle,'selected')"),
             ("ROM_sha256=P.sha256","ROM_sha256=P.sha256,variant=P.variant"),
             ("frame>=1800","frame>=2400"),
             ("1800 physical frame bound","2400 physical frame bound")]
    for old,new in changes:assert old in text,old;text=text.replace(old,new)
    # Pixels and CHR bytes must come from the menu page during selection, and
    # from the original full-size wrestler lease once lives/game rendering runs.
    old="assert(artIndex[physical]~=nil,'Granted original Hogan art page')";assert text.count(old)==1
    text=text.replace(old,old+"\n  assert(stage=='selected'and physical>=700 and physical<=703 or stage~='selected'and physical<700,'Menu/game graphics lease restoration')")
    text='HOGAN_ARGS='+lua(args)+'\n'+''.join(f'L[{json.dumps(n)}]={address(b,n)}\n'for n in['WfTagDone','WfHostReady','WfRenderBuffer','WfState','WfProxyValid','WfRawProxyCommit'])+text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    ok,error=LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(text);assert ok,error
    a.output.parent.mkdir(exist_ok=True)
    prepare(a.output,a.joint/'candidate.nes',text,[Path(__file__),template,art,metadata/'wf-meta-offsets.bin',metadata/'metadata.chr',a.joint/'assembly-stage.json'],expected=expected,timeout=150,scope='One existing WWF identity: real compact selection, Start, original full-size lives/game CHR/OAM/display restored and30 Main updates with ISR checks. Three selected PNGs; menu regression check, not new-character/full-stage/combat/audio admission.')


if __name__=='__main__':main()
