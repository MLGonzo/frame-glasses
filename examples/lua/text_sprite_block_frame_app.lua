local data = require('data.min')
local text_sprite_block = require('text_sprite_block.min')

-- Phone to Frame flags
TEXT_SPRITE_BLOCK = 0x20

-- register the message parsers so they are automatically called when matching data comes in
data.parsers[TEXT_SPRITE_BLOCK] = text_sprite_block.parse_text_sprite_block


-- Main app loop
function app_loop()
	frame.display.text('Frame App Started', 1, 1)
	frame.display.show()

	-- tell the host program that the frameside app is ready (waiting on await_print)
	print('Frame app is running')

	while true do
        rc, err = pcall(
            function()
				-- process any raw data items, if ready
				local items_ready = data.process_raw_items()

				-- one or more full messages received
				if items_ready > 0 then

					if (data.app_data[TEXT_SPRITE_BLOCK] ~= nil) then
						-- show the text sprite block
						local tsb = data.app_data[TEXT_SPRITE_BLOCK]

						-- it can be that we haven't got any sprites yet, so only proceed if we have a sprite
						if tsb.first_sprite_index > 0 then
							-- either we have all the sprites, or we want to do progressive/incremental rendering
							if tsb.progressive_render or (tsb.active_sprites == tsb.total_sprites) then

								-- for index = 1, tsb.active_sprites do
								-- 		local spr = tsb.sprites[index]
								-- 		local y_offset = 50 * (index - 1) -- TODO get proper offsets

								-- 		frame.display.bitmap(1, y_offset + 1, spr.width, 2^spr.bpp, 0, spr.pixel_data)
								-- end
								for index, spr in ipairs(tsb.sprites) do
									frame.display.bitmap(1, tsb.offsets[index].y + 1, spr.width, 2^spr.bpp, 0+index, spr.pixel_data)
								end

								frame.display.show()
							end
						end
					end

				end

				-- can't sleep for long, might be lots of incoming bluetooth data to process
				frame.sleep(0.001)
			end
		)
		-- Catch an error (including the break signal) here
		if rc == false then
			-- send the error back on the stdout stream and clear the display
			print(err)
			frame.display.text(' ', 1, 1)
			frame.display.show()
			break
		end
	end
end

-- run the main app loop
app_loop()