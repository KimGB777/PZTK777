# components/copy_button.py

import streamlit as st

def render_copy_button(text: str):
    """Copy to clipboard button"""
    st.button("Copy All", on_click=lambda: st.experimental_set_query_params(_clipboard=text))
