#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import json

async def explore_treq_frontend():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("🔍 Acessando Treq Enterprise...")
            await page.goto("http://localhost:3000", wait_until="networkidle")
            
            # Capturar título e URL atual
            title = await page.title()
            url = page.url
            print(f"📄 Título: {title}")
            print(f"🌐 URL: {url}")
            
            # Capturar elementos principais da página
            print("\n🎯 Elementos principais encontrados:")
            
            # Buscar por elementos comuns de interface
            selectors = [
                "h1, h2, h3",  # Títulos
                "button",      # Botões
                "input",       # Inputs
                "nav",         # Navegação
                "[data-testid]", # Elementos com test-id
                ".chat, #chat", # Elementos de chat
                "form"         # Formulários
            ]
            
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"\n{selector}:")
                    for i, element in enumerate(elements[:5]):  # Limitar a 5 elementos
                        text = await element.text_content()
                        tag = await element.evaluate("el => el.tagName")
                        classes = await element.get_attribute("class") or ""
                        test_id = await element.get_attribute("data-testid") or ""
                        
                        info = f"  [{i+1}] {tag}"
                        if classes: info += f" .{classes}"
                        if test_id: info += f" [testid={test_id}]"
                        if text and text.strip(): info += f" - '{text.strip()[:50]}'"
                        print(info)
            
            # Verificar se há elementos de chat/conversação
            print("\n💬 Verificando elementos de chat:")
            chat_selectors = [
                "[class*='chat']",
                "[class*='message']", 
                "[class*='conversation']",
                "textarea",
                "[placeholder*='message']",
                "[placeholder*='pergunt']"
            ]
            
            for selector in chat_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"  Encontrado: {selector} ({len(elements)} elementos)")
            
            # Capturar estrutura da página
            print("\n🏗️ Estrutura da página:")
            body_html = await page.evaluate("""
                () => {
                    const body = document.body;
                    const getStructure = (element, depth = 0) => {
                        if (depth > 3) return '';
                        let result = '  '.repeat(depth) + element.tagName;
                        if (element.className) result += ` .${element.className.split(' ').join('.')}`;
                        if (element.id) result += ` #${element.id}`;
                        result += '\\n';
                        
                        for (let child of element.children) {
                            if (child.tagName !== 'SCRIPT' && child.tagName !== 'STYLE') {
                                result += getStructure(child, depth + 1);
                            }
                        }
                        return result;
                    };
                    return getStructure(body);
                }
            """)
            print(body_html[:1000] + "..." if len(body_html) > 1000 else body_html)
            
            # Verificar se há JavaScript errors
            print("\n⚠️ Verificando erros JavaScript:")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.wait_for_timeout(2000)  # Aguardar 2 segundos
            
            if errors:
                for error in errors:
                    print(f"  ❌ {error}")
            else:
                print("  ✅ Nenhum erro JavaScript detectado")
            
            # Tentar interagir com elementos de input se existirem
            print("\n🖱️ Testando interações:")
            inputs = await page.query_selector_all("input, textarea")
            if inputs:
                for i, input_elem in enumerate(inputs[:2]):  # Testar apenas os 2 primeiros
                    placeholder = await input_elem.get_attribute("placeholder") or ""
                    input_type = await input_elem.get_attribute("type") or "text"
                    print(f"  Input {i+1}: type={input_type}, placeholder='{placeholder}'")
            
            # Screenshot para análise visual
            await page.screenshot(path="/home/brunoadsba/treq/frontend_screenshot.png")
            print("\n📸 Screenshot salvo em: frontend_screenshot.png")
            
        except Exception as e:
            print(f"❌ Erro ao explorar frontend: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(explore_treq_frontend())
