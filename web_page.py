import streamlit as st
from PIL import Image
from datetime import datetime
import pandas as pd
pd.options.mode.chained_assignment = None

#import requests as rq
import numpy as np
import re
import contractions
import wordninja
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pickle




# Page configuration
# st.set_page_config(
#     page_title="Wall of Content",
#     page_icon="✨",
# )

# Initialize session state
if 'content' not in st.session_state:
    st.session_state.content = []
def string( data):
        string = ' '
        return (string.join(data))
# Text processing function
def detectBullying(texts):
        text=[texts]
        tweet = pd.DataFrame(text, columns=['tweets_text'])
        tweet = tweet.replace(to_replace= '\\r', value= '', regex=True)
        
        tweet['tweets_text'] = tweet['tweets_text'].str.lower()
        
        temp = ''
        for index, row in enumerate(tweet['tweets_text']):
            temp = re.sub(r'(\brt)|(http\S+)|(\d+)|(&(gt;)+)|(&(lt;)+)|(&(amp;)+)|([^\w\s])', '', str(row))
            temp = re.sub('(\'| )|(\"| )|(_)', ' ', temp)
            tweet['tweets_text'][index] = temp
        
        for index, row in enumerate(tweet['tweets_text']):
            temp = []
            for word in row.split():
                temp.append(contractions.fix(word))
            tweet['tweets_text'][index] = string(temp)         
            
        slangWords = pd.read_csv("Slang.csv")
        slangWords = slangWords.replace(to_replace='\\r', value='', regex=True)   
        
        for num, row in enumerate(tweet['tweets_text']):
            temp = []
            for word in row.split():
                found = 0
                if (len(word)<6 and len(word)>2): 
                    for index, slang in enumerate(slangWords['slang']):
                        if (slang == word):
                            temp.append(slangWords['word'][index])
                            found = 1
                if (found != 1):
                    temp.append(word)
            tweet['tweets_text'][num] = string(temp)
            
        for index, row in enumerate(tweet['tweets_text']):
            temp = []
            for word in row.split():
                if (len(word)>8):
                    unmunched = wordninja.split(word)
                    temp.append(string(unmunched))
                else:
                    temp.append(word)
            tweet['tweets_text'][index] =string(temp)
            
        tokens = []
        for row in tweet['tweets_text']:
            tokens.append(word_tokenize(row))
        
        tweet['tokens'] = tokens   
        
        offenseWords = pd.read_csv("OffensiveWithSeverity.csv")
        offenseWords = offenseWords.replace(to_replace= '\\r', value= '', regex=True)
        
        negationWords = pd.read_csv("Negation.txt")
        negationWords = negationWords.replace(to_replace= '\\r', value= '', regex=True)

        totalWords, offensiveWords, severityWords = [], [], []

        for row in tweet['tokens']:
            words, temp1, temp2 = 0, [], []
            for index1, token in enumerate(row):
                words += 1
                for index2, offensive in enumerate(offenseWords['words']):
                    if (token == offensive):
                        negation = 0
                        for negation in negationWords['words']: #Checking for negation words at most 2 words before the negative word 
                            if (index1<1):
                                break
                            if (row[index1-1] == negation or row[index1-2] == negation):
                                negation = 1
                                break
                        if (negation != 1):
                            temp1.append(token)
                            temp2.append(offenseWords['severity'][index2])
            totalWords.append(words)
            offensiveWords.append(temp1)
            severityWords.append(temp2)

        tweet['total words'] = totalWords
        tweet['offensive words'] = offensiveWords
        tweet['severity words'] = severityWords
        
        density = []
        for total, offensive in zip(tweet['total words'], tweet['offensive words']):
            density.append(len(offensive) / total)
        tweet['density'] = density
        
        compound = []
        for row in tweet['tweets_text']:
            polarity = SentimentIntensityAnalyzer().polarity_scores(row)
            compound.append(polarity["compound"])
        tweet['sentiment analysis'] = compound
        
        severity, weights = [], [1, 2, 3, 4, 5]
        for severe in tweet['severity words']:
            count, product = [0] * 5, []
            for num in severe:
                if (num == '1'):
                    count[0] += 1
                elif (num == '2'):
                    count[1] += 1 
                elif (num == '3'):
                    count[2] += 1
                elif (num == '4'):
                    count[3] += 1 
                elif (num == '5'):
                    count[4] += 1       
            for num1, num2 in zip(count, weights):
                product.append(num1 * num2)

            totalProduct = sum(product)
            totalCount = sum(count)

            if (totalCount == 0):
                severity.append(0)
            else:
                severity.append(totalProduct / totalCount)

        tweet['severity'] = severity
        
        tweetDataM1 = tweet[['density', 'severity', 'sentiment analysis']].copy()
        tweetDataM1.head()
        
        model = pickle.load(open("cyberbullyingdetection.sav", 'rb'))
        
        cyberTarget = model.predict(tweetDataM1)
        if string(cyberTarget) == 'cyberbullying':
            tweet['cyberbullying'] = 'True'
        else:
            tweet['cyberbullying'] = 'False'
        if (tweet['cyberbullying'].values == 'True'):   
            ethnicityAndRaceGlossary=pd.read_csv("EthnicityAndRaceGlossary.txt")
            ethnicityAndRaceGlossary = ethnicityAndRaceGlossary.replace(to_replace= '\\r', value='', regex=True)

            ageDataGlossary=pd.read_csv("AgeGlossary.txt")
            ageDataGlossary = ageDataGlossary.replace(to_replace= '\\r', value='', regex=True)

            religiousDataGlossary=pd.read_csv("ReligionGlossary.txt")
            religiousDataGlossary = religiousDataGlossary.replace(to_replace= '\\r', value='', regex=True)

            genderDataGlossary=pd.read_csv("GenderGlossary.txt")
            genderDataGlossary = genderDataGlossary.replace(to_replace= '\\r', value='', regex=True)

            isEthnicityAndRace = []
            for row in tweet['tokens']:
                temp = 0
                for token in row:
                    for glossary in ethnicityAndRaceGlossary['words']:
                        if (token == glossary):
                            temp += 1
                            break
                isEthnicityAndRace.append(temp)

            tweet['ethnicity and race'] = isEthnicityAndRace

            isAge = []
            for row in tweet['tokens']:
                temp = 0
                for token in row:
                    for glossary in ageDataGlossary['words']:
                        if (token == glossary):
                            temp += 1
                            break
                isAge.append(temp)

            tweet['age'] = isAge

            isGender = []
            for row in tweet['tokens']:
                temp = 0
                for token in row:
                    for glossary in genderDataGlossary['words']:
                        if (token == glossary):
                            temp += 1
                            break
                isGender.append(temp)

            tweet['gender'] = isGender  

            isReligious = []
            for row in tweet['tokens']:
                temp = 0
                for token in row:
                    for glossary in religiousDataGlossary['words']:
                        if (token == glossary):
                            temp += 1
                            break
                isReligious.append(temp)

            tweet['religion'] = isReligious

            tweetDataM2 = tweet[['age', 'gender', 'religion', 'ethnicity and race']].copy()

            model = pickle.load(open("cyberbullyingtype.sav", 'rb'))

            classifyTarget = model.predict(tweetDataM2)

            return classifyTarget
    
        else:
            return 1


