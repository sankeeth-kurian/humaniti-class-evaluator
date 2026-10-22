import streamlit as st
from google import genai
import tempfile
import os
import requests
import re

# Page layout configuration
st.set_page_config(page_title="8x8 Class Quality Evaluator", layout="wide")

st.title("🎓 Humaniti AI - 8x8 Class Quality Evaluator")
st.markdown("Assess online class recording quality based on official 8x8 teaching evaluation criteria.")

# Sidebar for API Key
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")

if api_key:
    # Initialize the modern Google GenAI client
    client = genai.Client(api_key=api_key)

    st.subheader("Provide Class Recording Input")
    
    # Allows selection between File Upload and Recording Link
    input_method = st.radio(
        "Choose Input Method:", 
        ["Upload File (.vtt, .txt, .mp4, .mp3)", "Paste Recording Link (Drive / Video URL)"]
    )

    content_to_analyze = None
    media_file_path = None
    input_type = ""

    if input_method == "Upload File (.vtt, .txt, .mp4, .mp3)":
        uploaded_file = st.file_uploader(
            "Upload Recording or Transcript", 
            type=["vtt", "txt", "mp4", "mp3"]
        )
        if uploaded_file is not None:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension in ['.vtt', '.txt']:
                content_to_analyze = uploaded_file.read().decode("utf-8", errors="ignore")
                input_type = "text"
                with st.expander("View Transcript Preview"):
                    st.text(content_to_analyze[:1500] + ("..." if len(content_to_analyze) > 1500 else ""))
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    media_file_path = tmp_file.name
                input_type = "media"
                st.success(f"Uploaded media file: {uploaded_file.name}")
                
    else:
        recording_link = st.text_input("Paste Class Recording URL (Google Drive or direct video URL):")
        if recording_link:
            input_type = "link_input"

    # Process evaluation button
    if (content_to_analyze or media_file_path or (input_method == "Paste Recording Link (Drive / Video URL)" and locals().get('recording_link'))) and st.button("Evaluate Class Quality"):
        with st.spinner("Processing recording and analyzing class metrics..."):
            
            rubric_prompt = """
            You are an expert AI evaluator for 8x8 online classes for children.
            Evaluate the provided class recording input against these official evaluation criteria:

            1. Rapport & Introduction: Greeting, welcoming new joiners, energetic and pleasant communication.
            2. Student Interaction: One-to-one interaction, calling students individually by name, active engagement.
            3. Class Structure & Activities: Assigning Homework (HWs), playing topic-related videos, puzzle solving.
            4. Technical & Visual Setup: Virtual background present (8x8 background), camera/face visibility, lighting.

            CLASSIFICATION CATEGORIES:
            - Excellent
            - Good
            - Average
            - Poor (Weak / Quality Issue)

            PROVIDE YOUR ASSESSMENT IN THIS EXACT FORMAT:
            ### Final Quality Rating: [Excellent / Good / Average / Poor]

            ### Detailed Observations:
            - **Rapport & Intro:** 
            - **Student Interaction:** 
            - **Class Structure & Homework:** 
            - **Technical & Visual Setup:** 

            ### Actionable Feedback for Tutor:
            """

            try:
                response = None

                # Handle Google Drive or Direct Public URL Downloading
                if input_method == "Paste Recording Link (Drive / Video URL)" and locals().get('recording_link'):
                    if "drive.google.com" in recording_link:
                        st.info("Downloading video from Google Drive link...")
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                            output_path = tmp_file.name
                        
                        file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', recording_link)
                        if not file_id_match:
                            file_id_match = re.search(r'id=([a-zA-Z0-9_-]+)', recording_link)
                        
                        if file_id_match:
                            file_id = file_id_match.group(1)
                            URL = "https://docs.google.com/uc?export=download"
                            session = requests.Session()
                            response_req = session.get(URL, params={'id': file_id}, stream=True)
                            
                            token = None
                            for key, value in response_req.cookies.items():
                                if key.startswith('download_warning'):
                                    token = value
                                    break
                            if token:
                                response_req = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)
                            
                            with open(output_path, "wb") as f:
                                for chunk in response_req.iter_content(32768):
                                    if chunk:
                                        f.write(chunk)
                            
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                                media_file_path = output_path
                                input_type = "media"
                            else:
                                st.error("Download failed. Make sure the file sharing setting is set to 'Anyone with the link can view'.")
                        else:
                            st.error("Could not parse Google Drive File ID.")
                    else:
                        st.info("Downloading media from public direct URL...")
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                            output_path = tmp_file.name
                        
                        r = requests.get(recording_link, stream=True)
                        with open(output_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=32768):
                                if chunk:
                                    f.write(chunk)
                        media_file_path = output_path
                        input_type = "media"

                # Execute Gemini API processing
                if input_type == "text":
                    full_prompt = f"{rubric_prompt}\n\nINPUT CONTENT:\n{content_to_analyze[:20000]}"
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=full_prompt
                    )
                elif input_type == "media" and media_file_path:
                    st.info("Uploading media file to Gemini multimodal analyzer...")
                    video_file = client.files.upload(file=media_file_path)
                    response = client.models.generate_content(
                        model='gemini-3.8-flash',
                        contents=[video_file, rubric_prompt]
                    )
                    if os.path.exists(media_file_path):
                        os.remove(media_file_path)

                if response and response.text:
                    st.success("Evaluation Completed Successfully!")
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"API Processing Error: {e}")

else:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to proceed.")