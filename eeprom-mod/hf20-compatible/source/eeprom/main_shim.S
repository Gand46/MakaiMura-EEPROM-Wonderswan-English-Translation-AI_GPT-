.code16
.intel_syntax noprefix
.section .text
.global shim_start
.global boot_wrapper
.global eeprom_load
.global eeprom_commit
.global pause_start_wrapper
.global pause_start_orig_disp
.global pause_ui_wrapper
.global pause_orig_disp
.global render_save_ui
.global load_ui_tiles
.global boot_sig_disp
.global pause_orig_disp
.global shim_end
.global key_read_far
.global key_read_disp
.global native_reset_far
.global native_sig_disp
.global native_init_disp
.global eeprom_commit_far
.global options_render_finalize
.global aux_render_off
.global options_redraw_far
.global options_redraw_disp
.global options_finalize_disp
.global draw_glyph_far
.global draw_glyph_disp

/* Makaimura SRAM -> cartridge EEPROM 2 KiB
 * Phase 4.1E-r2: START-hold manual save + non-destructive OPTIONS modal.
 *
 * Mirror: 0037:0000..0284 -> physical 0370..05F4.
 * EEPROM writes: manual HOLD START SAVE, or confirmed OPTIONS ERASE through far helper.
 * A/B/X/Y remain untouched for the game's pause-screen Tip commands.
 *
 * Pause UI adds one sprite line at y=120:
 *   HOLD -> START -> SAVE (three cycling short messages)
 * and temporarily replaces it with:
 *   SAVED
 *
 * Native pause uses sprite table at 0000:1800, next pointer 0000:1A40,
 * count at 0000:1A42.  The original renderer finalizes count after this
 * hook, so appended sprites are included naturally.
 */

shim_start:
boot_wrapper:
    pusha
    push ds
    push es
    call eeprom_load
    xor ax, ax
    mov es, ax
    mov byte ptr es:0x05F6, 0x00
    mov byte ptr es:0x05F7, 0x00
    mov byte ptr es:0x05F8, 0x00
    mov byte ptr es:0x05F9, 0x00
    mov byte ptr es:0x05FA, 0x00
    mov byte ptr es:0x05FB, 0x00
    mov byte ptr es:0x05FC, 0x00
    mov byte ptr es:0x05FD, 0x00
    mov byte ptr es:0x05FE, 0x00
    mov byte ptr es:0x05FF, 0x00
    pop es
    pop ds
    popa
boot_sig_call:
    .byte 0xE8
boot_sig_disp:
    .word 0x0000
    ret

/* C8 bit0: read done. bounded wait. */
wait_done:
    push cx
    mov cx, 0x0032
1:  loop 1b
    mov cx, 0x0100
2:  in ax, dx
    test al, 0x01
    jnz 3f
    loop 2b
3:  pop cx
    ret

/* C8 bit1: ready/idle. bounded wait. */
wait_ready:
    push cx
    mov cx, 0x0032
4:  loop 4b
    mov cx, 0x0D55
5:  in ax, dx
    test al, 0x02
    jnz 6f
    loop 5b
6:  pop cx
    ret

/* AX=even EEPROM byte address; returns AX=data word. */
eep_read_ax:
    push dx
    shr ax, 1
    or ax, 0x1800
    mov dx, 0x00C6
    out dx, ax
    mov dx, 0x00C8
    mov ax, 0x0010
    out dx, ax
    call wait_done
    mov dx, 0x00C4
    in ax, dx
    pop dx
    ret

eep_unlock:
    push ax
    push dx
    mov dx, 0x00C6
    mov ax, 0x1300
    out dx, ax
    mov dx, 0x00C8
    mov ax, 0x0040
    out dx, ax
    call wait_ready
    pop dx
    pop ax
    ret

eep_lock:
    push ax
    push dx
    mov dx, 0x00C6
    mov ax, 0x1000
    out dx, ax
    mov dx, 0x00C8
    mov ax, 0x0040
    out dx, ax
    call wait_ready
    pop dx
    pop ax
    ret