# Main app
def main():
    st.title("Wall of Content")
    # Display wall content
    display_wall()

# Upload content to the wall
def upload_content(content_type, content, username):
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.content.append((content_type, content, username, timestamp))
    st.balloons()

# Display wall content
def display_wall():
    st.header("Wall Content")

    # Iterate through the wall content list and display items
    for content_type, content, username, timestamp in st.session_state.content:
        # Create columns for username, content, and timestamp
        col1, col2, col3 = st.columns([1, 10, 1])

        # Display username in the center column
        with col2:
            st.markdown(f"**{username}**", unsafe_allow_html=True)

        if content_type == "Text":
            # Display text content in the center column with much larger font
            with col2:
                display_text(content)

        elif content_type == "Image":
            # Display image content in the center column
            with col2:
                display_image(content)

        # Display timestamp in the right column
        with col3:
            st.write(f"*{timestamp}*", justify="right")

# Display text content with much larger font
def display_text(content):
    st.markdown(f"<p style='font-size:24px'>{content}</p>", unsafe_allow_html=True)

# Display image content
def display_image(content):
    st.image(content, caption="Uploaded Image", use_column_width=True)

# Upload Page
def upload_page():
    st.title("Upload Content")
    
    # Get user input for username
    username = st.text_input("Enter your username:")

    # Input for text content
    text_input = st.text_area("Enter your text here:")

    # Input for image content
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    # Upload button
    if st.button("Upload"):
        # Process the text content
        if text_input:
            result = detectBullying(text_input)
            if result == 1:
                upload_content("Text", text_input, username)
            else:
                st.error("Error: This content is inappropriate and cannot be uploaded."+result)
        # Upload image content
        if uploaded_file:
            upload_content("Image", uploaded_file, username)

if __name__ == "__main__":
    # Create a sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ("Wall", "Upload"))
    
    # Display the selected page
    if page == "Wall":
        main()
    elif page == "Upload":
        upload_page()
