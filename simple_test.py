#!/usr/bin/env python3
import asyncio
import sys
from playwright.async_api import async_playwright

async def simple_test():
    print("Iniciando teste simples...")
    try:
        async with async_playwright() as p:
            print("Playwright iniciado")
            browser = await p.chromium.launch(headless=True)
            print("Browser lançado")
            page = await browser.new_page()
            print("Página criada")
            
            print("Acessando localhost:3000...")
            response = await page.goto("http://localhost:3000")
            print(f"Response status: {response.status}")
            
            title = await page.title()
            print(f"Título da página: {title}")
            
            url = page.url
            print(f"URL atual: {url}")
            
            await browser.close()
            print("Browser fechado")
            
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())
