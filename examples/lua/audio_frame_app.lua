local data = require('data.min')
local code = require('code.min')
local audio = require('audio.min')

-- Phone to Frame flags
AUDIO_SUBS_MSG = 0x30

-- register the message parsers so they are automatically called when matching data comes in
data.parsers[AUDIO_SUBS_MSG] = code.parse_code

-- Main app loop
function app_loop()
	frame.display.text('Frame App Started', 1, 1)
	frame.display.show()

	local streaming = false

	-- tell the host program that the frameside app is ready (waiting on await_print)
	print('Frame app is running')

	while true do
        rc, err = pcall(
            function()
				-- process any raw data items, if ready
				local items_ready = data.process_raw_items()

				-- one or more full messages received
				if items_ready > 0 then

					if (data.app_data[AUDIO_SUBS_MSG] ~= nil) then

						if data.app_data[AUDIO_SUBS_MSG].value == 1 then
							audio_data = ''
							streaming = true
							audio.start({sample_rate=8000, bit_depth=16})
							frame.display.text("\u{F0010}", 300, 1)
						else
							-- 'stop' message
							-- don't set streaming = false here, it will be set
							-- when all the audio data is flushed
							audio.stop()
							frame.display.text(" ", 1, 1)
						end

						frame.display.show()
						data.app_data[AUDIO_SUBS_MSG] = nil
					end

				end

				-- send any pending audio data back
				-- Streams until AUDIO_SUBS_MSG is sent from host with a value of 0
				if streaming then
					-- read_and_send_audio() sends one MTU worth of samples
					-- so loop up to 10 times until we have caught up or the stream has stopped
					local sent = audio.read_and_send_audio()
					for i = 1, 10 do
						if sent == nil or sent == 0 then
							break
						end
						sent = audio.read_and_send_audio()
					end
					if sent == nil then
						streaming = false
					end

					-- 8kHz/16 bit is 16000b/s, which is ~66 packets/second, or 1 every 15ms
					frame.sleep(0.005)
				else
					-- not streaming, sleep for longer
					frame.sleep(0.1)
				end
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