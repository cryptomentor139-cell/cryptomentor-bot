"""
OpenClaw Vision Tools
Image analysis for trading charts using GPT-4 Vision
"""

import os
import logging
import base64
import httpx
from typing import Dict, Optional
from io import BytesIO

logger = logging.getLogger(__name__)


class OpenClawVisionTools:
    """Tools for analyzing trading chart images"""
    
    def __init__(self):
        """Initialize vision tools"""
        self.api_key = os.getenv('OPENCLAW_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENCLAW_BASE_URL', 'https://openrouter.ai/api/v1')
        
        if not self.api_key:
            logger.warning("No API key found for vision tools")
    
    async def analyze_chart_image(
        self,
        image_data: bytes,
        user_question: Optional[str] = None
    ) -> Dict:
        """
        Analyze trading chart image using GPT-4 Vision
        
        Args:
            image_data: Image bytes
            user_question: Optional specific question about the chart
            
        Returns:
            Dict with analysis results
        """
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'API key not configured'
                }
            
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare prompt
            if user_question:
                prompt = f"""Analyze this trading chart image and answer the following question:

{user_question}

Provide detailed technical analysis including:
1. Current trend (bullish/bearish/sideways)
2. Key support and resistance levels visible
3. Chart patterns identified
4. Technical indicators visible (if any)
5. Trading recommendation based on the chart
6. Risk assessment

Be specific and reference what you see in the chart."""
            else:
                prompt = """Analyze this trading chart image in detail:

1. **Trend Analysis:**
   - Current trend direction (bullish/bearish/sideways)
   - Trend strength
   - Timeframe visible

2. **Technical Levels:**
   - Key support levels
   - Key resistance levels
   - Current price position

3. **Chart Patterns:**
   - Any patterns visible (triangles, head & shoulders, flags, etc.)
   - Pattern completion status
   - Breakout potential

4. **Technical Indicators:**
   - Indicators visible on chart (RSI, MACD, MA, etc.)
   - Indicator signals
   - Divergences if any

5. **Volume Analysis:**
   - Volume trend
   - Volume confirmation

6. **Trading Recommendation:**
   - Entry points
   - Stop loss levels
   - Take profit targets
   - Risk/reward ratio

7. **Risk Assessment:**
   - Market conditions
   - Volatility assessment
   - Risk level (low/medium/high)

Provide actionable insights based on what you see in the chart."""
            
            # Call OpenRouter API with vision model
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-4-vision-preview",  # GPT-4 Vision
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": prompt
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.7
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = data['choices'][0]['message']['content']
                    
                    return {
                        'success': True,
                        'analysis': analysis,
                        'model': 'gpt-4-vision-preview',
                        'tokens_used': data.get('usage', {})
                    }
                else:
                    error_text = response.text
                    logger.error(f"Vision API error: {response.status_code} - {error_text}")
                    return {
                        'success': False,
                        'error': f"API error: {response.status_code}",
                        'details': error_text
                    }
                    
        except Exception as e:
            logger.error(f"Error analyzing chart image: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_telegram_photo(
        self,
        telegram_file,
        user_question: Optional[str] = None
    ) -> Dict:
        """
        Analyze photo from Telegram message
        
        Args:
            telegram_file: Telegram File object
            user_question: Optional specific question
            
        Returns:
            Dict with analysis results
        """
        try:
            # Download photo
            photo_bytes = await telegram_file.download_as_bytearray()
            
            # Analyze
            return await self.analyze_chart_image(
                bytes(photo_bytes),
                user_question
            )
            
        except Exception as e:
            logger.error(f"Error analyzing Telegram photo: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def quick_chart_analysis(self, image_data: bytes) -> Dict:
        """
        Quick chart analysis with concise output
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dict with quick analysis
        """
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'API key not configured'
                }
            
            # Encode image
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            prompt = """Analyze this trading chart quickly and provide:

1. **Trend:** Bullish/Bearish/Sideways
2. **Key Levels:** Support and resistance
3. **Pattern:** Any chart pattern visible
4. **Signal:** Buy/Sell/Hold recommendation
5. **Risk:** Low/Medium/High

Keep it concise and actionable."""
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-4-vision-preview",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{base64_image}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 500,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = data['choices'][0]['message']['content']
                    
                    return {
                        'success': True,
                        'analysis': analysis,
                        'model': 'gpt-4-vision-preview'
                    }
                else:
                    return {
                        'success': False,
                        'error': f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error in quick chart analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_vision_tools_instance = None

def get_vision_tools() -> OpenClawVisionTools:
    """Get singleton instance of vision tools"""
    global _vision_tools_instance
    if _vision_tools_instance is None:
        _vision_tools_instance = OpenClawVisionTools()
    return _vision_tools_instance
