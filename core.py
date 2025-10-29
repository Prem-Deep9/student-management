"""common dependencies among all pages"""
import logging
import os

import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


# -----------------------------------------------------------
# Setup & Initialization
# -----------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    """Initialize and cache Supabase client."""
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    return create_client(supabase_url, supabase_key)

supabase_client = init_supabase()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
