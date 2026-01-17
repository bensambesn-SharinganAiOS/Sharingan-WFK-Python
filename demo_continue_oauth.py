#!/usr/bin/env python3
"""
Continue GitHub OAuth flow - Go to GitHub, click Continue with Google, select email
"""
import sys
import time
sys.path.insert(0, '/root/Projets/Sharingan-WFK-Python')

from sharingan_app._internal.browser_controller_complete import BrowserController

def main():
    print("🚀 Starting GitHub OAuth flow...")
    
    ctrl = get_browser_controller()
    
    # Launch browser fresh
    print("1. Launching browser...")
    ctrl.launch_browser("chrome", headless=False)
    ctrl.navigate("https://github.com/login")
    time.sleep(3)
    
    print(f"   URL: {ctrl.get_current_url()}")
    print(f"   Title: {ctrl.get_page_title()}")
    
    # Step 2: Find and click "Continue with Google"
    print("\n2. Looking for 'Continue with Google' button...")
    time.sleep(2)
    
    # Try multiple selectors
    google_btn = None
    
    # Method 1: By button text
    buttons = ctrl.find_elements("button")
    for btn in buttons:
        text = ctrl.get_element_text(btn).lower() if btn else ""
        if "google" in text:
            google_btn = btn
            print(f"   Found by text: '{text}'")
            break
    
    # Method 2: By link containing Google
    if not google_btn:
        links = ctrl.find_elements("a")
        for link in links:
            text = ctrl.get_element_text(link).lower() if link else ""
            href = ctrl.get_element_attribute(link, "href") if link else ""
            if "google" in text or "google" in href:
                google_btn = link
                print(f"   Found by link: '{text}' -> {href[:60]}...")
                break
    
    # Method 3: By CSS selector for OAuth buttons
    if not google_btn:
        oauth_div = ctrl.find_elements('div[style*="google"]')
        if oauth_div:
            print(f"   Found OAuth div")
    
    if google_btn:
        print("\n3. Clicking 'Continue with Google'...")
        ctrl.click_element(google_btn)
        time.sleep(4)  # Wait for Google page to load
        
        print(f"   New URL: {ctrl.get_current_url()}")
        print(f"   Title: {ctrl.get_page_title()}")
    else:
        print("   ❌ Could not find Google button")
        # Show available buttons
        buttons = ctrl.find_elements("button")
        print(f"   Available buttons ({len(buttons)}):")
        for btn in buttons[:5]:
            text = ctrl.get_element_text(btn)[:50] if btn else "(empty)"
            print(f"      - {text}")
        return
    
    # Step 4: On Google page - select email
    print("\n4. Looking for email selection...")
    time.sleep(3)
    
    current_url = ctrl.get_current_url().lower()
    
    if "accounts.google.com" in current_url:
        print("   ✅ On Google accounts page")
        
        # Check for email list items (usually li or div elements)
        email_items = ctrl.find_elements("li") or ctrl.find_elements("div[role='listitem']") or ctrl.find_elements('div[data-email]')
        
        print(f"   Found {len(email_items)} list items")
        
        if email_items:
            # Click the first email (user's email should be there)
            print("   Clicking first email...")
            ctrl.click_element(email_items[0])
            time.sleep(3)
        else:
            # Try to find by email pattern
            all_divs = ctrl.find_elements("div")
            email_divs = [d for d in all_divs if d and "@" in (ctrl.get_element_text(d) or "")]
            print(f"   Found {len(email_divs)} divs with @ symbol")
            
            if email_divs:
                for div in email_divs[:5]:
                    text = ctrl.get_element_text(div)[:50]
                    print(f"      - {text}")
        
        print(f"   Current URL: {ctrl.get_current_url()}")
        print(f"   Title: {ctrl.get_page_title()}")
        
    else:
        print(f"   ❌ Not on Google page: {current_url}")
    
    # Step 5: If password needed, enter it
    print("\n5. Checking if password needed...")
    time.sleep(2)
    
    current_url = ctrl.get_current_url().lower()
    
    if "password" in ctrl.get_page_title().lower() or "sign in" in ctrl.get_page_title().lower():
        print("   Password page detected!")
        print("   ❌ Cannot enter password automatically (would need credentials)")
        print("   Please enter password manually, then press Enter...")
        input("   Press Enter when done...")
    
    # Step 6: Check final state
    print("\n6. Final state:")
    print(f"   URL: {ctrl.get_current_url()}")
    print(f"   Title: {ctrl.get_page_title()}")
    
    # Take screenshot
    try:
        ctrl.take_screenshot("/tmp/github_oauth_state.png")
        print("   Screenshot saved to /tmp/github_oauth_state.png")
    except:
        pass
    
    print("\n" + "="*60)
    print("OAuth flow in progress. Browser is OPEN.")
    print("="*60)

if __name__ == "__main__":
    main()
