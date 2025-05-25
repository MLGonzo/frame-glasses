import asyncio
from frame_msg import TxPlainText

async def safe_send_message(frame, msg_code, payload, max_retries=2):
    """
    Safely send a message to the Frame with retries.
    
    Args:
        frame: The FrameMsg instance
        msg_code: The message code to send
        payload: The message payload
        max_retries: Maximum number of retry attempts (default: 2)
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    for attempt in range(max_retries):
        try:
            await frame.send_message(msg_code, payload)
            return True
        except Exception as e:
            print(f"Error sending message (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)  # Wait before retry
    return False

async def safe_send_text(frame, text, max_retries=2):
    """
    Safely send a text message to the Frame with retries.
    
    Args:
        frame: The FrameMsg instance
        text: The text message to send
        max_retries: Maximum number of retry attempts (default: 2)
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    return await safe_send_message(frame, 0x0a, TxPlainText(text).pack(), max_retries) 