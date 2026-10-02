local function held(f,t) return f>=t and f<t+4 end
local function input()
 local f=emu.getState().frameCount; local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) then inp.a=true end
 if held(f,700) or held(f,740) or held(f,780) then inp.right=true end
 if held(f,840) then inp.a=true end
 emu.setInput(inp,0)
end
local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=930 and not done then
  done=true
  local path=os.getenv('MESEN_CAPTURE_PATH') or '/mnt/data/demons_index_hf9.png'
  local g=io.open(path,'wb'); g:write(emu.takeScreenshot()); g:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
