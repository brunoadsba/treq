#!/usr/bin/env python3
import asyncio
import sys
from playwright.async_api import async_playwright

async def analyze_treq_frontend():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Acessar a aplicação
            await page.goto("http://localhost:3000", wait_until="domcontentloaded", timeout=10000)
            
            # Aguardar um pouco para o JavaScript carregar
            await page.wait_for_timeout(3000)
            
            # Informações básicas
            title = await page.title()
            url = page.url
            
            print("=== ANÁLISE DO FRONTEND TREQ ENTERPRISE ===")
            print(f"Título: {title}")
            print(f"URL: {url}")
            print()
            
            # Verificar se foi redirecionado para login
            if "/login" in url:
                print("🔐 REDIRECIONADO PARA LOGIN")
                print("A aplicação possui autenticação obrigatória")
                
                # Analisar página de login
                login_elements = await page.query_selector_all("input, button, form")
                print(f"Elementos de login encontrados: {len(login_elements)}")
                
                for i, elem in enumerate(login_elements):
                    tag = await elem.evaluate("el => el.tagName")
                    input_type = await elem.get_attribute("type") or ""
                    placeholder = await elem.get_attribute("placeholder") or ""
                    text = await elem.text_content() or ""
                    
                    print(f"  [{i+1}] {tag} - type: {input_type}, placeholder: '{placeholder}', text: '{text[:30]}'")
                
            else:
                print("🏠 PÁGINA PRINCIPAL")
                
                # Analisar elementos principais
                main_elements = await page.query_selector_all("main, [role='main'], .chat, #chat")
                print(f"Elementos principais: {len(main_elements)}")
                
                # Verificar inputs de chat
                chat_inputs = await page.query_selector_all("input, textarea")
                print(f"Inputs encontrados: {len(chat_inputs)}")
                
                for i, input_elem in enumerate(chat_inputs):
                    placeholder = await input_elem.get_attribute("placeholder") or ""
                    input_type = await input_elem.get_attribute("type") or "text"
                    print(f"  Input {i+1}: {input_type} - '{placeholder}'")
            
            # Verificar estrutura geral da página
            print("\n📋 ESTRUTURA DA PÁGINA:")
            
            # Contar elementos por tipo
            buttons = await page.query_selector_all("button")
            inputs = await page.query_selector_all("input, textarea")
            headings = await page.query_selector_all("h1, h2, h3, h4, h5, h6")
            
            print(f"Botões: {len(buttons)}")
            print(f"Inputs: {len(inputs)}")
            print(f"Títulos: {len(headings)}")
            
            # Verificar se há elementos de chat específicos
            chat_indicators = [
                "[class*='chat']",
                "[class*='message']",
                "[placeholder*='pergunt']",
                "[placeholder*='message']",
                "[aria-label*='chat']"
            ]
            
            print("\n💬 INDICADORES DE CHAT:")
            for selector in chat_indicators:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"  ✅ {selector}: {len(elements)} elementos")
            
            # Capturar screenshot
            await page.screenshot(path="/home/brunoadsba/treq/treq_frontend_analysis.png", full_page=True)
            print(f"\n📸 Screenshot salvo: treq_frontend_analysis.png")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_treq_frontend())
