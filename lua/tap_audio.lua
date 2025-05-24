local data = require('data.min')
local code = require('code.min')
local audio = require('audio.min')
local tap = require('tap.min')

-- Phone to Frame flags
TAP_SUBS_MSG = 0x10
AUDIO_SUBS_MSG = 0x30

-- register the message parsers
data.parsers[TAP_SUBS_MSG] = code.parse_code
data.parsers[AUDIO_SUBS_MSG] = code.parse_code

function app_loop()
    frame.display.text('Tap to Record', 1, 1)
    frame.display.show()

    -- tell the host program that the frameside app is ready
    print('Frame app is running')

    local streaming = false
    local audio_data = ''

    while true do
        rc, err = pcall(
            function()
                -- Process any incoming messages
                local items_ready = data.process_raw_items()

                if items_ready > 0 then
                    -- Handle tap subscription
                    if data.app_data[TAP_SUBS_MSG] ~= nil then
                        if data.app_data[TAP_SUBS_MSG].value == 1 then
                            -- start subscription to tap events
                            frame.imu.tap_callback(tap.send_tap)
                            frame.display.text('Listening for taps', 1, 1)
                        else
                            -- cancel subscription to tap events
                            frame.imu.tap_callback(nil)
                            frame.display.text('Not listening for taps', 1, 1)
                        end
                        frame.display.show()
                        data.app_data[TAP_SUBS_MSG] = nil
                    end

                    -- Handle audio control
                    if data.app_data[AUDIO_SUBS_MSG] ~= nil then
                        if data.app_data[AUDIO_SUBS_MSG].value == 1 then
                            if not streaming then
                                audio_data = ''
                                streaming = true
                                audio.start({sample_rate=8000, bit_depth=16})
                                frame.display.text("\u{F0010}", 300, 1)
                            end
                        else
                            if streaming then
                                -- Stop recording but keep streaming until all data is sent
                                audio.stop()
                                frame.display.text(" ", 1, 1)
                                -- Don't set streaming = false here, it will be set when all data is sent
                            end
                        end
                        frame.display.show()
                        data.app_data[AUDIO_SUBS_MSG] = nil
                    end
                end

                -- Handle audio streaming
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
                    frame.sleep(0.01)
                end
            end
        )
        
        if rc == false then
            print(err)
            frame.display.text('Error', 1, 1)
            frame.display.show()
            break
        end
    end
end

-- run the main app loop
app_loop() 