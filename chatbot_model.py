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


# Create TF-IDF model
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


def get_troubleshooting_steps(issue):

    issue = issue.lower().strip()

    # First try exact match
    issue_data = troubleshooting_df[
        troubleshooting_df["Issue"]
        .str.lower()
        .str.strip()
        == issue
    ]

    # If exact match is not found,
    # try partial keyword matching
    if len(issue_data) == 0:

        keywords = issue.split()

        mask = troubleshooting_df["Issue"].str.lower().apply(
            lambda x: all(word in x for word in keywords)
        )

        issue_data = troubleshooting_df[mask]

    return issue_data.reset_index(drop=True)


# =========================================================
# FIND SUPPORT TEAM
# =========================================================

def get_support_team(issue):

    issue = issue.lower().strip()

    result = df[
        df["Question"]
        .str.lower()
        .str.strip()
        == issue
    ]

    if len(result) > 0:

        return result.iloc[0]["Support_Team"]

    return "Helpdesk Support Team"


# =========================================================
# CHECK USER RESPONSE
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
        "no",
        "no change",
        "problem remains"
    ]

    return any(
        phrase in message
        for phrase in not_working_phrases
    )


def is_not_understood(message):

    message = message.lower().strip()

    phrases = [
        "don't understand",
        "dont understand",
        "not understand",
        "how",
        "what does this mean",
        "explain",
        "can you explain"
    ]

    return any(
        phrase in message
        for phrase in phrases
    )


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
        "working"
    ]

    return any(
        phrase in message
        for phrase in phrases
    )


# =========================================================
# INTERACTIVE TROUBLESHOOTING
# =========================================================

def start_troubleshooting(issue):

    steps = get_troubleshooting_steps(issue)

    if len(steps) == 0:

        print(
            "\n🤖 Sorry, I could not find a troubleshooting guide "
            "for this issue."
        )

        return


    print(
        "\n🤖 AI Helpdesk Assistant"
    )

    print(
        "\nI will guide you step-by-step."
    )


    # -----------------------------------------------------
    # GO THROUGH EACH STEP
    # -----------------------------------------------------

    for index in range(len(steps)):

        step = steps.iloc[index]


        print(
            f"\n🔹 Step {index + 1}: "
            f"{step['Step']}"
        )


        # Number of times additional guidance was given
        additional_help = 0


        while True:

            user_message = input(
                "\nYour response: "
            )


            message = user_message.lower().strip()


            # -------------------------------------------------
            # USER SAYS NOT WORKING
            # -------------------------------------------------

            if is_not_working(message):

                if additional_help == 0:

                    print("\n🤖 AI:")

                    print(
                        "No problem. Let's troubleshoot it further. 🔧\n\n"
                        + step["If_Not_Working"]
                    )

                    additional_help += 1

                    continue


                else:

                    print("\n🤖 AI:")

                    print(
                        "Okay. This step did not resolve the issue. "
                        "Let's move to the next troubleshooting step."
                    )

                    break


            # -------------------------------------------------
            # USER DOES NOT UNDERSTAND
            # -------------------------------------------------

            elif is_not_understood(message):

                print("\n🤖 AI:")

                print(
                    "No problem 😊\n\n"
                    "Let me explain this step:\n\n"
                    + step["If_Dont_Understand"]
                )

                continue


            # -------------------------------------------------
            # USER COMPLETED THE STEP
            # -------------------------------------------------

            elif is_completed(message):

                print("\n🤖 AI:")

                print(
                    "Great! ✅ This step is completed."
                )

                break


            # -------------------------------------------------
            # UNKNOWN RESPONSE
            # -------------------------------------------------

            else:

                print("\n🤖 AI:")

                print(
                    "I understand. Please tell me if the "
                    "step worked, is still not working, "
                    "or you need an explanation."
                )


    # =====================================================
    # FINAL SUPPORT MESSAGE
    # =====================================================

    support_team = get_support_team(issue)


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


start_troubleshooting(issue)