-- Natural navigation; no emulator writes to game state or EEPROM.
local f=0
local base=assert(os.getenv('OUT'))
local wr=emu.memType.wsWorkRam
local ep=emu.memType.wsCartEeprom
local programCommands=0
local firstCommands=0
emu.addMemoryCallback(function() programCommands=programCommands+1 end,emu.callbackType.exec,0x5E312,0x5E312,emu.cpuType.ws)
local log=assert(io.open(base..'states.tsv','w'))
local function wc() local n=0;for _,v in pairs(emu.getAccessCounters(ep,emu.counterType.writeCount)) do n=n+v end;return n end
local function diff() local n=0;for i=0,0x284 do if emu.read(0x370+i,wr)~=emu.read(i,ep) then n=n+1 end end;return n end
local function dump(n,mt,addr,sz) local q=assert(io.open(base..n,'wb'));for i=0,sz-1 do q:write(string.char(emu.read(addr+i,mt))) end;q:close() end
local function shot(n) local p=assert(io.open(base..n..'.png','wb'));p:write(emu.takeScreenshot());p:close() end
local function rec(tag) log:write('commands='..programCommands..'\t');log:write(string.format('%d\t%s\tstate=%04X\tcursor=%d\tmode=%d\tarm=%d\thold=%d\twrites=%d\tdiff=%d\n',f,tag,emu.read16(0x1E33,wr),emu.read(0x1E37,wr),emu.read(0x5FC,wr),emu.read(0x5FD,wr),emu.read(0x5FE,wr),wc(),diff()));log:flush() end
local function check(ok,msg) if not ok then rec('FAIL '..msg); log:close();emu.stop(2);return false end;return true end
emu.resetAccessCounters()
local tags={[3755]='exit_normal',[3800]='short_start',[3918]='confirm_start_still_down',[3940]='confirm_ready',[3965]='cancel_restored',[4010]='mixed_keys_blocked',[4100]='second_confirm',[4140]='done',[4220]='after_done',[4350]='redundant_erase',[4430]='redundant_done'}
emu.addEventCallback(function()
 f=f+1
 if tags[f] then rec(tags[f]);shot(tags[f]) end
 if f==3755 or f==3800 or f==3965 or f==4010 then
  if not check(emu.read(0x5FC,wr)==0,'mode must be native') then return end
  if not check(wc()==0,'unsolicited EEPROM write') then return end
 end
 if f==3918 then if not check(emu.read(0x5FC,wr)==1 and emu.read(0x5FD,wr)==0 and wc()==0,'hold/release gate') then return end end
 if f==3940 or f==4100 then if not check(emu.read(0x5FC,wr)==1 and emu.read(0x5FD,wr)==1 and wc()==0,'confirmation ready without write') then return end end
 if f==3965 then dump('cancel.eeprom',ep,0,2048) end
 if f==4140 then
  if not check(emu.read(0x5FC,wr)==2 and wc()>0 and diff()==0,'erase completion') then return end
  firstCommands=programCommands;dump('erased.eeprom',ep,0,2048);dump('fresh_mirror.bin',wr,0x370,645)
 end
 if f==4220 then
  if not check(emu.read(0x5FC,wr)==0 and emu.read16(0x1E33,wr)==0x50,'return to OPTIONS') then return end
  dump('final.eeprom',ep,0,2048)
 end
 if f==4350 then
  if not check(wc()==2*firstCommands and programCommands==firstCommands and diff()==0,'redundant erase must not program') then return end
 end
 if f==4430 then
  if not check(emu.read(0x5FC,wr)==0 and programCommands==firstCommands,'feedback/reset no writes') then return end
  log:close();emu.stop(0)
 end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
 local k={start=false,up=false,down=false,left=false,right=false,a=false,b=false,up2=false,down2=false,left2=false,right2=false,sound=false}
 if f>=3505 and f<3515 then k.start=true end
 if (f>=3570 and f<3576) or (f>=3590 and f<3596) or (f>=3610 and f<3616) then k.down=true end
 if f>=3640 and f<3650 then k.a=true end
 if (f>=3700 and f<3706) or (f>=3720 and f<3726) or (f>=3740 and f<3746) then k.down=true end
 if f>=3775 and f<3782 then k.start=true end
 if f>=3870 and f<3925 then k.start=true end
 if f>=3917 and f<3922 then k.a=true end -- Must NOT accept YES while START held.
 if f>=3945 and f<3955 then k.b=true end
 if f>=3970 and f<4005 then k.start=true;k.a=true end -- Mixed cannot arm ERASE.
 if f>=4030 and f<4090 then k.start=true end
 if f>=4110 and f<4120 then k.a=true end
 if f>=4240 and f<4300 then k.start=true end
 if f>=4320 and f<4330 then k.a=true end
 emu.setInput(k,0)
end,emu.eventType.inputPolled)
