"""Root-invoked native smoke runner; default validates sources without output.

--run is the only path that writes a controller or invokes the existing Mesen
queue. The candidate ROM must already exist under Root's own task ownership.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse
import contextlib
import io
import json
import re

import compose_sonic_original_motion_1122 as Motion
import repair_contra_force_beans_ground_1122 as Beans

R = Motion.R
LUA = R/'tools/playthroughs/sonic_original_motion_smoke_1122.lua'
SONIC_ONLY_SHA = 'd1b2138dc59e714ae653cbb7067cb32766f5f14de24965f7c980b81dac48903c'
FORMS = ('sonic', 'super')
SHARED = R/'build/smb2-flag-native-1113'


def H(data): return sha256(data).hexdigest()


@lru_cache(maxsize=2)
def reference(parent):
    """a6 is metadata only when actual installed base is exact Beans32."""
    if H(parent) == Motion.PIN: return parent
    assert H(parent) == Beans.CANDIDATE, 'Only exact a6 or delivered Beans32 base'
    restored = Beans.inverse(parent)
    assert H(restored) == Motion.PIN == Beans.PARENT
    return restored


@lru_cache(maxsize=2)
def proposal(parent):
    """Compose the same reviewed Sonic spans onto actual a6 or Beans32."""
    a6 = reference(parent)
    sonic, receipt = Motion.proposal(a6)
    assert H(sonic) == SONIC_ONLY_SHA and len(parent) == len(a6) == len(sonic)
    spans = [(r['file'],r['bytes']) for r in receipt['spans']] + [(Motion.COOKIE_AT,16)]
    owned = {i for at,size in spans for i in range(at,at+size)}
    sonic_delta = {i for i,(a,b) in enumerate(zip(a6,sonic,strict=True)) if a!=b}
    assert sonic_delta <= owned
    beans_spans = [(Beans.TAIL,32),(Beans.GATE,len(Beans.GATE_BEFORE)),*((at,16) for at in Beans.COOKIES)]
    beans_owned = {i for at,size in beans_spans for i in range(at,at+size)}
    assert not owned & beans_owned, 'Declared Sonic/Beans ownership overlap'
    base_delta = {i for i,(a,b) in enumerate(zip(a6,parent,strict=True)) if a!=b}
    assert base_delta <= beans_owned and not base_delta & owned
    out = bytearray(parent)
    for at,size in spans:
        assert parent[at:at+size] == a6[at:at+size], 'Dirty actual Sonic span'
        out[at:at+size] = sonic[at:at+size]
    result = bytes(out)
    merged_delta = {i for i,(a,b) in enumerate(zip(parent,result,strict=True)) if a!=b}
    assert merged_delta == sonic_delta, 'Whole-length same-index Sonic delta required'
    assert all(result[i] == parent[i] for i in range(len(parent)) if i not in owned)
    assert all(result[at:at+size] == parent[at:at+size] for at,size in beans_spans)
    assert all(Motion.page(result,p) == Motion.page(sonic,p) for p in Motion.COOKIE_PAGES)
    q = dict(receipt,parent_SHA256=H(parent),candidate_SHA256=H(result),
             sonic_only_candidate_SHA256=SONIC_ONLY_SHA,metadata_reference_a6_SHA256=Motion.PIN,
             base_role='a6' if H(parent)==Motion.PIN else 'delivered Beans32',
             Beans_preserved=True,declared_spans_disjoint=True,whole_length_same_index_delta=True,
             all_actual_base_bytes_outside_Sonic_spans_exact=True,actual_base_changed_bytes=len(base_delta),
             Beans_spans=[dict(file=at,bytes=size) for at,size in beans_spans])
    return result,q


def value(v):
    if isinstance(v, dict): return '{'+','.join('['+value(k)+']='+value(x) for k,x in sorted(v.items()))+'}'
    if isinstance(v, (list, tuple)): return '{'+','.join(map(value,v))+'}'
    if isinstance(v, str): return json.dumps(v)
    if isinstance(v, bool): return 'true' if v else 'false'
    if v is None: return 'nil'
    assert isinstance(v, (int, float)); return str(v)


@lru_cache(maxsize=4)
def bindings(parent, candidate, form):
    assert form in FORMS
    expected, receipt = proposal(parent)
    assert H(expected) == H(candidate) and candidate == expected, 'Exact private composed motion candidate only'
    import current_sonic_stock_binding_1122 as Metadata
    old = Metadata.bindings(reference(parent), form, 'star')
    q = {k: deepcopy(old[k]) for k in ('form','select','name','CHR','ram')}
    kernel = Motion.kernel(candidate)
    def loaded(pc):
        if 0xa000 <= pc < 0xc000: return kernel[pc-0xa000:]
        for start, page in ((0xd000,328),(0xd400,333),(0xd800,334)):
            if start <= pc < start+1024: return Motion.page(candidate,page)[pc-start:]
        raise AssertionError(('Outside current private code',hex(pc)))
    hooks = {}
    for name in ('GameLoop','SonicHostMain','OriginalFrame'):
        h = deepcopy(old['hooks'][name]); pc, tag = h['pc'], h['tag']
        if tag >= 128:
            at = 16+(tag&127)*8192+(pc&8191)
            h['hex'] = candidate[at:at+32].hex()
            h['bank_SHA256'] = H(candidate[16+(tag&127)*8192:16+((tag&127)+1)*8192])
        else: h['hex'] = loaded(pc)[:32].hex()
        h['offset'] = (tag&127)*8192+(pc&8191)
        hooks[name] = h
    ctor = int.from_bytes(Motion.page(candidate,328)[58:60],'little')
    assert ctor == 0xbebb
    hooks['SonicHostConstruct'] = dict(pc=ctor,tag=3,offset=3*8192+(ctor&8191),hex=loaded(ctor)[:32].hex())
    assert hooks['SonicHostMain']['pc'] == 0xbd7a and hooks['OriginalFrame']['pc'] == 0xbbb0
    q.update(sha=H(candidate),cookie=receipt['cookie'],hooks=hooks,
             parent_SHA256=H(parent),metadata_reference_a6_SHA256=Motion.PIN,
             motion_source_SHA256=receipt['source_SHA256'])
    return q


@lru_cache(maxsize=4)
def controller(parent, candidate, form):
    config = bindings(parent,candidate,form)
    return 'local SONIC_CONFIG='+value(config)+'\n'+LUA.read_text(encoding='utf-8')


def report(form, result, validation):
    """Emit actual native diagnostics before raising on an unsuccessful run."""
    print('SONIC MOTION '+json.dumps(dict(form=form,validation=validation,
          script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],
          receipt=result['receipt']),separators=(',',':')),flush=True)
    assert result['passed'] and result['outputs_written']==0 and not result['images'],result['receipt']


def failure_diagnostics_probe():
    stream = io.StringIO()
    fixture = dict(passed=False,outputs_written=0,images=[],script_SHA256='source-mock',
                   receipt_SHA256='source-mock',receipt=dict(passed=False,reason='diagnostic order fixture'))
    with contextlib.redirect_stdout(stream):
        try: report('source-mock',fixture,dict(source_only=True))
        except AssertionError: pass
        else: raise AssertionError('Failed native result accepted')
    assert 'diagnostic order fixture' in stream.getvalue()
    return True


def validate(parent, candidate):
    from check_ff_stdout_controller_source_1110 import LuaRuntime, DLL, DLL_SHA
    assert H(DLL.read_bytes()) == DLL_SHA
    source = LUA.read_text(encoding='utf-8')
    executable = '\n'.join(line.split('--',1)[0] for line in source.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)', executable)
    assert 'SMB_NATIVE_RECEIPT ' in source
    required = set(re.findall(r"r\('([A-Za-z0-9_]+)'",source))
    summaries = []
    runtime = LuaRuntime()
    for form in FORMS:
        q = bindings(parent,candidate,form)
        assert required <= set(q['ram'])
        assert set(q['hooks']) == {'GameLoop','SonicHostMain','SonicHostConstruct','OriginalFrame'}
        text = controller(parent,candidate,form)
        runtime.compile(text)
        summaries.append(dict(form=form,select=q['select'],name=q['name'],cookie=q['cookie'],
                              script_SHA256=H(text.encode()),script_bytes=len(text.encode()),
                              callback_entries={k:dict(pc=h['pc'],tag=h['tag']) for k,h in q['hooks'].items()}))
    return dict(passed=True,source_compile_only=True,ROM_SHA256=H(candidate),
                composition=proposal(parent)[1],
                Lua_source_SHA256=H(LUA.read_bytes()),runner_source_SHA256=H(Path(__file__).read_bytes()),
                forms=summaries,failure_receipt_emitted_before_assertion=failure_diagnostics_probe(),outputs=0,native_Mesen=False,
                scope='Candidate-specific Lua5.4 syntax, native field presence, exact hook/header bindings and controller-only API scan. No gameplay execution or native smoke pass.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent',type=Path,default=Motion.ROM)
    parser.add_argument('--rom',type=Path,help='Root-owned existing exact private motion candidate matching the actual supported base')
    parser.add_argument('--output',type=Path,help='Root-owned output root for --run only')
    parser.add_argument('--shared-slot',action='store_true',help='Root only: temporarily reuse the established two-file native slot and restore it in finally')
    parser.add_argument('--form',choices=(*FORMS,'both'),default='both')
    parser.add_argument('--run',action='store_true',help='Root only: invoke shared Mesen queue after source validation')
    parser.add_argument('--validate',action='store_true',help='Explicit source-only mode, the default')
    args = parser.parse_args()
    assert not(args.run and args.validate)
    assert not args.shared_slot or args.run, '--shared-slot requires explicit --run'
    parent = args.parent.read_bytes()
    candidate = args.rom.read_bytes() if args.rom else proposal(parent)[0]
    if not args.run:
        def deny(*a,**kw): raise AssertionError('Source validation attempted output/process')
        with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
            q = validate(parent,candidate)
            a6 = reference(parent)
            other = Beans.compose(a6) if H(parent)==Motion.PIN else a6
            other_candidate, _ = proposal(other)
            other_validation = validate(other,other_candidate)
            q['other_supported_base_source_validation'] = other_validation
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
        return
    assert args.shared_slot or(args.rom and args.output), '--run needs --shared-slot or an existing ROM/output pair'
    output = SHARED.resolve() if args.shared_slot else args.output.resolve()
    if args.shared_slot and args.output: assert args.output.resolve()==output
    assert output.is_relative_to(R/'build') and output != (R/'build').resolve()
    import build_storage_guard_v1 as Storage
    from run_stdout_mesen_1110 import run
    Storage.preflight(private_root=output,reserved_files=0 if args.shared_slot else 1,fresh=True)
    validation = validate(parent,candidate)
    script = output/'controller.lua'
    target = output/'candidate.nes' if args.shared_slot else args.rom.resolve()
    originals, downloads_guard = None, None
    if args.shared_slot:
        from nightly_patch_guard_v1 import check
        assert {p.name for p in output.iterdir()}=={'candidate.nes','controller.lua'}, 'Exact existing two-file shared slot'
        downloads_guard = check(Motion.ROM)
        assert Motion.ROM.read_bytes()==parent and downloads_guard['ROM_sha256']==H(parent), 'Actual Downloads base must match'
        originals = (target.read_bytes(),script.read_bytes())
    else: output.mkdir(parents=True,exist_ok=True)
    forms = FORMS if args.form=='both' else (args.form,)
    try:
        if args.shared_slot: target.write_bytes(candidate)
        for form in forms:
            script.write_text(controller(parent,candidate,form),encoding='utf-8',newline='\n')
            try:
                q = run(script,target,output/'capture',H(candidate),180,extra_env={'SMB_STDOUT_IMAGES':'0'})
            except Exception as error:
                print('SONIC MOTION RUNNER FAILURE '+json.dumps(dict(form=form,ROM_SHA256=H(candidate),
                      script_SHA256=H(script.read_bytes()),error=repr(error)),separators=(',',':')),flush=True)
                raise
            report(form,q,validation)
        assert target.read_bytes()==candidate and args.parent.read_bytes()==parent
    finally:
        if originals is not None:
            target.write_bytes(originals[0]);script.write_bytes(originals[1])
            assert (target.read_bytes(),script.read_bytes())==originals
            assert {p.name for p in output.iterdir()}=={'candidate.nes','controller.lua'}
            after = check(Motion.ROM)
            assert after==downloads_guard and Motion.ROM.read_bytes()==parent
            print('SONIC MOTION SHARED RESTORED '+json.dumps(dict(files=2,Downloads_SHA256=H(parent),
                  Downloads_patch_guard_before_after=True,nightly_not_replaced=True),separators=(',',':')),flush=True)


if __name__ == '__main__': main()
