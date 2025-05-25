from frame_msg import FrameMsg, RxAudio, RxTap, TxCode
from utils.message import safe_send_message

async def cleanup(frame: FrameMsg, rx_audio: RxAudio, rx_tap: RxTap, recording: bool) -> None:
    """
    Safely clean up resources and stop the Frame app.
    
    Args:
        frame: The FrameMsg instance to clean up
        rx_audio: The RxAudio instance to detach
        rx_tap: The RxTap instance to detach
        recording: Whether audio is currently being recorded
    """
    try:
        # Stop recording if still recording
        if recording:
            await safe_send_message(frame, 0x30, TxCode(value=0).pack())
        
        # Stop listening for taps
        await safe_send_message(frame, 0x10, TxCode(value=0).pack())
        
        # Clean up
        rx_audio.detach(frame)
        rx_tap.detach(frame)
        frame.detach_print_response_handler()
        
        # Try to stop the frame app
        try:
            await frame.stop_frame_app()
        except Exception as e:
            print(f"Error stopping frame app: {e}")
        
        # Try to disconnect
        try:
            await frame.disconnect()
        except Exception as e:
            print(f"Error disconnecting: {e}")
            
    except Exception as e:
        print(f"Error during cleanup: {e}") 