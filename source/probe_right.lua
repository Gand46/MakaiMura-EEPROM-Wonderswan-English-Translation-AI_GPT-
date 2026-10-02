local function held(f,t) return f>=t and f<t+4 end
local function input()
 local f=emu.getState().frameCount; local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) then inp.a=true end
 if held(f,700) or held(f,780) or held(f,860) then inp.right=true end
 emu.setInput(inp,0)
end
local marks={[650]=0,[740]=1,[820]=2,[900]=3}
local function frame()
 local f=emu.getState().frameCount
 if marks[f]~=nil then local g=io.open('/mnt/data/pr_'..marks[f]..'.png','wb');g:write(emu.takeScreenshot());g:close() end
 if f>=920 then emu.stop(0) end
end
emu.addEventCallback(input,emu.eventType.inputPolled);emu.addEventCallback(frame,emu.eventType.endFrame)
