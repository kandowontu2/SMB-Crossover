"""Bind retained native guards to the private V42 ROM; run one worker at a time."""
from pathlib import Path
import argparse, csv, hashlib, json, re, subprocess, sys
from check_tmnt_render_oa import load, address, location

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
V = D / 'mmc3-parser-v42'
EXPECTED = 'bc89a756e24b354bfe1455d1c0dd942c9ef97392a721f2dc2e56da17e8e4183a'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def lua(v):
    if v is None: return 'nil'
    if isinstance(v,bool): return 'true' if v else 'false'
    if isinstance(v,str): return json.dumps(v)
    if isinstance(v,list): return '{'+','.join(lua(x) for x in v)+'}'
    if isinstance(v,dict): return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'
    return str(v)

def parse_table(text):
    tokens = re.findall(r'"(?:[^"\\]|\\.)*"|-?\d+|true|false|nil|[{}\[\]=,]', text)
    index = 0
    def value():
        nonlocal index
        token = tokens[index]; index += 1
        if token == '{':
            values, mapping = [], {}
            while tokens[index] != '}':
                if tokens[index] == '[':
                    index += 1; key = value(); assert tokens[index] == ']'; index += 1
                    assert tokens[index] == '='; index += 1; mapping[key] = value()
                else: values.append(value())
                if tokens[index] == ',': index += 1
            index += 1
            assert not(values and mapping)
            return mapping if mapping else values
        if token.startswith('"'): return json.loads(token)
        if token in ('true', 'false', 'nil'): return {'true': True, 'false': False, 'nil': None}[token]
        return int(token)
    return value()

def hook(b, name, delta=0, size=8):
    p = location(b, name) + delta
    return dict(address=address(b, name)+delta, physical_bank=(p-16)//8192,
                bytes=list(b['raw'][p:p+size]), label=name, delta=delta, rom_offset=p)

