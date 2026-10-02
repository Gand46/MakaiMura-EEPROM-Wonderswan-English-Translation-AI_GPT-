local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=60 and not done then
  done=true
  local g=io.open('/mnt/data/makai_hf7_work/evidence/test_runtime.png','wb'); g:write(emu.takeScreenshot()); g:close()
  local h=io.open('/mnt/data/makai_hf7_work/build/test_runtime.txt','w'); h:write('frame='..tostring(f)); h:close()
  emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
