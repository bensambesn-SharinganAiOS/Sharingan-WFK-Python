#!/usr/bin/env python3
"""
Control Chrome via Chrome DevTools Protocol using websockets library
"""
import asyncio
import json
import urllib.request
import websockets
import urllib.error

CDP_PORT = 35189
msg_id = 1

async def get_ws_url():
    targets = json.loads(urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json").read())
    for t in targets:
        if t.get('type') == 'page':
            return t['webSocketDebuggerUrl']
    return None

async def cdp_send(ws, method, params=None):
    global msg_id
    msg = {"id": msg_id, "method": method, "params": params or {}}
    msg_id += 1
    await ws.send(json.dumps(msg))
    response = await ws.recv()
    return json.loads(response)

async def click_google_button():
    ws_url = await get_ws_url()
    if not ws_url:
        print("ERROR: Could not find browser debug URL")
        return
    
    print(f"Connecting to Chrome DevTools...")
    
    async with websockets.connect(ws_url) as ws:
        print("Connected!")
        
        # Click "Continue with Google"
        print("\n[1] Clicking 'Continue with Google'...")
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": """
                (() => {
                    const btns = document.querySelectorAll('button');
                    for (let b of btns) {
                        if (b.innerText.toLowerCase().includes('continue with google')) {
                            b.click();
                            return 'CLICKED: ' + b.innerText.substring(0, 50);
                        }
                    }
                    return 'BUTTON_NOT_FOUND';
                })()
            """,
            "returnByValue": True
        })
        print(f"   Result: {result.get('result', {}).get('result', {}).get('value', 'unknown')}")
        
        await asyncio.sleep(3)
        
        # Check current URL
        print("\n[2] Checking location...")
        result = await cdp_send(ws, "Runtime.evaluate", {
            "expression": "window.location.href",
            "returnByValue": True
        })
        url = result.get('result', {}).get('result', {}).get('value', 'unknown')
        print(f"   URL: {url}")
        
        if 'accounts.google.com' in url or 'google' in url:
            print("\n[3] On Google page - typing email: bensambe.sn@gmail.com")
            
            # Type email
            result = await cdp_send(ws, "Runtime.evaluate", {
                "expression": """
                    (() => {
                        const selectors = [
                            'input[type="email"]',
                            'input[name="identifier"]', 
                            'input[id="identifierId"]'
                        ];
                        for (let sel of selectors) {
                            const inp = document.querySelector(sel);
                            if (inp) {
                                inp.value = '';
                                inp.value = 'bensambe.sn@gmail.com';
                                inp.dispatchEvent(new Event('input', {bubbles: true}));
                                inp.dispatchEvent(new Event('change', {bubbles: true}));
                                return 'FILLED: ' + inp.value;
                            }
                        }
                        return 'INPUT_NOT_FOUND';
                    })()
                """,
                "returnByValue": True
            })
            fill_result = result.get('result', {}).get('result', {}).get('value', 'unknown')
            print(f"   {fill_result}")
            
            await asyncio.sleep(1)
            
            # Click "Next"
            print("\n[4] Clicking Next...")
            result = await cdp_send(ws, "Runtime.evaluate", {
                "expression": """
                    (() => {
                        const btns = document.querySelectorAll('button, div[role="button"]');
                        for (let b of btns) {
                            const txt = b.innerText.toLowerCase();
                            if (txt.includes('next') || txt.includes('suivant')) {
                                b.click();
                                return 'CLICKED_NEXT: ' + txt.substring(0, 30);
                            }
                        }
                        return 'NEXT_NOT_FOUND';
                    })()
                """,
                "returnByValue": True
            })
            next_result = result.get('result', {}).get('result', {}).get('value', 'unknown')
            print(f"   {next_result}")
            
            await asyncio.sleep(2)
            
            # Check for password field
            print("\n[5] Checking for password field...")
            result = await cdp_send(ws, "Runtime.evaluate", {
                "expression": "document.querySelector('input[type=\"password\"]') ? 'PASSWORD_READY' : 'NO_PASSWORD_YET'",
                "returnByValue": True
            })
            pw_status = result.get('result', {}).get('result', {}).get('value', 'unknown')
            print(f"   {pw_status}")
            
            # Get current title
            result = await cdp_send(ws, "Runtime.evaluate", {
                "expression": "document.title",
                "returnByValue": True
            })
            title = result.get('result', {}).get('result', {}).get('value', 'unknown')
            print(f"   Title: {title}")
        
        print("\n" + "="*50)
        print("OAUTH FLOW PROGRESS")
        print("- Email entered: bensambe.sn@gmail.com")
        print("- Next button clicked")
        print("- NOW: Enter password manually")
        print("="*50)

async def main():
    await click_google_button()

if __name__ == "__main__":
    asyncio.run(main())
