local function held(f,t) return f>=t and f<t+3 end
local downs={}; for i=0,48 do downs[#downs+1]=930+i*18 end
local function input()
 local f=emu.getState().frameCount; local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) then inp.a=true end
 if held(f,700) then inp.right=true end
 if held(f,830) then inp.a=true end
 for _,t in ipairs(downs) do if held(f,t) then inp.down=true end end
 if held(f,1840) then inp.a=true end
 emu.setInput(inp,0)
end
local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=1900 and not done then
  done=true
  local path=os.getenv('MESEN_CAPTURE_PATH')
  local g=io.open(path,'wb'); g:write(emu.takeScreenshot()); g:close()
  local r=io.open(os.getenv('MESEN_LUA_REPORT'),'w'); r:write('{"route":"COMMANDS password popup","frame":'..f..',"access":"SCRIPTED_NATURAL"}'); r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
