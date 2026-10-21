-- Simon.as819..899: successful jumps enter ST_JUMP and stop attackAnimTmr.
-- Air direction controls preserve facing except when the fresh jump sets it.
SOURCE_MOVEMENT_CHARACTER=5
SOURCE_SIMON_JUMPS=true
dofile(TEST_DIR..'link-source-movement.lua')
