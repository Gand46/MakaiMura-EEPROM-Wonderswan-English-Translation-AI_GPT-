local function held(f,t) return f>=t and f<t+5 end
local function input()
 local f=emu.getState().frameCount; local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) then inp.a=true end
 if held(f,720) or held(f,900) or held(f,1080) then inp.right=true end
 if held(f,1260) then inp.a=true end
 emu.setInput(inp,0)
end
local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=1400 and not done then
  done=true
  local h=io.open('/mnt/data/demons_index_wram.bin','wb')
  for a=0,0x3fff do h:write(string.char(emu.read(a,emu.memType.wsWorkRam))) end
  h:close()
  local g=io.open('/mnt/data/demons_index_runtime_hf9.png','wb');g:write(emu.takeScreenshot());g:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled);emu.addEventCallback(frame,emu.eventType.endFrame)
