"""Typed copied/initialized extents instead of unowned predecessor tail102."""
import inspect
import json
from pathlib import Path
import check_dkjr_prince_cold_1103_v102 as T


def main():
    b,q=T.P.image();raw=b['raw'];pr=T.P.PR.O
    def native123(pc,count):
        at=16+123*8192+pc-0xa000;return raw[at:at+count]
    assert native123(0xafd5,8)==bytes.fromhex('080620d0d802d902')
    assert native123(0xafe9,8)==bytes.fromhex('090804d02d013101')
    assert native123(0xbf93,8)==bytes.fromhex('020008d069026b02')
    assert len((pr/'native-runtime-v153.bin').read_bytes())==0x1fdf
    assert len((pr/'native-metadata-v149.bin').read_bytes())==0x17cc
    # Exact immutable decoded source extents. Ex's legacy32zero pages are
    # intentionally retained; other owners preserve the shared clock/tail.
    extents={
        37:{2:[[0,8192]],3:[[0,0x1800],[0x1fe0,0x1ff0]]},
        38:{2:[[0,0x1fcc],[0x1fe0,0x1ff0]],3:[[0,0x1fdf],[0x1fe0,0x1ff0]]},
        39:{2:[[0,0x400],[0x1000,0x1400],[0x1fe0,0x1ff0]],3:[[0,8192]]},
        40:{2:[[0,0x900],[0x1000,0x1800],[0x1fe0,0x1ff0]],3:[[0,8192]]},
    }
    text=inspect.getsource(T.main)
    old="            m=N.fork(seeds[before]);C.fields(m,after)"
    assert text.count(old)==1
    text=text.replace(old,old+";prior_clock=bytes(m.ram[2][0x1fd0:0x1fd4])")
    old="            for bank in [2,3]:assert bytes(m.ram[bank])==bytes(seeds[after].ram[bank]),(before,after,bank)"
    new="""            for bank,ranges in TYPED_EXTENTS[after].items():
                for lo,hi in ranges:
                    assert bytes(m.ram[bank][lo:hi])==bytes(seeds[after].ram[bank][lo:hi]),(before,after,bank,lo,hi)
            assert bytes(m.ram[2][0x1fd0:0x1fd4])==(bytes(4)if after==37 else prior_clock),(before,after,'sharedclock')"""
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace('-v102-','-v104-')
    text=text.replace("bad_header_bytes_rejected=rejected,","bad_header_bytes_rejected=rejected,exact_transition_copied_initialized_extents=TYPED_EXTENTS,sharedclock='Ex37 retains original32pageclear; otherthree retain predecessorDFD0..DFD3',")
    text=text.replace("Path(__file__),Path(P.__file__),Path(C.__file__)","Path(__file__),V102_PATH,Path(P.__file__),Path(C.__file__)")
    text=text.replace("Foreign37/38/39 cold completeprivate images/maps match canonical159.","Foreign37/38/39 cold completeprivate images/maps match canonical159. Transitions compare everynewowner copied/initializedbyte plusbothcompleteheaders;103proves36retainedPrince-tail bytes differ onlybeyondDFCC/outsideheaders. Sharedclock retains predecessor exceptunchangedEx32pageclear.")
    env=dict(T.__dict__,__file__=__file__,TYPED_EXTENTS=extents,V102_PATH=Path(T.__file__))
    exec(compile(text,__file__,'exec'),env);env['main']()
    path=T.O/'native-combined-cold-v104-CPU.json';out=json.loads(path.read_text())
    out['bindings'].update({p.relative_to(T.R).as_posix():T.A.sha(p.read_bytes())for p in [T.O/'native-combined-transition-v103-diagnostic.json',pr/'native-runtime-v153.bin',pr/'native-metadata-v149.bin']})
    path.write_text(json.dumps(out,indent=2)+'\n')


if __name__=='__main__':
    try:main()
    except Exception as error:
        (T.O/'native-combined-cold-v104-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
