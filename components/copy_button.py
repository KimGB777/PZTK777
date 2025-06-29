# components/copy_button.py
import streamlit as st

def render_copy_button(text: str) -> None:
    js = f"""
    <script>
    async function copyAll() {{
      await navigator.clipboard.writeText(`{text.replace('`','\\`')}`);
      const s = document.getElementById('cb-status');
      s.textContent = '✅ 복사 완료';
      setTimeout(() => s.textContent = '', 2000);
    }}
    </script>
    <button onclick="copyAll()" style="
       background:#4ECDC4;color:#fff;border:none;padding:8px 16px;
       border-radius:6px;cursor:pointer;font-size:14px;">
       📋 전체 복사
    </button>
    <span id="cb-status" style="margin-left:8px;font-weight:bold;"></span>
    """
    st.markdown(js, unsafe_allow_html=True)
