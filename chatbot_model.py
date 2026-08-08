import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load Knowledge Base
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

def chatbot_response(user_question):

    # Convert user question into vector
    user_vector = vectorizer.transform(
        [user_question]
    )

    # Compare with knowledge base
    similarity = cosine_similarity(
        user_vector,
        knowledge_vectors
    )

    # Find best matching issue
    best_match = similarity.argmax()

    best_score = similarity[0][best_match]

    # If question is not relevant
    if best_score < 0.15:
        return {
            "found": False,
            "message": (
                "Sorry, I could not understand the issue clearly. "
                "Please provide more details or contact the Helpdesk Support Team."
            )
        }

    # Get matching knowledge article
    result = df.iloc[best_match]

    return {
        "found": True,
        "question": result["Question"],
        "category": result["Category"],
        "steps": result["Steps"],
        "resolution": result["Resolution"],
        "support_team": result["Support_Team"]
    }
    # -------------------------------------------------
# INTERACTIVE TROUBLESHOOTING
# -------------------------------------------------

troubleshooting_df = pd.read_csv(
    "Knowledge_Base/troubleshooting_steps.csv"
)


def get_troubleshooting_steps(issue):

    issue_data = troubleshooting_df[
        troubleshooting_df["Issue"].str.lower()
        == issue.lower()
    ]

    return issue_data.reset_index(drop=True)


def get_step_response(step, user_message):

    message = user_message.lower().strip()

    # User does not understand the step
    if any(word in message for word in [
        "don't understand",
        "dont understand",
        "not understand",
        "how",
        "what does this mean",
        "explain"
    ]):

        return (
            "No problem 😊\n\n"
            "Let me explain this step:\n\n"
            + step["If_Dont_Understand"]
        )


    # User says step is still not working
    if any(word in message for word in [
        "still not working",
        "still not woking"
        "not working",
        "doesn't work",
        "doesnt work",
        "not fixed",
        "no",
        "issue remains"
    ]):

        return (
            "No problem. Let's troubleshoot it further. 🔧\n\n"
            + step["If_Not_Working"]
        )


    # User says it is completed
    if any(word in message for word in [
        "done",
        "working",
        "worked",
        "fixed",
        "resolved",
        "yes"
    ]):

        return "Great! ✅ This step is completed."


    return (
        "I understand. Please tell me whether this step "
        "worked or you are still facing the issue."
    )


def start_troubleshooting(issue):

    steps = get_troubleshooting_steps(issue)

    if len(steps) == 0:

        return None

    return steps




issue = input(
    "\nEnter your issue: "
)

steps = start_troubleshooting(issue)


if steps is None:

    print(
        "\n🤖 Sorry, I could not find a troubleshooting guide "
        "for this issue."
    )

else:

    print(
        "\n🤖 AI Helpdesk Assistant"
    )

    print(
        "\nI will guide you step-by-step."
    )
    print("\nDEBUG - Total Steps:", len(steps))
    print(steps[["Issue", "Step_Number", "Step"]])

    for index in range(len(steps)):

        step = steps.iloc[index]

    print(
        f"\n🔹 Step {index + 1}: "
        f"{step['Step']}"
    )

    step_attempt = 0

    while step_attempt < 2:

        user_message = input(
            "\nYour response: "
        )

        message = user_message.lower().strip()

        # -----------------------------------------
        # NOT WORKING
        # -----------------------------------------

        if any(word in message for word in [
            "still not working",
            "stil not working",
            "not working",
            "doesn't work",
            "doesnt work",
            "not fixed",
            "not solve",
            "not solved",
            "issue remains",
            "no"
        ]):

            step_attempt += 1

            print("\n🤖 AI:")

            print(
                "No problem. Let's troubleshoot it further. 🔧\n\n"
                + step["If_Not_Working"]
            )

            if step_attempt == 2:

                print("\n🤖 AI:")

                print(
                    "Okay. This step did not resolve the issue. "
                    "Let's move to the next troubleshooting step."
                )

                break

            continue

        # -----------------------------------------
        # DON'T UNDERSTAND
        # -----------------------------------------

        elif any(word in message for word in [
            "don't understand",
            "dont understand",
            "not understand",
            "how",
            "what does this mean",
            "explain"
        ]):

            print("\n🤖 AI:")

            print(
                "No problem 😊\n\n"
                "Let me explain this step:\n\n"
                + step["If_Dont_Understand"]
            )

            continue

        # -----------------------------------------
        # COMPLETED
        # -----------------------------------------

        elif any(word in message for word in [
            "done",
            "working",
            "worked",
            "fixed",
            "resolved",
            "yes"
        ]):

            print("\n🤖 AI:")

            print(
                "Great! ✅ This step is completed."
            )

            break

        # -----------------------------------------
        # UNKNOWN RESPONSE
        # -----------------------------------------

        else:

            print("\n🤖 AI:")

            print(
                "Please tell me whether the step worked, "
                "is still not working, or you need an explanation."
            )


print("\n🆘 All troubleshooting steps have been completed.")

print(
    "If the issue is still not resolved, "
    "please contact the Application Support for further assistance."
)