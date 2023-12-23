import streamlit as st
# import pyrebase
from web_page import detectBullying
import firebase_admin
from firebase_admin import credentials, firestore, storage

from PIL import Image

import subprocess
import os

from tempfile import NamedTemporaryFile

conda_environment = 'modelenv'
activate_command = activate_command = f'conda activate {conda_environment}'

def app():

    # initialize_app(cred, {'storageBucket': 'cyberethics-watch.appspot.com'})
    cred = credentials.Certificate('serviceAccountKey.json')
    if not os.path.exists("images"):
        os.makedirs("images")
    if not firebase_admin._apps:
        # Initialize the app with a service account
        firebase_admin.initialize_app(cred)
    if 'db' not in st.session_state:
        st.session_state.db = ''

    # storage = storage()
    st.title("Image Upload to Firebase")

    db=firestore.client()
    st.session_state.db=db
    uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
    # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        bucket = storage.bucket(name= "cyberethics-watch.appspot.com")
        im_bytes = uploaded_file.read()
        filename, ext = os.path.splitext(uploaded_file.name)
        with NamedTemporaryFile(suffix= ext, dir="images", prefix=filename, delete=False) as temp_file:
            temp_file.write(im_bytes)  # Copy the content of the uploaded file to the temporary file
            name = os.path.basename(temp_file.name)
            try:
                run_script_command = f'conda activate modelenv && python getPredictions.py images/{name}'
                result = subprocess.run(run_script_command, shell=True, capture_output=True, text=True)
                # Access the output
                stdout_output = result.stdout
                stderr_output = result.stderr
                print("------------------------------------------------------------------")
                print("stdout: ", stdout_output)
                print("stderr: ", stderr_output)
                print("------------------------------------------------------------------")
            except Exception as e:
                st.error(e)

            can_upload = True if "0" in stdout_output.split(": ")[-1].replace('\\n', '') else False
            if can_upload:
                blob = bucket.blob(uploaded_file.name)
                blob.upload_from_string(im_bytes, content_type="image/jpg")
                blob.make_public()
                download_url = blob.public_url
                st.success(f"Image uploaded to Firebase Storage! {download_url}")

                if download_url is not None:
                    info = db.collection('Posts').document(st.session_state.username).get()
                    if info.exists:
                        info = info.to_dict()
                        if 'Content' in info.keys():
                            pos=db.collection('Posts').document(st.session_state.username)
                            pos.update({u'Content': firestore.ArrayUnion([u'{}'.format(download_url)])})
                        else:
                            data={"Content":[download_url],'Username':st.session_state.username}
                            db.collection('Posts').document(st.session_state.username).set(data)    
                    else:
                        data={"Content":[download_url],'Username':st.session_state.username}
                        db.collection('Posts').document(st.session_state.username).set(data)
            else:
                st.error("This image cannot be posted because it has some offensive content!")

    ph = ''
    if st.session_state.username=='':
        ph = 'Login to be able to post!!'
    else:
        ph='Post your thought'    
    post=st.text_area(label=' :orange[+ New Post]',placeholder=ph,height=None, max_chars=500)
    if st.button('Post',use_container_width=20):
        if post!='':
                    
            info = db.collection('Posts').document(st.session_state.username).get()
            if info.exists:
                info = info.to_dict()
                if 'Content' in info.keys():
                
                    pos=db.collection('Posts').document(st.session_state.username)
                    pos.update({u'Content': firestore.ArrayUnion([u'{}'.format(post)])})
                else:
                    
                    data={"Content":[post],'Username':st.session_state.username}
                    db.collection('Posts').document(st.session_state.username).set(data)    
            else:
                    
                data={"Content":[post],'Username':st.session_state.username}
                db.collection('Posts').document(st.session_state.username).set(data)
                
            st.success('Post uploaded!!')
    
    st.header(' :violet[Latest Posts] ')
    
    
    
    
    docs = db.collection('Posts').get()

    for doc in docs:
        d=doc.to_dict()
        try:
            content = d["Content"][-1]
            if(content.startswith("https://storage")):
                st.write(f"posted by {d['Username']}: ")
                st.image(content)
            else:
                res = detectBullying(content)
                if res == 1:
                    st.text_area(label=':green[Posted by:] '+':orange[{}]'.format(d['Username']),value=d['Content'][-1],height=20)
                else:
                    st.text_area(label=':green[Posted by:] '+':red[{}]'.format(d['Username']),value=f"This post cannot be displayed because it contains words related to {res[0]}",height=20)
        except Exception as e:
            st.error(e)
