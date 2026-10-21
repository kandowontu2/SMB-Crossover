-- Independent native0-only validation of the entire synthetic corner matrix.
local root=assert(TEST_DIR:match('^(.*)/tools/playthroughs/'))
NATIVE_WALL_CONTROL_ONLY=true
dofile(root..'/tests/menu-bootstrap.lua')
dofile(root..'/tests/native-wall-corner.lua')