/* Boot only: EEPROM -> mirror. */
eeprom_load:
    push ax
    push cx
    push dx
    push si
    push di
    push es
    cld
    mov ax, 0x0037
    mov es, ax
    xor di, di
    xor si, si
    mov cx, 0x0143
7:
    mov ax, si
    call eep_read_ax
    stosw
    add si, 2
    loop 7b
    pop es
    pop di
    pop si
    pop dx
    pop cx
    pop ax
    ret

/* Explicit SAVE: only changed words, then EWDS. */
eeprom_commit:
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    push ds
    call eep_unlock
    mov ax, 0x0037
    mov ds, ax
    xor si, si
    mov cx, 0x0143
8:
    mov di, word ptr [si]
    mov ax, si
    call eep_read_ax
    cmp ax, di
    je 9f
    mov ax, si
    shr ax, 1
    or ax, 0x1400
    mov dx, 0x00C6
    out dx, ax
    mov ax, di
    mov dx, 0x00C4
    out dx, ax
    mov ax, 0x0020
    mov dx, 0x00C8
.global program_word_out
program_word_out:
    out dx, ax
    call wait_ready
9:
    add si, 2
    loop 8b
    call eep_lock
    pop ds
    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

/* Copy missing D/N/V glyphs from the game's native pause font atlas
 * (runtime 8000:00D0/0170/01F0) into high tile slots 1FD/1FE/1FC.
 * Existing game letters are reused directly for all other characters.
 */
load_ui_tiles:
    push ax
    push cx
    push si
    push di
    push ds
    push es
    cld
    mov ax, 0x8000
    mov ds, ax
    xor ax, ax
    mov es, ax

    /* The native pause font atlas is 16 bytes/glyph.  These source
     * offsets were verified from the existing D/N/V mapping and the
     * contiguous A-Z ordering: H=110h, L=150h, O=180h, V=1F0h, D=D0h.
     */
    mov si, 0x0110             /* H */
    mov di, 0x3F80             /* tile 1F8h */
    mov cx, 0x0008
    rep movsw

    mov si, 0x0150             /* L */
    mov di, 0x3F90             /* tile 1F9h */
    mov cx, 0x0008
    rep movsw

    mov si, 0x0180             /* O */
    mov di, 0x3FA0             /* tile 1FAh */
    mov cx, 0x0008
    rep movsw

    mov si, 0x01F0             /* V */
    mov di, 0x3FC0             /* tile 1FCh */
    mov cx, 0x0008
    rep movsw

    mov si, 0x00D0             /* D */
    mov di, 0x3FD0             /* tile 1FDh */
    mov cx, 0x0008
    rep movsw

    pop es
    pop ds
    pop di
    pop si
    pop cx
    pop ax
    ret

/* Append sprite records to the game's current OAM build list.
 * If SAVED timer != 0, show SAVED. Otherwise cycle HOLD -> START -> SAVE.
 */
render_save_ui:
    push ax
    push bx
    push cx
    push si
    push di
    push ds
    push es

    call load_ui_tiles

    xor ax, ax
    mov es, ax
    mov bx, 0x1A40
    mov di, word ptr es:[bx]
    cmp di, 0x1A00             /* guard against unexpected table overflow */
    jae 12f

    cmp byte ptr es:0x05F7, 0x00
    je ui_cycle_select
    push cs
    pop ds
    mov si, offset saved_sprites
    mov cx, 10              /* 5 records x 2 words */
    mov al, 5
    jmp ui_copy
ui_cycle_select:
    /* Keep each pause hint at <=5 sprites to stay below the WS per-line
     * sprite budget used by the live gameplay scene behind the pause UI.
     * Cycle HOLD -> START -> SAVE while paused.
     */
    mov al, byte ptr es:0x05FB
    cmp al, 30
    jb ui_hold
    cmp al, 60
    jb ui_start
    push cs
    pop ds
    mov si, offset save_sprites
    mov cx, 8               /* 4 records */
    mov al, 4
    jmp ui_copy
