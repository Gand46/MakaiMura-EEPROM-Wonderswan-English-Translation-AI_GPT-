local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=60 and not done then done=true; local g=io.open('/mnt/data/hf11_work/evidence/simplecap.png','wb');g:write(emu.takeScreenshot());g:close();emu.stop(0) end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
