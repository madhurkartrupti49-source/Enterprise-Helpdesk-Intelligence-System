import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# LOAD KNOWLEDGE BASE
# =========================================================

knowledge_base = pd.read_csv(
    "Knowledge_Base/knowledge_base.csv"
)

troubleshooting = pd.read_csv(
    "Knowledge_Base/troubleshooting_steps.csv"
)


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):
    return str(text).lower().strip()


# =========================================================
# PREPARE KNOWLEDGE BASE
# =========================================================

knowledge_base["Search_Text"] = (
    knowledge_base["Question"].fillna("")
    + " "
    + knowledge_base["Category"].fillna("")
    + " "
    + knowledge_base["Steps"].fillna("")
    + " "
    + knowledge_base["Resolution"].fillna("")
)

knowledge_vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

knowledge_vectors = knowledge_vectorizer.fit_transform(
    knowledge_base["Search_Text"]
)


# =========================================================
# PREPARE TROUBLESHOOTING SEARCH
# =========================================================

unique_issues = (
    troubleshooting["Issue"]
    .dropna()
    .drop_duplicates()
    .reset_index(drop=True)
)

troubleshooting_vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)

troubleshooting_vectors = (
    troubleshooting_vectorizer.fit_transform(
        unique_issues
    )
)


# =========================================================
# FIND TROUBLESHOOTING ISSUE
# =========================================================

def find_troubleshooting_issue(user_question):

    question = clean_text(user_question)

    # -----------------------------------------------------
    # OUTLOOK
    # -----------------------------------------------------

    if "outlook" in question:

        if any(phrase in question for phrase in [
            "not working",
            "not opening",
            "doesn't open",
            "doesnt open",
            "cannot open",
            "can't open",
            "cant open",
            "won't open",
            "wont open",
            "not starting",
            "not launching",
            "cannot access",
            "can't access",
            "cant access"
        ]):
            return "Outlook is not opening"


    # -----------------------------------------------------
    # VPN
    # -----------------------------------------------------

    if "vpn" in question:

        if any(phrase in question for phrase in [
            "not connecting",
            "not working",
            "cannot connect",
            "can't connect",
            "cant connect",
            "connection problem",
            "connection issue",
            "unable to connect"
        ]):
            return "VPN is not connecting"


    # -----------------------------------------------------
    # EMAIL RECEIVING
    # IMPORTANT: CHECK BEFORE EMAIL SENDING
    # -----------------------------------------------------

    if "email" in question or "emails" in question or "mail" in question:

        if any(phrase in question for phrase in [
            "not receiving",
            "not receive",
            "not coming",
            "not getting",
            "not arrived",
            "not arriving",
            "cannot receive",
            "can't receive",
            "cant receive",
            "emails are not coming",
            "emails not coming",
            "mail not coming",
            "mails not coming"
        ]):
            return "Emails are not receiving"


    # -----------------------------------------------------
    # EMAIL SENDING
    # -----------------------------------------------------

    if "email" in question or "emails" in question or "mail" in question:

        if any(phrase in question for phrase in [
            "not sending",
            "not send",
            "cannot send",
            "can't send",
            "cant send",
            "unable to send",
            "email won't send",
            "email wont send"
        ]):
            return "Emails are not sending"


    # -----------------------------------------------------
    # EMAIL SYNC
    # -----------------------------------------------------

    if "email" in question or "emails" in question or "mail" in question:

        if any(phrase in question for phrase in [
            "not syncing",
            "not sync",
            "sync problem",
            "sync issue",
            "synchronization problem"
        ]):
            return "Email client is not syncing"


    # -----------------------------------------------------
    # GENERAL EMAIL
    # -----------------------------------------------------

    if "email" in question or "emails" in question or "mail" in question:

        if any(phrase in question for phrase in [
            "not working",
            "problem",
            "issue",
            "cannot access",
            "can't access",
            "cant access",
            "unable to access",
            "not accessible"
        ]):
            return "Email is not working"


    # -----------------------------------------------------
    # TF-IDF FALLBACK
    # -----------------------------------------------------

    user_vector = troubleshooting_vectorizer.transform(
        [question]
    )

    similarity = cosine_similarity(
        user_vector,
        troubleshooting_vectors
    )

    best_index = similarity.argmax()
    best_score = similarity[0][best_index]

    if best_score < 0.15:
        return None

    return unique_issues.iloc[best_index]


