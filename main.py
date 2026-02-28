#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CryptoMentor AI Bot - Main Entry Point
Simple entry point for Railway deployment
"""

if __name__ == "__main__":
    import bot
    import asyncio
    
    print("🚀 Starting CryptoMentor AI Bot...")
    
    # Create bot instance
    telegram_bot = bot.TelegramBot()
    
    # Run bot
    asyncio.run(telegram_bot.run())