def bind_guard(rom, out):
    b = load(rom)
    original = D / 'mmc3-static-call-v37/full-roster-v1/native-guard.lua'
    text = original.read_text()
    configs = {}
    for name in ['TINY_CALL_GUARD', 'MMC3_ROUTE_GUARD', 'MOTION_RAM', 'MOTION_HOOK']:
        match = re.search(r'^'+name+r'=(.*)$', text, re.M)
        configs[name] = parse_table(match[1])
        text = text[:match.start()] + text[match.end():]
    tiny, cache = configs['TINY_CALL_GUARD'], configs['MMC3_ROUTE_GUARD']
    tiny['common'] = hook(b, 'FarCallCommon', size=49)
    assert tiny['start'] == 0x155 and tiny['stack_floor'] == 0x5b
    assert tiny['mutable'] == {'319': True, '342': True, '346': True, '344': True, '345': True}
    # These aliases are the actual source SMC operand locations, unchanged in V42.
    assert address(b, 'NextBank') == 0x13f
    for name in ['ram']:
        cache[name] = {n: address(b,n) for n in cache[name] if n in b['syms']}
    cache['raw_chr'] = (V/'source/chr/characters/oversized-raw.chr').as_posix()
    assert Path(cache['raw_chr']).stat().st_size == 1048576
    for key in ['nmi', 'nmi_end', 'irq']:
        h = cache[key]; cache[key] = hook(b, h['label'], h.get('delta',0))
    # Resolve addresses of linked cache tables from their original guard labels.
    old = load(D/'mmc3-static-call-v37/candidate.nes')
    bindings = []
    for key in ['page_lo', 'page_high', 'masks', 'masks_high']:
        aliases = [n for n in old['syms'] if address(old,n)==cache[key] and n in b['syms']]
        assert aliases, (key,cache[key])
        chosen = next((n for n in aliases if not n.startswith('_')), aliases[0])
        bindings.append(dict(field=key,label=chosen,old=cache[key],actual=address(b,chosen)))
        cache[key] = address(b,chosen)
    configs['MOTION_RAM'] = {n: address(b,n) for n in configs['MOTION_RAM'] if n in b['syms']}
    size = int(b['syms']['GameLoop']['size'])
    configs['MOTION_HOOK'] = hook(b,'GameLoop',size-1)
    assert configs['MOTION_HOOK']['bytes'][0] == 0x60
    path=out/'native-guard.lua'
    path.write_text('OUTPUT=ROSTER_CONFIG.out\n'+'\n'.join(n+'='+lua(v) for n,v in configs.items())+'\n'+text)
    receipt=dict(ROM_sha256=sha(rom),original_guard_sha256=sha(original),guard_sha256=sha(path),
                 protected_tiny_bytes=6,protected_resident_bytes=49,stack_floor=91,
                 smc_fields=cache['smc_fields'],common=tiny['common'],table_bindings=bindings,
                 hooks={k:cache[k] for k in ['nmi','nmi_end','irq']},motion=configs['MOTION_HOOK'])
    (out/'guard-bindings.json').write_text(json.dumps(receipt,indent=2))
    return b,path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rom',type=Path,default=V/'candidate.nes')
    p.add_argument('--identity',choices=['sophia','chip','zelda2'],default='sophia')
    p.add_argument('--mode',choices=['easy','hard'],default='hard')
    p.add_argument('--policy',type=Path)
    p.add_argument('--frames',type=int,default=16000)
    p.add_argument('--sophia-hold-fire',action='store_true')
    p.add_argument('--sophia-wide-fire',action='store_true')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    assert not out.is_relative_to(ROOT)
    if a.rom.name=='candidate.nes' and a.rom.parent==V: assert sha(a.rom)==EXPECTED
    b,guard=bind_guard(a.rom,out)
    policy=a.policy or D/'mmc3-static-call-v37/native-sophia-v2/fresh/policy.lua'
    if a.identity=='chip' and a.policy is None:
        policy=D/'chip-ceiling-feedback-v1/mmc3/native-routes-v2/chip-easy-policy.lua'
    body=policy.read_text();first,body=body.split('\n',1)
    assert first.startswith('dofile('),first
    bindings=[]
    def bind(m):
        name,old=m[1],int(m[2])
        if name not in b['syms']: return m[0]
        actual=address(b,name);bindings.append(dict(symbol=name,old=old,actual=actual))
        return 'L.'+name+'='+str(actual)
    body=re.sub(r'^L\.(\w+)=(\d+)\s*$',bind,body,flags=re.M)
    if a.sophia_hold_fire:
        body='local baseline=(function()\n'+body+'\nend)()\nreturn function(c) local b=baseline(c); if c.char==11 then b.b=true end; return b end\n'
    if a.sophia_wide_fire:
        body='local baseline=(function()\n'+body+'\nend)()\nreturn function(c) local b=baseline(c); if c.char==11 then b.b=c.poll%16<8 end; return b end\n'
    linked=out/'policy.lua';linked.write_text('dofile('+lua(guard.as_posix())+')\n'+body)
    driver=D/'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'
    # Only add the explicit no-settings-save flag; retained runner and controller remain frozen.
    driver_text=driver.read_text()
    marker="'--option=--nes.ramPowerOnState=AllZeros'"
    assert marker in driver_text
    driver_text=driver_text.replace(marker,"'--option=--doNotSaveSettings',"+marker)
    private=out/'bound-runner.py';private.write_text(driver_text)
    route=out/(a.identity+'-'+a.mode)
    command=[sys.executable,str(private),a.identity,'--rom',str(a.rom),'--output',str(route),
             '--mapper','mmc3','--behavior',a.mode,'--frames',str(a.frames),'--capture','12',
             '--policy',str(linked),'--timeout','300']
    with (out/'host.log').open('w') as log:
        result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    manifest=json.loads((route/'manifest.json').read_text())
    guards={n:json.loads((route/(n+'.json')).read_text()) if (route/(n+'.json')).exists() else {}
            for n in ['full-smc-guard','mmc3-cache-guard','completed-loop-motion']}
    native=manifest.get('result') or {}
    passed=bool(result.returncode==0 and native.get('cleared') and native.get('deaths')==0 and all(v.get('passed') for v in guards.values()))
    proof=dict(passed=passed,goal_complete=False,adopted=False,ROM_sha256=sha(a.rom),
               identity=a.identity,mode=a.mode,exit=result.returncode,result=native,guards=guards,
               route=str(route),source_policy_sha256=sha(policy),linked_policy_sha256=sha(linked),
               actual_symbol_bindings=bindings,scope='Exact-ROM ordinary-controller full1-1 native architecture route. Complete tiny and49-byte resident code, SP>=5b, five SMC operands/NMI bank restoration, actual CHR/cache/VBlank/OAM and unchanged committed motion bounds. Direct independent PPU replay and performance are separate.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
    raise SystemExit(0 if passed else 1)

if __name__=='__main__':main()
