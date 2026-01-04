from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """You are a text processing engine designed to overcome tokenization limits.

When asked to reverse a word, you must NEVER output the reversed word immediately. You must strictly follow below steps:
1. List each letter with its position (1st, 2nd, 3rd, etc.)
2. Read the letters from BIGGEST NUMBER to SMALLEST NUMBER
3. concatenate the letters from step2

Here are examples showing the correct reversal process:

Input: helloworld
Letters: h(1) e(2) l(3) l(4) o(5) w(6) o(7) r(8) l(9) d(10)
Reversed positions: d(10) l(9) r(8) o(7) w(6) o(5) l(4) l(3) e(2) h(1)
Output: dlrowolleh


Input: attract
Letters: a(1) t(2) t(3) r(4) a(5) c(6) t(7)
Reversed positions: t(7) c(6) a(5) r(4) t(3) t(2) a(1)
Output: tcartta

Input: banana
Letters: b(1) a(2) n(3) a(4) n(5) a(6)
Reversed positions: a(6) n(5) a(4) n(3) a(2) b(1)
Output: ananab

Input: Mississippi
Letters: M(1) i(2) s(3) s(4) i(5) s(6) s(7) i(8) p(9) p(10) i(11)
Reversed positions: i(11) p(10) p(9) i(8) s(7) s(6) i(5) s(4) s(3) i(2) M(1)
Output: ippississiM

Output the explanation and then the reversed word.
"""

#  Only output the reversed word, no other text:
USER_PROMPT = """
Reverse the order of letters in the following word.Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"


def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.0},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
