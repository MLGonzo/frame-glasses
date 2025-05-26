import asyncio
import os
from datetime import datetime

from frame_msg import FrameMsg, RxAudio, RxTap, TxCode, TxPlainText
from utils.mock_ai import mock_process_audio
from utils.text import format_text_for_frame
from utils.message import safe_send_message
from utils.frame_utils import cleanup
from utils.audio_utils import transcribe_audio
from utils.ai_utils import get_ai_response

TEXT_CHANNEL = 0x0a
TAP_CHANNEL = 0x10
AUDIO_CHANNEL = 0x30

async def display_text_safely(frame, text_blocks, max_retries=2):
    """
    Safely display text on the Frame with retries.
    """
    for attempt in range(max_retries):
        try:
            # Join text blocks with newlines and format for display
            formatted_text = format_text_for_frame('\n'.join(text_blocks), max_lines=6)
            
            # Display each block with a small delay
            for block in formatted_text:
                await safe_send_message(frame, TEXT_CHANNEL, TxPlainText(block).pack())
                await asyncio.sleep(5)
            return True
        except Exception as e:
            print(f"Error displaying text (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1.0)  # Wait before retry
    return False

async def collect_audio_data(audio_queue, max_retries=3, timeout=5.0):
    """
    Attempt to collect audio data with retries.
    Returns the audio samples if successful, None if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            print(f"Collecting audio data (attempt {attempt + 1}/{max_retries})...")
            audio_samples = await asyncio.wait_for(audio_queue.get(), timeout=timeout)
            if audio_samples:
                return audio_samples
            print("No audio data received, retrying...")
        except asyncio.TimeoutError:
            print(f"Timeout waiting for audio data (attempt {attempt + 1}/{max_retries})")
        except Exception as e:
            print(f"Error collecting audio data: {e}")
        
        if attempt < max_retries - 1:
            await asyncio.sleep(1.0)  # Wait before retry
    
    return None

async def main():
    """
    Listen for taps on the Frame and record audio when a tap is detected.
    First tap starts recording, second tap stops recording.
    Process the audio through mock AI functions and display results.
    """
    frame = FrameMsg()
    speaker = None
    recording = False  # Initialize recording state
    rx_audio = None
    rx_tap = None

    try:
        await frame.connect()

        await frame.print_short_text("Loading...")
        
        # debug only: check our current battery level and memory usage
        batt_mem = await frame.send_lua('print(frame.battery_level() .. " / " .. collectgarbage("count"))', await_print=True)
        print(f"Battery Level/Memory used: {batt_mem}")

        # send the std lua files to Frame that handle data accumulation, TxCode signalling and audio
        await frame.upload_stdlua_libs(lib_names=['data', 'code', 'audio', 'tap', 'plain_text'])

        # Send the main lua application from this project to Frame that will run the app
        await frame.upload_frame_app(local_filename="lua/tap_audio.lua")

        # attach the print response handler so we can see stdout from Frame Lua print() statements
        frame.attach_print_response_handler()

        # Start the frame app
        await frame.start_frame_app()

        # Create audio directory if it doesn't exist
        os.makedirs('audio', exist_ok=True)

        # Set up audio recording
        rx_audio = RxAudio()
        audio_queue = await rx_audio.attach(frame)

        # Set up tap detection
        rx_tap = RxTap()
        tap_queue = await rx_tap.attach(frame)

        # Start listening for taps - this command tells Frame we are ready to receive taps
        await safe_send_message(frame, TAP_CHANNEL, TxCode(value=1).pack())
        print("Waiting for tap... (Press Ctrl+C to exit)")

        while True:
            try:
                # Wait for tap signal
                await asyncio.wait_for(tap_queue.get(), timeout=10.0)
                
                if not recording:
                    print("Tap detected! Starting recording...")
                    recording = True
                    # Start audio recording
                    await safe_send_message(frame, AUDIO_CHANNEL, TxCode(value=1).pack())
                    await safe_send_message(frame, TEXT_CHANNEL, TxPlainText("Recording...").pack())
                else:
                    print("Tap detected! Stopping recording...")
                    recording = False
                    # Stop recording
                    await safe_send_message(frame, AUDIO_CHANNEL, TxCode(value=0).pack())
                    await safe_send_message(frame, TEXT_CHANNEL, TxPlainText("Processing...").pack())
                    
                    # Small delay to ensure all audio data is collected
                    await asyncio.sleep(0.5)
                    
                    # Collect audio data with retries
                    audio_samples = await collect_audio_data(audio_queue)
                    
                    if audio_samples:
                        # Convert to WAV
                        wav_bytes = RxAudio.to_wav_bytes(audio_samples, sample_rate=8000, bits_per_sample=16, channels=1)
                        
                        # Save the file
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        wav_file_path = os.path.join('audio', f'frame_audio_{timestamp}.wav')
                        
                        with open(wav_file_path, 'wb') as wav_file:
                            wav_file.write(wav_bytes)
                        
                        print(f"Audio saved to: {wav_file_path}")

                        # Process audio through OpenAI Whisper
                        print("Transcribing audio...")
                        try:
                            transcribed_text = await transcribe_audio(wav_file_path)
                            print(f"Transcribed text: {transcribed_text}")
                            
                            # Get AI response
                            print("Getting AI response...")
                            ai_response = await get_ai_response(transcribed_text)
                            print(f"AI response: {ai_response}")
                            
                            # Display both the transcribed text and AI response
                            display_text = [
                                ai_response
                            ]
                            
                            if not await display_text_safely(frame, display_text):
                                print("Failed to display results on Frame")
                                await safe_send_message(frame, TEXT_CHANNEL, TxPlainText("Display failed").pack())
                        except Exception as e:
                            print(f"Error processing audio: {e}")
                            await safe_send_message(frame, TEXT_CHANNEL, TxPlainText("Processing failed").pack())
                    else:
                        print("Failed to collect audio data after all retries")
                        await safe_send_message(frame, TEXT_CHANNEL, TxPlainText("Recording failed").pack())
                    
                    print("Waiting for next tap...")
                    await safe_send_message(frame, TEXT_CHANNEL, TxPlainText("Tap to record").pack())
            
            except asyncio.TimeoutError:
                print("Timeout waiting for tap")
            except Exception as e:
                print(f"Error during recording cycle: {e}")
                if recording:
                    recording = False
                    await safe_send_message(frame, AUDIO_CHANNEL, TxCode(value=0).pack())
                await safe_send_message(frame, TEXT_CHANNEL, TxPlainText("Error occurred").pack())
                await asyncio.sleep(1.0)

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if rx_audio is not None and rx_tap is not None:
            await cleanup(frame, rx_audio, rx_tap, recording)
        if speaker is not None:
            speaker.delete()

if __name__ == "__main__":
    asyncio.run(main()) 