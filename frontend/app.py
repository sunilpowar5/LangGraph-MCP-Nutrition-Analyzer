import streamlit as st
from PIL import Image
import asyncio
import nest_asyncio 
import uuid
from client import calorie_graph


nest_asyncio.apply()

# Streamlit Page Setup 
st.set_page_config(page_title="Food Calories & Proteins Analyzer")
st.title("Food Calories and Proteins Analyzer")

# Session State Initialization 
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "mime" not in st.session_state:
    st.session_state.mime = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "nutrition_result" not in st.session_state:
    st.session_state.nutrition_result = None

# Image Upload
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

# Show uploaded imgae
if st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Food Image", width="content")

if uploaded_file is not None:
    uploaded_file.seek(0)
    new_image_bytes = uploaded_file.read()

    # Process only if a new image has been uploaded
    if st.session_state.image_bytes != new_image_bytes:
        st.session_state.uploaded_image = Image.open(uploaded_file)
        st.session_state.image_bytes = new_image_bytes
        st.session_state.mime = uploaded_file.type
        st.session_state.analysis_done = False
        st.session_state.chat_history = []

        # Run the asynchronous graph for image analysis
        with st.spinner("Analyzing..."):

            result_state = asyncio.run(
                calorie_graph.ainvoke(
                    {"image_bytes": st.session_state.image_bytes, "mime": st.session_state.mime},
                    config={"configurable": {"thread_id": st.session_state.thread_id}}
                )
            )

        # Store and display the initial result
        initial_result = result_state.get('result', "Analysis failed.")
        st.session_state.analysis_done = True
        st.session_state.nutrition_result = initial_result
        st.session_state.chat_history.append(("system", "Nutrition Analysis"))
        st.session_state.chat_history.append(("assistant", initial_result))

        # Rerun to update the display immediately
        st.rerun()

# Chat History Display 
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.chat_message("user").markdown(msg)
    elif role == "assistant":
        st.chat_message("assistant").markdown(msg)
    elif role == "system":
        st.markdown(f"### {msg}")

# Follow-up Question Logic 
if st.session_state.analysis_done:
    if user_question := st.chat_input("Ask a follow-up question"):

        st.session_state.chat_history.append(("user", user_question))
        st.chat_message("user").markdown(user_question)

        # Run the asynchronous graph for the follow-up question
        with st.spinner("Thinking..."):
            result_state = asyncio.run(
                calorie_graph.ainvoke(
                    {"user_query": user_question, "result": st.session_state.nutrition_result},
                    config={"configurable": {"thread_id": st.session_state.thread_id}}
                )
            )

        # Add the AI's response to chat history and display it
        followup_text = result_state.get("user_result", "I couldn't generate a response.")
        st.session_state.chat_history.append(("assistant", followup_text))
        st.rerun() # Rerun to show the new assistant message

# Reset Session Button
if st.button("Start New Session"):
    # Clear all session state variables
    st.session_state.clear()
    st.success("New session started. Please upload an image.")
    st.rerun()