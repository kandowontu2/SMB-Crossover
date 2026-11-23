"""Current-only ordinary Prince 1-1 hidden-life cap/ground source probes.

The immutable E161 control fixture is read in memory. Its 4193 retained
static bytes, the complete current packet/cookie and every native Main
hook authenticate independently; no historical whole-ROM tree is rebuilt.
No Mesen, state seeds, game changes or filesystem outputs are supported.
"""
import argparse
from functools import lru_cache
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import run_goku_stock_1123 as G
import repair_goku_hidden_head_1123 as Fix
import prince_cold_packet_1111 as Packet
import replay_prince_natural_stock_40a_1115 as Base
import replay_prince_natural_stock_returns_40a_1115 as Returns
import replay_prince_natural_stock_hold_40a_1115 as Hold
import replay_prince_natural_stock_fast_40a_1115 as Fast
import replay_prince_hidden_running_40a_1115 as Running
import replay_prince_hidden_partial_up_40a_1115 as Partial
import replay_prince_hidden_mount_release_40a_1115 as Release
import replay_prince_hidden_mount_fresh_A_40a_1115 as Fresh
import replay_prince_hidden_point67_full_ace_1115 as Point

H,W,N,Engine=G.H,G.W,G.N,G.Engine
PIN=G.PIN
CURRENT=Fix.CANDIDATE
FIXTURE=G.Stock.R/'tools/reference/prince40a_full_e161_1115.lua'
FIXTURE_SHA='e1614ed60e1bb2d3990df26c4f1f16e97fcda6a744ca9950bf346cc2a3ddbc2f'
HEADER='29039e216e9c07ac8b94fc26c9e99cc7f95a14db46f7eeaa43699b31e32ffbab'
PARTS=('419334acdc2c2e6b51d59cc4c854280e4355e2b5ca4a48a1cd85872d05d1c0fe',
       '804475010b2ebfc450a36ace8d7be9e0fcfe28d38fae9dbcd42075b4f11ca4bb',
       'f1b218736e64b893d2f61088df9b68e70b1e19fc1df477cb722363961d97be9b')
COOKIE='a72602350cd97981c60cc7748ecae33b'
CAP_NEGATIVE={
    'ROM_SHA256':CURRENT,
    'controller_SHA256':'a0e8cb8d36bd334545993e80c2b7dc133b62b9716127506ff6847d42fecf67e3',
    'receipt_SHA256':'0290335906ccd9b95b7d4b3f427981d1e735e7cf1f8ebdf53cb25113a787fe07',
    'receipt_inner_SHA256':'3af5ac98257c42cb57329d2b0b45d6282f47dce1404e082e0392195cdc40eb8d',
    'Main_and_Prince_returns':2159,'idle_cap':[937,112],
    'last_head_before_column':[1021,131,128,0],
    'first_head_inside_column':[1025,145,144,0],
    'terminal':[1046,176,3,2],'natural_1UP_born':False,
    'scope':'Linked real menu entry, ordinary cap idle/fresh-A route; actual CPU; geometry miss, no native or universal-unreachability claim',
}


def clone(fn,updates):
    fn=getattr(fn,'__wrapped__',fn);space=dict(fn.__globals__,**updates)
    exec(compile(inspect.getsource(fn),str(Path(__file__))+':current-only-control-transform','exec'),space)
    return space[fn.__name__]


def table(text,prefix):
    rows=[line for line in text.splitlines()if line.startswith(prefix)];assert len(rows)==1
    return Base.LuaRuntime(unpack_returned_tuples=True).eval(rows[0][len(prefix):])


@lru_cache(maxsize=2)
def authenticate(raw):
    assert H(raw)in(PIN,CURRENT)
    parent=Fix.recover_parent(raw)if H(raw)==CURRENT else raw;assert H(parent)==PIN
    head,parts,_=Packet.extract(raw);assert Packet.extract(parent)==Packet.extract(raw)
    assert H(head)==HEADER and tuple(map(H,parts))==PARTS and raw[Packet.COOKIE:Packet.COOKIE+16].hex()==COOKIE
    data=FIXTURE.read_bytes();assert H(data)==FIXTURE_SHA and len(data)==92961 and b'\r'not in data
    text=data.decode();rows=table(text,'local candidateStaticExtents=');count=0
    for i in range(1,len(rows)+1):
        row=rows[i];bank,offset=row['bank'],row['offset'];values=bytes(row['bytes'][j]for j in range(1,len(row['bytes'])+1))
        if bank==3:assert parts[0][offset:offset+len(values)]==values
        elif offset>=2048:assert parts[1][offset-2048:offset-2048+len(values)]==values
        else:assert parts[2].count(values)==1  # Original cold scatter owns runtime destinations.
        count+=len(values)
    assert count==4193 and parts[0][0x1310:0x1353]==Point.C.NEW
    hooks=table(text,'local verifiedHooks=')
    for h in[hooks['entry'],*[hooks['returns'][i]for i in range(1,len(hooks['returns'])+1)]]:
        at=16+h['offset'];expected=bytes(h['bytes'][i]for i in range(1,len(h['bytes'])+1))
        if h['pc']==0x82d9:
            assert expected.hex()=='a9ff8d3901205683';expected=bytes.fromhex('a9ff8d3901205983')
        assert raw[at:at+len(expected)]==parent[at:at+len(expected)]==expected
    return dict(packet=True,static_bytes=count,point_bytes=67,header=HEADER,parts=PARTS,cookie=COOKIE)


