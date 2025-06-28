import streamlit as st

def render_copy_button(all_text: str):
    """
    전체 텍스트를 클립보드에 복사하는 버튼을 렌더링합니다.
    """
    copy_js = f"""
    <script>
    async function copyToClipboard() {{
        const text = `{all_text.replace('`','\\`').replace('$','\\$')}`;
        try {{
            await navigator.clipboard.writeText(text);
            document.getElementById('copy-status').innerText = '✅ 복사 완료!';
        }} catch (e) {{
            document.getElementById('copy-status').innerText = '❌ 복사 실패';
        }}
        setTimeout(() => document.getElementById('copy-status').innerText = '', 3000);
    }}
    </script>
    <button onclick="copyToClipboard()" style="
        background: #4ECDC4; color: white; border:none;
        padding:8px 16px; border-radius:4px; cursor:pointer;
    ">📋 전체 내용 복사</button>
    <span id="copy-status" style="margin-left:10px;"></span>
    """
    st.markdown(copy_js, unsafe_allow_html=True)