# =========================================================
# GET TROUBLESHOOTING STEPS
# =========================================================

def get_steps(issue):

    issue_clean = clean_text(issue)

    steps = troubleshooting[
        troubleshooting["Issue"]
        .fillna("")
        .apply(clean_text)
        == issue_clean
    ].reset_index(drop=True)

    return steps


# =========================================================
# FIND KNOWLEDGE BASE ANSWER
# =========================================================

# =========================================================
# FIND KNOWLEDGE BASE ANSWER
# =========================================================

def find_knowledge_answer(question):

    question = clean_text(question)

    # -----------------------------------------------------
    # DIRECT KEYWORD MATCHING
    # -----------------------------------------------------

    keyword_matches = {
        "sla": ["sla", "service level agreement"],
        "mttr": ["mttr", "mean time to resolution"],
        "escalation": ["escalation", "escalate"],
        "helpdesk": ["helpdesk", "help desk"],
        "incident": ["incident"],
        "service request": [
            "service request",
            "service requests"
        ],
        "ticket": [
            "ticket",
            "support ticket"
        ]
    }

    for topic, keywords in keyword_matches.items():

        if any(
            keyword in question
            for keyword in keywords
        ):

            # Search topic in Knowledge Base
            topic_text = (
                knowledge_base["Search_Text"]
                .fillna("")
                .str.lower()
            )

            matches = knowledge_base[
                topic_text.str.contains(
                    topic,
                    regex=False,
                    na=False
                )
            ]

            if len(matches) > 0:

                return matches.iloc[0]


    # -----------------------------------------------------
    # TF-IDF FALLBACK
    # -----------------------------------------------------

    user_vector = knowledge_vectorizer.transform(
        [question]
    )

    similarity = cosine_similarity(
        user_vector,
        knowledge_vectors
    )

    best_index = similarity.argmax()

    best_score = similarity[0][best_index]

    # Slightly lower threshold
    if best_score < 0.05:

        return None

    return knowledge_base.iloc[best_index]


# =========================================================
# NOT WORKING
# =========================================================

def is_not_working(message):

    message = clean_text(message)

    phrases = [
        "still not working",
        "stil not working",
        "still not woking",
        "not working",
        "does not work",
        "doesn't work",
        "doesnt work",
        "not fixed",
        "not solve",
        "not solved",
        "not resolved",
        "issue remains",
        "problem remains",
        "remains problem",
        "no change",
        "not okay",
        "not ok",
        "didn't work",
        "didnt work",
        "issue is still there",
        "problem is still there",
        "no"
    ]

    return any(
        phrase == message
        or message.startswith(phrase + " ")
        for phrase in phrases
    )


# =========================================================
# DON'T UNDERSTAND / EXPLANATION
# =========================================================

def is_not_understood(message):

    message = clean_text(message)

    phrases = [
        "how",
        "how to",
        "how do i",
        "dont understand",
        "don't understand",
        "not understand",
        "explain",
        "what does this mean",
        "can you explain",
        "what should i do",
        "what do i do",
        "what is",
        "whats",
        "what's",
        "meaning",
        "means"
    ]

    return any(
        phrase == message
        or message.startswith(phrase + " ")
        for phrase in phrases
    )


# =========================================================
# COMPLETED
# =========================================================

def is_completed(message):

    message = clean_text(message)

    phrases = [
        "done",
        "okay",
        "ok",
        "yes",
        "working",
        "working now",
        "worked",
        "fixed",
        "resolved",
        "solved",
        "it works",
        "its working",
        "it's working",
        "problem solved",
        "issue solved",
        "issue resolved"
    ]

    return any(
        phrase == message
        or message.startswith(phrase + " ")
        for phrase in phrases
    )


# =========================================================
# THANK YOU / END CONVERSATION
# =========================================================

