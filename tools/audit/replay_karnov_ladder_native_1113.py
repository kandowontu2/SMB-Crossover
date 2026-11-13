"""Pure private level-DATA fixture and readonly native Ladder controller."""

from hashlib import sha256
from functools import lru_cache
import json
import re

import compose_karnov_ladder_native_1113 as Feature
import audit_current_roster_powerups_1110 as Roster

R=Feature.Owner.R
SOURCE=R/'tools/reference/karnov_ladder_native_1113.lua'
CURRENT='526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2'
FIXTURE='fbe4c2b392eda216ac357f4c69a7bd3ede5720da5bc9bf844b8bbce19d81e156'
POINTS=(80,192,304,416,528)
TOP=160


def digest(data):return sha256(data).hexdigest()


@lru_cache(maxsize=1)
def feature(candidate):
    """Authenticate the frozen current62 composition without changing it."""
    assert digest(candidate)==CURRENT,'This native factory is frozen on exact526'
    parent=Feature.inverse_current(candidate)
    assert digest(parent)==Feature.Audit.STEVE_CURRENT
    image,info=Feature.proposal_current(parent);assert image==candidate
    return info


def fixture(candidate):
    """Five lower native questions; level/enemy bytes only, never install."""
    feature(candidate)
    b=dict(Roster.W.Symbols.bundle(),raw=candidate)
    level=Roster.W.location(b,'L_GroundArea6');enemy=Roster.W.location(b,'E_GroundArea6')
    before=bytes.fromhex('502107814724570063017701c97168')
    assert candidate[level:level+15]==before
    assert candidate[enemy:enemy+5]==bytes.fromhex('1ec2006b06')
    stage=bytearray((0x50,0x21));page=0
    for x in POINTS:
        next_page=x//256;assert next_page-page in(0,1)
        stage.extend((((x//16)&15)*16+(TOP//16-2),0x80 if next_page!=page else 0))
        page=next_page
    stage.extend(b'\xfd'*(15-len(stage)))
    result=bytearray(candidate);result[level:level+15]=stage;result[enemy]=255
    allowed=set(range(level,level+15))|{enemy}
    changed=[i for i,(a,b)in enumerate(zip(candidate,result))if a!=b]
    assert set(changed)<=allowed and digest(result)==FIXTURE
    return bytes(result),dict(feature_SHA256=CURRENT,fixture_SHA256=digest(result),
        private_level_DATA_only=True,never_install=True,code_or_CHR_changes=0,
        runtime_state_writes=0,new_helpers=0,changed_bytes=len(changed),
        edits=[dict(file_offset=level,before=before.hex(),after=stage.hex()),
            dict(file_offset=enemy,before='1e',after='ff')],
        native_question_blocks=[dict(left=x,center=x+8,top=TOP)for x in POINTS],
        enemy_stream_terminated=True,natural_stock_fifth_item_qualification=False,output_files=0)


def inverse_fixture(image):
    assert digest(image)==FIXTURE,'Exact private DATA fixture required'
    result=bytearray(image)
    b=dict(Roster.W.Symbols.bundle(),raw=image)
    at=Roster.W.location(b,'L_GroundArea6');result[at:at+15]=bytes.fromhex('502107814724570063017701c97168')
    result[Roster.W.location(b,'E_GroundArea6')]=0x1e
    result=bytes(result);assert digest(result)==CURRENT and fixture(result)[0]==image
    return result


def controller(candidate,*,images=False):
    info=feature(candidate);private,proof=fixture(candidate)
    b=dict(Roster.W.Symbols.bundle(),raw=candidate)
    text=SOURCE.read_text()
    names=set(re.findall(r"\br\('([^']+)'",text));names.update(re.findall(r'\bL\.(\w+)',text))
    fields={name:Roster.W.address(b,name)for name in sorted(names)}
    pre='local L={'+','.join(f'{n}={v}'for n,v in fields.items())+'}\n'
    pre+=f'local FIXTURE_SHA={json.dumps(proof["fixture_SHA256"])}\n'
    pre+=f'local FEATURE_SHA={json.dumps(CURRENT)}\nlocal COOKIE={json.dumps(info["cookie"].hex())}\n'
    pre+='local POINTS={'+','.join(map(str,POINTS))+'}\n'
    pre+='local P={'+','.join(f'{n}={v}'for n,v in info['symbols'].items())+'}\n'
    for name in('GameLoop','HandlePowerUpCollision','NativeRarePlayerHeadCollisionCore'):
        pre+=f'local {name}_OFFSET={Roster.W.location(b,name)-16}\n'
    pre+='local WANT_IMAGES='+str(images).lower()+'\n'
    result=pre+text
    for forbidden in('emu.write','emu.setState','io.open','loadState','saveState'):
        assert forbidden not in result,forbidden
    assert result.count('emu.takeScreenshot()')==1 and 'assert(#imageTags<2' in result
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    assert digest(DLL.read_bytes())==DLL_SHA
    LuaRuntime().compile(result)
    return result


def factory(parent=None,*,images=False):
    """Root receives bytes/text in memory; this function writes no output."""
    if parent is None:parent=Feature.Owner.NIGHTLY.read_bytes()
    assert digest(parent)==Feature.Audit.STEVE_CURRENT
    candidate,info=Feature.proposal_current(parent);assert digest(candidate)==CURRENT
    private,proof=fixture(candidate);text=controller(candidate,images=images)
    return private,text,dict(proof,controller_SHA256=digest(text.encode()),controller_bytes=len(text.encode()),
        maximum_stdout_PNGs=2 if images else 0,source_SHA256=digest(SOURCE.read_bytes()))


if __name__=='__main__':
    _,_,report=factory();print(json.dumps(report,separators=(',',':')),flush=True)
