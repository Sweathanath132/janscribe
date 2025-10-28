import streamlit as st
import assemblyai as aai
import os
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="JanScribe - Diarization Demo",
    page_icon="🎙️",
    layout="wide"
)

# --- Load API Key ---
try:
    # Ensure this key name matches your secrets.toml
    aai.settings.api_key = st.secrets["ASSEMBLYAI_API_KEY"]
except FileNotFoundError:
    st.error("Secrets file not found. Please create .streamlit/secrets.toml and add your ASSEMBLYAI_API_KEY.")
    st.stop()
except KeyError:
    st.error("ASSEMBLYAI_API_KEY not found in secrets file. Please check your .streamlit/secrets.toml.")
    st.stop()

# --- AssemblyAI Transcriber ---
transcriber = aai.Transcriber()

# --- The App UI ---
st.title("JanScribe 🎙️ (Kannada Transcription + Speaker Labels)")
st.write("Reliable cloud transcription with Speaker Diarization via AssemblyAI.")
st.write("NEXATHON Hackathon - Final Working Demo")

st.divider()

# Use 2 columns again: Upload | Transcript
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Kannada Audio")

    audio_file = st.file_uploader(
        "Upload Kannada audio (mp3, wav, m4a, ogg, flac):",
        type=["mp3", "wav", "m4a", "ogg", "flac"]
    )

    if audio_file is not None:
        st.audio(audio_file, format='audio/wav')

        if st.button("Transcribe with Speaker Labels"):
            # Clear previous results
            st.session_state.clear()

            with st.spinner("Uploading to AssemblyAI and transcribing with diarization..."):

                # --- 1. Save Temp File ---
                temp_audio_path = os.path.join("temp_audio_upload")
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())

                # --- 2. Configure Transcription (ONLY Diarization) ---
                # *** REMOVED summarization, entity_detection, auto_chapters ***
                config = aai.TranscriptionConfig(
                    language_code="kn", # Explicitly set Kannada
                    speaker_labels=True # Keep diarization
                )

                # --- 3. Upload and Transcribe ---
                st.write("Sending to AssemblyAI cloud...")
                transcript = None # Reset
                try:
                    transcript = transcriber.transcribe(temp_audio_path, config)

                    if transcript.status == aai.TranscriptStatus.error:
                        st.error(f"Transcription failed: {transcript.error}")
                    elif transcript.utterances is not None and transcript.utterances: # Check utterances list is not empty
                        st.session_state.raw_transcript = transcript.text # Store plain text too
                        # Format the diarized transcript
                        diarized_text = ""
                        for utterance in transcript.utterances:
                             # Use speaker labels if available, otherwise just show text
                            speaker_label = f"Speaker {utterance.speaker}:" if utterance.speaker else ""
                            diarized_text += f"{speaker_label} {utterance.text}\n\n"
                        st.session_state.diarized_transcript = diarized_text.strip() # Remove trailing newline
                        st.success("✅ Transcription with speaker labels complete!")
                    elif transcript.text is not None: # Fallback if diarization fails but text exists
                         st.warning("Diarization might have failed or only one speaker detected. Showing plain transcript.")
                         st.session_state.raw_transcript = transcript.text
                         st.session_state.diarized_transcript = transcript.text # Show plain text in this case
                         st.success("✅ Transcription complete (plain text).")
                    else:
                         st.error("Transcription returned no result.")

                except Exception as e:
                    st.error(f"An API error occurred: {e}")
                    st.error(f"Error details: {getattr(e, 'response', 'No response details')}")

                # Clean up temp file
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                time.sleep(1)


# Display transcript in the second column
with col2:
    st.subheader("2. Kannada Transcript (w/ Speakers)")

    if "diarized_transcript" in st.session_state:
        st.text_area("Diarized Transcript:", st.session_state.diarized_transcript, height=400)

        # Optionally show raw text too
        with st.expander("Show Raw Transcript (No Speaker Labels)"):
             if "raw_transcript" in st.session_state:
                st.write(st.session_state.raw_transcript)
             else:
                 st.write("Raw transcript not available.")
    else:
        st.markdown("*Your Kannada transcript with speaker labels will appear here.*")