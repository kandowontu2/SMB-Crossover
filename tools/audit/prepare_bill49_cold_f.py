"""Correct only the relocated pure helper's initial mapped-bank test setup."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / 'build/verification/agent49o2-bill-shape-components-e'
OUT = ROOT / 'build/verification/root49-bill-cold-f'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    source = E / 'verify_cpu.py'
    assert sha(source) == '5aea4e8890252ee213a88675a25d2a065bef88e20f27314169ae2f6ccb2d4dc4'
    negative = ROOT / 'build/verification/root49s2-e-bill-cold-mmc3-a.json'
    n = json.loads(negative.read_text())
    assert n['status'] == 'FAIL_COMPONENT_UNWAIVED' and n['case'] == 0
    text = source.read_text()
    old = 'def execute(im,binding,name,spec,number,*,scope=None,stop=None,caller=None):'
    assert text.count(old) == 1
    text = text.replace(old, old.replace('caller=None)', 'caller=None,entry_bank=None)'))
    old = '  m=Memory(im,binding,number,bank)'
    assert text.count(old) == 1
    text = text.replace(old, '  if entry_bank is not None:bank=entry_bank\n' + old)
    old = "a=execute(old,O,'CrossoverBlockSize',s,case);b=execute(new,B,'BillBankedBlockSize',s,case);exact(a,b,current)"
    assert text.count(old) == 1
    new = "a=execute(old,O,'CrossoverBlockSize',s,case,entry_bank=new.hook('BillBankedBlockSize')['physical_bank']);b=execute(new,B,'BillBankedBlockSize',s,case);assert a['initial']==b['initial'],'Pure calls must have identical complete RAM inputs';exact(a,b,current)"
    text = text.replace(old, new)
    # Keep all E dependency checks; import them from their original frozen home.
    old = 'from common import HERE,ROOT,admission,image_class,verify_frozen,info'
    assert text.count(old) == 1
    text = text.replace(old, 'sys.path.insert(0,' + repr(str(E)) + ')\n' + old)
    OUT.mkdir()
    core = OUT / 'verify_cpu.py'
    core.write_text(text)
    compile(text, str(core), 'exec')
    (OUT / 'preparation.json').write_text(json.dumps(dict(
        status='PREPARED_SETUP_CORRECTION_NO_EXECUTION_CLAIM',
        original_cpu=dict(path=str(source.relative_to(ROOT)), sha256=sha(source)),
        original_negative=dict(path=str(negative.relative_to(ROOT)), sha256=sha(negative)),
        corrected_core=dict(path=str(core.relative_to(ROOT)), sha256=sha(core)),
        script_sha256=sha(__file__),
        changes=[
            'Pure old resident helper starts with the same A000 bank as the relocated helper; both mappings are valid entry states.',
            'Assert identical all10240 initial RAM bytes before retaining original exact register/RAM/write comparison.',
            'Actual caller tests, all256 P sweeps, source oracle, ordered transport write predictions, and all rejection assertions are unchanged.',
            'Original frozen E dependencies remain imported and verified at their original paths.'],
        runtime_changed=False, masks_added=[]), indent=2) + '\n')
    print(str(core), sha(core))


if __name__ == '__main__':
    main()
