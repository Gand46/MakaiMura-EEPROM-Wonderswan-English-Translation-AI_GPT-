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
  local path=os.getenv('MESEN_CAPTURE_PATH') or '/mnt/data/makai_hf10_work/evidence/HF10_INDEX_RUNTIME.png'
  local g=io.open(path,'wb');g:write(emu.takeScreenshot());g:close()
  local r=io.open('/mnt/data/makai_hf10_work/build/HF10_INDEX_RUNTIME.json','w');r:write('{"route":"Library > Demons > Index","frame":'..f..',"access":"SCRIPTED_NATURAL","emulator":"Mesen 2.1.1"}');r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled);emu.addEventCallback(frame,emu.eventType.endFrame)