ui_hold:
    push cs
    pop ds
    mov si, offset hold_sprites
    mov cx, 8               /* 4 records */
    mov al, 4
    jmp ui_copy
ui_start:
    push cs
    pop ds
    mov si, offset start_sprites
    mov cx, 10              /* 5 records */
    mov al, 5
ui_copy:
    /* each record is word tile/attr + word (x<<8 | y) */
    push ax
    rep movsw
    pop ax
    add byte ptr es:[bx+2], al
ui_done_ptr:
    mov word ptr es:[bx], di
12:
    pop es
    pop ds
    pop di
    pop si
    pop cx
    pop bx
    pop ax
    ret

/* Hook replacing native CALL A237 at 4000:6E96.
 * Native pause transitions are preserved except state 2 -> 3, which is
 * delayed until START is released.  This lets us distinguish TAP from HOLD.
 *
 * RAM control bytes outside the 645-byte mirror:
 *   05F8 = START hold counter
 *   05F9 = save latch (1 after HOLD SAVE until START release)
 *   05FA = START armed (requires a release after entering pause)
 */
pause_start_wrapper:
    pushf
    pusha
    push ds
    xor ax, ax
    mov ds, ax

    cmp byte ptr ds:0x1E92, 0x02
    je ps_state2

    /* All native enter/exit transitions except stable-pause START handling. */
    pop ds
    popa
    popf
pause_start_orig_call:
    .byte 0xE8
pause_start_orig_disp:
    .word 0x0000

    /* Arm only after native state 1 -> 2 completed with START released. */
    pushf
    pusha
    push ds
    xor ax, ax
    mov ds, ax
    cmp byte ptr ds:0x1E92, 0x02
    jne ps_nonpause_done
    mov ax, word ptr ds:0x1E39
    test ax, 0x0200
    jnz ps_nonpause_done
    mov byte ptr ds:0x05FA, 0x01
    mov byte ptr ds:0x05F8, 0x00
    mov byte ptr ds:0x05F9, 0x00
ps_nonpause_done:
    pop ds
    popa
    popf
    ret

ps_state2:
    mov ax, word ptr ds:0x1E39       /* current packed keys */
    test ax, 0x0200                   /* START */
    jnz ps_start_down

    /* START released.  A prior short hold means TAP -> native return. */
    cmp byte ptr ds:0x05F9, 0x00
    jne ps_release_after_save
    cmp byte ptr ds:0x05FA, 0x01
    jne ps_arm_release
    cmp byte ptr ds:0x05F8, 0x00
    je ps_done

    /* Short START tap: enter native state 3.  Next frame A237 completes 3->0. */
    mov byte ptr ds:0x1E92, 0x03
    mov byte ptr ds:0x05F8, 0x00
    mov byte ptr ds:0x05FA, 0x00
    jmp ps_done

ps_arm_release:
    mov byte ptr ds:0x05FA, 0x01
    mov byte ptr ds:0x05F8, 0x00
    jmp ps_done

ps_release_after_save:
    /* HOLD SAVE never exits pause.  Release rearms START for a later tap. */
    mov byte ptr ds:0x05F9, 0x00
    mov byte ptr ds:0x05F8, 0x00
    mov byte ptr ds:0x05FA, 0x01
    jmp ps_done

ps_start_down:
    cmp byte ptr ds:0x05FA, 0x01
    jne ps_done
    cmp byte ptr ds:0x05F9, 0x00
    jne ps_done
    cmp byte ptr ds:0x05F8, 45
    jae ps_done
    inc byte ptr ds:0x05F8
    cmp byte ptr ds:0x05F8, 45
    jne ps_done

    /* HOLD threshold reached: save exactly once and remain paused. */
    call eeprom_commit
    xor ax, ax
    mov ds, ax
    mov byte ptr ds:0x05F6, 0x01
    mov byte ptr ds:0x05F7, 0x3C
    mov byte ptr ds:0x05F9, 0x01

