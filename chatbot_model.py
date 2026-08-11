import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# LOAD KNOWLEDGE BASE
# =========================================================

df = pd.read_csv(
    "Knowledge_Base/knowledge_base.csv"
)


# Combine question and category
df["Search_Text"] = (
    df["Question"].fillna("")
    + " "
    + df["Category"].fillna("")
)


# =========================================================
# CREATE MAIN CHATBOT TF-IDF MODEL
# =========================================================

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english"
)


knowledge_vectors = vectorizer.fit_transform(
    df["Search_Text"]
)


# Save chatbot model
joblib.dump(
    vectorizer,
    "Models/chatbot_vectorizer.pkl"
)

joblib.dump(
    knowledge_vectors,
    "Models/chatbot_vectors.pkl"
)

joblib.dump(
    df,
    "Models/chatbot_knowledge.pkl"
)


print("Chatbot Knowledge Base Loaded Successfully!")
print("Total Knowledge Articles:", len(df))
print("Chatbot Model Created Successfully!")


# =========================================================
# CHATBOT RESPONSE
# =========================================================

def chatbot_response(user_question):

    user_question = user_question.lower().strip()

    user_vector = vectorizer.transform(
        [user_question]
    )

    similarity = cosine_similarity(
        user_vector,
        knowledge_vectors
    )

    best_match = similarity.argmax()

    best_score = similarity[0][best_match]


    if best_score < 0.15:

        return {
            "found": False,
            "message": (
                "Sorry, I could not understand the issue clearly. "
                "Please provide more details or contact the Helpdesk Support Team."
            )
        }


    result = df.iloc[best_match]


    return {
        "found": True,
        "question": result["Question"],
        "category": result["Category"],
        "steps": result["Steps"],
        "resolution": result["Resolution"],
        "support_team": result["Support_Team"]
    }


# =========================================================
# LOAD TROUBLESHOOTING KNOWLEDGE
# =========================================================

troubleshooting_df = pd.read_csv(
    "Knowledge_Base/troubleshooting_steps.csv"
)


# =========================================================
# CREATE TROUBLESHOOTING ISSUE MODEL
# =========================================================

troubleshooting_issues = (
    troubleshooting_df["Issue"]
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
        troubleshooting_issues
    )
)


# =========================================================
# FIND BEST TROUBLESHOOTING ISSUE
# =========================================================

def get_troubleshooting_steps(user_issue):

    user_issue = user_issue.lower().strip()


    # -----------------------------------------------------
    # FIRST: EXACT MATCH
    # -----------------------------------------------------

    exact_match = troubleshooting_df[
        troubleshooting_df["Issue"]
        .str.lower()
        .str.strip()
        == user_issue
    ]


    if len(exact_match) > 0:

        return (
            exact_match.reset_index(drop=True),
            exact_match.iloc[0]["Issue"]
        )


    # -----------------------------------------------------
    # SECOND: AI / TF-IDF SIMILARITY MATCH
    # -----------------------------------------------------

    user_vector = troubleshooting_vectorizer.transform(
        [user_issue]
    )


    similarity = cosine_similarity(
        user_vector,
        troubleshooting_vectors
    )


    best_match_index = similarity.argmax()

    best_score = similarity[0][best_match_index]


    matched_issue = troubleshooting_issues.iloc[
        best_match_index
    ]


    # -----------------------------------------------------
    # MINIMUM SIMILARITY
    # -----------------------------------------------------

    if best_score < 0.15:

        return None, None


    # Get all steps for matched issue
    issue_data = troubleshooting_df[
        troubleshooting_df["Issue"]
        .str.lower()
        .str.strip()
        == matched_issue.lower().strip()
    ]


    return (
        issue_data.reset_index(drop=True),
        matched_issue
    )


# =========================================================
# FIND SUPPORT TEAM
# =========================================================

def get_support_team(issue):

    issue = issue.lower().strip()


    # Exact match in knowledge base
    result = df[
        df["Question"]
        .str.lower()
        .str.strip()
        == issue
    ]


    if len(result) > 0:

        return result.iloc[0]["Support_Team"]


    # -----------------------------------------------------
    # Try AI matching if exact match is not available
    # -----------------------------------------------------

    result = chatbot_response(issue)


    if result["found"]:

        return result["support_team"]


    return "Helpdesk Support Team"


# =========================================================
# CHECK IF USER SAYS ISSUE IS NOT WORKING
# =========================================================

