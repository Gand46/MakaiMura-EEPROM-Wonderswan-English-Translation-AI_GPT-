local function held(f,t) return f>=t and f<t+4 end
local function input()
 local f=emu.getState().frameCount; local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) or held(f,700) or held(f,820) or held(f,940) then inp.a=true end
 emu.setInput(inp,0)
end
local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=1020 and not done then
  done=true
  local g=io.open(os.getenv('MESEN_CAPTURE_PATH'),'wb'); g:write(emu.takeScreenshot()); g:close()
  local r=io.open(os.getenv('MESEN_LUA_REPORT'),'w'); r:write('{"route":"System Records","frame":'..f..',"access":"SCRIPTED_NATURAL"}'); r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
