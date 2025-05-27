import streamlit as st
import requests
#import requests  # Ensure this is at the top of your app.py
import re
import uuid
import asyncio
from tech_scanner import scan_technologies
from password_checker import check_password_strength
from phishing_detector import detect_phishing
from subdomain_finder import find_subdomains
from pyppeteer import launch
from bs4 import BeautifulSoup

st.set_page_config(page_title="ThreatGuardian AI", layout="wide")

API_KEY = "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"
MODEL_NAME = "llama3-70b-8192"
SYSTEM_PROMPT = (
    "You are CortexIQ, a friendly and intelligent AI chatbot who explains anything about technology topics simply and clearly. You tailor your explanations "
    "to the user's level, providing detailed insights, examples, and step-by-step guidance. "
    "Be warm and patient, encouraging curiosity and further questions. When possible, include "
    "practical advice or code snippets to help users learn effectively."
)

if "history" not in st.session_state:
    st.session_state.history = {}
if "titles" not in st.session_state:
    st.session_state.titles = {}
if "current_chat_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_chat_id = new_id
    st.session_state.history[new_id] = []
    st.session_state.titles[new_id] = "New Chat"

st.sidebar.title("🛡️ ThreatGuardian AI")
st.sidebar.subheader("Your Free AI-Powered Cybersecurity Assistant")

selected = st.sidebar.radio("Choose a feature", [
    "Home", 
    "Password Strength Checker", 
    "Phishing Email Detector",
    "Website Technology Scanner",
    "Subdomain Finder",
    "CortexIQ Chat"
])

def get_groq_response(user_msg):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in st.session_state.history[st.session_state.current_chat_id]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.5
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        result = response.json()
        return result["choices"][0]["message"]["content"] if "choices" in result else "❌ No response."
    except Exception as e:
        return f"❌ Error: {str(e)}"

if selected == "Home":
    st.title("Welcome to ThreatGuardian AI")
    st.markdown("""
    Protect your digital world with free tools for:
    - 🔐 Password Strength Checking
    - 📧 Phishing Email Detection
    - 🕵️ Website Technology Scanning
    - 🌐 Subdomain Enumeration
    - 🤖 AI Chatbot
    """)
#Password Strength Checker
elif selected == "Password Strength Checker":
    st.subheader("🔐 Check Your Password Strength")

    if "reset_password" not in st.session_state:
        st.session_state.reset_password = False
    if "password_input" not in st.session_state:
        st.session_state.password_input = ""
    if st.session_state.reset_password:
        st.session_state.password_input = ""
        st.session_state.reset_password = False

    password = st.text_input("Enter your password", type="password", key="password_input")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Check Strength"):
            if password:
                strength, message = check_password_strength(password)
                st.info(f"**Strength:** {strength}")
                st.write(message)
            else:
                st.warning("Please enter a password to check.")

    with col2:
        if st.button("🔄 Reset"):
            st.session_state.reset_password = True
            st.rerun()

#Phishing Email Detector
elif selected == "Phishing Email Detector":
    from phishing_detector import detect_phishing

    st.subheader("📧 Phishing Email Detector")

    if "result" not in st.session_state:
        st.session_state.result = None
    if "message" not in st.session_state:
        st.session_state.message = ""

    def reset_inputs():
        st.session_state["email_input"] = ""
        st.session_state.result = None
        st.session_state.message = ""

    st.text_area("Paste the full email message:", key="email_input", height=200)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Analyze"):
            if st.session_state.email_input.strip():
                label, message = detect_phishing(st.session_state.email_input)
                st.session_state.result = label
                st.session_state.message = message
            else:
                st.warning("Please enter an email message before analyzing.")

    with col2:
        st.button("🔄 Reset", on_click=reset_inputs)

    if st.session_state.result is not None:
        if st.session_state.result == "Phishing":
            st.error(f"**Result:** {st.session_state.result}")
        else:
            st.success(f"**Result:** {st.session_state.result}")
        st.write(st.session_state.message)

