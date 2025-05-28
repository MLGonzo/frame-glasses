import asyncio
from frame_msg import FrameMsg, RxPhoto, TxCaptureSettings
from PIL import Image
import io

async def capture_photo(frame: FrameMsg) -> Image.Image:
    """
    Take a photo using the Frame camera and return it as a PIL Image.
    
    Args:
        frame: The FrameMsg instance to use for communication
        
    Returns:
        PIL.Image: The captured photo
        
    Raises:
        Exception: If there's an error capturing the photo
    """
    try:
        # Set up photo receiver
        rx_photo = RxPhoto()
        photo_queue = await rx_photo.attach(frame)
        
        # Let autoexposure settle
        await asyncio.sleep(5.0)
        
        # Request the photo
        await frame.send_message(0x0d, TxCaptureSettings(resolution=720).pack())
        
        # Get the photo data
        jpeg_bytes = await asyncio.wait_for(photo_queue.get(), timeout=10.0)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(jpeg_bytes))
        
        # Clean up
        rx_photo.detach(frame)
        
        return image
        
    except Exception as e:
        print(f"Error taking photo: {e}")
        raise 