def is_goodbye(message):

    message = clean_text(message)

    phrases = [
        "no thanks",
        "no thank you",
        "thanks",
        "thank you",
        "bye",
        "goodbye",
        "that's all",
        "thats all",
        "nothing else"
    ]

    return any(
        phrase == message
        for phrase in phrases
    )


# =========================================================
# SESSION FINISHED RESPONSE
# =========================================================

def is_session_finished_response(message):

    message = clean_text(message)

    phrases = [
        "ok",
        "okay",
        "yes",
        "thanks",
        "thank you",
        "no thanks",
        "no thank you",
        "issue solved",
        "issue solve",
        "problem solved",
        "problem is solved",
        "issue resolved",
        "problem resolved",
        "solved",
        "resolved",
        "fixed now",
        "it is fixed",
        "it works now",
        "working now"
    ]

    return any(
        phrase == message
        for phrase in phrases
    )


# =========================================================
# CONVERSATION STATE
# =========================================================

current_issue = None
current_steps = None
current_step_index = 0
additional_help_given = False

last_session_completed = False
waiting_for_new_question = False


# =========================================================
# RESET CONVERSATION
# =========================================================

def reset_conversation():

    global current_issue
    global current_steps
    global current_step_index
    global additional_help_given

    current_issue = None
    current_steps = None
    current_step_index = 0
    additional_help_given = False


# =========================================================
# START NEW ISSUE
# =========================================================

def start_new_issue(question):

    global current_issue
    global current_steps
    global current_step_index
    global additional_help_given
    global last_session_completed
    global waiting_for_new_question

    matched_issue = find_troubleshooting_issue(
        question
    )

    if matched_issue is None:
        return False

    steps = get_steps(
        matched_issue
    )

    if len(steps) == 0:
        return False

    current_issue = matched_issue
    current_steps = steps
    current_step_index = 0
    additional_help_given = False

    last_session_completed = False
    waiting_for_new_question = False

    return True


# =========================================================
# SHOW CURRENT STEP
# =========================================================

def show_current_step():

    if current_steps is None:
        return False

    if current_step_index >= len(current_steps):
        return False

    step = current_steps.iloc[
        current_step_index
    ]

    print(
        f"\n🔹 Step {current_step_index + 1}: "
        f"{step['Step']}"
    )

    return True


# =========================================================
# HANDLE CURRENT STEP
# =========================================================

def handle_response(message):

    global current_step_index
    global additional_help_given
    global last_session_completed
    global waiting_for_new_question

    if current_steps is None:
        return


    # -----------------------------------------------------
    # SAFETY CHECK
    # -----------------------------------------------------

    if current_step_index >= len(current_steps):

        last_session_completed = True
        waiting_for_new_question = True

        reset_conversation()

        print(
            "\n🤖 This troubleshooting session is already complete."
        )

        return


    step = current_steps.iloc[
        current_step_index
    ]


    # =====================================================
    # NOT WORKING
    # =====================================================

    if is_not_working(message):

        if not additional_help_given:

            print("\n🤖 AI:")

            print(
                "No problem. Let's troubleshoot it further. 🔧\n\n"
                + str(step["If_Not_Working"])
            )

            additional_help_given = True

            return

        else:

            print("\n🤖 AI:")

            print(
                "Okay. This step did not resolve the issue."
            )

            current_step_index += 1
            additional_help_given = False

            if current_step_index < len(current_steps):

                print(
                    "\nLet's move to the next step."
                )

                show_current_step()

            else:

                print(
                    "\n🆘 All troubleshooting steps have been completed."
                )

                print(
                    "\nThe issue could not be resolved "
                    "using the available troubleshooting steps."
                )

                print(
                    "\nPlease contact the appropriate "
                    "Support Team for further assistance."
                )

                print(
                    "\n🤖 You can ask me another IT Helpdesk "
                    "question whenever you are ready."
                )

                last_session_completed = True
                waiting_for_new_question = True

                reset_conversation()

            return


    # =====================================================
    # DON'T UNDERSTAND
    # =====================================================

    if is_not_understood(message):

        print("\n🤖 AI:")

        print(
            "No problem 😊\n\n"
            "Let me explain this step:\n\n"
            + str(step["If_Dont_Understand"])
        )

        return


    # =====================================================
    # COMPLETED
    # =====================================================

    if is_completed(message):

        print("\n🤖 AI:")

        print(
            "Great! ✅ This step is completed."
        )

        current_step_index += 1
        additional_help_given = False

        if current_step_index < len(current_steps):

            print(
                "\nLet's move to the next step."
            )

            show_current_step()

        else:

            print(
                "\n🎉 All troubleshooting steps have been completed."
            )

            print(
                "\nIf the issue is still not resolved, "
                "please contact the appropriate Support Team."
            )

            print(
                "\n🤖 You can ask me another IT Helpdesk "
                "question whenever you are ready."
            )

            last_session_completed = True
            waiting_for_new_question = True

            reset_conversation()

        return


    # =====================================================
    # UNKNOWN RESPONSE
    # =====================================================

    print("\n🤖 AI:")

    print(
        "I understand. Please tell me:"
    )

    print(
        "  • Done / OK if the step worked"
    )

    print(
        "  • Still not working if the issue remains"
    )

    print(
        "  • How / Explain if you need help"
    )


