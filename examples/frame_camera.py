import asyncio
from PIL import Image
import io
from pathlib import Path
from frame_msg import FrameMsg, RxPhoto, TxCaptureSettings

async def _take_photo_async(output_path: str = None, resolution: int = 720, autoexposure_time: float = 5.0):
    """
    Internal async function to take a photo using the Frame camera.
    
    Args:
        output_path (str, optional): Path where to save the photo. If None, returns the image object.
        resolution (int, optional): Photo resolution. Defaults to 720.
        autoexposure_time (float, optional): Time in seconds to wait for autoexposure. Defaults to 5.0.
    
    Returns:
        PIL.Image.Image or None: Returns the image object if output_path is None, otherwise saves to file and returns None
    """
    frame = FrameMsg()
    try:
        await frame.connect()
        
        # Upload required Lua libraries and app
        await frame.upload_stdlua_libs(lib_names=['data', 'camera'])
        await frame.upload_frame_app(local_filename="lua/camera_frame_app.lua")
        
        # Set up handlers
        frame.attach_print_response_handler()
        await frame.start_frame_app()
        
        # Set up photo receiver
        rx_photo = RxPhoto()
        photo_queue = await rx_photo.attach(frame)
        
        # Wait for autoexposure
        print(f"Letting autoexposure loop run for {autoexposure_time} seconds to settle")
        await asyncio.sleep(autoexposure_time)
        print("Capturing a photo")
        
        # Request the photo
        await frame.send_message(0x0d, TxCaptureSettings(resolution=resolution).pack())
        
        # Get the jpeg bytes
        jpeg_bytes = await asyncio.wait_for(photo_queue.get(), timeout=10.0)
        
        # Process the image
        image = Image.open(io.BytesIO(jpeg_bytes))
        
        if output_path:
            # Ensure the directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            print(f"Photo saved to: {output_path}")
            return None
        else:
            return image
            
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        # Clean up
        if 'rx_photo' in locals():
            rx_photo.detach(frame)
        if 'frame' in locals():
            frame.detach_print_response_handler()
            await frame.stop_frame_app()
            await frame.disconnect()

def take_photo(output_path: str = None, resolution: int = 720, autoexposure_time: float = 5.0):
    """
    Take a photo using the Frame camera.
    
    Args:
        output_path (str, optional): Path where to save the photo. If None, returns the image object.
        resolution (int, optional): Photo resolution. Defaults to 720.
        autoexposure_time (float, optional): Time in seconds to wait for autoexposure. Defaults to 5.0.
    
    Returns:
        PIL.Image.Image or None: Returns the image object if output_path is None, otherwise saves to file and returns None
    """
    return asyncio.run(_take_photo_async(output_path, resolution, autoexposure_time))

if __name__ == "__main__":
    # Example usage
    # Save to file
    take_photo("photos/my_photo.jpg")
    
    # Or get image object
    image = take_photo()
    image.show() 