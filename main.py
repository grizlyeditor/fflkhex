from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Text Encoder API",
    description="API لتشفير النص باستخدام سورس GPL ZIX",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_packet_data(text_3704, user_id):
    text_3704 = text_3704[:3704].ljust(3704, ' ')
    packet_structure = (
        b'\x12\x00\x00\x0f/\x08\xce\xc2\xf1\x05\x10\x12 \x02*\xa2\x1e\x08\xce\xc2\xf1\x05\x10\xce\xc2\xf1\x05"\xfa\x1c\n' +
        text_3704.encode('utf-8') +
        b' \n(\xa0\x83\xca\xbd\x06J%\n\x0bOUT\xe3\x85\xa4ALVIN\x10\xe7\xb2\x90\xae\x03 \xd2\x01(\xc1\xb7\xf8\xb1\x03B\x077Radaa!R\x02arjd\n^https://lh3.googleusercontent.com/a/ACg8ocJaMCcUolCU9qHWll-yPnvQm3Tx-0F00M0Yjc3PCw72ozDP=s96-c\x10\x01\x18\x01r\x00'
    )
    hex_data = packet_structure.hex().upper()
    modified_hex = hex_data.replace('CEC2F105', user_id.upper())
    
    if len(modified_hex) > 7784:
        extra = len(modified_hex) - 7784
        mid_point = len(modified_hex) // 2
        start = mid_point - (extra // 2)
        end = mid_point + (extra // 2)
        if extra % 2 != 0:
            end += 1
        modified_hex = modified_hex[:start] + modified_hex[end:]
    elif len(modified_hex) < 7784:
        modified_hex = modified_hex.ljust(7784, '0')
    
    return modified_hex[:7784]

@app.get("/")
async def root():
    return {
        "message": "مرحباً بك في Text Encoder API",
        "version": "1.0",
        "developer": "FOX",
        "endpoints": {
            "encode": "/encode?text=YOUR_TEXT&user_id=USER_ID",
            "default_encode": "/encode/default?text=YOUR_TEXT",
            "health": "/health",
            "docs": "/docs"
        },
        "default_user_id": "c8f0dacb08"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Text Encoder API"}

@app.get("/encode")
async def encode_text(text: str, user_id: str):
    """
    تشفير النص مع معرف مستخدم مخصص
    """
    try:
        if len(user_id) != 8:
            raise HTTPException(status_code=400, detail="user_id يجب أن يكون 8 أحرف")
        
        if not all(c in '0123456789ABCDEFabcdef' for c in user_id):
            raise HTTPException(status_code=400, detail="user_id يجب أن يحتوي على أحرف hex فقط")
        
        encoded_result = process_packet_data(text, user_id)
        
        return {
            "encoded_text": encoded_result,
            "length": len(encoded_result),
            "status": "success",
            "user_id": user_id.upper(),
            "original_text_length": len(text)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding text: {str(e)}")

@app.get("/encode/default")
async def encode_text_default(text: str):
    """
    تشفير النص باستخدام المعرف الافتراضي
    """
    try:
        default_user_id = "c8f0dacb08"
        encoded_result = process_packet_data(text, default_user_id)
        
        return {
            "encoded_text": encoded_result,
            "length": len(encoded_result),
            "status": "success",
            "user_id": default_user_id,
            "original_text_length": len(text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding text: {str(e)}")

@app.get("/userid/validate")
async def validate_user_id(user_id: str):
    """
    التحقق من صحة معرف المستخدم
    """
    if len(user_id) != 8:
        return {"valid": False, "message": "يجب أن يكون 8 أحرف", "user_id": user_id}
    
    if not all(c in '0123456789ABCDEFabcdef' for c in user_id):
        return {"valid": False, "message": "يجب أن يحتوي على أحرف hex فقط", "user_id": user_id}
    
    return {"valid": True, "message": "معرف صالح", "user_id": user_id.upper()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)