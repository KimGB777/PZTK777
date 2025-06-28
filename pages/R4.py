import streamlit as st
import os

def render():
    st.title("🔒 R4참고")
    pw = st.text_input("비밀번호 입력", type="password")
    if st.button("접속"):
        correct = os.environ.get("r4pw") or st.secrets.get("r4pw", "")
        if pw == correct:
            st.success("접근 승인")
            st.write("🔍 R4 전용 참고 내용이 여기에 표시됩니다.")
        else:
            st.error("비밀번호가 틀렸습니다")
