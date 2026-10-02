local function held(f,t) return f>=t and f<t+4 end
local downs={}
for i=0,41 do downs[#downs+1]=1450+i*24 end
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
local marks={
 [1415]='HF11_NAMES_01_06.png',
 [1605]='HF11_NAMES_07_12.png',
 [1750]='HF11_NAMES_13_18.png',
 [1895]='HF11_NAMES_19_24.png',
 [2040]='HF11_NAMES_25_30.png',
 [2185]='HF11_NAMES_31_36.png',
 [2330]='HF11_NAMES_37_42.png',
}
local done={}
local function frame()
 local f=emu.getState().frameCount; local n=marks[f]
 if n and not done[n] then
  done[n]=true; local g=io.open('/mnt/data/hf11_work/evidence/'..n,'wb');g:write(emu.takeScreenshot());g:close()
 end
 if f>=2370 then emu.stop(0) end
end
emu.addEventCallback(input,emu.eventType.inputPolled);emu.addEventCallback(frame,emu.eventType.endFrame)
