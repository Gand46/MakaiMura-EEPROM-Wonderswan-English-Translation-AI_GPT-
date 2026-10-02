local function held(f,t) return f>=t and f<t+5 end
local downs={}; for i=0,60 do downs[#downs+1]=1450+i*20 end
local function input()
 local f=emu.getState().frameCount; local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) then inp.a=true end
 if held(f,720) or held(f,900) or held(f,1080) then inp.right=true end
 if held(f,1260) then inp.a=true end
 for _,t in ipairs(downs) do if held(f,t) then inp.down=true end end
 emu.setInput(inp,0)
end
local done=false
local function frame()
 local f=emu.getState().frameCount
 if f>=2720 and not done then done=true; local g=io.open('/mnt/data/hf11_work/evidence/HF11_NAMES_END_37_42.png','wb');g:write(emu.takeScreenshot());g:close();emu.stop(0) end
end
emu.addEventCallback(input,emu.eventType.inputPolled);emu.addEventCallback(frame,emu.eventType.endFrame)
