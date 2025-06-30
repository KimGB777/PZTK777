# components/copy_button.py
import streamlit as st
import streamlit.components.v1 as components

def render_copy_button(text: str, button_text: str = "📋 전체 복사") -> None:
    """
    텍스트를 클립보드에 복사하는 버튼을 렌더링합니다.
    
    Args:
        text: 복사할 텍스트
        button_text: 버튼에 표시할 텍스트
    """
    # HTML과 JavaScript로 복사 기능 구현
    button_id = f"copy_btn_{hash(text) % 10000}"
    
    html_code = f"""
    <div style="margin: 10px 0;">
        <button 
            id="{button_id}"
            onclick="copyToClipboard_{button_id}()"
            style="
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.3s;
            "
            onmouseover="this.style.backgroundColor='#FF5252'"
            onmouseout="this.style.backgroundColor='#FF6B6B'"
        >
            {button_text}
        </button>
        <span id="status_{button_id}" style="margin-left: 10px; color: green; font-size: 12px;"></span>
    </div>
    
    <script>
    function copyToClipboard_{button_id}() {{
        const text = `{text.replace('`', '\\`').replace('$', '\\$')}`;
        
        // 최신 브라우저용 Clipboard API
        if (navigator.clipboard) {{
            navigator.clipboard.writeText(text).then(function() {{
                document.getElementById('status_{button_id}').innerText = '✅ 복사완료!';
                setTimeout(function() {{
                    document.getElementById('status_{button_id}').innerText = '';
                }}, 2000);
            }}, function(err) {{
                fallbackCopyTextToClipboard(text);
            }});
        }} else {{
            fallbackCopyTextToClipboard(text);
        }}
        
        function fallbackCopyTextToClipboard(text) {{
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {{
                const successful = document.execCommand('copy');
                if (successful) {{
                    document.getElementById('status_{button_id}').innerText = '✅ 복사완료!';
                }} else {{
                    document.getElementById('status_{button_id}').innerText = '❌ 복사실패';
                }}
            }} catch (err) {{
                document.getElementById('status_{button_id}').innerText = '❌ 복사실패';
            }}
            
            document.body.removeChild(textArea);
            
            setTimeout(function() {{
                document.getElementById('status_{button_id}').innerText = '';
            }}, 2000);
        }}
    }}
    </script>
    """
    
    # Streamlit components를 사용하여 HTML 렌더링
    components.html(html_code, height=60)