def is_not_working(message):

    message = message.lower().strip()


    not_working_phrases = [
        "still not working",
        "stil not working",
        "still not woking",
        "not working",
        "doesn't work",
        "doesnt work",
        "not fixed",
        "not solve",
        "not solved",
        "issue remains",
        "no change",
        "problem remains",
        "not resolved",
        "no",
        "remains problem",
        "problem still exists",
        "issue still exists",
        "still having problem",
        "still facing issue",
    ]


    return any(
        phrase in message
        for phrase in not_working_phrases
    )


# =========================================================
# CHECK IF USER DOES NOT UNDERSTAND
# =========================================================

def is_not_understood(message):

    message = message.lower().strip()


    phrases = [
        "don't understand",
        "dont understand",
        "not understand",
        "how",
        "what does this mean",
        "explain",
        "can you explain",
        "i don't know how"
    ]


    return any(
        phrase in message
        for phrase in phrases
    )


# =========================================================
# CHECK IF USER COMPLETED THE STEP
# =========================================================

def is_completed(message):

    message = message.lower().strip()


    phrases = [
        "done",
        "working now",
        "worked",
        "fixed",
        "resolved",
        "yes",
        "it works",
        "working",
        "solved"
    ]


    return any(
        phrase in message
        for phrase in phrases
    )


# =========================================================
# INTERACTIVE TROUBLESHOOTING
# =========================================================

def start_troubleshooting(user_issue):


    # -----------------------------------------------------
    # FIND BEST MATCH
    # -----------------------------------------------------

    steps, matched_issue = get_troubleshooting_steps(
        user_issue
    )


    # -----------------------------------------------------
    # ISSUE NOT FOUND
    # -----------------------------------------------------

    if steps is None:

        print(
            "\n🤖 Sorry, I could not find a suitable "
            "troubleshooting guide for this issue."
        )

        print(
            "\nPlease provide a little more detail "
            "about the problem."
        )

        return


    # -----------------------------------------------------
    # START CHATBOT
    # -----------------------------------------------------

    print(
        "\n🤖 AI Helpdesk Assistant"
    )


    print(
        "\nI will guide you step-by-step."
    )


    # -----------------------------------------------------
    # GO THROUGH EACH TROUBLESHOOTING STEP
    # -----------------------------------------------------

    for index in range(len(steps)):


        step = steps.iloc[index]


        print(
            f"\n🔹 Step {index + 1}: "
            f"{step['Step']}"
        )


        # Tracks whether additional guidance
        # has already been given
        additional_help = False


        while True:


            user_message = input(
                "\nYour response: "
            )


            message = user_message.lower().strip()


            # =================================================
            # USER SAYS NOT WORKING
            # =================================================

            if is_not_working(message):


                if not additional_help:


                    print(
                        "\n🤖 AI:"
                    )


                    print(
                        "No problem. Let's troubleshoot it further. 🔧\n\n"
                        + str(step["If_Not_Working"])
                    )


                    additional_help = True


                    continue


                else:


                    print(
                        "\n🤖 AI:"
                    )


                    print(
                        "Okay. This step did not resolve the issue. "
                        "Let's move to the next troubleshooting step."
                    )


                    break


            # =================================================
            # USER DOES NOT UNDERSTAND
            # =================================================

            elif is_not_understood(message):


                print(
                    "\n🤖 AI:"
                )


                print(
                    "No problem 😊\n\n"
                    "Let me explain this step:\n\n"
                    + str(step["If_Dont_Understand"])
                )


                continue


            # =================================================
            # USER COMPLETED THE STEP
            # =================================================

            elif is_completed(message):


                print(
                    "\n🤖 AI:"
                )


                print(
                    "Great! ✅ This step is completed."
                )


                break


            # =================================================
            # UNKNOWN RESPONSE
            # =================================================

            else:


                print(
                    "\n🤖 AI:"
                )


                print(
                    "I understand. Please tell me if the "
                    "step worked, is still not working, "
                    "or you need an explanation."
                )


    # =========================================================
    # FINAL SUPPORT MESSAGE
    # =========================================================

    support_team = get_support_team(
        matched_issue
    )


    print(
        "\n🆘 All troubleshooting steps have been completed."
    )


    print(
        "\nThe issue could not be resolved using "
        "the available troubleshooting steps."
    )


    print(
        f"\nPlease contact the {support_team} "
        "for further assistance."
    )


# =========================================================
# START CHATBOT
# =========================================================

issue = input(
    "\nEnter your issue: "
)


start_troubleshooting(
    issue
)