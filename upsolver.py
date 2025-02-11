import requests
import streamlit as st

# Function to get last 10 contests the user participated in
def get_last_10_contests(handle):
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    response = requests.get(url).json()

    if response["status"] != "OK":
        return None

    contests = response["result"]
    last_10 = sorted(contests, key=lambda x: x["contestId"], reverse=True)[:10]

    return [contest["contestId"] for contest in last_10]

# Function to get all solved problems of the user
def get_solved_problems(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    response = requests.get(url).json()

    if response["status"] != "OK":
        return None

    solved = set()
    for sub in response["result"]:
        if sub["verdict"] == "OK":
            problem = sub["problem"]
            problem_id = f"{problem['contestId']}-{problem['index']}"
            solved.add(problem_id)

    return solved

# Function to find the first unsolved problem from each of the last 10 contests
def get_unsolved_problems_from_contests(handle):
    contests = get_last_10_contests(handle)
    solved = get_solved_problems(handle)
    unsolved_problems = []

    if contests is None or solved is None:
        return None

    for contest_id in contests:
        url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=100&showUnofficial=true"
        response = requests.get(url).json()

        if response["status"] != "OK":
            continue

        problems = response["result"]["problems"]
        found_unsolved = False  # Ensure only one problem per contest is selected

        for problem in problems:
            problem_id = f"{contest_id}-{problem['index']}"
            if problem_id not in solved:
                unsolved_problems.append({
                    "contest_id": contest_id,
                    "name": problem["name"],
                    "rating": problem.get("rating", "Unknown"),
                    "link": f"https://codeforces.com/contest/{contest_id}/problem/{problem['index']}"
                })
                found_unsolved = True
                break  # Stop after selecting the first unsolved problem

        # If all problems are solved in a contest, add a placeholder
        if not found_unsolved:
            unsolved_problems.append({
                "contest_id": contest_id,
                "name": "🎉 All problems solved!",
                "rating": "N/A",
                "link": f"https://codeforces.com/contest/{contest_id}"
            })

    return unsolved_problems

# Streamlit UI
st.title("🚀 Codeforces Upsolver")
handle = st.text_input("Enter your Codeforces Handle")

if st.button("Find Problems to Upsolve"):
    problems = get_unsolved_problems_from_contests(handle)

    if problems:
        st.write(f"### ✅ Upsolve And Improve")
        for problem in problems:
            st.markdown(f"🔹 **[{problem['name']}]({problem['link']})** (Contest `{problem['contest_id']}`) - Rating: `{problem['rating']}`")
    else:
        st.write("🎉 You have solved all problems from the last 10 contests!")