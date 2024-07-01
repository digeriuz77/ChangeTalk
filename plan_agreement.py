import streamlit as st

def create_plan():
    st.subheader("Creating Your Plan")

    st.write("Let's work together to create a viable plan for your change.")

    changes = st.text_area("The changes I want to make are:", help="List specific areas or ways in which you want to change. Include positive goals (beginning, increasing, improving behavior)")

    reasons = st.text_area("The most important reasons why I want to make these changes are:", help="What are some likely consequences of action and inaction? Which motivations for change seem most important to you?")

    steps = st.text_area("The steps I plan to take in changing are:", help="How do you plan to achieve the goals? Within the general plan, what are some specific first steps you might take? When, where and how will these steps be taken?")

    support = st.text_area("The ways other people can help me are:", help="List specific ways that others can help support you in your change attempt. How will you go about eliciting others' support?")

    success_indicators = st.text_area("I will know that my plan is working if:", help="What do you hope will happen as a result of the change? What benefits can you expect from the change?")

    potential_obstacles = st.text_area("Some things that could interfere with my plan are:", help="Anticipate situations or changes that could undermine the plan. What could go wrong? How might you stick with the plan despite the changes or setbacks?")

    plan_summary = f"""
    Change Plan:

    1. The changes I want to make are:
    {changes}

    2. The most important reasons why I want to make these changes are:
    {reasons}

    3. The steps I plan to take in changing are:
    {steps}

    4. The ways other people can help me are:
    {support}

    5. I will know that my plan is working if:
    {success_indicators}

    6. Some things that could interfere with my plan are:
    {potential_obstacles}
    """

    st.text_area("Plan Summary:", plan_summary, height=400)

    if st.button("Complete Plan"):
        return plan_summary
    else:
        return None