# Website Technology Scanner
elif selected == "Website Technology Scanner":

    st.subheader("🕵️ Website Technology Scanner")

    if "reset_scan" not in st.session_state:
        st.session_state.reset_scan = False
    if "site_input" not in st.session_state:
        st.session_state.site_input = ""
    if "scan_result" not in st.session_state:
        st.session_state.scan_result = None
    if "scanned" not in st.session_state:
        st.session_state.scanned = False

    if st.session_state.reset_scan:
        st.session_state.site_input = ""
        st.session_state.scan_result = None
        st.session_state.scanned = False
        st.session_state.reset_scan = False

    url = st.text_input("Enter website URL (e.g., https://example.com)", key="site_input")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Scan Website"):
            if url.strip():
                with st.spinner("Launching browser and scanning (may take 10–20 sec)..."):
                    try:
                        result = scan_technologies(url)

                        # Try getting the web server and headers
                        try:
                            headers = {}
                            response = requests.head(url, timeout=10, allow_redirects=True)
                            headers = response.headers
                            server = headers.get("Server", "")
                            if not server:
                                # fallback to GET request
                                response = requests.get(url, timeout=10)
                                headers = response.headers
                                server = headers.get("Server", "")
                            if server:
                                result["Web Server"] = [server]
                            else:
                                result["Web Server"] = ["Not exposed"]
                        except Exception as e:
                            result["Web Server"] = [f"Error: {str(e)}"]
                            headers = {}

                        # CDN detection from headers
                        cdn_providers = {
                            "cloudflare": "Cloudflare",
                            "akamai": "Akamai",
                            "fastly": "Fastly",
                            "stackpath": "StackPath",
                            "incapsula": "Imperva Incapsula"
                        }
                        cdns = []
                        for k, v in headers.items():
                            for key, name in cdn_providers.items():
                                if key in k.lower() or key in v.lower():
                                    cdns.append(name)
                        if cdns:
                            result["CDN"] = list(set(cdns))

                        # CMS detection from HTML
                        try:
                            html = requests.get(url, timeout=10).text.lower()
                            cms_list = []
                            if "wp-content" in html or "wordpress" in html:
                                cms_list.append("WordPress")
                            if "cdn.shopify.com" in html or "shopify" in html:
                                cms_list.append("Shopify")
                            if "drupal" in html:
                                cms_list.append("Drupal")
                            if "joomla" in html:
                                cms_list.append("Joomla")
                            if cms_list:
                                result["CMS"] = cms_list
                        except:
                            pass

                        st.session_state.scan_result = result
                        st.session_state.scanned = True
                    except Exception as e:
                        st.session_state.scan_result = {"Error": [str(e)]}
                        st.session_state.scanned = True
            else:
                st.warning("⚠️ Please enter a website URL.")

    with col2:
        if st.button("🔄 Reset"):
            st.session_state.reset_scan = True
            st.rerun()

    if st.session_state.scanned:
        results = st.session_state.scan_result
        if not results or results == {}:
            st.warning("⚠️ No technologies detected. The site might not reveal them or is too minimal.")
        elif "Error" in results:
            st.error(f"❌ {results['Error'][0]}")
        else:
            st.success("✅ Technologies Detected:")
            for tech_type, tech_names in results.items():
                st.markdown(f"**{tech_type}:**")
                for name in tech_names:
                    st.markdown(f"- `{name}`")

#Subdomain Finder
elif selected == "Subdomain Finder":
    st.subheader("🌐 Subdomain Finder")

    if "reset_scan" not in st.session_state:
        st.session_state.reset_scan = False
    if "domain_input" not in st.session_state:
        st.session_state.domain_input = ""
    if "subdomain_result" not in st.session_state:
        st.session_state.subdomain_result = None

    if st.session_state.reset_scan:
        st.session_state.domain_input = ""
        st.session_state.subdomain_result = None
        st.session_state.reset_scan = False

    domain = st.text_input("Enter domain (e.g., example.com)", value=st.session_state.domain_input, key="domain_input")
    scan_mode = st.radio("Scan Mode", ["Quick", "Deep"], horizontal=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔎 Find Subdomains"):
            if domain.strip():
                from subdomain_finder import find_subdomains
                mode = "quick" if scan_mode == "Quick" else "deep"

                with st.spinner(f"Scanning in {scan_mode} mode..."):
                    result = find_subdomains(domain, mode=mode)
                    st.session_state.subdomain_result = result
            else:
                st.warning("⚠️ Please enter a valid domain.")

    with col2:
        if st.button("🔄 Reset"):
            st.session_state.reset_scan = True
            st.rerun()

    result = st.session_state.subdomain_result

    if result is not None:
        if isinstance(result, list) and result and isinstance(result[0], str) and result[0].lower().startswith("error"):
            st.error(result[0])
        elif isinstance(result, list) and len(result) > 0:
            st.success(f"✅ Found {len(result)} subdomains:")
            for sub in result:
                st.markdown(f"- `{sub}`")
        else:
            st.warning("⚠️ No subdomains found.")

#CortexIQ Chat
elif selected == "CortexIQ Chat":
    st.title("🤖 CortexIQ Chat")
    st.caption("Ask me anything....")

    st.sidebar.subheader("📋 Chat History")
    chat_ids = list(st.session_state.history.keys())
    for chat_id in chat_ids:
        title = st.session_state.titles.get(chat_id, "Untitled")[:40]
        cols = st.sidebar.columns([0.8, 0.2])
        if cols[0].button(f"📄 {title}", key=f"view_{chat_id}"):
            st.session_state.current_chat_id = chat_id
        if cols[1].button("🗑️", key=f"delete_{chat_id}"):
            del st.session_state.history[chat_id]
            st.session_state.titles.pop(chat_id, None)
            if st.session_state.current_chat_id == chat_id:
                if st.session_state.history:
                    st.session_state.current_chat_id = list(st.session_state.history.keys())[0]
                else:
                    new_id = str(uuid.uuid4())
                    st.session_state.current_chat_id = new_id
                    st.session_state.history[new_id] = []
                    st.session_state.titles[new_id] = "New Chat"
            st.experimental_rerun()

    if st.sidebar.button("➕ New Chat"):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.history[new_id] = []
        st.session_state.titles[new_id] = "New Chat"

    for msg in st.session_state.history[st.session_state.current_chat_id]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    uploaded_file = st.file_uploader("📎 Upload a file", type=["txt", "pdf", "csv", "docx"], label_visibility="collapsed")
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8", errors="ignore")
        snippet = content[:2000]
        st.session_state.history[st.session_state.current_chat_id].append({
            "role": "user",
            "content": f"📎 Uploaded file: {uploaded_file.name}\n\n```text\n{snippet}\n```"
        })
        st.rerun()

    user_input = st.chat_input("Type your question here...")
    if user_input:
        chat_id = st.session_state.current_chat_id
        if st.session_state.titles.get(chat_id) == "New Chat":
            st.session_state.titles[chat_id] = user_input[:40]
        st.session_state.history[chat_id].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("CortexIQ is thinking..."):
                reply = get_groq_response(user_input)
                st.markdown(reply)
        st.session_state.history[chat_id].append({"role": "assistant", "content": reply})