ps_done:
    pop ds
    popa
    popf
    ret

/* Hook replacing native CALL A2B2 at 4000:6E99.
 * A2B2 remains untouched functionally; this wrapper only adds the UI.
 */
pause_ui_wrapper:
pause_orig_call:
    .byte 0xE8
pause_orig_disp:
    .word 0x0000

    pushf
    pusha
    push ds
    push es
    xor ax, ax
    mov ds, ax

    cmp byte ptr ds:0x05F7, 0x00
    je pui_no_timer
    dec byte ptr ds:0x05F7
pui_no_timer:
    cmp byte ptr ds:0x1E92, 0x02
    jne pui_reset_cycle
    inc byte ptr ds:0x05FB
    cmp byte ptr ds:0x05FB, 90
    jb pui_render
    mov byte ptr ds:0x05FB, 0
pui_render:
    call render_save_ui
    jmp pui_done
pui_reset_cycle:
    mov byte ptr ds:0x05FB, 0
pui_done:
    pop es
    pop ds
    popa
    popf
    ret

/* attr 3800h matches Makaimura's native pause text sprites.
 * coordinates are stored as y low / x high in the second word.
 */
hold_sprites:
    .word 0x39F8, 0x6078       /* H x=96  y=120 */
    .word 0x39FA, 0x6878       /* O x=104 */
    .word 0x39F9, 0x7078       /* L x=112 */
    .word 0x39FD, 0x7878       /* D x=120 */

start_sprites:
    .word 0x3872, 0x5C78       /* S x=92  y=120 */
    .word 0x381C, 0x6478       /* T x=100 */
    .word 0x3879, 0x6C78       /* A x=108 */
    .word 0x3875, 0x7478       /* R x=116 */
    .word 0x381C, 0x7C78       /* T x=124 */

save_sprites:
    .word 0x3872, 0x6078       /* S x=96  y=120 */
    .word 0x3879, 0x6878       /* A x=104 */
    .word 0x39FC, 0x7078       /* V x=112 */
    .word 0x381F, 0x7878       /* E x=120 */

saved_sprites:
    .word 0x3872, 0x5C78       /* S x=92 */
    .word 0x3879, 0x6478       /* A x=100 */
    .word 0x39FC, 0x6C78       /* V x=108 */
    .word 0x381F, 0x7478       /* E x=116 */
    .word 0x39FD, 0x7C78       /* D x=124 */


/* Far-call helpers used by the Phase 4.1E OPTIONS extension in bank 15. */
key_read_far:
    .byte 0xE8
key_read_disp:
    .word 0x0000
    retf

/* Re-run the exact native fresh-save path: signature check then initializer. */
native_reset_far:
    .byte 0xE8
native_sig_disp:
    .word 0x0000
    .byte 0xE8
native_init_disp:
    .word 0x0000
    retf

eeprom_commit_far:
    call eeprom_commit
    retf

/* Called IN PLACE OF the native CALL F3AA at 4000:1274, once per redraw.
 * Normal OPTIONS: exact native OAM, no extra sprites or second finalization.
 * Modal: append only to the native cursor/values list BEFORE finalizing it.
 */
options_render_finalize:
    pushf
    cmp byte ptr ds:0x05FC, 0
    je orf_native
    .byte 0x9A
aux_render_off:
    .word 0x0000
    .word 0x5000
orf_native:
    popf
    .byte 0xE8
options_finalize_disp:
    .word 0x0000
    ret

/* Modal input calls the entire original OPTIONS renderer (cursor+values). */
options_redraw_far:
    .byte 0xE8
options_redraw_disp:
    .word 0x0000
    retf

/* Far-callable native glyph renderer (4000:F349). */
draw_glyph_far:
    .byte 0xE8
draw_glyph_disp:
    .word 0x0000
    retf

shim_end:
