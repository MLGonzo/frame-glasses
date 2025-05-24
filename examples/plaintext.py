import asyncio
from frame_msg import FrameMsg, TxPlainText
from utils.text import format_text_for_frame

async def main():
    frame = FrameMsg()
    await frame.connect()
    batt_mem = await frame.send_lua('print(frame.battery_level() .. " / " .. collectgarbage("count"))', await_print=True)
    print(f"Battery Level/Memory used: {batt_mem}")
    
    await frame.print_short_text('Loading...')
    
    await frame.upload_stdlua_libs(lib_names=['data', 'plain_text'])
    
    await frame.upload_frame_app(local_filename='lua/plaintext.lua')
    
    await frame.start_frame_app()
    
    display_string = """The Brilliant Frame is an innovative augmented reality device that combines cutting-edge technology with everyday eyewear. This device represents a significant step forward in wearable computing, offering users a seamless way to interact with digital content while maintaining a natural view of the world around them. The Frame's display technology allows for crisp, clear text and images to be overlaid onto the user's field of vision, making it perfect for a wide range of applications from navigation to information display. The device's compact design and comfortable fit make it suitable for extended wear, while its powerful processing capabilities enable complex applications and real-time interactions. The Frame's camera system provides high-quality image capture, and its various sensors enable sophisticated environmental awareness and user interaction. This technology opens up new possibilities for how we interact with digital information in our daily lives, making augmented reality more accessible and practical than ever before."""
    
    # Format the text into blocks of 6 lines
    blocks = format_text_for_frame(display_string)
    
    # Display each block with a pause between them
    for block in blocks:
        await frame.send_message(0x0a, TxPlainText(block).pack())
        await asyncio.sleep(5.0)
    
    await frame.stop_frame_app()
    
    await frame.disconnect()
    
if __name__ == '__main__':
    asyncio.run(main())
