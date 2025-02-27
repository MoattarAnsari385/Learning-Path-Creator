import streamlit as st
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# Function to send email
def send_email(review, user_email=None, subject="New Review Submitted on Learning Path Creator"):
    # Validate email
    if user_email and not is_valid_email(user_email):
        st.error("Please enter a valid email address.")
        return False

    # Fetch email credentials from secrets.toml
    try:
        sender_email = st.secrets["email"]["email"]
        sender_password = st.secrets["email"]["password"]
        receiver_email = st.secrets["email"]["email"]

    # Create the email
        body = f"""
        A new review has been submitted:
        
        Review: {review}
        
        User Email: {user_email if user_email else "Not provided"}
        """

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Send the email
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Use Gmail's SMTP server
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            return True
        except Exception as e:
            st.error(f"Failed to send email: {e}")
            return False

    except KeyError as e:
        st.error(f"Missing configuration: {e}. Please check your secrets.toml file.")
        st.stop()


# Function to validate email
def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

# Initialize session states
def initialize_session_states():
    if 'steps' not in st.session_state:
        st.session_state.steps = []
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    if 'reviews' not in st.session_state:
        st.session_state.reviews = {}
    if 'show_tutorial' not in st.session_state:
        st.session_state.show_tutorial = True
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

# Page Configuration
def configure_page():
    st.set_page_config(
        page_title="Learning Path Creator",
        page_icon="📚",
        layout="wide"
    )

# Custom CSS for Styling
def apply_custom_css():
    st.markdown("""
    <style>
    .stTextArea textarea {
        color: #000000 !important; 
        background-color: #ffffff !important; 
    }
    .stTextArea label {
        color: #000000 !important; 
    }
    .stButton button {
        color:rgb(136, 135, 135) !important; 
    }
    .big-font {
        font-size:24px !important;
        margin-bottom: 20px !important;
    }
    .medium-font {
        font-size:18px !important;
        margin-bottom: 15px !important;
    }
    .section-spacing {
        margin-top: 40px !important;
        margin-bottom: 30px !important;
    }
    .progress-bar {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 3px;
    }
    .resource-card {
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .review-section {
        margin-top: 10px;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 8px;
        color: #000000;
        font-family: Arial;
        font-weight: 500 
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f8f9fa;
        padding: 10px;
        text-align: center;
        font-size: 14px;
        color: #000000;
        border-top: 1px solid #e9ecef;
        z-index: 1000; 
    }
    .stApp {
        padding-bottom: 60px; 
    }
    </style>
    """, unsafe_allow_html=True)


