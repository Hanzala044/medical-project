#!/usr/bin/env python3
"""
Startup script for MEDicos Medical Chatbot
This script starts both the chatbot API and the main website
"""

import subprocess
import time
import sys
import os
import signal
import requests
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatbotStarter:
    def __init__(self):
        self.chatbot_process = None
        self.website_process = None
        self.running = True
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        logger.info("🔍 Checking dependencies...")
        
        try:
            import openai
            logger.info("✅ OpenAI package found")
        except ImportError:
            logger.warning("⚠️ OpenAI package not found. Install with: pip install openai")
        
        try:
            import google.generativeai
            logger.info("✅ Google Generative AI package found")
        except ImportError:
            logger.warning("⚠️ Google Generative AI package not found. Install with: pip install google-generativeai")
        
        try:
            import flask
            logger.info("✅ Flask package found")
        except ImportError:
            logger.error("❌ Flask package not found. Install with: pip install flask")
            return False
        
        return True
    
    def check_environment(self):
        """Check environment variables"""
        logger.info("🔍 Checking environment variables...")
        
        openai_key = os.getenv('OPENAI_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if not openai_key and not google_key:
            logger.warning("⚠️ No AI API keys found. Set OPENAI_API_KEY or GOOGLE_API_KEY in .env file")
            logger.info("   The chatbot will work with fallback responses only")
        else:
            if openai_key:
                logger.info("✅ OpenAI API key found")
            if google_key:
                logger.info("✅ Google API key found")
        
        return True
    
    def start_chatbot_api(self):
        """Start the chatbot API server"""
        logger.info("🚀 Starting Chatbot API...")
        
        try:
            self.chatbot_process = subprocess.Popen(
                [sys.executable, "chatbot_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            # Check if the server is running
            try:
                response = requests.get("http://localhost:5001/api/chatbot/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Chatbot API started successfully on http://localhost:5001")
                    return True
                else:
                    logger.error(f"❌ Chatbot API health check failed: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Chatbot API not responding: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start Chatbot API: {e}")
            return False
    
    def start_website(self):
        """Start the main website"""
        logger.info("🚀 Starting MEDicos Website...")
        
        try:
            self.website_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            # Check if the website is running
            try:
                response = requests.get("http://localhost:5000", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Website started successfully on http://localhost:5000")
                    return True
                else:
                    logger.error(f"❌ Website health check failed: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Website not responding: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start Website: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor running processes"""
        while self.running:
            # Check chatbot process
            if self.chatbot_process and self.chatbot_process.poll() is not None:
                logger.warning("⚠️ Chatbot API process stopped unexpectedly")
                self.running = False
                break
            
            # Check website process
            if self.website_process and self.website_process.poll() is not None:
                logger.warning("⚠️ Website process stopped unexpectedly")
                self.running = False
                break
            
            time.sleep(5)
    
    def stop_services(self):
        """Stop all running services"""
        logger.info("🛑 Stopping services...")
        
        if self.chatbot_process:
            self.chatbot_process.terminate()
            try:
                self.chatbot_process.wait(timeout=5)
                logger.info("✅ Chatbot API stopped")
            except subprocess.TimeoutExpired:
                self.chatbot_process.kill()
                logger.info("⚠️ Chatbot API force stopped")
        
        if self.website_process:
            self.website_process.terminate()
            try:
                self.website_process.wait(timeout=5)
                logger.info("✅ Website stopped")
            except subprocess.TimeoutExpired:
                self.website_process.kill()
                logger.info("⚠️ Website force stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
        self.stop_services()
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        print("=" * 60)
        print("🚀 MEDicos Medical Chatbot Startup")
        print("=" * 60)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("❌ Dependency check failed. Please install required packages.")
            return False
        
        # Check environment
        self.check_environment()
        
        # Start services
        chatbot_started = self.start_chatbot_api()
        website_started = self.start_website()
        
        if not chatbot_started or not website_started:
            logger.error("❌ Failed to start one or more services")
            self.stop_services()
            return False
        
        print("\n" + "=" * 60)
        print("🎉 All services started successfully!")
        print("=" * 60)
        print("📱 Website: http://localhost:5000")
        print("🤖 Chatbot API: http://localhost:5001")
        print("📋 API Health: http://localhost:5001/api/chatbot/health")
        print("🧪 Test Chatbot: python test_chatbot.py")
        print("\n💡 The chatbot will appear as a floating button on all pages")
        print("💡 Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Start monitoring
        monitor_thread = Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Keyboard interrupt received")
        finally:
            self.stop_services()
        
        return True

def main():
    """Main function"""
    starter = ChatbotStarter()
    success = starter.run()
    
    if success:
        logger.info("✅ Services stopped successfully")
    else:
        logger.error("❌ Services failed to start or stopped with errors")
        sys.exit(1)

if __name__ == "__main__":
    main() 