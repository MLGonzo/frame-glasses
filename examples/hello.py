import asyncio
from pathlib import Path

from frame_msg import FrameMsg, TxSprite

async def main():
    """
    Displays sample images on the Frame display.

    The images are indexed (palette) PNG images, in 2, 4,
    and 16 colors (that is, 1-, 2- and 4-bits-per-pixel).
    """
    frame = FrameMsg()
    try:
        await frame.connect()

        # Let the user know we're starting
        await frame.print_short_text('Loading...')
        
        await asyncio.sleep(1.0)
        
        await frame.print_short_text('Hello, World!') 
        
        # Wait a bit before ending
        await asyncio.sleep(2.0)
        
        batt_mem = await frame.send_lua('print(frame.battery_level() .. " / " .. collectgarbage("count"))', await_print=True)
        
        await frame.print_short_text(batt_mem)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # clean disconnection
        await frame.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