# Onboarding Tutorial
def show_onboarding_tutorial():
    if st.session_state.show_tutorial:
        st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
        st.markdown("<div class='big-font'>🎉 Welcome to Learning Path Creator! 🎉</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='medium-font'>
        Here's how to get started:<br>
        1. 📌 Enter your interests in the sidebar<br>
        2. 🎯 Select your main field and sub-field<br>
        3. 🚀 Set your learning goal<br>
        4. 📊 Track your progress<br>
        5. 📥 Download your progress report<br>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Got it! Let's get started ✨"):
            st.session_state.show_tutorial = False
            st.rerun()

# Main App
def main_app():
    if not st.session_state.show_tutorial:
        # App title and welcome message
        st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
        st.markdown("<div class='big-font'>📚 Personalized Learning Path Creator 🎯</div>", unsafe_allow_html=True)
        
        # Sidebar Section
        with st.sidebar:
            st.title("⚙️ User Inputs")
            
            # Interests
            st.header("🎨 Your Interests")
            interests = st.multiselect(
                'Select your interests:',
                ['Programming', 'Reading', 'Gaming', 'Traveling', 'Cooking', 'Sports']
            )

            # Main Field
            st.header("🎯 Main Field")
            main_field = st.selectbox(
                'Select your main field:',
                ['', 'Programming', 'Reading', 'Gaming', 'Traveling', 'Cooking', 'Sports']
            )

            # Sub-fields
            sub_fields = {
                "Programming": ['Python', 'JavaScript', 'Java', 'C++', 'Ruby', "AI/ML"],
                "Reading": ['Fiction', 'Non-fiction', 'Science Fiction', 'Fantasy', 'Biography'],
                "Gaming": ['Action', 'Adventure', 'Strategy', 'RPG', 'Sports'],
                "Traveling": ['Adventure', 'Cultural', 'Beach', 'Mountain', 'City'],
                "Cooking": ['Baking', 'Grilling', 'Vegetarian', 'Seafood', 'Desserts'],
                "Sports": ['Football', 'Basketball', 'Cricket', 'Tennis', 'Swimming']
            }

            if main_field:
                st.header(f"🔍 {main_field} Sub-Field")
                sub_field = st.selectbox(
                    f'Select sub-field:',
                    sub_fields[main_field]
                )

            # Goals
            st.header("🚀 Your Goals")
            goals = st.selectbox(
                'Select your primary goal:',
                ['', 'Learn a new skill', 'Improve fitness', 'Read more books', 'Travel more', 'Cook new recipes']
            )

            # Save/Reset buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Inputs"):
                    if main_field and sub_field and goals:
                        st.session_state.user_data = {
                            "interests": interests,
                            "main_field": main_field,
                            "sub_field": sub_field,
                            "goal": goals
                        }
                        st.success("Inputs saved!")
            with col2:
                if st.button("🔄 Reset All"):
                    st.session_state.steps = []
                    st.session_state.favorites = []
                    st.session_state.reviews = {}
                    st.session_state.user_data = {}
                    st.rerun()

            # Feedback Section
            with st.expander("💬 Feedback & Rating"):
                st.write("We'd love to hear your feedback!")
                rating = st.slider("Rate the app (1 to 5 stars):", 1, 5, 5)
                feedback = st.text_area("Your feedback:")
                if st.button("Submit Feedback"):
                    if feedback:
                        send_email(f"App Rating: {rating}/5\nFeedback: {feedback}")
                        st.success("Thank you for your feedback! We appreciate it.")
                    else:
                        st.warning("Please provide feedback before submitting.")

        # Learning Path Section
        if st.session_state.user_data.get("goal"):
            st.markdown(f"<div class='big-font'>📚 Your {st.session_state.user_data['goal']} Learning Path</div>", unsafe_allow_html=True)
            
            # Initialize steps
            if not st.session_state.steps:
                predefined_steps = {
                    "Learn a new skill": [
                        "Identify the skill you want to learn",
                        "Gather resources (books, courses, articles)",
                        "Set daily/weekly practice schedule",
                        "Join a community or find a mentor",
                        "Track progress and adjust learning plan"
                    ],
                    "Improve fitness": [
                        "Set specific fitness goals",
                        "Create a workout plan",
                        "Find a workout buddy",
                        "Track your progress",
                        "Adjust your plan as needed"
                    ],
                    "Read more books": [
                        "Create a reading list",
                        "Set reading goals",
                        "Find a reading spot",
                        "Join a book club",
                        "Track your progress"
                    ],
                    "Travel more": [
                        "Create a travel bucket list",
                        "Set a travel budget",
                        "Research destinations",
                        "Plan your trips",
                        "Track your experiences"
                    ],
                    "Cook new recipes": [
                        "Identify recipes to try",
                        "Gather ingredients",
                        "Set a cooking schedule",
                        "Join a cooking class",
                        "Track your experiments"
                    ]
                }.get(st.session_state.user_data["goal"], [])
                st.session_state.steps = predefined_steps.copy()

            # Step Customization
            with st.expander("✏️ Customize Your Learning Path"):
                new_step = st.text_input("Add new step:")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➕ Add Step") and new_step:
                        st.session_state.steps.append(new_step)
                        st.rerun()
                with col2:
                    if st.button("➖ Remove Last Step") and st.session_state.steps:
                        st.session_state.steps.pop()
                        st.rerun()

                # Editable Steps
                edited_steps = []
                for i, step in enumerate(st.session_state.steps, 1):
                    edited_step = st.text_input(f"Step {i}:", value=step)
                    edited_steps.append(edited_step)
                st.session_state.steps = edited_steps

            # Display Steps
            for idx, step in enumerate(st.session_state.steps, 1):
                st.markdown(f"📌 **Step {idx}:** {step}")

            # Save Learning Path
            if st.button("💾 Save Learning Path"):
                st.session_state.user_data["learning_path"] = st.session_state.steps
                with open("user_data.json", "w") as f:
                    json.dump(st.session_state.user_data, f)
                st.success("Learning path saved!")

        # Resource Recommendations Section
        if st.session_state.user_data.get("main_field") and st.session_state.user_data.get("sub_field"):
            st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
            st.markdown("<div class='big-font'>📚 Recommended Resources</div>", unsafe_allow_html=True)
            
            # Search Bar
            search_query = st.text_input("🔍 Search resources:")
            
            # Resources Database
            resources = {
                "Programming": {
                    "Python": [
                        {"title": "Learn Python the Hard Way", "type": "Book", "link": "https://learnpythonthehardway.org/"},
                        {"title": "Eric Mathes Python Crash Course PDF", "type": "Book", "link": "https://khwarizmi.org/wp-content/uploads/2021/04/Eric_Matthes_Python_Crash_Course_A_Hands.pdf"},
                        {"title": "Automate the Boring Stuff with Python", "type": "Course", "link": "https://automatetheboringstuff.com/"},
                        {"title": "Corey Schafer's Python Tutorials", "type": "YouTube Channel", "link": "https://www.youtube.com/user/schafer5"},
                        {"title": "Python Crash Course - Panaversity", "type": "YouTube Channel", "link": "https://www.youtube.com/playlist?list=PL0vKVrkG4hWrEujmnC7v2mSiaXMV_Tfu0"},
                        {"title": "Code With Mosh Python Tutorial", "type": "YouTube Channel", "link": "https://www.youtube.com/watch?v=K5KVEU3aaeQ&t=866s"},
                        {"title": "Python for Data Science 2024", "type": "Course", "link": "https://www.coursera.org/specializations/python-data-science"},
                        {"title": "Advanced Python Programming 2025", "type": "Book", "link": "https://www.oreilly.com/library/view/advanced-python-programming/9781492051367/"}
                    ],
                    "JavaScript": [
                        {"title": "Eloquent JavaScript", "type": "Book", "link": "https://eloquentjavascript.net/"},
                        {"title": "JavaScript.info", "type": "Article", "link": "https://javascript.info/"},
                        {"title": "Traversy Media", "type": "YouTube Channel", "link": "https://www.youtube.com/user/TechGuyWeb"},
                        {"title": "Javascript Beginners Course - FreeCodeCamp", "type": "YouTube Channel", "link": "https://www.youtube.com/watch?v=Zi-Q0t4gMC8"},
                        {"title": "Modern JavaScript 2024", "type": "Course", "link": "https://www.udemy.com/course/modern-javascript/"},
                        {"title": "JavaScript Frameworks 2025", "type": "Book", "link": "https://www.manning.com/books/javascript-frameworks"}
                    ],
                    "Java": [
                        {"title": "Effective Java", "type": "Book", "link": "https://www.oreilly.com/library/view/effective-java/9780134686097/"},
                        {"title": "Java Programming and Software Engineering Fundamentals", "type": "Course", "link": "https://www.coursera.org/specializations/java-programming"},
                        {"title": "Java Brains", "type": "YouTube Channel", "link": "https://www.youtube.com/user/koushks"},
                        {"title": "FreeCodeCamps Java Tutorial", "type": "YouTube Channel", "link": "https://www.youtube.com/watch?v=A74TOX803D0"},
                        {"title": "Java for Beginners 2024", "type": "Course", "link": "https://www.udemy.com/course/java-for-beginners/"},
                        {"title": "Advanced Java Programming 2025", "type": "Book", "link": "https://www.oreilly.com/library/view/advanced-java-programming/9781492051367/"}
                    ],
                    "C++": [
                        {"title": "C++ Primer", "type": "Book", "link": "https://www.oreilly.com/library/view/c-primer-5th/9780133053043/"},
                        {"title": "The Cherno", "type": "YouTube Channel", "link": "https://www.youtube.com/user/TheChernoProject"},
                        {"title": "FreeCodeCamp C++ Tutorial", "type": "YouTube Channel", "link": "https://www.youtube.com/watch?v=8jLOx1hD3_o"},
                        {"title": "C++ for Game Development 2024", "type": "Course", "link": "https://www.udemy.com/course/cpp-for-game-development/"},
                        {"title": "Advanced C++ Programming 2025", "type": "Book", "link": "https://www.oreilly.com/library/view/advanced-c-programming/9781492051367/"}
                    ],
                    "Ruby": [
                        {"title": "The Well-Grounded Rubyist", "type": "Book", "link": "https://www.manning.com/books/the-well-grounded-rubyist-third-edition"},
                        {"title": "Ruby on Rails Tutorial", "type": "Course", "link": "https://www.railstutorial.org/"},
                        {"title": "Ruby for Web Development 2024", "type": "Course", "link": "https://www.udemy.com/course/ruby-for-web-development/"},
                        {"title": "Advanced Ruby Programming 2025", "type": "Book", "link": "https://www.oreilly.com/library/view/advanced-ruby-programming/9781492051367/"}
                    ],
                    "AI/ML": [
                        {"title": "Deep Learning Specialization by Andrew Ng", "type": "Course", "link": "https://www.coursera.org/specializations/deep-learning"},
                        {"title": "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow", "type": "Book", "link": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/"},
                        {"title": "3Blue1Brown - Neural Networks", "type": "YouTube Channel", "link": "https://www.youtube.com/c/3blue1brown"},
                        {"title": "Krish Naik - AI/ML Tutorials", "type": "YouTube Channel", "link": "https://www.youtube.com/c/KrishNaik"},
                        {"title": "Fast.ai - Practical Deep Learning for Coders", "type": "Course", "link": "https://www.fast.ai/"},
                        {"title": "StatQuest with Josh Starmer", "type": "YouTube Channel", "link": "https://www.youtube.com/c/joshstarmer"},
                        {"title": "Google Machine Learning Crash Course", "type": "Course", "link": "https://developers.google.com/machine-learning/crash-course"},
                        {"title": "AI/ML Trends 2024", "type": "Article", "link": "https://www.towardsdatascience.com/ai-ml-trends-2024"},
                        {"title": "Advanced AI/ML Techniques 2025", "type": "Book", "link": "https://www.oreilly.com/library/view/advanced-ai-ml-techniques/9781492051367/"}
                    ]
                },
                "Reading": {
                    "Fiction": [
                        {"title": "The Great Gatsby", "type": "Book", "link": "https://www.goodreads.com/book/show/4671.The_Great_Gatsby"},
                        {"title": "1984 by George Orwell", "type": "Book", "link": "https://www.goodreads.com/book/show/5470.1984"},
                        {"title": "BookTubers to Follow", "type": "YouTube Channel", "link": "https://www.youtube.com/results?search_query=booktubers"},
                        {"title": "Best Fiction Books 2024", "type": "Article", "link": "https://www.goodreads.com/list/show/175351.Best_Fiction_Books_2024"}
                    ],
                    "Non-fiction": [
                        {"title": "Sapiens: A Brief History of Humankind", "type": "Book", "link": "https://www.goodreads.com/book/show/23692271-sapiens"},
                        {"title": "TED Talks", "type": "YouTube Channel", "link": "https://www.youtube.com/user/TEDtalksDirector"},
                        {"title": "Best Non-Fiction Books 2024", "type": "Article", "link": "https://www.goodreads.com/list/show/175352.Best_Non_Fiction_Books_2024"}
                    ],
                    "Science Fiction": [
                        {"title": "Dune by Frank Herbert", "type": "Book", "link": "https://www.goodreads.com/book/show/44767458-dune"},
                        {"title": "Sci-Fi Book Recommendations", "type": "YouTube Channel", "link": "https://www.youtube.com/results?search_query=sci-fi+books"},
                        {"title": "Best Sci-Fi Books 2024", "type": "Article", "link": "https://www.goodreads.com/list/show/175353.Best_Sci_Fi_Books_2024"}
                    ],
                    "Fantasy": [
                        {"title": "The Hobbit by J.R.R. Tolkien", "type": "Book", "link": "https://www.goodreads.com/book/show/5907.The_Hobbit_or_There_and_Back_Again"},
                        {"title": "Fantasy Book Reviews", "type": "YouTube Channel", "link": "https://www.youtube.com/results?search_query=fantasy+book+reviews"},
                        {"title": "Best Fantasy Books 2024", "type": "Article", "link": "https://www.goodreads.com/list/show/175354.Best_Fantasy_Books_2024"}
                    ],
                    "Biography": [
                        {"title": "Steve Jobs by Walter Isaacson", "type": "Book", "link": "https://www.goodreads.com/book/show/11084145-steve-jobs"},
                        {"title": "Biographies to Read", "type": "YouTube Channel", "link": "https://www.youtube.com/results?search_query=biographies"},
                        {"title": "Best Biographies 2024", "type": "Article", "link": "https://www.goodreads.com/list/show/175355.Best_Biographies_2024"}
                    ]
                },
                "Gaming": {
                    "Action": [
                        {"title": "Game Development with Unity", "type": "Course", "link": "https://unity.com/learn"},
                        {"title": "Brackeys", "type": "YouTube Channel", "link": "https://www.youtube.com/user/Brackeys"},
                        {"title": "Best Action Games 2024", "type": "Article", "link": "https://www.ign.com/lists/best-action-games-2024"}
                    ],
                    "Adventure": [
                        {"title": "Game Design and Development", "type": "Course", "link": "https://www.coursera.org/specializations/game-design"},
                        {"title": "Extra Credits", "type": "YouTube Channel", "link": "https://www.youtube.com/user/ExtraCreditz"},
                        {"title": "Best Adventure Games 2024", "type": "Article", "link": "https://www.ign.com/lists/best-adventure-games-2024"}
                    ],
                    "Strategy": [
                        {"title": "The Art of Game Design", "type": "Book", "link": "https://www.goodreads.com/book/show/409640.The_Art_of_Game_Design"},
                        {"title": "GDC", "type": "YouTube Channel", "link": "https://www.youtube.com/user/gdconf"},
                        {"title": "Best Strategy Games 2024", "type": "Article", "link": "https://www.ign.com/lists/best-strategy-games-2024"}
                    ],
                    "RPG": [
                        {"title": "RPG Maker Tutorials", "type": "Course", "link": "https://www.rpgmakerweb.com/support/tutorial"},
                        {"title": "RPG Limit Break", "type": "YouTube Channel", "link": "https://www.youtube.com/user/RPGLimitBreak"},
                        {"title": "Best RPG Games 2024", "type": "Article", "link": "https://www.ign.com/lists/best-rpg-games-2024"}
                    ],
                    "Sports": [
                        {"title": "FIFA Coaching and Tips", "type": "YouTube Channel", "link": "https://www.youtube.com/user/EAFIFADevTeam"},
                        {"title": "Best Sports Games 2024", "type": "Article", "link": "https://www.ign.com/lists/best-sports-games-2024"}
                    ]
                },
                "Cooking": {
                    "Baking": [
                        {"title": "The Joy of Baking", "type": "Book", "link": "https://www.goodreads.com/book/show/14494.Joy_of_Baking"},
                        {"title": "Cupcake Jemma", "type": "YouTube Channel", "link": "https://www.youtube.com/user/CupcakeJemma"},
                        {"title": "Best Baking Recipes 2024", "type": "Article", "link": "https://www.allrecipes.com/best-baking-recipes-2024"}
                    ],
                    "Grilling": [
                        {"title": "The Barbecue Bible", "type": "Book", "link": "https://www.goodreads.com/book/show/527234.The_Barbecue_Bible"},
                        {"title": "BBQ Pit Boys", "type": "YouTube Channel", "link": "https://www.youtube.com/user/BarbecueWeb"},
                        {"title": "Best Grilling Recipes 2024", "type": "Article", "link": "https://www.allrecipes.com/best-grilling-recipes-2024"}
                    ],
                    "Vegetarian": [
                        {"title": "Vegetarian Cooking for Everyone", "type": "Book", "link": "https://www.goodreads.com/book/show/61913.Vegetarian_Cooking_for_Everyone"},
                        {"title": "Pick Up Limes", "type": "YouTube Channel", "link": "https://www.youtube.com/channel/UCq2E1mIwUKMWzCA4liA_XGQ"},
                        {"title": "Best Vegetarian Recipes 2024", "type": "Article", "link": "https://www.allrecipes.com/best-vegetarian-recipes-2024"}
                    ],
                    "Seafood": [
                        {"title": "Fish: Recipes from the Sea", "type": "Book", "link": "https://www.goodreads.com/book/show/161303.Fish"},
                        {"title": "Bart’s Fish Tales", "type": "YouTube Channel", "link": "https://www.youtube.com/user/bartsfishtales"},
                        {"title": "Best Seafood Recipes 2024", "type": "Article", "link": "https://www.allrecipes.com/best-seafood-recipes-2024"}
                    ],
                    "Desserts": [
                        {"title": "The Art of French Pastry", "type": "Book", "link": "https://www.goodreads.com/book/show/18167490-the-art-of-french-pastry"},
                        {"title": "Preppy Kitchen", "type": "YouTube Channel", "link": "https://www.youtube.com/channel/UCB4gFkDmRZ2fFTEZ3P8FI3g"},
                        {"title": "Best Dessert Recipes 2024", "type": "Article", "link": "https://www.allrecipes.com/best-dessert-recipes-2024"}
                    ]
                },
                "Sports": {
                    "Football": [
                        {"title": "Coaching Soccer Tactics", "type": "YouTube Channel", "link": "https://www.youtube.com/user/LaureusTV"},
                        {"title": "Inverting The Pyramid: The History of Football Tactics", "type": "Book", "link": "https://www.amazon.com/Inverting-Pyramid-History-Football-Tactics/dp/1409102041"},
                        {"title": "Best Football Drills 2024", "type": "Article", "link": "https://www.soccercoachweekly.net/best-football-drills-2024"}
                    ],
                    "Basketball": [
                        {"title": "Basketball Fundamentals", "type": "YouTube Channel", "link": "https://www.youtube.com/user/LaureusTV"},
                        {"title": "Basketball: Steps to Success", "type": "Book", "link": "https://www.amazon.com/Basketball-Steps-Success/dp/0736067078"},
                        {"title": "Best Basketball Drills 2024", "type": "Article", "link": "https://www.basketballforcoaches.com/best-basketball-drills-2024"}
                    ],
                    "Cricket": [
                        {"title": "Cricket Coaching Tips", "type": "YouTube Channel", "link": "https://www.youtube.com/user/LaureusTV"},
                        {"title": "The Art of Cricket", "type": "Book", "link": "https://www.amazon.com/Art-Cricket-Don-Bradman/dp/1405278242"},
                        {"title": "Best Cricket Drills 2024", "type": "Article", "link": "https://www.cricketcoaching.com/best-cricket-drills-2024"}
                    ],
                    "Tennis": [
                        {"title": "Tennis Instruction and Tips", "type": "YouTube Channel", "link": "https://www.youtube.com/user/LaureusTV"},
                        {"title": "Tennis Science for Tennis Players", "type": "Book", "link": "https://www.amazon.com/Tennis-Science-Players-Howard-Brody/dp/0812213340"},
                        {"title": "Best Tennis Drills 2024", "type": "Article", "link": "https://www.tenniscoaching.com/best-tennis-drills-2024"}
                    ],
                    "Swimming": [
                        {"title": "Swimming Techniques", "type": "YouTube Channel", "link": "https://www.youtube.com/user/LaureusTV"},
                        {"title": "Total Immersion: The Revolutionary Way To Swim Better, Faster, and Easier", "type": "Book", "link": "https://www.amazon.com/Total-Immersion-Revolutionary-Better-Faster/dp/0743253434"},
                        {"title": "Best Swimming Drills 2024", "type": "Article", "link": "https://www.swimmingcoach.com/best-swimming-drills-2024"}
                    ]
                },
                "Traveling": {
                    "Adventure": [
                        {"title": "Lonely Planet Adventure Travel Guide", "type": "Website", "link": "https://www.lonelyplanet.com/"},
                        {"title": "Best Adventure Travel Destinations", "type": "Article", "link": "https://www.nationalgeographic.com/adventure/travel"},
                        {"title": "Top Adventure Travel Spots 2024", "type": "Article", "link": "https://www.travelandleisure.com/top-adventure-travel-spots-2024"}
                    ],
                    "Cultural": [
                        {"title": "Cultural Travel Guide", "type": "Website", "link": "https://www.culturaltravelguide.com/"},
                        {"title": "UNESCO World Heritage Sites", "type": "Website", "link": "https://whc.unesco.org/"},
                        {"title": "Top Cultural Destinations 2024", "type": "Article", "link": "https://www.cntraveler.com/top-cultural-destinations-2024"}
                    ],
                    "Beach": [
                        {"title": "Top Beach Destinations", "type": "Website", "link": "https://www.travelchannel.com/interests/beaches/articles/top-beach-destinations"},
                        {"title": "Beach Travel Tips", "type": "Article", "link": "https://www.travelandleisure.com/travel-tips/beach"},
                        {"title": "Best Beaches 2024", "type": "Article", "link": "https://www.tripadvisor.com/best-beaches-2024"}
                    ],
                    "Mountain": [
                        {"title": "Mountain Travel Guide", "type": "Website", "link": "https://www.backpacker.com/"},
                        {"title": "Best Hiking Trails in the World", "type": "Article", "link": "https://www.nationalgeographic.com/adventure/adventures/best-hikes/"},
                        {"title": "Top Mountain Destinations 2024", "type": "Article", "link": "https://www.outsideonline.com/top-mountain-destinations-2024"}
                    ],
                    "City": [
                        {"title": "Top City Destinations", "type": "Website", "link": "https://www.cntraveler.com/galleries/2015-09-08/world-s-best-cities"},
                        {"title": "City Travel Tips", "type": "Article", "link": "https://www.thetravel.com/best-city-travel-tips/"},
                        {"title": "Best Cities to Visit 2024", "type": "Article", "link": "https://www.lonelyplanet.com/best-cities-to-visit-2024"}
                    ]
                }
            }.get(st.session_state.user_data["main_field"], {}).get(st.session_state.user_data["sub_field"], [])

            # Filter resources
            filtered_resources = [r for r in resources if search_query.lower() in r['title'].lower()]

            # Display Resources
            for resource in filtered_resources:
                with st.container():
                    st.markdown(f"<div class='resource-card'>", unsafe_allow_html=True)
                    st.markdown(f"### [{resource['title']}]({resource['link']})")
                    st.markdown(f"**Type:** {resource['type']}")
                    
                    # Favorites
                    col1, col2 = st.columns([1,3])
                    with col1:
                        if st.button(f"⭐ Add to Favorites", key=f"fav_{resource['title']}"):
                            if resource not in st.session_state.favorites:
                                st.session_state.favorites.append(resource)
                    
                    # Reviews
                    with st.expander("💬 Add Review"):
                        review = st.text_area("Your review:", key=f"review_{resource['title']}")
                        if st.button("Submit Review", key=f"submit_{resource['title']}"):
                            if resource['title'] not in st.session_state.reviews:
                                st.session_state.reviews[resource['title']] = []
                            st.session_state.reviews[resource['title']].append(review)
                            
                            # Ask user if they want to send the review via email
                            send_to_email = st.checkbox("Send this review to the admin via email", key=f"email_checkbox_{resource['title']}")
                            if send_to_email:
                                user_email = st.text_input("Enter your email (optional):", key=f"user_email_{resource['title']}")
                                if send_email(review, user_email):
                                    st.success("Review submitted and email sent successfully!")
                                else:
                                    st.error("Failed to send email. Please try again.")
                        
                        if resource['title'] in st.session_state.reviews:
                            st.markdown("### User Reviews")
                            for idx, rev in enumerate(st.session_state.reviews[resource['title']], 1):
                                st.markdown(f"<div class='review-section'>📝 Review {idx}: {rev}</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)

            # Favorites Section
            with st.expander("❤️ My Favorites"):
                if st.session_state.favorites:
                    for fav in st.session_state.favorites:
                        st.markdown(f"### {fav['title']}")
                        st.markdown(f"Type: {fav['type']}")
                else:
                    st.write("No favorites yet!")

        # PDF Report Generation
        st.markdown("<div class='section-spacing'></div>", unsafe_allow_html=True)
        st.markdown("<div class='big-font'>📄 Download Progress Report</div>", unsafe_allow_html=True)
        
        if st.button("📥 Download PDF Report"):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, "Learning Path Report")
            y = 730
            for key, value in st.session_state.user_data.items():
                if isinstance(value, list):
                    c.drawString(100, y, f"{key}:")
                    y -= 20
                    for item in value:
                        c.drawString(120, y, f"- {item}")
                        y -= 20
                else:
                    c.drawString(100, y, f"{key}: {value}")
                    y -= 20
            c.save()
            buffer.seek(0)
            st.download_button(
                label="Download PDF",
                data=buffer,
                file_name="learning_path_report.pdf",
                mime="application/pdf"
            )

    # Footer
    st.markdown("<div class='medium-font footer'>© 2024 Learning Path Creator. All rights reserved.</div>", unsafe_allow_html=True)

# Main function to run the app
def main():
    initialize_session_states()
    configure_page()
    apply_custom_css()
    show_onboarding_tutorial()
    main_app()

if __name__ == "__main__":
    main()