local finished=false
local stop=emu.stop
local function finish(code) if not finished then finished=true;stop(code) end end
local f=0
local out=assert(io.open(assert(os.getenv('OUT'))..'options_exit_regression.tsv','w'))
local function rec(tag)
 out:write(string.format('%d\t%s\tstate=%04X\tcursor=%02X\tmode=%02X\n',f,tag,emu.read16(0x1E33,emu.memType.wsWorkRam),emu.read(0x1E37,emu.memType.wsWorkRam),emu.read(0x5FC,emu.memType.wsWorkRam)));out:flush()
end
emu.addEventCallback(function()
  if finished then return end
 f=f+1
 if f==3680 then rec('OPTIONS') end
 if f==3760 then rec('EXIT_ROW') end
 if f==3810 then rec('AFTER_A_EXIT');out:close(); if emu.read16(0x1E33,emu.memType.wsWorkRam)~=0x0050 then finish(0) else finish(2) end end
 if f>3850 then out:close();finish(3) end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
  if finished then return end
 local start=false;local down=false;local a=false
 if f>=3505 and f<3515 then start=true end
 if (f>=3570 and f<3576) or (f>=3590 and f<3596) or (f>=3610 and f<3616) then down=true end
 if f>=3640 and f<3650 then a=true end
 -- options cursor to EXIT = 3
 if (f>=3700 and f<3706) or (f>=3720 and f<3726) or (f>=3740 and f<3746) then down=true end
 if f>=3770 and f<3780 then a=true end
 emu.setInput({start=start,a=a,b=false,up=false,down=down,left=false,right=false,up2=false,down2=false,left2=false,right2=false,sound=false},0)
end,emu.eventType.inputPolled)