@lru_cache(maxsize=4)
def controller(raw,route='cap'):
    authenticate(raw);pin=H(raw)
    def fixture(image):assert image==raw;return FIXTURE.read_text()
    frozen=SimpleNamespace(**dict(Base.Frozen.__dict__,controller=fixture))
    first=clone(Base.controller,dict(Frozen=frozen,PIN=pin))
    base=SimpleNamespace(**dict(Base.__dict__,controller=first,PIN=pin))
    second=clone(Returns.controller,dict(Previous=base,PIN=pin))
    returns=SimpleNamespace(**dict(Returns.__dict__,controller=second,PIN=pin))
    held=clone(Hold.controller,dict(Previous=returns,PIN=pin))
    def traced(image,mode='oneup',jump=8):return Fast.head_trace(held(image,mode,jump),image)
    fast=SimpleNamespace(**dict(Fast.__dict__,controller=traced,PIN=pin,Previous=SimpleNamespace(**dict(Hold.__dict__,Previous=returns))))
    running=clone(Running.controller,dict(Previous=fast,PIN=pin))
    if route=='ground':text=running(raw,'oneup',8,start='ground')
    else:
        run=SimpleNamespace(**dict(Running.__dict__,controller=running,PIN=pin,Previous=fast))
        partial=clone(Partial.controller,dict(Previous=run,PIN=pin))
        part=SimpleNamespace(**dict(Partial.__dict__,controller=partial,PIN=pin,Previous=run))
        release=clone(Release.controller,dict(Previous=part,PIN=pin))
        released=SimpleNamespace(**dict(Release.__dict__,controller=release,PIN=pin,Previous=part))
        fresh=clone(Fresh.controller,dict(Previous=released,PIN=pin))
        text=fresh(raw,'oneup',8)
    once=G.First.once
    text=once(text,Base.PIN,pin)
    line=next(s for s in text.splitlines()if s.startswith('local verifiedHooks='))
    text=once(text,line,line.replace('{169,255,141,57,1,32,86,131}','{169,255,141,57,1,32,89,131}',1))
    text=once(text,"local cookie = 'a7260209e6eb04c8dbe70c3197b0cb4b'","local cookie = '"+COOKIE+"'")
    text=once(text,"local rom = os.getenv('SMB_STDOUT_ROM_SHA') or ''","local rom = CPU_CONTROLLER_OPENING and '"+pin+"' or os.getenv('SMB_STDOUT_ROM_SHA')or''")
    text=once(text,"local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')","local variant = 3")
    text=once(text,'local route=coroutine.create(function()','''local route=coroutine.create(function()
  if CPU_CONTROLLER_OPENING then
   initial=state();previousCommits=commits;switch('settle-start',0)
   while not stopped do tick();coroutine.yield()end;return
  end''')
    text=clone(Point.point_readback,dict(PIN=pin))(text,raw)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    Base.LuaRuntime().compile(text);return text


def cold(raw):
    authenticate(raw);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in(8,2,2,2,32):W.UI.key(m,pad)
    assert N.get(m,'CrossoverMenuIndex')==29 and N.get(m,'SelectedCharacter')==38
    start=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(G.First.Base.Host.Family.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'Player_X_Position')==40 and m.ram[2][0x6cf]==5
            assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            assert all(bytes(m.ram[bank][0x1fe0:0x1ff0]).hex()==COOKIE for bank in(2,3))
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Current genuine Prince linked-menu/Select/Start entry bound')


def source(raw,route,limit):
    text=controller(raw,route)
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',H(raw)):return Engine.run(raw,limit,text=text)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',action='store_true');p.add_argument('--route',choices=('cap','ground'),default='cap');p.add_argument('--limit',type=int,default=3000)
    a=p.parse_args();assert 1000<=a.limit<=4200;raw=G.ROM.read_bytes()
    def deny(*a,**k):raise AssertionError('Prince source probe attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        text=controller(raw,a.route);print('PRINCE_CURRENT_COMPILE '+json.dumps(dict(ROM=H(raw),route=a.route,controller=H(text.encode()),binding=authenticate(raw)),separators=(',',':')),flush=True)
        if not a.source:return 0
        q=source(raw,a.route,a.limit);r=q.get('receipt',{});s=r.get('natural_stock',{})
        keys=('start','actual_mount','cap_ready','standing_admission','standing_landing','running_admission','head_queries','born','mature','collector','collected','credit','completed_at_main_return')
        compact={k:s[k]for k in keys if k in s}
        print('PRINCE_CURRENT_SOURCE '+json.dumps(dict(passed=q['passed'],source_passes=q['source_passes'],controller=q['controller_SHA256'],receipt=q['receipt_SHA256'],inner=q['receipt_inner_SHA256'],reason=r.get('reason'),phase=r.get('phase'),terminal=r.get('terminal'),stock=compact,readback=r.get('new_candidate_readback'),point=r.get('point67_readback')),separators=(',',':')),flush=True)
        return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