# =========================================================
# MAIN CHATBOT
# =========================================================

print(
    "\n🤖 AI Helpdesk Assistant"
)

print(
    "----------------------------"
)

print(
    "\nAsk me any IT Helpdesk question."
)

print(
    "Type 'exit' to stop."
)


while True:

    user_input = input(
        "\nYou: "
    ).strip()

    message = clean_text(
        user_input
    )


    # =====================================================
    # EXIT
    # =====================================================

    if message == "exit":

        print(
            "\n🤖 Goodbye! 👋"
        )

        break


    # =====================================================
    # EMPTY INPUT
    # =====================================================

    if message == "":

        print(
            "\n🤖 Please enter an IT Helpdesk question."
        )

        continue


    # =====================================================
    # GOODBYE / THANKS
    # =====================================================

    if waiting_for_new_question and is_goodbye(message):

        print(
            "\n🤖 You're welcome! 😊"
        )

        print(
            "\nYou can ask me another IT Helpdesk question "
            "whenever you are ready."
        )

        continue


    # =====================================================
    # AFTER SESSION COMPLETED
    # =====================================================

    if last_session_completed:

        # -------------------------------------------------
        # Customer says OK / Thanks / Solved
        # -------------------------------------------------

        if is_session_finished_response(message):

            print(
                "\n🤖 You're welcome! 😊"
            )

            print(
                "\nYou can ask me another IT Helpdesk question "
                "whenever you are ready."
            )

            waiting_for_new_question = True

            continue

        # -------------------------------------------------
        # Customer asks a NEW question
        # -------------------------------------------------

        last_session_completed = False
        waiting_for_new_question = False


    # =====================================================
    # ACTIVE TROUBLESHOOTING
    # =====================================================

    if current_steps is not None:

        handle_response(
            user_input
        )

        continue


    # =====================================================
    # NEW TROUBLESHOOTING ISSUE
    # =====================================================

    matched = start_new_issue(
        user_input
    )

    if matched:

        print(
            "\n🤖 I understand your issue as:"
        )

        print(
            f"   {current_issue}"
        )

        print(
            "\nI will guide you step-by-step."
        )

        show_current_step()

        continue


    # =====================================================
    # KNOWLEDGE BASE ANSWER
    # =====================================================

    result = find_knowledge_answer(
        user_input
    )

    if result is not None:

        print(
            "\n🤖 AI:"
        )

        print(
            f"\n📂 Category: {result['Category']}"
        )

        print(
            "\n🔧 Recommended Solution:"
        )

        print(
            result["Resolution"]
        )

        print(
            "\n🆘 If the issue continues:"
        )

        print(
            f"Please contact the {result['Support_Team']}."
        )

        continue


    # =====================================================
    # UNKNOWN QUESTION
    # =====================================================

    print(
        "\n🤖 AI:"
    )

    print(
        "I could not find enough information in the "
        "Helpdesk Knowledge Base to answer this question."
    )

    print(
        "\nPlease provide more details about the IT issue."
    )