"""Bind the retained Arthur 1-1 controls to a ROM without capture writers."""

import re

import probe_arthur_cache_conflict_1123 as Cold


BASE = Cold.R / 'tools/reference/arthur_retained_full11_combat_1102_v13.lua'
BASE_SHA = '388e4baeb0863d11b65dc8f553fedf7cae2dbec86b046930d59c22b25f21022f'
FLOWER = Cold.R / 'tools/reference/arthur_retained_flower_maturity_1102_v12.lua'
FLOWER_SHA = '30535c0ea71f041a586703969f52f8ee0063e4fcadfe410abe41ae5b8f388a47'
FINISH = r'''local function finish(passed,reason)
 if done then return end;done=true
 local ok=passed and sourceSteps>0 and r('ArHostReady')==167 and startLives==2
 print('SMB_NATIVE_RECEIPT '..string.format(
  '{"passed":%s,"reason":"%s","ROM_SHA256":"%s","controller_only":true,"files":0,"images":0,"frames":%d,"source_steps":%d,"main_calls":%d,"x":%d,"y":%d,"world":%d,"level":%d,"engine":%d,"lives":%d,"pipes":%d,"gaps":%d,"grounded_returns":%d,"source_injuries":%d}',
  tostring(ok),reason,C.sha,frame,sourceSteps,mainCalls,wx(),r('Player_Y_Position'),
  r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),r('NumberofLives'),
  clearedPipes,clearedGaps,grounded,injuryCalls))
 emu.stop(ok and 0 or 1)
end
'''
FLOWER_FINISH = r'''local function finish(passed,reason)
 if done then return end;done=true
 local ok=passed and seenItem and mature and torchCalls>0 and r('ArHostReady')==167
 print('SMB_NATIVE_RECEIPT '..string.format(
  '{"passed":%s,"reason":"%s","ROM_SHA256":"%s","controller_only":true,"files":0,"images":0,"frames":%d,"x":%d,"y":%d,"lives":%d,"weapon":%d,"pickup":%d,"mature":%s,"torch_calls":%d,"source_steps":%d}',
  tostring(ok),reason,C.sha,frame,wx(),r('Player_Y_Position'),r('NumberofLives'),
  r('ArR_053A'),r('ArLastPickup'),tostring(mature),torchCalls,sourceSteps))
 emu.stop(ok and 0 or 1)
end
'''


def controller(raw):
    original = BASE.read_bytes()
    assert Cold.H(original) == BASE_SHA
    text = original.decode()

    def replace(before, after):
        nonlocal text
        assert text.count(before) == 1, before
        text = text.replace(before, after, 1)

    start, stop = text.index('local injuryLog='), text.index('local clearedPipes=')
    text = text[:start] + 'local underground, lastGroundedMain, grounded, done=nil,nil,0,false\n' + text[stop:]
    start, stop = text.index('local function shot('), text.index('local function block(')
    text = text[:start] + 'local function shot()end\nlocal function row()end\n' + FINISH + text[stop:]
    start, stop = text.index('  if age%36==0 or'), text.index('  if r(\'NumberofLives\')~=startLives')
    text = text[:start] + text[stop:]
    line = next(line for line in text.splitlines() if 'injuryLog:write' in line)
    replace(line + '\n', '')
    replace("elseif phase=='play' and age>=120 then b=travel() end",
            "elseif phase=='play' and age>=120 and not underground then b=travel() end")
    replace("   finish(clearedPipes==4 and clearedGaps==3,'Reached actual 1-2 gameplay');return",
            "   underground=true\n"
            "   if r('Player_State')~=0 then grounded=0\n"
            "   elseif mainCalls~=lastGroundedMain then grounded=grounded+1 end\n"
            "   lastGroundedMain=mainCalls\n"
            "   if grounded>=25 then\n"
            "    finish(clearedPipes==4 and clearedGaps==3,'Reached 1-2 with 25 more movement updates')\n"
            "   end;return")

    return bind(raw, text)


def flower_controller(raw):
    original = FLOWER.read_bytes()
    assert Cold.H(original) == FLOWER_SHA
    text = original.decode()
    start, stop = text.index('local highChanges='), text.index('local clearedPipes=')
    text = text[:start] + 'local done=false\n' + text[stop:]
    start, stop = text.index('local function shot('), text.index('local function block(')
    text = text[:start] + 'local function shot()end\nlocal function row()end\n' + FLOWER_FINISH + text[stop:]
    start = text.index('emu.addMemoryCallback(function(_,value)')
    end = 'end,emu.callbackType.write,assert(L.Player_Y_HighPos))\n'
    stop = text.index(end, start) + len(end)
    return bind(raw, text[:start] + text[stop:])


def bind(raw, text):
    names = set(re.findall(r"r\('([A-Za-z0-9_]+)'", text))
    names.update(re.findall(r'\bL\.([A-Za-z0-9_]+)', text))
    bundle = dict(Cold.W.Symbols.bundle(), raw=raw)
    fields = {name: Cold.W.address(bundle, name) for name in sorted(names)}
    banks = {name: (Cold.W.location(bundle, name) - 16) // 8192
             for name in sorted(set(re.findall(r'\bB\.([A-Za-z0-9_]+)', text)))}
    header = '\n'.join((
        'local C=' + Cold.Stock.value(dict(sha=Cold.H(raw))),
        'local L=' + Cold.Stock.value(fields),
        'local B=' + Cold.Stock.value(banks),
        "assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact Arthur stage ROM')",
    ))
    text = header + '\n' + text
    assert not any(v in text for v in ('io.open', 'emu.takeScreenshot', 'emu.write', 'setState', 'loadState'))
    Cold.Stock.LuaRuntime().compile(text)
    return text.encode()
